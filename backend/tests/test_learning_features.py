"""Isolated feature tests: no live database, payment, Google, or push requests."""
import datetime
from unittest.mock import AsyncMock, patch

import pytest
from bson import ObjectId
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

import database
from auth import get_current_user
from main import app
from routes import payments
from services.reviews import sm2, today_eat
from services.subscriptions import has_active_subscription


@pytest.fixture
async def feature_context(monkeypatch):
    db = AsyncMongoMockClient().test_features
    monkeypatch.setattr(database, 'db', db)
    user = {'_id': ObjectId(), 'name': 'Learner', 'email': 'learner@example.com', 'role': 'student',
            'created_at': datetime.datetime.utcnow(), 'active_languages': ['sw'], 'streak': 0}
    await db.users.insert_one(user)
    await db.languages.insert_one({'id': 'sw', 'name': 'Swahili', 'code': 'sw', 'flag_emoji': 'KE'})
    for order in (1, 4):
        await db.units.insert_one({'id': f'unit-{order}', 'language_id': 'sw', 'order': order, 'title': f'Unit {order}'})
        await db.lessons.insert_one({'id': f'lesson-{order}', 'unit_id': f'unit-{order}', 'title': f'Lesson {order}',
            'order': 1, 'status': 'published', 'xp_reward': 10, 'questions': [
                {'id': 'q1', 'type': 'translate', 'prompt': 'Habari?', 'native_text': 'How are you?', 'correct_answer_id': 'a', 'options': []}]})
    async def current():
        return await db.users.find_one({'_id': user['_id']})
    app.dependency_overrides[get_current_user] = current
    async with AsyncClient(transport=ASGITransport(app=app), base_url='https://test') as client:
        yield client, db, user
    app.dependency_overrides.clear()


@pytest.mark.parametrize('ease,interval,score,expected', [
    (2.5, 0, 100, (2.5, 1)), (2.5, 1, 100, (2.5, 3)), (2.5, 3, 100, (2.5, 8)),
    (2.5, 3, 80, (2.5, 8)), (2.3, 3, 60, (2.3, 3)), (2.5, 0, 60, (2.5, 0)),
    (2.5, 9, 59, (2.3, 1)), (1.3, 9, 0, (1.3, 1)),
])
def test_sm2_transitions(ease, interval, score, expected):
    assert sm2(ease, interval, score) == expected


def test_subscription_expiration():
    assert has_active_subscription({'subscription_status': 'active'})
    assert not has_active_subscription({'subscription_status': 'active', 'expires_at': '2020-01-01T00:00:00Z'})
    assert not has_active_subscription({'is_premium': True})


async def test_paywall_covers_all_lesson_entrypoints(feature_context):
    client, db, user = feature_context
    units = (await client.get('/api/languages/sw/units')).json()
    assert len(units) == 2
    assert units[1]['locked'] and units[1]['lessons'] == []
    assert not units[0]['locked'] and len(units[0]['lessons']) == 1
    assert (await client.get('/api/lessons/lesson-4')).status_code == 403
    assert (await client.get('/api/units/unit-4/lessons')).status_code == 403
    assert (await client.post('/api/lessons/answer', json={'lesson_id': 'lesson-4', 'question_id': 'q1', 'answer_id': 'a'})).status_code == 403
    assert (await client.post('/api/lessons/lesson-4/complete', json={'score': 100})).status_code == 403
    assert await db.progress.count_documents({}) == 0
    await db.users.update_one({'_id': user['_id']}, {'$set': {'subscription_status': 'active'}})
    assert (await client.get('/api/lessons/lesson-4')).status_code == 200


async def test_completion_advances_review_schedule(feature_context):
    client, db, user = feature_context
    for interval in (1, 3, 8):
        response = await client.post('/api/lessons/lesson-1/complete', json={'score': 100})
        assert response.status_code == 200, response.text
        progress = await db.progress.find_one({'lesson_id': 'lesson-1'})
        assert progress['review_schedule']['interval_days'] == interval
        assert progress['review_schedule']['next_review_date'] == (today_eat() + datetime.timedelta(days=interval)).isoformat()
    assert (await client.post('/api/lessons/missing/complete', json={'score': 100})).status_code == 404
    assert (await client.post('/api/lessons/lesson-1/complete', json={'score': 101})).status_code == 422


