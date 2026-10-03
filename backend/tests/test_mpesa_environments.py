"""M-Pesa environment isolation using in-memory MongoDB and mocked Daraja calls."""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import httpx
import pytest
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from mongomock_motor import AsyncMongoMockClient

from auth import get_current_user
from routes import payments, users
from services.subscriptions import has_active_subscription


@pytest.fixture
async def mpesa_context(monkeypatch):
    # Override every payment setting so no deployment credentials are used.
    for name in ('MPESA_CONSUMER_KEY', 'MPESA_CONSUMER_SECRET', 'MPESA_SHORTCODE',
                 'MPESA_PASSKEY', 'MPESA_CALLBACK_SECRET'):
        monkeypatch.setenv(name, 'fixture-value')
    monkeypatch.setenv('MPESA_CALLBACK_URL', 'https://example.invalid/callback')
    monkeypatch.setenv('MPESA_ENVIRONMENT', 'production')
    monkeypatch.setenv('APP_ENV', 'production')
    provider = AsyncMock(side_effect=AssertionError('Unexpected provider request'))
    monkeypatch.setattr(payments, 'mpesa_request', provider)
    # ASGITransport is in-process; any accidental outbound HTTP must fail the test.
    monkeypatch.setattr(httpx.AsyncHTTPTransport, 'handle_async_request',
                        AsyncMock(side_effect=AssertionError('External HTTP is forbidden')))

    db = AsyncMongoMockClient().mpesa_environment_tests
    user = {'_id': ObjectId(), 'name': 'Learner', 'email': 'learner@example.com',
            'role': 'student', 'created_at': datetime.now(timezone.utc)}
    await db.users.insert_one(user)
    monkeypatch.setattr(payments, 'get_db', lambda: db)
    app = FastAPI()
    app.include_router(payments.router)
    app.include_router(users.router)

    async def current_user():
        return await db.users.find_one({'_id': user['_id']})

    app.dependency_overrides[get_current_user] = current_user
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='https://test') as client:
        yield client, db, user, provider


async def checkout(db, user, environment='production', status='pending'):
    record = {'_id': 'mpesa-checkout', 'checkout_id': 'checkout', 'provider': 'mpesa',
              'user_id': str(user['_id']), 'tier': 'monthly', 'status': status,
              'amount': 1299, 'currency': 'KES',
              'expires_at': datetime.now(timezone.utc) + timedelta(days=30)}
    if environment is not None:
        record['environment'] = environment
    await db.payments.insert_one(record)
    return record


async def invoke(client, db, record, entry):
    if entry == 'initiation':
        return await client.post('/api/payments/mpesa/stk-push', json={'phone': '0712345678', 'tier': 'monthly'})
    if entry == 'callback':
        # A success claim in the callback must never replace provider verification.
        return await client.post('/api/payments/mpesa/callback', params={'secret': 'fixture-value'},
                                 json={'Body': {'stkCallback': {'CheckoutRequestID': 'checkout', 'ResultCode': 0}}})
    if entry == 'status':
        return await client.get('/api/payments/mpesa/checkout')
    try:
        await payments.confirm_mpesa(db, record)
    except HTTPException as exc:
        return httpx.Response(exc.status_code, json={'detail': exc.detail})
    return httpx.Response(200)


@pytest.mark.parametrize('app_env', [None, 'production', 'staging', '', 'DEVELOPMENT'])
@pytest.mark.parametrize('entry', ['initiation', 'confirmation', 'callback', 'status'])
async def test_sandbox_requires_explicit_development(mpesa_context, monkeypatch, app_env, entry):
    client, db, user, provider = mpesa_context
    if app_env is None:
        monkeypatch.delenv('APP_ENV', raising=False)
    else:
        monkeypatch.setenv('APP_ENV', app_env)
    monkeypatch.setenv('MPESA_ENVIRONMENT', 'sandbox')
    record = await checkout(db, user, 'sandbox')
    response = await invoke(client, db, record, entry)
    assert response.status_code == 503
    assert 'M-Pesa is unavailable' in response.json()['detail']
    assert 'fixture-value' not in response.text
    provider.assert_not_awaited()
    assert not has_active_subscription(await db.users.find_one({'_id': user['_id']}))
    assert (await db.payments.find_one({'_id': record['_id']}))['status'] == 'pending'
    assert await db.payments.count_documents({}) == 1


@pytest.mark.parametrize('entry', ['initiation', 'confirmation', 'callback', 'status'])
async def test_unsupported_provider_environment_is_unavailable(mpesa_context, monkeypatch, entry):
    client, db, user, provider = mpesa_context
    monkeypatch.setenv('APP_ENV', 'development')
    monkeypatch.setenv('MPESA_ENVIRONMENT', 'invalid-environment')
    record = await checkout(db, user)
    response = await invoke(client, db, record, entry)
    assert response.status_code == 503
    provider.assert_not_awaited()
    assert not has_active_subscription(await db.users.find_one({'_id': user['_id']}))


