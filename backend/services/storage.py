"""Media storage: Cloudflare R2 when configured, local disk otherwise.

Railway's filesystem is ephemeral, so the local backend is a development-only
fallback -- anything written there disappears on the next redeploy. Call
``storage_status()`` to see which backend a running instance actually picked.
"""

import asyncio
import logging
import os
import uuid

import aiofiles
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

_REQUIRED_R2_VARS = ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_PUBLIC_URL")


def _missing_r2_vars() -> list[str]:
    return [name for name in _REQUIRED_R2_VARS if not os.getenv(name)]


def r2_enabled() -> bool:
    """R2 is used when explicitly enabled *or* when fully configured.

    Reading the env at call time (rather than import time) means a Railway
    variable change takes effect on restart without a code change, and makes
    the behaviour testable.
    """
    explicit = os.getenv("R2_ENABLED", "").strip().lower()
    if explicit in ("false", "0", "no"):
        return False
    if _missing_r2_vars():
        if explicit in ("true", "1", "yes"):
            logger.error(
                "R2_ENABLED is set but these variables are missing: %s. "
                "Falling back to local disk, which is EPHEMERAL on Railway.",
                ", ".join(_missing_r2_vars()),
            )
        return False
    return True


def storage_status() -> dict:
    """Human-readable description of the active backend, for diagnostics."""
    missing = _missing_r2_vars()
    if r2_enabled():
        return {
            "backend": "r2",
            "bucket": os.getenv("R2_BUCKET_NAME", "vernaculearn-media"),
            "public_url": os.getenv("R2_PUBLIC_URL"),
            "persistent": True,
        }
    return {
        "backend": "local",
        "missing_r2_vars": missing,
        "persistent": False,
        "warning": (
            "Uploads are written to the container filesystem and are lost on every "
            "redeploy. Configure R2 for production."
        ),
    }


def _get_r2_client():
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


async def _upload_to_r2(content: bytes, key: str, content_type: str) -> str:
    bucket = os.getenv("R2_BUCKET_NAME", "vernaculearn-media")
    public_url = (os.getenv("R2_PUBLIC_URL") or "").rstrip("/")
    if not public_url:
        raise HTTPException(500, "Media storage is misconfigured (R2_PUBLIC_URL is not set).")

    def _sync():
        _get_r2_client().put_object(
            Bucket=bucket, Key=key, Body=content, ContentType=content_type
        )

    try:
        await asyncio.to_thread(_sync)
    except Exception as exc:
        logger.exception("R2 upload failed for %s", key)
        raise HTTPException(502, f"Upload to media storage failed: {exc}") from exc
    return f"{public_url}/{key}"


def _public_base_url(request: Request) -> str:
    """Absolute base URL, honouring the proxy headers Railway/Vercel set.

    Without this the fallback could hand back an http:// (or localhost) URL
    that a browser on an https page refuses to load.
    """
    override = (os.getenv("PUBLIC_BASE_URL") or "").strip().rstrip("/")
    if override:
        return override
    base = str(request.base_url).rstrip("/")
    forwarded_proto = (request.headers.get("x-forwarded-proto") or "").split(",")[0].strip()
    if forwarded_proto and base.startswith("http://"):
        base = f"{forwarded_proto}://{base.split('://', 1)[1]}"
    return base


async def _upload_local(content: bytes, subdir: str, filename: str, request: Request) -> str:
    dest = os.path.join(UPLOAD_DIR, subdir)
    os.makedirs(dest, exist_ok=True)
    async with aiofiles.open(os.path.join(dest, filename), "wb") as handle:
        await handle.write(content)
    logger.warning(
        "Stored %s/%s on local disk. This is EPHEMERAL on Railway - configure R2.",
        subdir, filename,
    )
    return f"{_public_base_url(request)}/uploads/{subdir}/{filename}"


async def store_media(
    content: bytes, subdir: str, extension: str, content_type: str, request: Request
) -> tuple[str, str]:
    """Persist bytes and return (absolute_public_url, filename)."""
    filename = f"{uuid.uuid4()}{extension}"
    key = f"{subdir}/{filename}"
    if r2_enabled():
        url = await _upload_to_r2(content, key, content_type)
    else:
        url = await _upload_local(content, subdir, filename, request)
    return url, filename
