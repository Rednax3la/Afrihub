"""No lifespan, live MongoDB, SMTP, payment, or identity provider calls."""
import asyncio
import smtplib
from datetime import timedelta
from unittest.mock import Mock

import pytest
from bson import ObjectId
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

import auth
import database
from main import app
from services import password_reset as recovery
from services import reset_email

PASSWORD = 'NewPassword1!'


@pytest.fixture
async def ctx(monkeypatch):
    db = AsyncMongoMockClient().recovery_tests
    monkeypatch.setattr(database, 'db', db)
    for key, value in {
        'PASSWORD_RESET_ORIGIN': 'https://vernaculearn.africa',
        'SMTP_HOST': 'smtp.example.com', 'SMTP_PORT': '587', 'SMTP_SECURITY': 'starttls',
        'SMTP_USERNAME': 'sender@example.com', 'SMTP_PASSWORD': 'test-only',
        'SMTP_FROM': 'sender@example.com',
    }.items():
        monkeypatch.setenv(key, value)
    # Fails closed if a test accidentally misses the mocked delivery function.
    monkeypatch.setattr(smtplib, 'SMTP', Mock(side_effect=AssertionError('SMTP is forbidden')))
    monkeypatch.setattr(smtplib, 'SMTP_SSL', Mock(side_effect=AssertionError('SMTP is forbidden')))
    sent = []
    monkeypatch.setattr(recovery, 'send_reset_email', lambda config, email, token: sent.append((email, token)))
    user = {'_id': ObjectId(), 'name': 'Learner', 'email': 'learner@example.com',
            'password_hash': auth.hash_password('weak'), 'created_at': recovery.utcnow()}
    await db.users.insert_one(user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url='https://test') as client:
        yield client, db, user, sent


async def issue(ctx, email=None):
    client, db, user, sent = ctx
    response = await client.post('/api/auth/forgot-password', json={'email': email or user['email']})
    assert response.status_code == 202, response.text
    return sent[-1][1] if sent else None


async def confirm(client, token, password=PASSWORD):
    return await client.post('/api/auth/reset-password', json={'token': token, 'password': password})


async def test_request_hash_only_expiry_account_unchanged_and_enumeration(ctx):
    client, db, user, sent = ctx
    before = await db.users.find_one({'_id': user['_id']})
    await db.users.insert_one({'email': 'google@example.com', 'password_hash': None, 'auth_provider': 'google'})
    responses = [await client.post('/api/auth/forgot-password', json={'email': email})
                 for email in (user['email'], 'absent@example.com', 'google@example.com')]
    assert {r.status_code for r in responses} == {202}
    assert all(r.json() == responses[0].json() for r in responses)
    assert all(r.headers['cache-control'] == 'no-store' for r in responses)
    assert len(sent) == 1
    assert await db.users.find_one({'_id': user['_id']}) == before
    records = await db.password_reset_tokens.find().to_list(None)
    assert len(records) == 1
    assert records[0]['_id'] == recovery.token_hash(sent[0][1])
    assert sent[0][1] not in repr(records)
    assert timedelta(minutes=29) < records[0]['expires_at'] - recovery.utcnow() <= timedelta(minutes=30)


@pytest.mark.parametrize('delta', [0, -1, -1800])
async def test_expiry_enforced_without_ttl_cleanup(ctx, monkeypatch, delta):
    client, db, user, sent = ctx
    token = await issue(ctx)
    from routes import password_reset as reset_routes
    from unittest.mock import AsyncMock
    await db.password_reset_tokens.drop_index('expires_at_1')
    monkeypatch.setattr(reset_routes, 'ensure_indexes', AsyncMock())
    await db.password_reset_tokens.update_one({'_id': recovery.token_hash(token)}, {
        '$set': {'expires_at': recovery.utcnow() + timedelta(seconds=delta)}})
    assert await db.password_reset_tokens.find_one({'_id': recovery.token_hash(token)}) is not None
    assert (await confirm(client, token)).status_code == 400
    assert (await db.users.find_one({'_id': user['_id']}))['password_hash'] == user['password_hash']


