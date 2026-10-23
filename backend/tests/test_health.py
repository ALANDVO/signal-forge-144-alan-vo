"""Backend tests for health endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test basic health check endpoint."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "signal-forge"


@pytest.mark.asyncio
async def test_health_check_db(async_client: AsyncClient):
    """Test database health check endpoint."""
    response = await async_client.get("/api/v1/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_root_redirect(async_client: AsyncClient):
    """Test root endpoint returns 404 (no root route defined)."""
    response = await async_client.get("/")
    assert response.status_code == 404