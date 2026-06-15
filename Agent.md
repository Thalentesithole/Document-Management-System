# AGENTS.md

## Project Name

AI-Powered Document Management System (DMS)

## Overview

This project is a secure web-based document management platform that allows organizations to upload invoices and credit notes, automatically extract key information using AI, route documents through a 3-step approval workflow, detect duplicates, generate reports, and provide AI-powered insights.

The platform will be built using:

* Frontend: Google Antigravity Generated UI
* Backend: Python (FastAPI)
* Database: Supabase PostgreSQL
* Authentication: Supabase Auth
* Storage: Supabase Storage
* AI Processing: Gemini API
* Reporting Engine: Python
* Deployment: Vercel (Frontend) + Railway/Render (Backend)

---

# Agent Architecture

The system consists of specialized AI agents responsible for specific business processes.

---

## 1. Authentication Agent

### Responsibility

Manage user authentication and role permissions.

### Capabilities

* User registration
* Secure login
* Password reset
* Session validation
* Role assignment

### Roles

#### Admin

* Full system access
* Manage users
* View reports
* Final approval authority

#### Approver

* Review documents
* Approve or reject workflows

#### Viewer

* Read-only access

### Database Tables

users
roles
user_roles

---

## 2. Document Intake Agent

### Responsibility

Handle document uploads and validation.

### Accepted Files

* PDF
* PNG
* JPG
* JPEG

### Validation Rules

* File size limit
* Supported file types only
* Virus scanning
* Duplicate file hash detection

### Actions

1. Upload file
2. Store in Supabase Storage
3. Generate document hash
4. Create document record

### Output

Document ID

---

## 3. AI Extraction Agent

### Responsibility

Extract structured information from uploaded invoices and credit notes.

### Extraction Fields

* Vendor Name
* Invoice Number
* Invoice Date
* VAT Amount
* Total Amount
* Currency
* Document Type

### Processing Flow

1. Retrieve uploaded document
2. Send to Gemini
3. Parse extracted data
4. Validate fields
5. Save results

### Output Schema

{
"vendor_name": "",
"invoice_number": "",
"invoice_date": "",
"vat_amount": 0,
"total_amount": 0,
"document_type": ""
}

### Confidence Score

Store confidence score for every extracted field.

---

## 4. Duplicate Detection Agent

### Responsibility

Prevent duplicate invoices and credit notes.

### Validation Rules

Primary Match

* Invoice Number

Secondary Match

* Vendor Name
* Amount
* Invoice Date

File Match

* SHA256 hash comparison

### Duplicate Levels

#### Exact Duplicate

Same invoice number

#### Probable Duplicate

Vendor + Amount match

#### File Duplicate

Hash match

### Output

Duplicate Status
Risk Score

---

## 5. Workflow Agent

### Responsibility

Manage the mandatory 3-step approval process.

### Workflow Stages

#### Stage 1

Role: Reviewer

Actions:

* Approve
* Reject

#### Stage 2

Role: Manager

Actions:

* Approve
* Reject

#### Stage 3

Role: Finance/Admin

Actions:

* Final Approval
* Reject

### Statuses

* Draft
* Pending Review
* Pending Manager Approval
* Pending Finance Approval
* Approved
* Rejected

### Rules

* Stage order cannot be skipped
* Only assigned role may approve
* Every action must be audited

---

## 6. Audit Agent

### Responsibility

Track every system action.

### Audit Events

* Login
* Logout
* Upload
* Extraction
* Approval
* Rejection
* Report Generation

### Stored Data

* User ID
* Timestamp
* Action
* Resource
* Previous Value
* New Value

---

## 7. Reporting Agent

### Responsibility

Generate business reports.

### Reports

#### Spend Summary

Filters:

* Date Range

#### Vendor Analysis

Filters:

* Vendor

#### Approval Status

Filters:

* Approved
* Rejected
* Pending

#### VAT Report

Filters:

* Date Range
* Vendor

### Export Formats

* PDF
* Excel
* CSV

---

## 8. AI Insights Agent

### Responsibility

Generate business intelligence insights from financial documents.

### Analysis Types

#### Spending Trends

* Monthly spending
* Quarterly spending

#### Vendor Analysis

* Top vendors
* Vendor concentration

#### Anomaly Detection

* Unusual invoice amounts
* Duplicate patterns
* Suspicious activity

#### Cashflow Insights

* Spending forecasts
* Cost drivers

### Output Example

* Spending increased 24% compared to last month.
* Vendor ABC accounts for 41% of total spend.
* Three invoices exceed historical averages.

---

# Supabase Schema

## documents

* id
* file_name
* file_url
* document_type
* vendor_name
* invoice_number
* invoice_date
* vat_amount
* total_amount
* status
* created_by
* created_at

## approvals

* id
* document_id
* stage
* approver_id
* action
* comments
* created_at

## duplicate_checks

* id
* document_id
* duplicate_type
* confidence_score

## reports

* id
* report_type
* generated_by
* generated_at

## audit_logs

* id
* user_id
* action
* resource_type
* resource_id
* created_at

---

# API Standards

## Backend Framework

FastAPI

## Architecture

backend/
├── app/
│   ├── api/
│   ├── services/
│   ├── agents/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── middleware/
│   └── utils/

## Rules

* Service layer contains business logic
* Repository layer handles database access
* API routes remain thin
* Use dependency injection
* Async everywhere possible

---

# Security Requirements

* JWT Authentication
* Row Level Security in Supabase
* Password hashing
* Secure file uploads
* Audit logging
* Rate limiting
* Input validation
* Role-based authorization

---

# Frontend Requirements

## Pages

* Login
* Dashboard
* Upload Documents
* Document Details
* Workflow Queue
* Reports
* AI Insights
* User Management

## Design Principles

* Professional enterprise UI
* Mobile responsive
* Dark/light mode support
* Accessibility compliant
* Fast loading

---

# Success Criteria

The system is complete when:

1. Users can authenticate securely.
2. Invoices and credit notes can be uploaded.
3. AI extracts required fields.
4. Duplicate detection works.
5. 3-step approval workflow functions correctly.
6. Reports generate successfully.
7. AI insights are produced.
8. Audit logs are stored.
9. Role-based access control is enforced.
10. Application is deployed publicly and testable.
