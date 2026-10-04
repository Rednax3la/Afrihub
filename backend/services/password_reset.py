"""Shared MongoDB limits and single-use password recovery, without transactions."""
import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from starlette.concurrency import run_in_threadpool

from auth import SECRET_KEY, hash_password
from services.reset_email import send_reset_email

logger = logging.getLogger(__name__)
REQUEST_MESSAGE = ('If this address supports password recovery, we will attempt to send a reset email. '
                   'Delivery is not guaranteed. Check your inbox and spam folder; if no email arrives, '
                   'try again later or use your usual sign-in method.')
INVALID_LINK = 'This reset link is invalid, expired, or already used. Request a new link.'


def utcnow():
    # Motor uses naive UTC by default.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def token_hash(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


async def ensure_indexes(db):
    # Lazily created: missing email configuration never blocks application startup.
    await db.password_reset_tokens.create_index('expires_at', expireAfterSeconds=0)
    await db.password_reset_limits.create_index('expires_at', expireAfterSeconds=0)


async def rate_limit(db, scope, identity, limit, seconds=900):
    now = utcnow()
    window = int(now.replace(tzinfo=timezone.utc).timestamp()) // seconds
    digest = hmac.new(SECRET_KEY.encode(), f'{scope}:{identity}:{window}'.encode(), hashlib.sha256).hexdigest()
    query = {'_id': digest}
    update = {'$inc': {'count': 1}, '$setOnInsert': {'expires_at': now + timedelta(seconds=seconds * 2)}}
    try:
        record = await db.password_reset_limits.find_one_and_update(
            query, update, upsert=True, return_document=ReturnDocument.AFTER)
    except DuplicateKeyError:
        # Concurrent creation of the same window across processes: retry increment.
        record = await db.password_reset_limits.find_one_and_update(
            query, {'$inc': {'count': 1}}, return_document=ReturnDocument.AFTER)
    if record is None or record['count'] > limit:
        raise HTTPException(429, 'Too many password recovery attempts. Try again in 15 minutes.',
                            headers={'Retry-After': str(seconds)})


async def deliver_reset(db, email, config):
    """All account-dependent work happens after the identical HTTP response is sent.

    This is a best-effort in-process task, not a durable delivery queue. Never log
    exceptions here: provider messages may contain recipient data or credentials.
    """
    digest = None
    try:
        user = await db.users.find_one({'email': email})
        if not user or not user.get('password_hash'):
            return
        token = secrets.token_urlsafe(32)
        digest = token_hash(token)
        await db.password_reset_tokens.insert_one({
            '_id': digest, 'user_id': user['_id'],
            'session_version': user.get('session_version', 0),
            'expires_at': utcnow() + timedelta(minutes=30),
        })
        await run_in_threadpool(send_reset_email, config, user['email'], token)
    except Exception:
        logger.warning('Password recovery delivery failed; no delivery guarantee was made')
        if digest:
            try:
                await db.password_reset_tokens.delete_one({'_id': digest})
            except Exception:
                logger.warning('Password recovery cleanup failed; token expiry still applies')


async def reset_password(db, token, password):
    record = await db.password_reset_tokens.find_one({'_id': token_hash(token)})
    if not record or record['expires_at'] <= utcnow():
        raise HTTPException(400, INVALID_LINK)
    hashed = await run_in_threadpool(hash_password, password)
    # Recheck after the deliberately expensive password hash operation.
    if record['expires_at'] <= utcnow():
        raise HTTPException(400, INVALID_LINK)
    version = record['session_version']
    query = {'_id': record['user_id'], 'password_hash': {'$type': 'string', '$ne': ''}}
    if version == 0:
        query['$or'] = [{'session_version': 0}, {'session_version': {'$exists': False}}]
    else:
        query['session_version'] = version
    # This single-document compare-and-set IS consumption. Only one submission
    # (even of different links from the same generation) can win. Password change,
    # JWT revocation, and invalidation of every outstanding link commit together.
    result = await db.users.update_one(query, {
        '$set': {'password_hash': hashed}, '$inc': {'session_version': 1},
    })
    if result.modified_count != 1:
        raise HTTPException(400, INVALID_LINK)
    # Records can remain until TTL cleanup: their generation can no longer match.
