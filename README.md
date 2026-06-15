# Secure AI-Powered Document Management System (DMS)

This is the backend for a production-ready Document Management System that leverages Supabase for data management and Google Gemini 2.5 Flash for AI-powered invoice data extraction and business insights.

## Features

- **JWT Authentication & RBAC**: Uses Supabase or local JWTs to handle User Registration, Login, and Role-Based Access Control.
- **AI Extraction Agent**: Automatically processes uploaded invoices using Gemini to extract key fields (Vendor, Amounts, Dates).
- **Duplicate Detection Agent**: Background Celery task that flags potential duplicate invoices based on hash and matched fields.
- **3-Stage Workflow Agent**: Formal review, manager approval, and finance approval routing.
- **AI Insights & Reporting**: Generates spend analytics and AI insights (trends, forecasting) directly from aggregated database records.
- **Audit Logging**: Immutable tracking of all API actions (Uploads, Approvals, Rejections).

## Tech Stack

- **Backend**: FastAPI (Python 3.12+)
- **Database**: Supabase PostgreSQL (via SQLAlchemy 2.0 & asyncpg)
- **Migrations**: Alembic
- **Storage**: Supabase Storage
- **Background Jobs**: Celery + Redis
- **AI**: Google `google-genai` SDK (Gemini 2.5 Flash)
- **Testing**: Pytest & httpx

## Local Setup

### 1. Environment Configuration

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/dms
REDIS_URL=redis://redis:6379/0
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=local_jwt_secret
```

### 2. Start Services via Docker Compose

```bash
docker-compose up -d --build
```

This will spin up:
- FastAPI Application on `http://localhost:8000`
- PostgreSQL Database on port `5432`
- Redis on port `6379`
- Celery Worker for background tasks

### 3. Run Database Migrations

Access the API container and run Alembic migrations:

```bash
docker-compose exec api alembic upgrade head
```

## API Documentation

Once the server is running, interactive API documentation is available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Testing

Run the automated test suite locally (using in-memory SQLite):

```bash
pytest backend/tests/
```
