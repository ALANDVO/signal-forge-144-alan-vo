# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-23

### Added
- FastAPI backend with health check endpoints (`/api/v1/health`, `/api/v1/health/db`)
- React + TypeScript + Vite frontend with health dashboard
- Docker Compose configuration with backend, frontend, and Keycloak services
- Keycloak realm configuration with viewer/operator/admin roles
- Backend tests (3 tests for health endpoints)
- Frontend tests (3 tests for App component)
- SQLite database with SQLAlchemy async ORM
- CORS configuration for local development
- Environment configuration template (`.env.example`)
- Project documentation (README, architecture diagram, API reference)

### Security
- OIDC authentication flow configured (implementation in progress)
- HttpOnly cookie session management planned
- CSRF protection planned for cookie-authenticated writes
- Non-root Docker users

### Infrastructure
- GitHub Actions CI workflow (planned)
- Health checks for all Docker services
- Persistent volumes for database and Keycloak data