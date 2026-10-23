# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

signal-processing-engine

## Roadmap

### core-skeleton — Core FastAPI/React Skeleton with Health Check

Status: done

Acceptance:
- FastAPI backend runs on port 8000 with /health endpoint
- React + TypeScript + Vite frontend runs on port 5173
- Docker Compose with backend, frontend, and Keycloak services
- Backend tests with pytest (at least 3 tests)
- Frontend typecheck and build pass

Implementation: `backend/app/main.py`, `backend/app/api/health.py`, `backend/requirements.txt`, `backend/Dockerfile`, `frontend/package.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/vite.config.ts`, `compose.yaml`, `.env.example`

Tests: `backend/tests/test_health.py`, `frontend/src/App.test.tsx`

### signal-processing-engine — Signal Processing Domain Engine

Status: planned

Acceptance:
- REST API for creating, listing, and processing signals
- Signal generation (sine, square, sawtooth, noise)
- Signal operations (FFT, filtering, convolution)
- Persistent SQLite storage with audit log

Implementation: `backend/app/models/signal.py`, `backend/app/services/signal_service.py`, `backend/app/api/signals.py`, `backend/app/core/database.py`

Tests: `backend/tests/test_signal_service.py`, `backend/tests/test_signals_api.py`

### signal-workflows — Three Core User Workflows

Status: planned

Acceptance:
- Workflow 1: Generate and visualize a signal
- Workflow 2: Apply filter and compare before/after
- Workflow 3: Export signal data as CSV/JSON

Implementation: `frontend/src/components/SignalGenerator.tsx`, `frontend/src/components/SignalVisualizer.tsx`, `frontend/src/components/SignalProcessor.tsx`, `frontend/src/components/SignalExporter.tsx`, `frontend/src/api/client.ts`

Tests: `frontend/src/components/SignalGenerator.test.tsx`, `frontend/src/components/SignalProcessor.test.tsx`

### auth-oidc — OIDC Authentication with Keycloak

Status: planned

Acceptance:
- Keycloak realm configuration
- Backend session management with HttpOnly cookies
- Frontend login/logout flow
- Protected API endpoints

Implementation: `backend/app/core/auth.py`, `backend/app/api/auth.py`, `backend/app/core/security.py`, `keycloak/realm-export.json`, `frontend/src/components/Login.tsx`, `frontend/src/contexts/AuthContext.tsx`

Tests: `backend/tests/test_auth.py`

### llm-integration — LLM Advisory Explanations

Status: planned

Acceptance:
- Optional LLM explanations for signal operations
- Support for OpenAI-compatible, Anthropic, Gemini, Ollama
- Provider configuration via environment variables
- Clear advisory labeling and error handling

Implementation: `backend/app/services/llm_service.py`, `backend/app/api/llm.py`, `backend/app/core/llm_providers.py`

Tests: `backend/tests/test_llm_service.py`

### documentation — Documentation and Packaging

Status: done

Acceptance:
- README with install/run/test steps and architecture diagram
- CHANGELOG.md
- portfolio.json
- LICENSE
- pyproject.toml
- CI workflow

Implementation: `README.md`, `CHANGELOG.md`, `portfolio.json`, `LICENSE`, `pyproject.toml`, `.github/workflows/ci.yml`

