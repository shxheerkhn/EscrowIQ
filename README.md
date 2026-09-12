EscrowIQ

EscrowIQ is a freelance marketplace prototype built around escrow-based transactions, AI-assisted marketplace analysis, and an Agentic AI Hiring Assistant.

The platform connects clients and freelancers through a controlled marketplace workflow:

Client posts a job
        ↓
Freelancers submit proposals
        ↓
Client reviews proposals
        ↓
Client accepts a proposal
        ↓
Escrow is funded
        ↓
Freelancer submits work
        ↓
Client reviews the submission
        ↓
Approve / Request Changes / Complaint
        ↓
Release / Refund / Dispute Resolution

EscrowIQ combines a Flask backend, PostgreSQL persistence, server-rendered Jinja2 templates, vanilla JavaScript, session authentication, CSRF protection, SMTP notifications, deterministic/hybrid marketplace analysis, a Groq chatbot, and a bounded Groq-based Agentic AI Hiring Assistant.

Project status: Working academic/prototype application. It is not presented as a production payment platform or production-grade legal/privacy infrastructure.

Table of Contents

Overview

Key Features

Marketplace Workflow

Agentic AI Hiring Assistant

AI and Intelligent Features

Technology Stack

Architecture

Repository Structure

Local Setup

Environment Configuration

Running the Application

Demo and Seed Data

Testing

Security Controls

Important Routes

Database and Persistence

Deployment

Current Limitations

Project Documentation

License and Project Status

Overview

EscrowIQ models the core lifecycle of a freelance marketplace while keeping important transaction state behind server-side validation and database transactions.

A client can create a job containing:

Job title

Description

Required skills

Budget

Deadline

Freelancers can discover suitable opportunities and submit proposals containing:

Bid amount

Timeline

Cover letter

After a proposal is accepted, the accepted bid becomes the basis for escrow funding. The freelancer can then submit work, after which the client can approve the delivery, request changes, or open a complaint.

The platform also includes AI-assisted marketplace capabilities:

Hybrid freelancer matching

Fraud analysis

Proposal generation

General Groq chatbot

Agentic AI Hiring Assistant

The Hiring Assistant is intentionally different from the general chatbot. It can inspect marketplace information through a small allowlisted tool set, use deterministic backend analysis, compare available candidates, produce a recommendation, and prepare a proposal-acceptance recommendation that requires explicit client approval.

Key Features

Marketplace

Client and freelancer accounts

Email verification

Login and logout

Password reset

Profile editing

Client job posting with validation

Required skills and deadlines

Freelancer proposals

Proposal acceptance/rejection

Competing pending-proposal rejection

Escrow funding, release, and refund

Work submission through notes, links, ZIP uploads, or folder uploads

Revision/change requests

Complaints and admin resolution

Accepted-project messaging

In-app notifications

SMTP email notifications

AI / Intelligent Features

Agentic AI Hiring Assistant

Groq-powered general chatbot

TF-IDF and hybrid freelancer matching

Skill synonyms and semantic similarity

Rating and review signals

Rule-based fraud analysis

TF-IDF-assisted fraud analysis

Template-based proposal generation

Security and Reliability

Session-based authentication

Role-based access checks

CSRF protection for mutating API requests

Password hashing using Werkzeug

Server-side ownership validation

Server-side state validation

Transactional marketplace operations

Validated Agent tool arguments

Allowlisted Agent tools

Explicit human approval for the Agent's consequential action

Persistent Agent run and audit records

Marketplace Workflow

Client

Register and verify the account.

Sign in.

Create a job with title, description, skills, budget, and deadline.

Review incoming proposals.

Accept one proposal.

Fund escrow.

Review submitted work.

Approve the work, request changes, or open a complaint.

Freelancer

Register and verify the account.

Complete the freelancer profile.

Browse jobs or matched opportunities.

Submit a proposal with bid, timeline, and cover letter.

Wait for acceptance and escrow funding.

Submit completed work.

Respond to requested changes where applicable.

