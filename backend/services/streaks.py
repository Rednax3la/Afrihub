"""Streak maths, all evaluated against the Africa/Nairobi (UTC+3) calendar day.

A single source of truth for both halves of the streak:

* ``next_streak``      — what a lesson completion should write.
* ``effective_streak`` — what every read path should show. A streak that has
  already lapsed reads as 0 immediately; it does not wait for the user's next
  completion (and there is no cron job involved).
"""

import datetime

from services.reviews import today_eat  # single definition of "today" in EAT

EAT = datetime.timezone(datetime.timedelta(hours=3))

__all__ = ["today_eat", "to_eat_date", "next_streak", "effective_streak"]


def to_eat_date(value) -> datetime.date | None:
    """Normalise a stored ``last_activity_date`` to an EAT calendar date.

    Historic documents hold naive UTC datetimes; newer code may store aware
    datetimes, plain dates or ISO strings. All four are accepted.
    """
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value.astimezone(EAT).date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def next_streak(user: dict, today: datetime.date | None = None) -> int:
    """The streak to store when this user completes a lesson right now."""
    today = today or today_eat()
    last = to_eat_date(user.get("last_activity_date"))
    current = user.get("streak") or 0
    if last == today:
        # Already counted today — but this completion must leave them on at
        # least a 1-day streak.
        return max(current, 1)
    if last == today - datetime.timedelta(days=1):
        return current + 1
    # No activity, or a gap of two or more days: this lesson starts day one.
    return 1


def effective_streak(user: dict, today: datetime.date | None = None) -> int:
    """The streak to display. 0 once the last activity is older than yesterday."""
    today = today or today_eat()
    last = to_eat_date(user.get("last_activity_date"))
    if last is None:
        return 0
    if last < today - datetime.timedelta(days=1):
        return 0
    return user.get("streak") or 0
