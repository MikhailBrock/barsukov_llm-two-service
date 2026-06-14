import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.api.deps import get_db
from app.db.base import Base


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def test_register(client):
    resp = await client.post("/auth/register", json={"email": "tversky@email.com", "password": "pass123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "tversky@email.com"
    assert "password_hash" not in data


async def test_login_and_me(client):
    await client.post("/auth/register", json={"email": "tversky@email.com", "password": "pass123"})
    resp = await client.post("/auth/login", data={"username": "tversky@email.com", "password": "pass123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me_resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "tversky@email.com"


async def test_duplicate_register(client):
    await client.post("/auth/register", json={"email": "tversky@email.com", "password": "pass123"})
    resp = await client.post("/auth/register", json={"email": "tversky@email.com", "password": "pass123"})
    assert resp.status_code == 409


async def test_wrong_password(client):
    await client.post("/auth/register", json={"email": "tversky@email.com", "password": "pass123"})
    resp = await client.post("/auth/login", data={"username": "tversky@email.com", "password": "wrongpass"})
    assert resp.status_code == 401


async def test_me_no_token(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_invalid_token(client):
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401