Admin

Access the complaint queue.

Inspect disputed marketplace activity.

Resolve complaints using the supported release, refund, or close outcomes.

The backend updates the relevant marketplace state using server-side validation and transaction handling.

Agentic AI Hiring Assistant

The EscrowIQ Hiring Assistant is an agent/orchestrator for client hiring analysis, not merely a conversational chatbot.

A client can provide an objective such as:

Find the strongest freelancer for my Python machine-learning job, evaluate compatibility and relevant risk, compare the strongest candidates, and recommend the best option.

The Agent then works through controlled backend tools.

Agent Architecture

flowchart TD
    A[Client objective] --> B[Agent Controller]
    B --> C[Groq structured decision]
    C --> D[Allowlisted tool]
    D --> E[Deterministic backend service]
    E --> F[Structured tool result]
    F --> B
    B --> G[Recommendation]
    G --> H[Explicit client approval]
    H --> I[Server-side revalidation]
    I --> J[Normal proposal acceptance path]

The architecture deliberately separates model reasoning from application authority:

User objective
      ↓
Agent Controller
      ↓
Groq structured decision
      ↓
Validated tool
      ↓
Existing deterministic backend service
      ↓
Structured result
      ↓
Agent continues or recommends
      ↓
Human approval
      ↓
Server-side revalidation
      ↓
Existing marketplace transaction path

The LLM plans and orchestrates.

The backend remains the source of truth for:

Marketplace data

Matching

Ranking

Fraud analysis

Authorization

Job ownership

Proposal state

Current marketplace state

State-changing operations

Structured Agent Loop

The controller runs a bounded loop of structured Groq completions:

Receive the client objective.

Ask Groq for a structured decision.

Validate the requested tool/action.

Execute the allowlisted backend tool.

Record the execution.

Return the actual backend result as structured tool_result context.

Ask Groq for the next structured decision.

Continue until a final recommendation or bounded failure.

The model's decisions are preserved as assistant turns, while backend results are returned as structured tool-result context before the next decision.

The controller accepts a final response only when it is valid JSON with a non-empty summary and, when present, a valid pending-proposal recommendation.

Waiting/planning prose is not treated as a successful final Agent response.

Hidden chain-of-thought is not exposed in the user interface.

Provider and Model

The Agent uses the Groq Python SDK through GroqAgentProvider.

Current intended configuration:

GROQ_MODEL=openai/gpt-oss-120b

The Agent requires:

GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-120b

There is no automatic Agent provider/model fallback.

The general chatbot also uses the configured GROQ_MODEL when available and otherwise follows its existing default behavior.

Allowlisted Tools

The current Agent registry exposes only validated, read-only marketplace tools:

Tool

Purpose

list_client_jobs

Lists the authenticated client's open jobs.

get_job_candidates

Retrieves suitable verified freelancers for an owned open job using the deterministic hybrid matcher.

get_pending_proposals

Lists pending proposals for an owned open job.

The Agent cannot use:

Arbitrary SQL

Arbitrary Python

Shell commands

Unrestricted filesystem access

Unrestricted HTTP requests

Unapproved tools

Tool arguments are validated before execution, and the backend performs relevant ownership and job-state checks.

Human Approval

The Agent may recommend acceptance of an existing pending proposal, but it cannot autonomously accept it.

The consequential flow is:

Agent analysis
      ↓
Recommendation
      ↓
Pending approval
      ↓
Explicit client approval
      ↓
Server-side revalidation
      ↓
Normal proposal acceptance path

Before acceptance, the server revalidates client ownership, proposal status, and current marketplace state.

The Agent does not autonomously:

Fund escrow

Release escrow

Refund escrow

Resolve complaints

Perform arbitrary marketplace mutations

Agent Persistence and Audit

Agent execution is persisted in PostgreSQL through:

agent_runs

agent_audit_events

Run records contain information such as:

Client

Prompt/objective

Summary

Proposed action

Status

Timestamps

Errors

Audit events capture important lifecycle events such as:

