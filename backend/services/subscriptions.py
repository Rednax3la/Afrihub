from datetime import datetime, timezone
from fastapi import HTTPException


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
    unit = await db.units.find_one({'id': lesson.get('unit_id')})
    if unit and unit.get('order', 0) > 3 and not has_active_subscription(user):
        raise HTTPException(403, 'An active subscription is required for this unit')