async def test_due_reviews_are_user_scoped_and_joined(feature_context):
    client, db, user = feature_context
    await db.progress.insert_many([
        {'user_id': str(user['_id']), 'lesson_id': 'lesson-1', 'review_schedule': {'next_review_date': today_eat().isoformat()}},
        {'user_id': 'another-user', 'lesson_id': 'lesson-1', 'review_schedule': {'next_review_date': today_eat().isoformat()}},
        {'user_id': str(user['_id']), 'lesson_id': 'lesson-4', 'review_schedule': {'next_review_date': '2099-01-01'}},
    ])
    response = await client.get('/api/progress/me/due-for-review')
    assert response.status_code == 200, response.text
    assert len(response.json()) == 1
    assert response.json()[0]['language_name'] == 'Swahili'
    assert response.json()[0]['title'] == 'Lesson 1'
    await db.progress.update_one({'lesson_id': 'lesson-4'}, {'$set': {'review_schedule.next_review_date': today_eat().isoformat()}})
    reviews = (await client.get('/api/progress/me/due-for-review')).json()
    assert len(reviews) == 2
    assert next(r for r in reviews if r['lesson_id'] == 'lesson-4')['locked'] is True


async def test_dictionary_literal_search_and_publication(feature_context):
    client, db, _ = feature_context
    await db.lessons.insert_one({'id': 'draft', 'unit_id': 'unit-1', 'status': 'draft', 'questions': [
        {'type': 'translate', 'prompt': 'Secret', 'native_text': 'Hidden'}]})
    results = (await client.get('/api/dictionary/search', params={'q': 'hAbArI', 'language_id': 'sw'})).json()
    assert len(results) == 1
    assert results[0]['native'] == 'Habari?' and results[0]['english'] == 'How are you?'
    assert (await client.get('/api/dictionary/search', params={'q': 'Secret'})).json() == []
    assert (await client.get('/api/dictionary/search', params={'q': '.*'})).json() == []
    assert (await client.get('/api/dictionary/search', params={'q': 'Habari', 'language_id': 'other'})).json() == []
    assert (await client.get('/api/dictionary/search', params={'q': 'a', 'limit': 101})).status_code == 422


async def test_student_cannot_self_activate(feature_context):
    client, _, _ = feature_context
    response = await client.patch('/api/users/me/subscription', json={
        'subscription_status': 'active', 'subscription_tier': 'yearly', 'expires_at': '2099-01-01T00:00:00Z'})
    assert response.status_code == 403


async def test_google_test_payment_idempotency_and_production_gate(feature_context, monkeypatch):
    client, db, user = feature_context
    monkeypatch.setenv('GOOGLE_PAY_ENVIRONMENT', 'TEST')
    monkeypatch.setenv('APP_ENV', 'production')
    body = {'payment_token': 'test-token', 'tier': 'monthly'}
    assert (await client.post('/api/payments/google-pay', json=body)).status_code == 503
    monkeypatch.setenv('APP_ENV', 'development')
    assert (await client.post('/api/payments/google-pay', json=body)).status_code == 200
    first = await db.users.find_one({'_id': user['_id']})
    assert first['subscription_status'] == 'active'
    assert (await client.post('/api/payments/google-pay', json=body)).status_code == 200
    second = await db.users.find_one({'_id': user['_id']})
    assert first['expires_at'] == second['expires_at']
    assert await db.payments.count_documents({}) == 1
    assert (await client.post('/api/payments/google-pay', json={**body, 'tier': 'yearly'})).status_code == 409


async def test_google_production_requires_charge_confirmation(feature_context, monkeypatch):
    client, db, user = feature_context
    monkeypatch.setenv('GOOGLE_PAY_ENVIRONMENT', 'PRODUCTION')
    with patch.object(payments, 'charge_google_token', AsyncMock(side_effect=HTTPException(402, 'Declined'))):
        response = await client.post('/api/payments/google-pay', json={'payment_token': 'prod-token', 'tier': 'yearly'})
        assert response.status_code == 402
    assert not has_active_subscription(await db.users.find_one({'_id': user['_id']}))
    with patch.object(payments, 'charge_google_token', AsyncMock(return_value='pi_verified')):
        assert (await client.post('/api/payments/google-pay', json={'payment_token': 'prod-token', 'tier': 'yearly'})).status_code == 200
    assert has_active_subscription(await db.users.find_one({'_id': user['_id']}))


