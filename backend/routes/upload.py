import os

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from auth import get_current_user, require_role
from services.storage import store_media, storage_status

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Browser MediaRecorder output is webm (Chrome/Firefox) or mp4/m4a (Safari).
ALLOWED_AUDIO = {".mp3", ".wav", ".ogg", ".m4a", ".webm", ".mp4", ".aac", ".oga", ".opus"}
ALLOWED_IMAGE = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_VIDEO = {".mp4", ".webm", ".mov"}

MAX_AUDIO_SIZE = 25 * 1024 * 1024   # 25 MB — a long tutor take at a sane bitrate
MAX_IMAGE_SIZE = 15 * 1024 * 1024   # 15 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB

# A MediaRecorder blob often arrives as "blob" with no extension, so the MIME
# type is the only reliable signal.
_MIME_EXTENSIONS = {
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/wave": ".wav",
    "audio/ogg": ".ogg",
    "audio/opus": ".opus",
    "audio/webm": ".webm",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/aac": ".aac",
    "video/webm": ".webm",
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/heic": ".heic",
    "image/heif": ".heic",
}


def _resolve_extension(file: UploadFile, allowed: set[str], label: str) -> str:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        # Fall back to the declared MIME type before giving up.
        mime = (file.content_type or "").split(";")[0].strip().lower()
        mapped = _MIME_EXTENSIONS.get(mime)
        if mapped in allowed:
            return mapped
        if mapped in (".heic",):
            raise HTTPException(
                400,
                "HEIC images aren't supported yet. Please choose JPEG, PNG or WebP "
                "(on iPhone: Settings > Camera > Formats > Most Compatible).",
            )
        got = ext or mime or "unknown"
        raise HTTPException(
            400,
            f"Unsupported {label} format ({got}) - allowed: {', '.join(sorted(allowed))}",
        )
    return ext


async def _read_within_limit(file: UploadFile, max_size: int) -> bytes:
    content = await file.read()
    if not content:
        raise HTTPException(400, "The uploaded file was empty.")
    if len(content) > max_size:
        raise HTTPException(
            400,
            f"File too large ({len(content) / 1024 / 1024:.1f} MB). "
            f"Maximum is {max_size // 1024 // 1024} MB.",
        )
    return content


@router.get("/status")
async def upload_status(admin=Depends(require_role("admin"))):
    """Which storage backend this instance is actually using."""
    return storage_status()


@router.post("/audio")
async def upload_audio(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    ext = _resolve_extension(file, ALLOWED_AUDIO, "audio")
    content = await _read_within_limit(file, MAX_AUDIO_SIZE)
    url, filename = await store_media(
        content, "audio", ext, file.content_type or "audio/mpeg", request
    )
    return {"url": url, "filename": filename}


@router.post("/video")
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    ext = _resolve_extension(file, ALLOWED_VIDEO, "video")
    content = await _read_within_limit(file, MAX_VIDEO_SIZE)
    url, filename = await store_media(
        content, "video", ext, file.content_type or "video/mp4", request
    )
    return {"url": url, "filename": filename}


@router.post("/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    ext = _resolve_extension(file, ALLOWED_IMAGE, "image")
    content = await _read_within_limit(file, MAX_IMAGE_SIZE)
    url, filename = await store_media(
        content, "image", ext, file.content_type or "image/jpeg", request
    )
    return {"url": url, "filename": filename}
