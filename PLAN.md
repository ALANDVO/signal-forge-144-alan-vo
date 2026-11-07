# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

continue-implementation

## Roadmap

### continue-implementation — Continue implementation and resolve known failures

Status: done

Acceptance:
- Run checks, fix failures, and implement the next planned feature
- Fixed SQLAlchemy reserved attribute name conflict (metadata -> signal_metadata)
- Fixed Pydantic response model to correctly expose metadata via validation alias

Implementation: `backend/app/models/signal.py`, `backend/app/services/signal_service.py`

Tests: `backend/tests/test_signal_service.py`, `backend/tests/test_signals_api.py`

### next-feature — Implement frontend signal visualization

Status: planned

Acceptance:
- React frontend with signal generation form
- Time-domain and frequency-domain charts using Chart.js or Recharts
- Signal list with pagination
- Filter configuration UI

---

Alan Vo · [alanvo.net](https://alanvo.net)
