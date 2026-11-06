# Changelog

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-11-06

### Fixed
- Fixed SQLAlchemy reserved attribute name conflict: renamed `metadata` column to `signal_metadata` in Signal model
- Fixed Pydantic response model to correctly expose metadata via validation alias

## [1.0.0] - 2024-01-01

### Added
- Initial project structure with FastAPI backend and React frontend
- Signal generation (sine, square, sawtooth, noise, custom)
- FFT computation endpoint
- Digital filtering (lowpass, highpass, bandpass)
- Signal convolution
- Operation audit logging
- Health check endpoints
- Docker Compose deployment with Keycloak OIDC
- SQLite database with SQLAlchemy async ORM
- Pytest test suite for backend services and API