Run start

Tool use/rejection

Approval request

Completion/failure

Cancellation

Stale approval

Completed approval

Current run statuses include:

running
completed
pending_approval
failed
approving
approved
stale
cancelled

The Agent loop is bounded by:

AGENT_MAX_STEPS=4
AGENT_GROQ_TIMEOUT_SECONDS=20

The application caps the maximum Agent step count.

AI and Intelligent Features

Freelancer Matching

The matching service uses deterministic/hybrid analysis rather than allowing the LLM to invent candidate rankings.

Signals include:

Required skills

Freelancer skills

Skill synonyms

TF-IDF semantic similarity

Cosine similarity

Ratings

Review counts

This allows the Agent to orchestrate existing marketplace intelligence while keeping ranking logic inside the backend.

Fraud Analysis

Fraud analysis combines:

Rule-based checks

TF-IDF-assisted analysis

The application produces risk-oriented analysis for relevant marketplace activity.

Proposal Generation

The application includes template-based proposal generation using job context such as:

Job title

Description

Required skills

General Chatbot

The general chatbot is available through:

POST /api/chatbot

It is intended for conversational assistance around the marketplace.

Chatbot vs Hiring Agent

Component

Purpose

General Chatbot

Conversational marketplace help

Hiring Assistant

Agentic hiring analysis using controlled tools and explicit approval

The Hiring Assistant is therefore a separate agentic workflow rather than simply a renamed chatbot.

Technology Stack

Area

Technology

Language

Python

Backend

Flask

Database

PostgreSQL

Database access

SQLAlchemy Core, psycopg2-binary

Frontend

Jinja2, vanilla JavaScript, custom CSS

Matching

scikit-learn TF-IDF, cosine similarity, deterministic rules

LLM

Groq Python SDK

Email

Python SMTP

Password security

Werkzeug security helpers

Testing

Python unittest

Local server

Flask development server

Deployment server

Gunicorn

Deployment configuration

Railway/Nixpacks

Architecture

At a high level:

┌───────────────────────────────────────────────┐
│                  Frontend                     │
│ Jinja2 + Vanilla JavaScript + CSS            │
└───────────────────────┬───────────────────────┘
                        ↓
┌───────────────────────────────────────────────┐
│                Flask Backend                  │
│ Routes + Auth + Validation + Marketplace     │
│ Logic + APIs + Notifications                 │
└───────────────┬───────────────────┬───────────┘
                ↓                   ↓
┌────────────────────────┐  ┌───────────────────┐
│ PostgreSQL             │  │ AI Services       │
│ Users / Jobs / Bids    │  │ Matching          │
│ Escrow / Submissions   │  │ Fraud Analysis    │
│ Agent Runs / Audit     │  │ Proposal Drafting │
└────────────────────────┘  │ Groq Chatbot      │
                            │ Groq Agent        │
                            └───────────────────┘

The important design principle is:

The LLM orchestrates; the backend decides what is actually allowed.

Repository Structure

Project/
├── Backend/
│   ├── app.py
│   ├── run.py
│   ├── seed_ai_test_data.py
│   ├── fraud_detection.py
│   ├── ml_matching.py
│   ├── requirements.txt
│   └── agentic/
│       ├── controller.py
│       ├── provider.py
│       ├── registry.py
│       └── __init__.py
│
├── Frontend/
│   ├── templates/
│   │   └── agent_workspace.html
│   ├── script/
│   │   └── nothing.js
│   └── static/
│
├── tests/
│   ├── test_agent_controller.py
│   ├── test_agent_provider.py
│   └── test_core_flows.py
│
├── requirements.txt
├── Procfile
├── railway.toml
├── AGENTS.md
├── AI_TEST_CASES.md
└── CODEX_HANDOFF.md

Runtime/local files such as Backend/.env, uploaded submissions, caches, virtual environments, and generated files are intentionally omitted.

Do not commit Backend/.env to GitHub.

Local Setup

Prerequisites

Python 3.10+

PostgreSQL

