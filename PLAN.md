# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

next-feature

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

Status: in_progress

Acceptance:
- React frontend with signal generation form
- Time-domain and frequency-domain charts using Chart.js or Recharts
- Signal list with pagination
- Filter configuration UI

Implementation: `frontend/src/components/SignalForm.tsx`, `frontend/src/components/SignalChart.tsx`, `frontend/src/components/SpectrumChart.tsx`, `frontend/src/components/SignalList.tsx`, `frontend/src/components/FilterPanel.tsx`, `frontend/src/App.tsx`

Tests: `frontend/src/App.test.tsx`

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
