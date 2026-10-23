"""Pytest configuration and fixtures."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app


@pytest.fixture(scope="function")
def async_client():
    """Create test client."""
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture(scope="function", autouse=True)
async def setup_teardown(async_client):
    yield
    await async_client.aclose()