Git

Groq API key for live AI functionality

SMTP credentials if email delivery is required

1. Create a Virtual Environment

From the repository root:

python -m venv .venv
.venv\Scripts\Activate.ps1

2. Install Dependencies

python -m pip install -r requirements.txt

Or from the backend context:

python -m pip install -r Backend/requirements.txt

3. Create the PostgreSQL Database

Create a PostgreSQL database for EscrowIQ and configure DATABASE_URL.

Example:

DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/escrowiq

The application uses additive schema initialization in init_db() and does not currently use Alembic migrations.

Environment Configuration

Create:

Backend/.env

Use placeholders locally and never commit real credentials.

Example:

SECRET_KEY=your-secret-key

DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/escrowiq

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=no-reply@example.com
SMTP_USE_TLS=true

ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password

FOUNDER_ALERT_EMAILS=alerts@example.com

SESSION_COOKIE_SECURE=false

AI_MODE=hybrid
AI_FALLBACK_ENABLED=true

GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-120b

AGENT_MAX_STEPS=4
AGENT_GROQ_TIMEOUT_SECONDS=20

Configuration Notes

Variable

Purpose

SECRET_KEY

Flask/session security

DATABASE_URL

PostgreSQL connection

SMTP_*

Email notifications

ADMIN_*

Local/admin configuration

GROQ_API_KEY

Groq API authentication

GROQ_MODEL

Configured Groq model

AGENT_MAX_STEPS

Agent loop bound

AGENT_GROQ_TIMEOUT_SECONDS

Agent Groq request timeout

AI_MODE

AI/fraud-analysis behavior

AI_FALLBACK_ENABLED

Existing AI/fraud-analysis behavior

AI_MODE and AI_FALLBACK_ENABLED are not Agent provider-switch settings.

Running the Application

Start the application from the repository root:

python Backend/run.py

The startup process:

Loads configuration

Initializes the database schema

Seeds demo data

Starts Flask

The local application is normally available at:

http://localhost:5000

Health check:

GET /health

Hiring Assistant:

/agent

General chatbot API:

POST /api/chatbot

Demo and Seed Data

The normal startup process includes demo-data seeding.

Optional AI-focused seed data:

python Backend/seed_ai_test_data.py

The AI test seed includes a demo client:

ai_test_client@escrowiq.local

with the seed password:

demo123

Use seeded credentials only for local testing.

Testing

EscrowIQ uses Python's built-in unittest framework.

For core marketplace integration tests:

python -m unittest tests.test_core_flows

For Agent tests:

python -m unittest tests.test_agent_controller tests.test_agent_provider

The Agent tests cover areas including:

Structured Agent tool loop

Preservation of tool results

Invalid waiting/planning responses

Groq provider validation

Approval handling

Cancellation

Stale-action handling

Single-use approval

Client ownership protections

Core integration tests require PostgreSQL and can skip when an appropriate test DATABASE_URL is unavailable.

Security Controls

EscrowIQ applies security controls at both the marketplace and Agent levels.

Authentication

Session authentication

Role checks

Email verification

Password hashing with Werkzeug

Password reset workflow

Request Protection

