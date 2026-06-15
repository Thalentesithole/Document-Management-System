"""
Shared test configuration and fixtures for the entire test suite.

Provides:
- In-memory SQLite async database with per-test isolation
- Multi-role user fixtures (admin, reviewer, manager, viewer)
- Authenticated HTTPX client fixtures
- Auth header helper
- Document factory fixtures
"""
import pytest
import pytest_asyncio
import httpx
import uuid
from httpx import ASGITransport

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool
from sqlalchemy import select, event

from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, RoleEnum
from app.models.document import Document, DocumentStatusEnum
from app.models.audit_log import AuditLog
from app.models.duplicate_check import DuplicateCheck
from app.models.approval_workflow import ApprovalWorkflow
from app import models  # noqa: F401 — ensure all models loaded for metadata.create_all


# ---------------------------------------------------------------------------
# Database engine (in-memory SQLite, shared across tests in the session)
# ---------------------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Override FastAPI's get_db dependency
# ---------------------------------------------------------------------------
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------------------------
# Session-scoped: create/drop tables once
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# Per-test database session
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


# ---------------------------------------------------------------------------
# HTTPX Async Client (unauthenticated)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Helper: generate auth headers for a given user
# ---------------------------------------------------------------------------
def auth_headers_for(user: User) -> dict[str, str]:
    """Create a Bearer token header dict for the given user."""
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Multi-role user fixtures
# ---------------------------------------------------------------------------
async def _get_or_create_user(
    db: AsyncSession,
    email: str,
    role: RoleEnum,
    full_name: str | None = None,
) -> User:
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalars().first()
    if existing:
        return existing

    user = User(
        email=email,
        password_hash=get_password_hash("password123"),
        role=role,
        full_name=full_name or f"Test {role.value.title()}",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    return await _get_or_create_user(db_session, "admin@test.com", RoleEnum.admin, "Test Admin")


@pytest_asyncio.fixture
async def reviewer_user(db_session: AsyncSession) -> User:
    return await _get_or_create_user(db_session, "reviewer@test.com", RoleEnum.reviewer, "Test Reviewer")


@pytest_asyncio.fixture
async def manager_user(db_session: AsyncSession) -> User:
    return await _get_or_create_user(db_session, "manager@test.com", RoleEnum.manager, "Test Manager")


@pytest_asyncio.fixture
async def viewer_user(db_session: AsyncSession) -> User:
    return await _get_or_create_user(db_session, "viewer@test.com", RoleEnum.viewer, "Test Viewer")


# Keep backward compat with old tests expecting `test_user`
@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    return await _get_or_create_user(db_session, "test@example.com", RoleEnum.admin, "Test User")


# ---------------------------------------------------------------------------
# Authenticated HTTPX clients per role
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def admin_client(admin_user: User):
    transport = ASGITransport(app=app)
    headers = auth_headers_for(admin_user)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers=headers,
    ) as client:
        yield client


@pytest_asyncio.fixture
async def reviewer_client(reviewer_user: User):
    transport = ASGITransport(app=app)
    headers = auth_headers_for(reviewer_user)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers=headers,
    ) as client:
        yield client


@pytest_asyncio.fixture
async def manager_client(manager_user: User):
    transport = ASGITransport(app=app)
    headers = auth_headers_for(manager_user)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers=headers,
    ) as client:
        yield client


@pytest_asyncio.fixture
async def viewer_client(viewer_user: User):
    transport = ASGITransport(app=app)
    headers = auth_headers_for(viewer_user)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers=headers,
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Document factory helper
# ---------------------------------------------------------------------------
async def create_document(
    db: AsyncSession,
    *,
    file_name: str = "invoice.pdf",
    file_url: str = "https://storage.example.com/invoice.pdf",
    file_hash: str | None = None,
    status: DocumentStatusEnum = DocumentStatusEnum.pending_review,
    uploaded_by: uuid.UUID | None = None,
    vendor_name: str | None = "Acme Corp",
    invoice_number: str | None = "INV-001",
    total_amount: float | None = 1500.00,
    currency: str | None = "USD",
    vat_amount: float | None = 250.00,
    subtotal_amount: float | None = 1250.00,
) -> Document:
    doc = Document(
        file_name=file_name,
        file_url=file_url,
        file_hash=file_hash or uuid.uuid4().hex,
        status=status,
        uploaded_by=uploaded_by or uuid.uuid4(),
        vendor_name=vendor_name,
        invoice_number=invoice_number,
        total_amount=total_amount,
        currency=currency,
        vat_amount=vat_amount,
        subtotal_amount=subtotal_amount,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@pytest_asyncio.fixture
async def sample_document(db_session: AsyncSession, admin_user: User) -> Document:
    """A ready-made document in pending_review for quick use."""
    return await create_document(db_session, uploaded_by=admin_user.id)