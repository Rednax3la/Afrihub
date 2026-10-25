import os

from datetime import datetime, timezone
from fastapi import HTTPException

# Premium unit gating is temporarily switched off. The paywall code below is
# intact -- set PAYWALL_ENABLED=true to turn it back on without a code change.
PAYWALL_DEFAULT = "false"


def paywall_enabled() -> bool:
    """Read at call time so the flag is a pure env change (and testable)."""
    return os.getenv("PAYWALL_ENABLED", PAYWALL_DEFAULT).strip().lower() in ("true", "1", "yes")


def unit_requires_subscription(unit) -> bool:
    """Whether this unit sits behind the paywall. False whenever it is off."""
    if not paywall_enabled():
        return False
    return bool(unit) and unit.get("order", 0) > 3


def has_active_subscription(user):
    if user.get('subscription_status') != 'active':
        return False
    expiry = user.get('expires_at')
    if not expiry:
        return True
    if isinstance(expiry, str):
        expiry = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    return expiry > datetime.now(timezone.utc)


async def update_subscription(db, user_id, tier, expires_at):
    """Shared by verified payment handlers and the privileged subscription endpoint."""
    await db.users.update_one({'_id': user_id}, {'$set': {
        'subscription_status': 'active', 'subscription_tier': tier,
        'is_premium': True,
    }, '$max': {'expires_at': expires_at}})


async def require_lesson_access(db, lesson, user):
    if not lesson or lesson.get('status') in ('draft', 'rejected', 'pending_review'):
        raise HTTPException(404, 'Lesson not found')
    if not paywall_enabled():
        return
    unit = await db.units.find_one({'id': lesson.get('unit_id')})
    if unit_requires_subscription(unit) and not has_active_subscription(user):
        raise HTTPException(403, 'An active subscription is required for this unit')
