# Production Go-Live Checklist

## Pre-Deployment Verification
- [ ] **Environment Variables Configured:** All `.env` variables (Database URL, Redis URL, Gemini API Key, Resend API Key, Sentry DSN) are populated in Vercel/Render.
- [ ] **Database Migrations:** Verified that the startup process handles `alembic upgrade head` and all tables exist (including `password_reset_tokens`).
- [ ] **Email Service Verified:** The Resend API key is valid and the sending domain is verified.
- [ ] **Backups Configured:** Supabase automated backups are active (Point-in-Time Recovery enabled for production instances). Daily snapshots scheduled.

## Deployment & Security
- [ ] **HTTPS Verified:** Vercel edge and Nginx enforce HTTPS/SSL. No mixed content warnings.
- [ ] **Security Headers:** HSTS, X-Frame-Options, Content-Security-Policy are active.
- [ ] **Monitoring Configured:** Sentry SDK is capturing events and traces.
- [ ] **Security Scan Completed:** `bandit` and `npm audit` returned 0 critical vulnerabilities.

## Application Health & Performance
- [ ] **Health Checks Passing:** `/health`, `/ready`, and `/live` endpoints return 200 OK.
- [ ] **Performance Testing Completed:** Dashboard loads under 3s, API responds under 500ms.
- [ ] **Logging:** JSON structured logging is appearing properly in the monitoring aggregation.

## User Acceptance Testing (Post-Deployment)
- [ ] **Authentication:** Login, registration, and JWT token validation work.
- [ ] **Password Reset:** Successfully receive Resend email, click link, and change password.
- [ ] **Uploads:** Verify upload limits (Max 10MB) and allowed extensions (PDF, PNG, JPG).
- [ ] **AI Extraction:** Gemini API successfully extracts details from an invoice.
- [ ] **Workflow:** A document successfully navigates the 3-step approval process.
- [ ] **Reports & Exports:** Spend summary, tax/vat reports generate. PDF/Excel downloads correctly.

## Final Sign-Off
- [ ] Validation Script (`validate_prod.sh`) completes with no errors.
- [ ] System is ready for PCG Review.
