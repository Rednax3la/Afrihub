import asyncio
import json
import logging
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def valid_push_endpoint(endpoint):
    url = urlparse(endpoint)
    host = url.hostname or ''
    domains = ('fcm.googleapis.com', 'updates.push.services.mozilla.com', 'push.apple.com', 'notify.windows.com')
    return (url.scheme == 'https' and not url.username and not url.password and url.port in (None, 443)
            and any(host == domain or host.endswith('.' + domain) for domain in domains))


async def send_push(db, user, body, title='Vernaculearn'):
    subscription = user.get('push_subscription')
    key = os.getenv('VAPID_PRIVATE_KEY')
    email = os.getenv('VAPID_CLAIM_EMAIL')
    if not subscription or not key or not email or not valid_push_endpoint(subscription.get('endpoint', '')):
        return False
    from pywebpush import webpush, WebPushException
    try:
        await asyncio.to_thread(webpush, subscription_info=subscription,
            data=json.dumps({'title': title, 'body': body}), vapid_private_key=key,
            vapid_claims={'sub': email if email.startswith('mailto:') else 'mailto:' + email}, timeout=10)
        return True
    except WebPushException as exc:
        if exc.response is not None and exc.response.status_code in (404, 410):
            await db.users.update_one({'_id': user['_id'], 'push_subscription.endpoint': subscription['endpoint']},
                                      {'$unset': {'push_subscription': ''}})
        logger.warning('Push delivery failed for user %s', user['_id'])
    except Exception:
        logger.warning('Push configuration or delivery failed for user %s', user['_id'])
    return False