async def test_mpesa_callback_does_not_trust_payload(feature_context, monkeypatch):
    client, db, user = feature_context
    monkeypatch.setenv('MPESA_CALLBACK_SECRET', 'test-secret')
    await db.payments.insert_one({'_id': 'mpesa-checkout', 'checkout_id': 'checkout', 'user_id': str(user['_id']),
        'environment': 'production',
        'tier': 'monthly', 'status': 'pending', 'expires_at': datetime.datetime.utcnow() + datetime.timedelta(days=30)})
    body = {'Body': {'stkCallback': {'CheckoutRequestID': 'checkout', 'ResultCode': 0}}}
    assert (await client.post('/api/payments/mpesa/callback', json=body)).status_code == 403
    with patch.object(payments, 'mpesa_config', return_value={'environment': 'production'}), patch.object(payments, 'mpesa_credentials', return_value={}), patch.object(payments, 'mpesa_request', AsyncMock(return_value={'ResultCode': '1032'})):
        assert (await client.post('/api/payments/mpesa/callback?secret=test-secret', json=body)).status_code == 200
    assert not has_active_subscription(await db.users.find_one({'_id': user['_id']}))
    with patch.object(payments, 'mpesa_config', return_value={'environment': 'production'}), patch.object(payments, 'mpesa_credentials', return_value={}), patch.object(payments, 'mpesa_request', AsyncMock(return_value={'ResultCode': '0'})):
        assert (await client.post('/api/payments/mpesa/callback?secret=test-secret', json=body)).status_code == 200
    assert has_active_subscription(await db.users.find_one({'_id': user['_id']}))


async def test_push_subscription_validation_and_unsubscribe(feature_context):
    client, db, user = feature_context
    payload = {'endpoint': 'http://127.0.0.1/internal', 'keys': {'p256dh': 'key', 'auth': 'auth'}}
    assert (await client.post('/api/users/me/push-subscription', json=payload)).status_code == 422
    payload['endpoint'] = 'https://fcm.googleapis.com/fcm/send/test'
    assert (await client.post('/api/users/me/push-subscription', json=payload)).status_code == 200
    assert (await client.get('/api/users/me')).json()['push_enabled']
    assert (await client.delete('/api/users/me/push-subscription')).status_code == 200
    assert 'push_subscription' not in await db.users.find_one({'_id': user['_id']})


async def test_reminders_skip_today_and_are_once_per_day(feature_context):
    _, db, user = feature_context
    from tasks.reminders import send_streak_reminders
    await db.users.update_one({'_id': user['_id']}, {'$set': {'streak': 3, 'push_subscription': {'endpoint': 'test'}}})
    with patch('tasks.reminders.send_push', AsyncMock(return_value=True)) as send:
        await send_streak_reminders(db)
        await send_streak_reminders(db)
        assert send.await_count == 1
    await db.users.update_one({'_id': user['_id']}, {'$unset': {'last_reminder_date': ''}, '$set': {'last_activity_date': datetime.datetime.utcnow()}})
    with patch('tasks.reminders.send_push', AsyncMock(return_value=True)) as send:
        await send_streak_reminders(db)
        send.assert_not_awaited()


async def test_google_login_and_passwordless_login(feature_context, monkeypatch):
    client, db, _ = feature_context
    monkeypatch.setenv('GOOGLE_CLIENT_ID', 'test-client')
    payload = {'sub': 'google-123', 'email': 'google-user@gmail.com', 'email_verified': True, 'name': 'Google Learner'}
    with patch('google.oauth2.id_token.verify_oauth2_token', return_value=payload) as verify:
        response = await client.post('/api/auth/google', json={'id_token': 'google-token'})
        assert response.status_code == 200, response.text
        assert response.json()['user']['role'] == 'student'
        assert verify.call_args.args[2] == 'test-client'
        assert (await client.post('/api/auth/google', json={'id_token': 'google-token'})).status_code == 200
    assert await db.users.count_documents({'email': payload['email']}) == 1
    assert (await client.post('/api/auth/login', json={'email': payload['email'], 'password': 'anything'})).status_code == 401
    with patch('google.oauth2.id_token.verify_oauth2_token', side_effect=ValueError('bad token')):
        assert (await client.post('/api/auth/google', json={'id_token': 'invalid'})).status_code == 401