async def test_legacy_login_reset_reuse_outstanding_links_and_session_revocation(ctx):
    client, db, user, sent = ctx
    legacy_jwt = auth.create_access_token({'sub': str(user['_id'])})
    headers = {'Authorization': 'Bearer ' + legacy_jwt}
    assert (await client.get('/api/users/me', headers=headers)).status_code == 200
    login = await client.post('/api/auth/login', json={'email': user['email'], 'password': 'weak'})
    assert login.status_code == 200
    token1, token2 = await issue(ctx), await issue(ctx)
    response = await confirm(client, token1)
    assert response.status_code == 200
    assert 'access_token' not in response.json()
    assert (await confirm(client, token1)).status_code == 400
    assert (await confirm(client, token2)).status_code == 400
    for jwt in (legacy_jwt, login.json()['access_token']):
        assert (await client.get('/api/users/me', headers={'Authorization': 'Bearer ' + jwt})).status_code == 401
    assert (await client.post('/api/auth/login', json={'email': user['email'], 'password': 'weak'})).status_code == 401
    new_login = await client.post('/api/auth/login', json={'email': user['email'], 'password': PASSWORD})
    assert new_login.status_code == 200
    assert (await client.get('/api/users/me', headers={'Authorization': 'Bearer ' + new_login.json()['access_token']})).status_code == 200


@pytest.mark.parametrize('same_token', [True, False])
async def test_concurrent_consumption_only_one_winner(ctx, monkeypatch, same_token):
    client, db, user, sent = ctx
    token1 = await issue(ctx)
    token2 = token1 if same_token else await issue(ctx)
    # Force both requests past the token read before either reaches the atomic write.
    arrived = 0
    ready = asyncio.Event()
    original = recovery.run_in_threadpool
    async def barrier(func, *args):
        nonlocal arrived
        result = await original(func, *args)
        arrived += 1
        if arrived == 2:
            ready.set()
        await asyncio.wait_for(ready.wait(), 5)
        return result
    monkeypatch.setattr(recovery, 'run_in_threadpool', barrier)
    responses = await asyncio.gather(confirm(client, token1), confirm(client, token2, 'OtherPassword2!'))
    assert sorted(r.status_code for r in responses) == [200, 400]
    assert (await db.users.find_one({'_id': user['_id']}))['session_version'] == 1


async def test_google_only_cannot_gain_password_even_with_stale_token(ctx):
    client, db, user, sent = ctx
    token = await issue(ctx)
    await db.users.update_one({'_id': user['_id']}, {'$set': {'password_hash': None, 'auth_provider': 'google'}})
    assert (await confirm(client, token)).status_code == 400
    assert (await db.users.find_one({'_id': user['_id']}))['password_hash'] is None


async def test_expiry_rechecked_after_hashing(ctx, monkeypatch):
    client, db, user, sent = ctx
    token = await issue(ctx)
    record = await db.password_reset_tokens.find_one({'_id': recovery.token_hash(token)})
    original = recovery.run_in_threadpool
    async def delayed_hash(func, *args):
        result = await original(func, *args)
        monkeypatch.setattr(recovery, 'utcnow', lambda: record['expires_at'])
        return result
    monkeypatch.setattr(recovery, 'run_in_threadpool', delayed_hash)
    assert (await confirm(client, token)).status_code == 400
    assert (await db.users.find_one({'_id': user['_id']}))['password_hash'] == user['password_hash']


