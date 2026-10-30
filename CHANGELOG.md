# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — 2026-10-30

### Added
- FastAPI backend with health endpoints (`/health`, `/health/db`)
- SQLite database with SQLAlchemy async ORM
- React/Vite frontend with health dashboard
- Backend pytest tests (2 passing)
- Frontend TypeScript build and vitest tests (3 passing)
- Pydantic settings with environment variable support
- CORS configuration for local development
- Vite proxy for `/health` API in development

### Fixed
- Frontend TypeScript errors (email rendering, ImportMeta types, jest-dom matchers)
- Missing `index.html` entry point for Vite
- Test setup for `@testing-library/jest-dom`

### Known Issues
- React `act()` warnings in vitest tests (non-blocking)
