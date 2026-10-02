from datetime import datetime, timedelta, timezone
from services.notifications import send_push
from services.reviews import today_eat


async def send_streak_reminders(db):
    today = today_eat()
    midnight = datetime.combine(today, datetime.min.time(), tzinfo=timezone(timedelta(hours=3))).astimezone(timezone.utc)
    query = {'push_subscription': {'$exists': True, '$ne': None}, 'streak': {'$gt': 0},
             '$or': [{'last_activity_date': {'$lt': midnight}}, {'last_activity_date': None}],
             'last_reminder_date': {'$ne': today.isoformat()}}
    async for user in db.users.find(query):
        # A database claim prevents duplicate reminders across scheduler processes.
        claim = await db.users.update_one({'_id': user['_id'], **query}, {'$set': {'last_reminder_date': today.isoformat()}})
        if claim.modified_count:
            await send_push(db, user, "Don't break your streak! Open Vernaculearn.")