async def test_subsequent_reset_new_generation_and_google_linked_login(ctx, monkeypatch):
    client, db, user, sent = ctx
    assert (await confirm(client, await issue(ctx))).status_code == 200
    new_token = await issue(ctx)
    assert (await confirm(client, new_token, 'AnotherPassword2!')).status_code == 200
    from google.oauth2 import id_token
    monkeypatch.setenv('GOOGLE_CLIENT_ID', 'mock-client')
    await db.users.update_one({'_id': user['_id']}, {'$set': {'google_sub': 'mock-google'}})
    monkeypatch.setattr(id_token, 'verify_oauth2_token', lambda *args: {
        'email': user['email'], 'email_verified': True, 'sub': 'mock-google'})
    response = await client.post('/api/auth/google', json={'id_token': 'mock-identity'})
    assert response.status_code == 200
    assert (await client.get('/api/users/me', headers={
        'Authorization': 'Bearer ' + response.json()['access_token']})).status_code == 200


async def test_background_work_runs_after_response_and_ignores_host(ctx, monkeypatch):
    client, db, user, sent = ctx
    body_sent = False
    original = recovery.send_reset_email
    def delivery(config, email, token):
        assert body_sent
        assert config.origin == 'https://vernaculearn.africa'
        original(config, email, token)
    monkeypatch.setattr(recovery, 'send_reset_email', delivery)
    async def observe(scope, receive, send):
        async def sending(message):
            nonlocal body_sent
            if message['type'] == 'http.response.body' and not message.get('more_body'):
                body_sent = True
            await send(message)
        await app(scope, receive, sending)
    async with AsyncClient(transport=ASGITransport(app=observe), base_url='https://attacker.example') as other:
        response = await other.post('/api/auth/forgot-password', json={'email': user['email']})
    assert response.status_code == 202
    assert len(sent) == 1


async def test_database_failure_is_service_error_not_invalid_credentials(ctx, monkeypatch):
    client, db, user, sent = ctx
    from pymongo.errors import ServerSelectionTimeoutError
    from unittest.mock import AsyncMock
    from types import SimpleNamespace
    from routes import auth as auth_routes
    unavailable = AsyncMock(side_effect=ServerSelectionTimeoutError('mock outage'))
    monkeypatch.setattr(auth_routes, 'get_db', lambda: SimpleNamespace(users=SimpleNamespace(find_one=unavailable)))
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='https://test') as other:
        response = await other.post('/api/auth/login', json={'email': user['email'], 'password': 'weak'})
    assert response.status_code == 500
    unavailable.assert_awaited_once()
    assert response.headers['cache-control'] == 'no-store'
    assert 'mock outage' not in response.text


async def test_shared_concurrent_request_limits_for_existing_and_missing_accounts(ctx):
    client, db, user, sent = ctx
    for email in [user['email'], 'missing@example.com']:
        responses = await asyncio.gather(*[
            client.post('/api/auth/forgot-password', json={'email': email}) for _ in range(7)])
        assert sorted(r.status_code for r in responses) == [202] * 5 + [429] * 2
        assert all(r.headers['retry-after'] == '900' for r in responses if r.status_code == 429)
    assert await db.password_reset_limits.count_documents({}) == 3


async def test_token_attempt_limit_persists_across_clients(ctx):
    client, db, user, sent = ctx
    for _ in range(20):
        assert (await confirm(client, 'invalid-token')).status_code == 400
    async with AsyncClient(transport=ASGITransport(app=app), base_url='https://test') as other_client:
        assert (await confirm(other_client, 'invalid-token')).status_code == 429


async def test_ip_limits_cannot_be_bypassed_with_forwarded_header(ctx):
    client, db, user, sent = ctx
    for i in range(20):
        r = await client.post('/api/auth/forgot-password', json={'email': f'person{i}@example.com'},
                              headers={'X-Forwarded-For': f'192.0.2.{i}'})
        assert r.status_code == 202
    assert (await client.post('/api/auth/forgot-password', json={'email': 'fresh@example.com'})).status_code == 429


