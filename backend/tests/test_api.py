"""
Basic integration tests for the Afrihub API.

Run with:
    cd backend
    pip install httpx pytest pytest-asyncio
    pytest tests/
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

BASE = "http://test"
TEST_USER = {
    "name": "Test User",
    "email": "test_runner@afrihub.dev",
    "password": "testpass123",
    "location": "Accra, Ghana",
}


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE) as ac:
        yield ac


@pytest.fixture
async def auth_headers(client):
    """Register (or login) a test user and return auth headers."""
    resp = await client.post("/api/auth/register", json=TEST_USER)
    if resp.status_code == 400:
        # Already registered — log in instead
        resp = await client.post(
            "/api/auth/login",
            json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
        )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Auth ────────────────────────────────────────────────────────────────────────

class TestAuth:
    async def test_register_success(self, client):
        import uuid
        unique_email = f"user_{uuid.uuid4().hex[:6]}@test.com"
        resp = await client.post(
            "/api/auth/register",
            json={"name": "New User", "email": unique_email, "password": "pass1234"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == unique_email

    async def test_register_duplicate_email(self, client, auth_headers):
        resp = await client.post("/api/auth/register", json=TEST_USER)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    async def test_login_success(self, client, auth_headers):
        resp = await client.post(
            "/api/auth/login",
            json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_wrong_password(self, client):
        resp = await client.post(
            "/api/auth/login",
            json={"email": TEST_USER["email"], "password": "wrongpassword"},
        )
        assert resp.status_code == 401


# ── Users ───────────────────────────────────────────────────────────────────────

class TestUsers:
    async def test_get_me(self, client, auth_headers):
        resp = await client.get("/api/users/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == TEST_USER["email"]

    async def test_get_me_unauthenticated(self, client):
        resp = await client.get("/api/users/me")
        assert resp.status_code == 401

    async def test_update_profile(self, client, auth_headers):
        resp = await client.patch(
            "/api/users/me",
            json={"location": "Lagos, Nigeria"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["location"] == "Lagos, Nigeria"


# ── Languages ───────────────────────────────────────────────────────────────────

class TestLanguages:
    async def test_list_languages(self, client):
        resp = await client.get("/api/languages")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_get_language_units(self, client, auth_headers):
        langs = (await client.get("/api/languages")).json()
        if langs:
            resp = await client.get(f"/api/languages/{langs[0]['id']}/units")
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)
