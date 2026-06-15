import pytest
from httpx import AsyncClient
from tests.fixtures.factories import UserFactory
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password

@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient, db_session: AsyncSession):
    response = await async_client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "password": "password123",
        "full_name": "New User"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify db
    res = await db_session.execute(select(User).where(User.email == "newuser@test.com"))
    user = res.scalar_one()
    assert user is not None
    assert user.full_name == "New User"
    assert verify_password("password123", user.password_hash)

@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient, admin_user: User):
    response = await async_client.post("/api/v1/auth/register", json={
        "email": admin_user.email,
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_register_missing_password(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/register", json={
        "email": "test@test.com"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, admin_user: User):
    response = await async_client.post("/api/v1/auth/login", data={
        "username": admin_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient, admin_user: User):
    response = await async_client.post("/api/v1/auth/login", data={
        "username": admin_user.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_login_nonexistent_email(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/login", data={
        "username": "doesnotexist@test.com",
        "password": "password123"
    })
    assert response.status_code == 400
