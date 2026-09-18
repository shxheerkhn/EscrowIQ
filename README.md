# EscrowIQ — Intelligent Freelance Marketplace with Escrow & Agentic AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1%2B-black?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-2.0%2B-blue?logo=postgresql)
![Groq](https://img.shields.io/badge/Groq-AI%20SDK-orange)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-TF--IDF-orange?logo=scikit-learn)
![Deployment](https://img.shields.io/badge/Deploy-Railway%20%2F%20Nixpacks-purple)

**EscrowIQ** is an end-to-end freelance marketplace platform featuring escrow-backed financial transactions, real-time AI fraud detection, hybrid semantic freelancer matching, context-aware proposal generation, and a bounded **Agentic AI Hiring Assistant** powered by Groq.

The platform bridges client needs with freelancer talent through a strictly validated financial lifecycle and intelligent AI orchestration while preserving a foundational security boundary: **The LLM orchestrates; the backend enforces authority.**

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Marketplace Workflows & State Machines](#marketplace-workflows--state-machines)
- [Agentic AI Hiring Assistant](#agentic-ai-hiring-assistant)
- [AI & Machine Learning Engine](#ai--machine-learning-engine)
- [Database Architecture & Schema](#database-architecture--schema)
- [API Reference](#api-reference)
- [Security Architecture & Controls](#security-architecture--controls)
- [Environment Configuration](#environment-configuration)
- [Local Setup & Installation](#local-setup--installation)
- [Demo Credentials](#demo-credentials)
- [Testing Suite](#testing-suite)
- [Deployment & Production Hardening](#deployment--production-hardening)
- [Repository Structure](#repository-structure)
- [Current Scope & Limitations](#current-scope--limitations)
- [License & Project Status](#license--project-status)

---

## Overview

EscrowIQ implements the full operational lifecycle of a modern freelance platform. It enables clients to post jobs, receive bids, fund escrow, review work deliverables, release funds upon approval, or initiate dispute resolution. 

Unlike traditional platforms, EscrowIQ incorporates:
1. **Escrow State Machine**: Transactions are secured via server-validated database state transitions (`held`, `submitted`, `approved`, `released`, `refunded`, `disputed`).
2. **Hybrid Semantic Matching**: Combines rule-based skill overlap, rating, and review metrics with **scikit-learn TF-IDF + Cosine Similarity** to match candidates beyond exact keywords.
3. **Real-time Fraud Analysis**: Evaluates job postings using a hybrid engine blending regex pattern rules with semantic AI vector comparisons against known scam vs. legitimate job exemplars.
4. **Agentic AI Hiring Assistant**: A bounded autonomous hiring agent that uses allowlisted read-only backend tools to analyze candidates, evaluate risk, generate structured recommendations, and prepare single-use proposal acceptances subject to explicit client approval.

> **Project Status**: EscrowIQ is a fully functional academic/prototype application demonstrating advanced marketplace control systems and safe LLM tool orchestration.

---

## Key Features

### 🛒 Marketplace Operations
- **User Authentication**: Role-based signup (`client`, `freelancer`), password strength validation, session management, and email verification with 6-digit OTPs.
- **Job Management**: Job posting with automated fraud scoring, skill tag parsing, budget/deadline constraints, and status tracking (`open`, `in_progress`, `completed`, `cancelled`).
- **Proposal Lifecycle**: Proposal submission with bid amount, timeline, and cover letter; atomic single-proposal acceptance with automatic rejection of competing pending bids.
- **Work Submissions**: Deliverables submitted via message notes, external URLs, single ZIP archives, or full multi-file folder uploads (automatically packaged server-side into ZIP archives).
- **Direct Messaging & Notifications**: Contextual in-app messaging per job, in-app notification badge counts, and asynchronous SMTP email notifications.

### 🛡️ Financial Escrow & Dispute Resolution
- **Escrow Funding**: Atomically locks client balance into escrow upon proposal acceptance or manual deposit.
- **Multi-Option Review**: Clients can approve work (triggers instant escrow payout to freelancer), request revisions with feedback, or open an admin complaint.
- **Admin Complaint Resolution**: Admin panel for inspecting disputed jobs, logs, and work submissions, with capabilities to force fund release to freelancer, process refund to client, or close complaints.

### 🤖 AI & Intelligent Features
- **Agentic AI Hiring Assistant**: Bounded Groq agent loop with allowlisted read-only tools, persistent audit tracking, step limits, and mandatory human approval gates.
- **Groq Conversational Chatbot**: General-purpose AI assistant (`POST /api/chatbot`) providing platform assistance and guidance.
- **Hybrid Freelancer Matching**: Dual-stage scoring algorithm evaluating skill synonyms, TF-IDF cosine similarity, rating percentile, and experience logarithmic curves.
- **Scam & Fraud Detection**: Dual-stage analysis classifying job postings into `Low`, `Medium`, or `High` risk with granular category breakdowns.
- **Smart Proposal Generator**: Generates tailored cover letters across multiple writing styles (`Professional`, `Direct`, `Detailed`).

---

## System Architecture

EscrowIQ separates presentation, business logic, persistence, deterministic AI analytics, and LLM orchestration layers:

```mermaid
graph TD
    subgraph ClientLayer["Client Layer"]
        UI["Jinja2 Templates + Vanilla JS + HTML5/CSS3"]
        Browser["Web Browser / REST Client"]
    end

    subgraph BackendLayer["Backend Application Layer (Flask)"]
        App["Flask Application Core - app.py"]
        Auth["Auth & Session Manager"]
        Marketplace["Marketplace Controller & Escrow Engine"]
        Security["CSRF & Input Validation Middleware"]
    end

    subgraph AnalyticsLayer["Intelligent Services & Analytics Layer"]
        Matcher["Hybrid Matcher - ml_matching.py"]
        Fraud["Fraud Detection Engine - fraud_detection.py"]
        ProposalGen["Template Proposal Generator"]
        Chatbot["Groq Chatbot API"]
    end

    subgraph AgenticLayer["Bounded Agentic AI Layer"]
        AgentCtrl["Agent Controller - agentic/controller.py"]
        AgentProv["Groq Agent Provider - agentic/provider.py"]
        AgentReg["Allowlisted Tool Registry - agentic/registry.py"]
    end

    subgraph StorageLayer["Storage & External Services Layer"]
        DB[("PostgreSQL Database")]
        GroqAPI["Groq LLM Cloud API"]
        SMTP["SMTP Email Server"]
        Uploads["Local Submission Storage"]
    end

    Browser --> UI
    UI --> App
    App --> Security
    Security --> Auth
    Security --> Marketplace
    
    Marketplace --> Matcher
    Marketplace --> Fraud
    Marketplace --> ProposalGen
    
    App --> AgentCtrl
    AgentCtrl --> AgentProv
    AgentProv --> GroqAPI
    AgentCtrl --> AgentReg
    AgentReg --> Matcher
    AgentReg --> DB
    
    Marketplace --> DB
    Marketplace --> SMTP
    Marketplace --> Uploads
```

### Architectural Principles

1. **Strict Authority Boundary**: The LLM engine never mutates persistent state directly. State mutation requires deterministic backend authorization, re-validation, and transactional database commits.
2. **Defense in Depth**: CSRF tokens protect all mutating `/api/*` routes, session cookies use `HttpOnly` and `SameSite=Lax` attributes, passwords use Werkzeug PBKDF2/scrypt hashing, and queries use parameterized SQL execution via SQLAlchemy Core.
3. **Bounded Agent Execution**: The AI Hiring Assistant operates within strict limits: maximum step counts, tight request timeouts, read-only allowlisted tools, and mandatory client approval for consequential operations.

---

## Marketplace Workflows & State Machines

### 1. Escrow & Work Submission Lifecycle

The marketplace follows a locked state machine for transactions:

```mermaid
stateDiagram-v2
    [*] --> JobPosted: Client creates job
    JobPosted --> ProposalSubmitted: Freelancer bids
    ProposalSubmitted --> ProposalAccepted: Client accepts proposal
    ProposalAccepted --> EscrowFunded: Escrow deposited
    EscrowFunded --> WorkSubmitted: Freelancer submits deliverable
    
    state WorkSubmitted {
        [*] --> UnderReview
        UnderReview --> ChangesRequested: Client requests revisions
        ChangesRequested --> UnderReview: Freelancer resubmits
    }

    WorkSubmitted --> EscrowReleased: Client approves work
    WorkSubmitted --> DisputeOpened: Dispute opened
    
    DisputeOpened --> EscrowReleased: Admin payouts freelancer
    DisputeOpened --> EscrowRefunded: Admin refunds client
    DisputeOpened --> Closed: Admin closes dispute

    EscrowReleased --> [*]: Funds added to Freelancer balance
    EscrowRefunded --> [*]: Funds returned to Client balance
```

### 2. Proposal Acceptance & Competing Proposal Rejection

When a client accepts a proposal:
1. An atomic database transaction with `FOR UPDATE` row locks is initiated.
2. The target proposal state changes from `pending` -> `accepted`.
3. All other `pending` proposals for the same `job_id` are automatically marked as `rejected`.
4. The job status changes from `open` -> `in_progress`.
5. Real-time notifications and optional email alerts are dispatched to all affected freelancers.

---

## Agentic AI Hiring Assistant

The **EscrowIQ Hiring Assistant** is a bounded agentic orchestrator located in `Backend/agentic/`. It is accessible through the `/agent` workspace UI and REST endpoints.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant UI as Agent Workspace UI
    participant Ctrl as Agent Controller
    participant LLM as Groq LLM
    participant Reg as Tool Registry
    participant DB as PostgreSQL DB
    
    Client->>UI: Input hiring objective
    UI->>Ctrl: POST /api/agent/runs
    Ctrl->>DB: Create agent_run (status: running)
    
    loop Bounded Loop (Max 4 Steps)
        Ctrl->>LLM: Send prompt + tool schemas (JSON mode)
        LLM-->>Ctrl: Structured decision JSON
        
        alt Tool Call Requested
            Ctrl->>Reg: Validate tool name and arguments
            Reg->>DB: Execute allowlisted query
            DB-->>Reg: Return deterministic data
            Reg-->>Ctrl: Structured tool_result
            Ctrl->>DB: Log audit event (tool_used)
            Ctrl->>LLM: Append tool_result to messages
        else Final Recommendation
            Ctrl-->>Ctrl: Validate final JSON and proposal_id
        end
    end

    alt Proposed Acceptance Present
        Ctrl->>DB: Save proposed_action and set pending_approval
        Ctrl-->>UI: Return summary + Proposal Recommendation Card
        Client->>UI: Click "Approve & Accept Proposal"
        UI->>Ctrl: POST /api/agent/runs/run_id/approve
        Ctrl->>DB: Claim run FOR UPDATE
        Ctrl->>DB: Execute accept_pending_proposal
        Ctrl->>DB: Update run status to approved
        Ctrl-->>UI: Return success & updated job state
    else Recommendation Only
        Ctrl->>DB: Update run status to completed
        Ctrl-->>UI: Return summary response
    end
```

### Allowlisted Agent Tools

The agent registry (`Backend/agentic/registry.py`) exposes **only** 3 read-only backend tools:

| Tool Name | Scope & Purpose | Required Arguments | Backend Validation |
| :--- | :--- | :--- | :--- |
| `list_client_jobs` | Lists all open jobs owned by the authenticated client. | None | Filtered by `client_id = current_user.id` and `status = 'open'`. |
| `get_job_candidates` | Evaluates verified freelancers using the hybrid matcher. | `job_id` (int) | Verifies job ownership and `status = 'open'`. Returns top 5 scored candidates. |
| `get_pending_proposals` | Retrieves all pending proposals for a client's open job. | `job_id` (int) | Verifies job ownership and `status = 'open'`. Returns bids, cover letters, and ratings. |

### Security Safeguards for the Agent
- **No Arbitrary Execution**: The agent cannot execute SQL strings, Python code, shell commands, or external HTTP requests.
- **Strict Single-Use Approval Gate**: Proposed proposal acceptances are stored in `agent_runs.proposed_action`. When the client approves, the server re-validates ownership, locks the row (`FOR UPDATE`), checks status = `pending_approval`, transitions state to `approving`, and calls `accept_pending_proposal()`.
- **Bounded Resources**: Capped at `AGENT_MAX_STEPS=4` iterations and `AGENT_GROQ_TIMEOUT_SECONDS=20`.

---

## AI & Machine Learning Engine

### 1. Hybrid Freelancer Matching (`Backend/ml_matching.py` & `Backend/app.py`)

EscrowIQ uses a composite formula to rank freelancers for open job postings:

$$\text{Final Score} = 0.55 \cdot S_{\text{semantic}} + 0.25 \cdot S_{\text{skill}} + 0.15 \cdot R_{\text{norm}} + 0.05 \cdot E_{\text{norm}}$$

Where:
- **Semantic Score ($S_{\text{semantic}}$)**: TF-IDF vectorization with `ngram_range=(1, 2)` and sublinear term frequency scaling on job text vs. freelancer profile (skills + bio), scored via cosine similarity ($0–100\%$).
- **Skill Overlap Score ($S_{\text{skill}}$)**: Heuristic skill matching with synonym normalization map.
- **Rating Score ($R_{\text{norm}}$)**: Normalized rating score ($(\text{rating} / 5.0) \times 100$).
- **Experience Score ($E_{\text{norm}}$)**: Logarithmic review scaling ($\min(100, \frac{\ln(1 + \text{reviews})}{\ln(1 + 50)} \times 100)$).

#### Skill Normalization Dictionary

```python
SKILL_SYNONYMS = {
    'js': 'javascript', 'node': 'node.js', 'nodejs': 'node.js',
    'react.js': 'react', 'vue.js': 'vue', 'postgres': 'postgresql',
    'psql': 'postgresql', 'py': 'python', 'ts': 'typescript',
    'k8s': 'kubernetes', 'ml': 'machine learning', 'ai': 'machine learning',
    'ui': 'ui/ux', 'ux': 'ui/ux', 'rest': 'rest api'
}
```

### 2. Fraud & Scam Detection Engine (`Backend/fraud_detection.py`)

Every job posting undergoes real-time fraud assessment:

```
Hybrid Fraud Score = 0.40 * (Rule-Based Score) + 0.60 * (Semantic AI Score)
```

1. **Rule-Based Engine**: Matches 14 regex patterns across categories:
   - *Payment*: Cryptocurrency, untraceable methods (Western Union, Wire Transfer, Zelle).
   - *Personal Data*: Requests for bank details, SSN, routing numbers.
   - *Urgency & Manipulation*: Artificial urgency ("ASAP", "today only"), get-rich-quick claims.
   - *External Redirection*: Off-platform messaging links ("Telegram", "WhatsApp").
   - *Quality & Scope*: Low word count (<15 words), excessive capitalization, missing scope.
2. **Semantic AI Engine**: Vectorizes the job posting using TF-IDF and computes max cosine similarity against 30 fraud exemplars vs. 30 legitimate job exemplars to compute a risk confidence rating.

---

## Database Architecture & Schema

EscrowIQ uses **PostgreSQL** with 11 relational tables managed via SQLAlchemy Core and transactional SQL.

```mermaid
erDiagram
    users ||--o{ jobs : "posts"
    users ||--o{ proposals : "submits"
    users ||--o{ escrow : "funds or receives"
    users ||--o{ work_submissions : "delivers"
    users ||--o{ complaints : "involved in"
    users ||--o{ notifications : "receives"
    users ||--o{ email_codes : "requests"
    users ||--o{ messages : "sends or receives"
    users ||--o{ agent_runs : "executes"
    
    jobs ||--o{ proposals : "receives"
    jobs ||--o{ escrow : "secures"
    jobs ||--o{ work_submissions : "contains"
    jobs ||--o{ complaints : "disputed in"
    jobs ||--o{ messages : "context for"
    
    escrow ||--o{ work_submissions : "linked to"
    escrow ||--o{ complaints : "disputed in"
    
    work_submissions ||--o{ complaints : "complained about"
    agent_runs ||--o{ agent_audit_events : "generates"
```

### Database Tables Overview

| Table Name | Description | Key Fields & Types | Indexes & Constraints |
| :--- | :--- | :--- | :--- |
| `users` | Marketplace accounts | `id` (PK), `username` (UQ), `email` (UQ), `password`, `role` (client/freelancer), `rating`, `balance`, `email_verified` | Unique username & email indexes |
| `jobs` | Job postings | `id` (PK), `client_id` (FK), `title`, `description`, `skills_required`, `budget`, `deadline`, `status`, `fraud_score`, `fraud_level` | Indexes on `client_id`, `status` |
| `proposals` | Freelancer bids | `id` (PK), `job_id` (FK), `freelancer_id` (FK), `cover_letter`, `bid_amount`, `timeline`, `status` | UNIQUE(`job_id`, `freelancer_id`), FK indexes |
| `escrow` | Locked transaction funds | `id` (PK), `job_id` (FK), `client_id` (FK), `freelancer_id` (FK), `amount`, `status` (`held`, `released`, `refunded`) | FK references to jobs & users |
| `work_submissions` | Delivered work items | `id` (PK), `job_id` (FK), `freelancer_id` (FK), `escrow_id` (FK), `delivery_message`, `upload_archive_path`, `status` | Index on `(job_id, created_at DESC)` |
| `complaints` | Dispute records | `id` (PK), `job_id` (FK), `escrow_id` (FK), `complainant_id` (FK), `against_user_id` (FK), `message`, `status`, `resolution_action` | Index on `(status, created_at DESC)` |
| `notifications` | In-app user notifications | `id` (PK), `user_id` (FK), `message`, `action_url`, `type`, `is_read` | Index on `(user_id, is_read)` |
| `email_codes` | OTP verification codes | `id` (PK), `user_id` (FK), `email`, `purpose`, `code`, `expires_at`, `consumed_at` | Index on `(email, purpose, created_at DESC)` |
| `messages` | Direct project messages | `id` (PK), `job_id` (FK), `sender_id` (FK), `recipient_id` (FK), `content`, `is_read` | Indexes on job & recipient |
| `agent_runs` | Hiring assistant runs | `id` (PK), `client_id` (FK), `prompt`, `status`, `summary`, `proposed_action` (JSONB), `error_message` | Index on `(client_id, created_at DESC)` |
| `agent_audit_events` | Granular agent event logs | `id` (PK), `run_id` (FK CASCADE), `event_type`, `payload` (JSONB), `created_at` | Index on `(run_id, created_at ASC)` |

---

## API Reference

All mutating API endpoints require session authentication and a valid CSRF header (`X-CSRF-Token`). Responses follow standard HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `500 Internal Error`).

### 1. Core & Page Routes

| Route | Method | Access | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Public | Marketplace landing page |
| `/health` | `GET` | Public | System health check (`{"status": "ok", "database": "postgresql"}`) |
| `/register` | `GET` | Public | Account registration page |
| `/login` | `GET` | Public | Authentication login page |
| `/dashboard` | `GET` | Authenticated | Role-specific dashboard (Client or Freelancer view) |
| `/jobs` | `GET` | Public | Job search and discovery catalog |
| `/jobs/<job_id>` | `GET` | Public | Job details, bids, proposals, matching, & messaging |
| `/agent` | `GET` | Client Only | Agentic AI Hiring Assistant workspace |
| `/escrow` | `GET` | Authenticated | Escrow account balance & transaction history |
| `/admin/complaints`| `GET` | Admin Only | Administrative dispute queue and inspection panel |

### 2. Authentication & User APIs

| Endpoint | Method | Payload / Arguments | Description |
| :--- | :--- | :--- | :--- |
| `/api/register` | `POST` | `{username, full_name, email, password, role, skills, bio}` | Create client or freelancer account |
| `/api/login` | `POST` | `{email, password}` | Establish authenticated session |
| `/api/logout` | `POST` | None | Terminate current session |
| `/api/auth/verify-email` | `POST` | `{email, code}` | Verify account using 6-digit email OTP |
| `/api/auth/resend-verification` | `POST` | `{email}` | Resend 6-digit OTP verification code |
| `/api/auth/request-password-reset` | `POST` | `{email}` | Generate password reset OTP |
| `/api/auth/reset-password` | `POST` | `{email, code, new_password}` | Reset password using valid OTP |
| `/api/profile` | `PUT` | `{full_name, bio, skills}` | Update user profile information |

### 3. Jobs & Marketplace APIs

| Endpoint | Method | Payload / Arguments | Description |
| :--- | :--- | :--- | :--- |
| `/api/jobs` | `POST` | `{title, description, skills_required, budget, deadline}` | Create a job posting with real-time fraud scoring |
| `/api/jobs/<job_id>` | `DELETE` | None | Delete an open job posting (owner only) |
| `/api/proposals` | `POST` | `{job_id, bid_amount, timeline, cover_letter}` | Freelancer submits bid proposal |
| `/api/proposals/<id>/accept` | `POST` | None | Accept proposal (atomically rejects competing bids) |
| `/api/proposals/<id>/reject` | `POST` | None | Manually reject a pending proposal |
| `/api/jobs/<job_id>/messages` | `POST` | `{recipient_id, content}` | Send direct project message |

### 4. Escrow & Work Submission APIs

| Endpoint | Method | Payload / Arguments | Description |
| :--- | :--- | :--- | :--- |
| `/api/escrow/deposit` | `POST` | `{job_id, amount}` | Deposit funds into escrow for accepted job |
| `/api/escrow/<id>/release` | `POST` | None | Release held escrow funds to freelancer balance |
| `/api/escrow/<id>/refund` | `POST` | None | Refund held escrow funds back to client balance |
| `/api/jobs/<job_id>/submit-work` | `POST` | Form Data (`delivery_message`, `delivery_url`, `zip_file` or multi-file `folder`) | Freelancer submits completed work deliverable |
| `/api/submissions/<id>/approve` | `POST` | None | Client approves work submission and releases escrow |
| `/api/submissions/<id>/request-changes` | `POST` | `{client_feedback}` | Client requests work changes/revisions |
| `/submissions/<id>/download` | `GET` | None | Download submitted work ZIP archive |

### 5. AI Services & Agentic Assistant APIs

| Endpoint | Method | Payload / Arguments | Description |
| :--- | :--- | :--- | :--- |
| `/api/ai/generate-proposal` | `POST` | `{job_title, job_description, job_skills, style}` | Generate template cover letter (`Professional`, `Direct`, `Detailed`) |
| `/api/ai/analyze-fraud` | `POST` | `{title, description}` | Evaluate risk score and fraud categories |
| `/api/ai/match-freelancers/<job_id>` | `GET` | None | Retrieve heuristic candidate matches |
| `/api/ai/ml-match/<job_id>` | `GET` | None | Retrieve TF-IDF ML semantic candidate matches |
| `/api/chatbot` | `POST` | `{message}` | Conversational Groq chatbot response |
| `/api/agent/runs` | `POST` | `{prompt}` | Initialize and execute Agentic AI Hiring run |
| `/api/agent/runs/<run_id>` | `GET` | None | Fetch run status, summary, audit log, & proposed action |
| `/api/agent/runs/<run_id>/cancel` | `POST` | None | Cancel active or pending-approval agent run |
| `/api/agent/runs/<run_id>/approve` | `POST` | None | Execute human approval gate for proposed proposal acceptance |

### 6. Admin & Dispute APIs

| Endpoint | Method | Payload / Arguments | Description |
| :--- | :--- | :--- | :--- |
| `/api/jobs/<job_id>/complaints` | `POST` | `{message}` | Open a dispute complaint for a job |
| `/api/admin/complaints/<id>/resolve` | `POST` | `{resolution_action, admin_notes}` | Resolve complaint (`release`, `refund`, or `close`) |

---

## Security Architecture & Controls

EscrowIQ incorporates defense-in-depth security principles:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Security Layer Controls                         │
├───────────────────────┬────────────────────────────────────────────────┤
│ Session Security      │ HttpOnly, SameSite=Lax, Secure flags           │
│ Request Protection    │ CSRF token validation on mutating /api/* calls │
│ Data Hashing          │ Werkzeug PBKDF2/scrypt password hashing        │
│ Database Safety       │ Parameterized SQL queries via SQLAlchemy Core  │
│ State Concurrency     │ Transaction locks (FOR UPDATE) on proposal/run │
│ LLM Guardrails        │ Allowlisted read-only tools, step caps         │
│ Consequential Actions │ Mandatory human client approval gate           │
└───────────────────────┴────────────────────────────────────────────────┘
```

1. **CSRF Protection**: Non-GET API requests require matching session CSRF tokens supplied via the `X-CSRF-Token` header.
2. **Strict Session Isolation**: Role checks (`client`, `freelancer`, `admin`) are enforced at route decorators (`@login_required`, `@admin_required`).
3. **Transactional Integrity**: Critical state updates (proposal acceptance, escrow release, agent run approvals) use atomic PostgreSQL transactions with `FOR UPDATE` row locks to prevent race conditions or double-spending.
4. **Agent Sandbox**: The Groq agent runs in a sandbox with zero access to filesystem, shell, arbitrary SQL, or mutation methods.

---

## Environment Configuration

Configure the application by creating a `Backend/.env` file. Refer to `Backend/.env.example` for defaults:

| Variable | Required | Default | Purpose & Description |
| :--- | :---: | :--- | :--- |
| `SECRET_KEY` | **Yes** | *None* | Cryptographic key for Flask session signing. Must be random in production. |
| `DATABASE_URL` | **Yes** | *None* | PostgreSQL connection string (`postgresql+psycopg2://user:pass@host:5432/dbname`). |
| `PORT` | No | `5000` | Port for the local development server or production process. |
| `GROQ_API_KEY` | Optional | `""` | API key for Groq cloud LLM services (required for chatbot & hiring agent). |
| `GROQ_MODEL` | No | `openai/gpt-oss-120b` | Target Groq model identifier used by the provider. |
| `AGENT_MAX_STEPS` | No | `4` | Maximum tool execution iterations per agent run ($1 \le n \le 6$). |
| `AGENT_GROQ_TIMEOUT_SECONDS` | No | `20` | HTTP request timeout in seconds for Groq agent API completions. |
| `AI_MODE` | No | `hybrid` | Fraud detection mode (`hybrid`, `rules`, or `model`). |
| `AI_FALLBACK_ENABLED` | No | `true` | Falls back to rule-based fraud detection if the ML model fails. |
| `SESSION_COOKIE_SECURE` | No | `false` | Set `true` in production behind HTTPS to enforce secure cookies. |
| `SMTP_HOST` | No | `""` | SMTP hostname for sending email notifications and OTP codes. |
| `SMTP_PORT` | No | `587` | SMTP port (typically 587 for TLS or 465 for SSL). |
| `SMTP_USERNAME` | No | `""` | SMTP authentication username. |
| `SMTP_PASSWORD` | No | `""` | SMTP authentication password or app password. |
| `SMTP_FROM_EMAIL` | No | `""` | Sender email address for outgoing notification emails. |
| `SMTP_USE_TLS` | No | `true` | Enable TLS encryption for SMTP email delivery. |
| `ADMIN_EMAIL` | No | `""` | Email address permitted to access `/admin/complaints`. |
| `ADMIN_PASSWORD` | No | `""` | Password used for admin authentication. |
| `FOUNDER_ALERT_EMAILS` | No | `""` | Comma-separated email addresses to receive dispute alert notifications. |

---

## Local Setup & Installation

### Prerequisites
- **Python**: 3.10 or higher
- **PostgreSQL**: 13 or higher (running locally or hosted on Cloud/Neon)
- **Git**: Installed
- **Groq API Key**: (Optional, for live LLM agent & chatbot capabilities)

### Step 1: Clone Repository & Create Virtual Environment

```bash
git clone https://github.com/shxheerkhn/EscrowIQ.git
cd EscrowIQ

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create `Backend/.env`:

```ini
SECRET_KEY=super-secret-local-key-change-me
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/escrowiq
PORT=5000

# Optional Groq API Key for AI features
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Optional SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=no-reply@escrowiq.local
SMTP_USE_TLS=true

ADMIN_EMAIL=admin@escrowiq.local
ADMIN_PASSWORD=AdminPassword123!
```

### Step 4: Run Application Startup Script

Run `Backend/run.py` to automatically connect to PostgreSQL, initialize database tables, and seed initial demo data:

```bash
python Backend/run.py
```

The server will initialize the schema and start at `http://localhost:5000`.

### Step 5: (Optional) Seed AI Test Data

To populate additional test scenarios for fraud detection and hiring agent evaluations:

```bash
python Backend/seed_ai_test_data.py
```

---

## Demo Credentials

The startup script populates pre-configured test users with password `demo123`:

| Role | Name | Username | Email | Seed Balance |
| :--- | :--- | :--- | :--- | :---: |
| **Client** | Sarah Mitchell | `sarah_mitchell` | `sarah@demo.com` | \$8,500.00 |
| **Client** | Ahmed Raza | `ahmed_raza` | `ahmed@demo.com` | \$6,200.00 |
| **Client** | Maya Chen | `maya_chen` | `maya@demo.com` | \$9,100.00 |
| **Client** | AI Test Client | `ai_test_client` | `ai_test_client@escrowiq.local` | \$5,000.00 |
| **Freelancer** | Alex Morgan | `alex_dev` | `alex@demo.com` | \$2,200.00 |
| **Freelancer** | Priya Nair | `priya_design` | `priya@demo.com` | \$1,800.00 |
| **Freelancer** | Omar Hassan | `omar_fullstack` | `omar@demo.com` | \$3,100.00 |
| **Freelancer** | Ayesha Khan | `ayesha_ai` | `ayesha_ai@escrowiq.local` | \$1,200.00 |
| **Admin** | Admin User | `admin` | `admin@example.com` (from `.env`) | N/A |

---

## Testing Suite

EscrowIQ includes unit tests for agent logic, Groq provider integration, and core marketplace workflows:

```bash
# Run Agent Controller & Groq Provider Unit Tests
python -m unittest tests.test_agent_controller tests.test_agent_provider

# Run Core Marketplace Integration Tests (Requires test DATABASE_URL)
python -m unittest tests.test_core_flows
```

---

## Deployment & Production Hardening

### Deployment Configuration
The repository includes configuration for Railway / Nixpacks deployment via `railway.toml` and `Procfile`:

- **Procfile**:
  ```procfile
  web: gunicorn --bind 0.0.0.0:${PORT:-5000} Backend.app:app
  ```
- **railway.toml**:
  ```toml
  [build]
  builder = "NIXPACKS"

  [deploy]
  startCommand = "gunicorn --bind 0.0.0.0:$PORT Backend.app:app"
  healthcheckPath = "/health"
  healthcheckTimeout = 30
  restartPolicyType = "ON_FAILURE"
  ```

### Production Checklist
1. **HTTPS Enforce**: Set `SESSION_COOKIE_SECURE=true` in environment variables.
2. **Secret Key**: Use a strong, random 64-character string for `SECRET_KEY`.
3. **Database Connection Pooling**: Ensure `DATABASE_URL` connects to a production PostgreSQL instance (e.g., Neon Postgres).
4. **Persistent File Storage**: Replace local folder uploads (`Backend/uploads/submissions`) with S3 or object storage for multi-instance deployments.

---

## Repository Structure

```
EscrowIQ/
├── Backend/
│   ├── app.py                   # Main Flask application, API routes, schema init, & business logic
│   ├── run.py                   # Development startup script & demo data seeder
│   ├── seed_ai_test_data.py     # AI evaluation test data seeder
│   ├── fraud_detection.py       # Hybrid rule + TF-IDF scam detection engine
│   ├── ml_matching.py           # scikit-learn TF-IDF semantic freelancer matcher
│   ├── requirements.txt         # Backend Python dependencies
│   ├── .env.example             # Template environment variable configuration
│   └── agentic/
│       ├── __init__.py          # Agent package initialization
│       ├── controller.py        # Bounded Groq agent controller loop
│       ├── provider.py          # Groq SDK provider integration
│       └── registry.py          # Allowlisted read-only tool definitions & validators
│
├── Frontend/
│   ├── static/                  # CSS stylesheets, client-side JS, images & LOGO.png
│   └── templates/               # Jinja2 HTML templates
│       ├── base.html            # Base template layout with navbar & flash alerts
│       ├── index.html           # Landing page
│       ├── login.html           # Login page
│       ├── register.html        # Registration page
│       ├── verify_email.html    # OTP email verification page
│       ├── forgot_password.html # Password reset request/confirm page
│       ├── dashboard_client.html# Client dashboard page
│       ├── dashboard_freelancer.html # Freelancer dashboard page
│       ├── jobs.html            # Job search catalog page
│       ├── job_detail.html      # Job view, proposal management, matching, & messaging
│       ├── agent_workspace.html # Agentic AI Hiring Assistant workspace
│       ├── escrow.html           # Escrow balance & transaction log page
│       ├── profile.html         # User profile editor
│       └── admin_complaints.html# Admin dispute queue page
│
├── tests/
│   ├── test_agent_controller.py # Unit tests for agent loop & JSON parsing
│   ├── test_agent_provider.py   # Unit tests for Groq provider error handling
│   └── test_core_flows.py       # Integration tests for core marketplace & escrow flows
│
├── Procfile                     # Deployment process configuration for Gunicorn
├── railway.toml                 # Nixpacks configuration for Railway deployment
├── requirements.txt             # Root Python dependencies list
├── .gitignore                   # Git exclusions (.env, .venv, pycache, uploads)
└── README.md                    # System documentation
```

---

## Current Scope & Limitations

1. **Payment Gateway Integration**: EscrowIQ models escrow state transitions and balance ledger tracking internally. Real-world commercial deployment would require integration with Stripe Connect, PayPal Marketplace, or Web3 smart contracts.
2. **File Durability**: Deliverable uploads are currently stored in `Backend/uploads/submissions`. Durable production hosting requires object storage (e.g. AWS S3, Cloudflare R2, or Neon Object Storage).
3. **Database Migrations**: Database initialization uses additive `CREATE TABLE IF NOT EXISTS` and `ALTER TABLE` execution in `init_db()`. Future schema evolution should adopt Alembic migrations.

---

## License & Project Status

- **Status**: Academic / Prototype Freelance Marketplace System.
- **Maintainer**: Spiral Labs Work / EscrowIQ Team.
- **License**: Proprietary / Evaluation License (Refer to project repository owner for permissions).