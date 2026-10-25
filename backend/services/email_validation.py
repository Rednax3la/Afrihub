"""Sign-up email legitimacy checks.

Applied to student and tutor registration only -- never to login, so an
existing account can never be locked out by a rule added after it was created.

Layers, in order:
  1. Normalise (strip + lowercase).
  2. Exempt the @vernaculearn.com seed/mock domain from everything but syntax.
  3. Syntax validation (email-validator).
  4. Obvious typo domains -> a friendly "Did you mean ...?" message.
  5. Disposable-domain blocklist (backend/data/disposable_domains.txt).
  6. MX / domain existence. Fails *open* on DNS trouble so a resolver blip
     never blocks signups.
"""

import logging
import os
from functools import lru_cache

from email_validator import EmailNotValidError, EmailUndeliverableError, validate_email
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

# Seed/mock accounts live on this domain and have no real mailbox.
EXEMPT_DOMAIN = "vernaculearn.com"

_BLOCKLIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "disposable_domains.txt"
)

# Near-misses for the big providers. Mapped to what the user almost certainly meant.
TYPO_DOMAINS = {
    "gmial.com": "gmail.com",
    "gmal.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmai.com": "gmail.com",
    "gmail.co": "gmail.com",
    "gmaill.com": "gmail.com",
    "gnail.com": "gmail.com",
    "yaho.com": "yahoo.com",
    "yahooo.com": "yahoo.com",
    "yhoo.com": "yahoo.com",
    "hotmial.com": "hotmail.com",
    "hotmai.com": "hotmail.com",
    "hotmil.com": "hotmail.com",
    "hotnail.com": "hotmail.com",
    "outlok.com": "outlook.com",
    "outllok.com": "outlook.com",
    "iclod.com": "icloud.com",
    "icloud.co": "icloud.com",
}


@lru_cache(maxsize=1)
def disposable_domains() -> frozenset[str]:
    """Blocklist read once per process. Missing file degrades to an empty set."""
    try:
        with open(_BLOCKLIST_PATH, encoding="utf-8") as handle:
            return frozenset(
                line.strip().lower()
                for line in handle
                if line.strip() and not line.lstrip().startswith("#")
            )
    except OSError:
        logger.warning("Disposable-domain blocklist not readable at %s", _BLOCKLIST_PATH)
        return frozenset()


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _domain_of(email: str) -> str:
    return email.rsplit("@", 1)[-1] if "@" in email else ""


def _check_syntax(email: str, *, deliverability: bool) -> str:
    try:
        result = validate_email(email, check_deliverability=deliverability)
    except EmailUndeliverableError as exc:
        raise HTTPException(400, f"We couldn't find a mail server for that address. {exc}") from exc
    except EmailNotValidError as exc:
        raise HTTPException(400, f"That email address doesn't look valid. {exc}") from exc
    return result.normalized.lower()


def _validate_sync(email: str) -> str:
    normalized = normalize_email(email)
    domain = _domain_of(normalized)

    # Mock/seed accounts: syntax only, no MX and no blocklists.
    if domain == EXEMPT_DOMAIN:
        return _check_syntax(normalized, deliverability=False)

    # Syntax first so the later checks always see a well-formed address.
    normalized = _check_syntax(normalized, deliverability=False)
    domain = _domain_of(normalized)

    suggestion = TYPO_DOMAINS.get(domain)
    if suggestion:
        raise HTTPException(400, f"Did you mean {suggestion}?")

    if domain in disposable_domains():
        raise HTTPException(
            400, "Please use a permanent email address - disposable inboxes aren't accepted."
        )

    # Deliverability last. Any DNS problem that email-validator does not turn
    # into a definitive "this domain cannot receive mail" is treated as a pass.
    # Read at call time so tests/offline environments can switch it off.
    if os.getenv("EMAIL_DELIVERABILITY_CHECK", "true").lower() != "true":
        return normalized
    try:
        _check_syntax(normalized, deliverability=True)
    except HTTPException:
        raise
    except Exception:  # resolver missing/misconfigured, socket errors, ...
        logger.warning("DNS deliverability check failed open for %s", domain, exc_info=True)

    return normalized


async def validate_signup_email(email: str) -> str:
    """Validate and return the normalized address, or raise HTTPException(400)."""
    # DNS lookups block, so keep them off the event loop.
    return await run_in_threadpool(_validate_sync, email)
