# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-skeleton

## Roadmap

### core-skeleton — FastAPI/React skeleton with SQLite persistence and basic API

Status: in_progress

Acceptance:
- FastAPI app starts and serves health endpoint
- React/Vite frontend builds and loads
- SQLite database initializes with schema
- Backend tests pass (pytest)
- Frontend typecheck and build pass

Implementation: `backend/app/main.py`, `backend/app/api/v1/health.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/requirements.txt`, `frontend/package.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`

Tests: `backend/tests/test_health.py`, `frontend/src/__tests__/App.test.tsx`

### auth-oidc — OIDC authentication with Keycloak (PKCE flow)

Status: planned

Acceptance:
- Login redirects to Keycloak
- Callback exchanges code for tokens
- Protected endpoints require valid token
- Logout clears session

### vector-engine — Vector embedding storage and similarity search

Status: planned

Acceptance:
- Store document chunks with embeddings
- Similarity search returns ranked results
- Batch embedding generation endpoint
- Deterministic offline mode without LLM key

### rag-workflow — RAG workflow: ingest, search, generate

Status: planned

Acceptance:
- Ingest documents (text/PDF) with chunking
- Semantic search across corpus
- LLM-backed answer generation (opt-in)

### docker-ci — Dockerfiles, compose.yaml, and CI workflow

Status: planned

Acceptance:
- Backend and frontend Dockerfiles build
- compose.yaml includes Keycloak + DB
- CI runs pytest, npm build/test, docker build

### docs-packaging — README, LICENSE, CHANGELOG, portfolio.json, .env.example

Status: planned

Acceptance:
- README with install/run/test steps
- MIT LICENSE with author
- CHANGELOG with actual changes
- portfolio.json with required fields
- .env.example with blank credentials