@pytest.mark.parametrize('environment,app_env', [('sandbox', 'development'), ('production', 'production'), ('production', None)])
async def test_new_checkout_records_environment_and_verified_activation(mpesa_context, monkeypatch, environment, app_env):
    client, db, user, provider = mpesa_context
    monkeypatch.setenv('MPESA_ENVIRONMENT', environment)
    if app_env is None:
        monkeypatch.delenv('APP_ENV')
    else:
        monkeypatch.setenv('APP_ENV', app_env)
    provider.side_effect = None
    provider.return_value = {'ResponseCode': '0', 'CheckoutRequestID': 'checkout'}
    response = await invoke(client, db, None, 'initiation')
    assert response.status_code == 200
    record = await db.payments.find_one({'_id': 'mpesa-checkout'})
    assert record['environment'] == environment
    assert record['status'] == 'pending'
    assert provider.await_args.args[1]['Amount'] == 1299
    assert provider.await_args.args[2]['environment'] == environment
    assert not has_active_subscription(await db.users.find_one({'_id': user['_id']}))

    provider.reset_mock()
    provider.return_value = {'ResultCode': '0'}
    response = await invoke(client, db, record, 'callback')
    assert response.status_code == 200
    provider.assert_awaited_once()
    assert provider.await_args.args[0] == '/mpesa/stkpushquery/v1/query'
    assert provider.await_args.args[1]['CheckoutRequestID'] == 'checkout'
    activated = await db.users.find_one({'_id': user['_id']})
    assert has_active_subscription(activated)
    assert activated['subscription_tier'] == 'monthly'
    assert activated['expires_at'] == record['expires_at']
    assert (await db.payments.find_one({'_id': record['_id']}))['status'] == 'completed'
    # Repeated callback/status reads neither requery nor extend access.
    provider.reset_mock()
    assert (await invoke(client, db, record, 'callback')).status_code == 200
    assert (await invoke(client, db, record, 'status')).json()['status'] == 'completed'
    provider.assert_not_awaited()
    assert (await db.users.find_one({'_id': user['_id']}))['expires_at'] == record['expires_at']


@pytest.mark.parametrize('configured,recorded', [
    ('production', 'sandbox'), ('sandbox', 'production'),
    ('production', None), ('sandbox', None), ('production', 'unsupported'),
])
@pytest.mark.parametrize('entry', ['confirmation', 'callback', 'status'])
async def test_mismatched_and_legacy_checkouts_require_reconciliation(mpesa_context, monkeypatch, configured, recorded, entry):
    client, db, user, provider = mpesa_context
    monkeypatch.setenv('APP_ENV', 'development')
    monkeypatch.setenv('MPESA_ENVIRONMENT', configured)
    record = await checkout(db, user, recorded)
    response = await invoke(client, db, record, entry)
    assert response.status_code == 409
    assert 'requires reconciliation' in response.json()['detail']
    provider.assert_not_awaited()
    assert not has_active_subscription(await db.users.find_one({'_id': user['_id']}))
    stored = await db.payments.find_one({'_id': record['_id']})
    assert stored['status'] == 'pending'
    assert stored.get('environment') == recorded


@pytest.mark.parametrize('entry', ['confirmation', 'callback', 'status'])
async def test_completed_legacy_records_are_not_assumed_verified(mpesa_context, entry):
    client, db, user, provider = mpesa_context
    record = await checkout(db, user, None, status='completed')
    response = await invoke(client, db, record, entry)
    assert response.status_code == 409
    assert 'requires reconciliation' in response.json()['detail']
    provider.assert_not_awaited()
    assert not has_active_subscription(await db.users.find_one({'_id': user['_id']}))


@pytest.mark.parametrize('entry', ['callback', 'status'])
@pytest.mark.parametrize('result,expected_status,active', [
    ({'ResultCode': '0'}, 'completed', True),
    ({'ResultCode': '1032'}, 'failed', False),
    ({'ResponseCode': '0'}, 'pending', False),
])
async def test_production_confirmation_requires_provider_success(mpesa_context, entry, result, expected_status, active):
    client, db, user, provider = mpesa_context
    record = await checkout(db, user)
    provider.side_effect = None
    provider.return_value = result
    response = await invoke(client, db, record, entry)
    assert response.status_code == 200
    provider.assert_awaited_once()
    assert provider.await_args.args[2]['base'] == 'https://api.safaricom.co.ke'
    assert has_active_subscription(await db.users.find_one({'_id': user['_id']})) is active
    assert (await db.payments.find_one({'_id': record['_id']}))['status'] == expected_status


async def test_missing_configuration_only_disables_mpesa(mpesa_context, monkeypatch):
    client, db, user, provider = mpesa_context
    monkeypatch.delenv('MPESA_CONSUMER_SECRET')
    response = await invoke(client, db, None, 'initiation')
    assert response.status_code == 503
    assert response.json()['detail'] == 'M-Pesa is unavailable: payment configuration is incomplete'
    provider.assert_not_awaited()
    assert (await client.get('/api/users/me')).status_code == 200
    assert not has_active_subscription(await db.users.find_one({'_id': user['_id']}))