CSRF enforcement for mutating /api/* requests

Server-side validation

Server-side ownership checks

Marketplace State Protection

Important marketplace operations validate:

User role

Resource ownership

Job state

Proposal state

Escrow state

Transactional database handling is used for the supported state-changing workflows.

Agent Security

The Agent is constrained by:

Allowlisted tools

Argument validation

Ownership checks

State checks

Bounded execution

Structured output validation

No arbitrary SQL

No arbitrary Python execution

No shell execution

No unrestricted tool execution

Explicit human approval for the consequential Agent action

The LLM is never treated as the authority for persistent marketplace state.

Important Routes

Page Routes

Key routes include:

/
 /register
 /login
 /verify-email
 /forgot-password
 /dashboard
 /jobs
 /jobs/<job_id>
 /profile
 /escrow
 /admin/complaints
 /agent
 /health

Agent API

POST /api/agent/runs
GET  /api/agent/runs/<run_id>
POST /api/agent/runs/<run_id>/cancel
POST /api/agent/runs/<run_id>/approve

General AI API

POST /api/chatbot

Additional APIs support authentication, jobs, proposals, escrow, submissions, complaints, profiles, notifications, messaging, matching, fraud analysis, and proposal generation.

Frontend/templates/ai_features.html is a legacy unrouted template and is not part of the active AI workflow.

Database and Persistence

PostgreSQL is the primary persistence layer.

Database access uses SQLAlchemy Core and psycopg2-binary.

Marketplace data includes:

Users

Profiles

Jobs

Proposals

Escrow records

Work submissions

Complaints

Notifications

Related marketplace state

Agent-specific persistence includes:

agent_runs
agent_audit_events

The application currently initializes/updates its schema through application initialization logic rather than a versioned migration framework such as Alembic.

Deployment

The repository contains Railway/Nixpacks deployment configuration.

The production-style server command is:

gunicorn --bind 0.0.0.0:${PORT:-5000} Backend.app:app

Deployment configuration is provided through:

Procfile
railway.toml

For deployment:

Configure all required environment variables.

Provide a reachable PostgreSQL database.

Configure SMTP if email is required.

Configure GROQ_API_KEY for live AI.

Use HTTPS.

Set:

SESSION_COOKIE_SECURE=true

when running behind HTTPS.
7. Use a strong production SECRET_KEY.

Uploaded submissions currently use:

Backend/uploads/submissions

Local disk should not be assumed to provide durable production storage.

The repository does not contain a verified Vercel configuration.

Current Limitations

EscrowIQ is a prototype, so several production concerns remain outside its current scope.

Database migrations

There is no full Alembic-style migration system.

Payment infrastructure

The escrow workflow models marketplace escrow state but should not be interpreted as integration with a regulated real-world payment processor.

File storage

Uploads currently use local storage. A production deployment would require durable object/file storage.

AI dependency

Live chatbot and Agent responses require the configured Groq service.

Agent scope

The Hiring Assistant is intentionally bounded to hiring analysis and recommendation. It does not autonomously operate the complete marketplace.

Frontend architecture

The application uses Jinja2 and vanilla JavaScript rather than a separate frontend framework.

Production hardening

Additional security, infrastructure, observability, storage, database, privacy, and operational hardening would be required before production use.

Project Documentation

Additional project documentation includes:

AGENTS.md — development/agent guidance

AI_TEST_CASES.md — AI-focused test scenarios

CODEX_HANDOFF.md — project handoff/development notes

These documents complement this README.

Key Implementation Files

File

Responsibility

Backend/app.py

Main Flask application, routes, schema initialization, marketplace APIs and logic

Backend/run.py

Local startup and demo-data seeding

Backend/fraud_detection.py

Fraud-analysis logic

Backend/ml_matching.py

Freelancer matching logic

Backend/agentic/controller.py

Agent orchestration and bounded loop

Backend/agentic/provider.py

Groq Agent provider

Backend/agentic/registry.py

Allowlisted Agent tools and validation

Frontend/templates/agent_workspace.html

Hiring Assistant workspace

tests/test_agent_controller.py

Agent controller tests

tests/test_agent_provider.py

Groq provider tests

tests/test_core_flows.py

Marketplace integration tests

Project Status

EscrowIQ currently combines:

Freelance Marketplace
        +
Escrow Workflow
        +
AI-Assisted Analysis
        +
Groq Chatbot
        +
Agentic AI Hiring Assistant
        +
Human Approval Controls

The Agentic AI component demonstrates controlled tool use, backend-grounded analysis, bounded orchestration, persistent audit records, and human approval for consequential actions.

The central design principle is:

AI assists the hiring decision; the application backend controls what the system is actually allowed to do.

No license file is currently present in the repository.

EscrowIQ is a working academic/prototype project and should be evaluated against its current implementation and test suite rather than treated as a production payment service.