async def test_email_failure_is_generic_and_removes_token(ctx, monkeypatch, caplog):
    client, db, user, sent = ctx
    def fail(*args):
        raise RuntimeError('sensitive-provider-detail')
    monkeypatch.setattr(recovery, 'send_reset_email', fail)
    existing = await client.post('/api/auth/forgot-password', json={'email': user['email']})
    missing = await client.post('/api/auth/forgot-password', json={'email': 'absent@example.com'})
    assert existing.status_code == missing.status_code == 202
    assert existing.json() == missing.json()
    assert 'sensitive-provider-detail' not in caplog.text
    assert await db.password_reset_tokens.count_documents({}) == 0
    assert (await db.users.find_one({'_id': user['_id']}))['password_hash'] == user['password_hash']


@pytest.mark.parametrize('setting,value', [('SMTP_PASSWORD', ''), ('SMTP_SECURITY', 'none'),
    ('PASSWORD_RESET_ORIGIN', 'https://trusted.test/evil'), ('PASSWORD_RESET_ORIGIN', 'http://trusted.test')])
async def test_missing_or_invalid_email_config_does_not_break_login(ctx, monkeypatch, setting, value):
    client, db, user, sent = ctx
    monkeypatch.setenv(setting, value)
    for email in [user['email'], 'absent@example.com']:
        r = await client.post('/api/auth/forgot-password', json={'email': email})
        assert r.status_code == 503
        assert r.headers['cache-control'] == 'no-store'
    assert (await client.post('/api/auth/login', json={'email': user['email'], 'password': 'weak'})).status_code == 200


@pytest.mark.parametrize('password', ['Short1!', 'lowercase1!', 'UPPERCASE1!', 'NoDigitsHere!',
    'NoSpecial123', 'Spaces 123', 'Strong1!' + 'x' * 65, 'Strong1!' + 'é' * 33, 'NullChar1!\x00'])
async def test_new_password_policy_registration_tutor_reset(ctx, password):
    client, db, user, sent = ctx
    for path in ['/api/auth/register', '/api/auth/register/tutor']:
        response = await client.post(path, json={'name': 'New User', 'email': 'new@example.com', 'password': password})
        assert response.status_code == 422
        assert 'input' not in response.text
    token = await issue(ctx)
    assert (await confirm(client, token, password)).status_code == 422
    assert (await confirm(client, token)).status_code == 200


async def test_passwords_not_trimmed_and_bcrypt_byte_boundary(ctx):
    client, db, user, sent = ctx
    password = ' Strong1!' + 'é' * 31 + ' '
    assert len(password.encode()) == 72
    r = await client.post('/api/auth/register', json={'name': 'New User', 'email': 'new@example.com', 'password': password})
    assert r.status_code == 201
    for value, expected in [(password, 200), (password.strip(), 401), (password + 'x', 401)]:
        r = await client.post('/api/auth/login', json={'email': 'new@example.com', 'password': value})
        assert r.status_code == expected


@pytest.mark.parametrize('security', ['ssl', 'starttls'])
def test_smtp_tls_verified_timeout_and_trusted_fragment_link(monkeypatch, security):
    transport = Mock()
    transport.__enter__ = Mock(return_value=transport)
    transport.__exit__ = Mock(return_value=False)
    transport.send_message.return_value = {}
    factory = Mock(return_value=transport)
    monkeypatch.setattr(smtplib, 'SMTP_SSL' if security == 'ssl' else 'SMTP', factory)
    config = reset_email.EmailConfig('https://vernaculearn.africa', 'smtp.example.com',
        465 if security == 'ssl' else 587, security, 'sender', 'mock-secret', 'sender@example.com', 10)
    reset_email.send_reset_email(config, 'learner@example.com', 'mock-token')
    message = transport.send_message.call_args.args[0]
    assert 'https://vernaculearn.africa/reset-password#token=mock-token' in message.get_content()
    assert '30 minutes' in message.get_content()
    assert factory.call_args.kwargs['timeout'] == 10
    context = factory.call_args.kwargs['context'] if security == 'ssl' else transport.starttls.call_args.kwargs['context']
    assert context.check_hostname
    if security == 'starttls':
        assert [call[0] for call in transport.method_calls].index('starttls') < [call[0] for call in transport.method_calls].index('login')
