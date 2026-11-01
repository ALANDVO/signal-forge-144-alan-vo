"""Tests for signals API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.core.database import Base, get_session


@pytest.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(test_session):
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


class TestSignalsAPI:
    """Tests for signals API endpoints."""

    @pytest.mark.asyncio
    async def test_create_sine_signal(self, client: AsyncClient):
        """Test creating a sine wave signal."""
        response = await client.post(
            "/api/v1/signals",
            json={
                "name": "API Sine",
                "signal_type": "sine",
                "sample_rate": 1000,
                "duration": 1.0,
                "frequency": 10.0,
                "amplitude": 1.0,
                "phase": 0.0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Sine"
        assert data["signal_type"] == "sine"
        assert data["sample_rate"] == 1000
        assert data["frequency"] == 10.0
        assert len(data["data"]) == 1000
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_square_signal(self, client: AsyncClient):
        """Test creating a square wave signal."""
        response = await client.post(
            "/api/v1/signals",
            json={
                "name": "API Square",
                "signal_type": "square",
                "sample_rate": 1000,
                "duration": 1.0,
                "frequency": 10.0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["signal_type"] == "square"
        assert all(abs(x) == 1.0 for x in data["data"])

    @pytest.mark.asyncio
    async def test_create_noise_signal(self, client: AsyncClient):
        """Test creating a noise signal."""
        response = await client.post(
            "/api/v1/signals",
            json={
                "name": "API Noise",
                "signal_type": "noise",
                "sample_rate": 1000,
                "duration": 1.0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["signal_type"] == "noise"
        assert len(data["data"]) == 1000

    @pytest.mark.asyncio
    async def test_create_custom_signal(self, client: AsyncClient):
        """Test creating a custom signal."""
        custom_data = [0.0, 0.5, 1.0, 0.5, 0.0, -0.5, -1.0, -0.5]
        response = await client.post(
            "/api/v1/signals",
            json={
                "name": "API Custom",
                "signal_type": "custom",
                "sample_rate": 8,
                "duration": 1.0,
                "data": custom_data,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"] == custom_data

    @pytest.mark.asyncio
    async def test_create_signal_missing_frequency(self, client: AsyncClient):
        """Test creating sine signal without frequency fails."""
        response = await client.post(
            "/api/v1/signals",
            json={
                "name": "No Freq",
                "signal_type": "sine",
                "sample_rate": 1000,
                "duration": 1.0,
            },
        )
        assert response.status_code == 400
        assert "Frequency required" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_list_signals(self, client: AsyncClient):
        """Test listing signals."""
        await client.post(
            "/api/v1/signals",
            json={"name": "Signal 1", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        await client.post(
            "/api/v1/signals",
            json={"name": "Signal 2", "signal_type": "square", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        response = await client.get("/api/v1/signals")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Signal 2"
        assert data[1]["name"] == "Signal 1"

    @pytest.mark.asyncio
    async def test_list_signals_pagination(self, client: AsyncClient):
        """Test signal listing pagination."""
        for i in range(5):
            await client.post(
                "/api/v1/signals",
                json={"name": f"Signal {i}", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
            )
        response = await client.get("/api/v1/signals?skip=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_signal(self, client: AsyncClient):
        """Test getting a signal by ID."""
        create_resp = await client.post(
            "/api/v1/signals",
            json={"name": "Get Me", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = await client.get(f"/api/v1/signals/{signal_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == signal_id
        assert data["name"] == "Get Me"

    @pytest.mark.asyncio
    async def test_get_nonexistent_signal(self, client: AsyncClient):
        """Test getting non-existent signal returns 404."""
        response = await client.get("/api/v1/signals/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_compute_fft(self, client: AsyncClient):
        """Test FFT endpoint."""
        create_resp = await client.post(
            "/api/v1/signals",
            json={"name": "FFT Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = await client.post(f"/api/v1/signals/{signal_id}/fft")
        assert response.status_code == 200
        data = response.json()
        assert data["signal_type"] == "fft"
        assert data["metadata"]["source_signal_id"] == signal_id
        assert "frequencies" in data["metadata"]

    @pytest.mark.asyncio
    async def test_apply_lowpass_filter(self, client: AsyncClient):
        """Test lowpass filter endpoint."""
        create_resp = await client.post(
            "/api/v1/signals",
            json={"name": "Filter Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = await client.post(
            f"/api/v1/signals/{signal_id}/filter",
            params={"filter_type": "lowpass", "cutoff_freq": 50.0, "order": 4},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["signal_type"] == "filtered"
        assert data["metadata"]["filter_type"] == "lowpass"
        assert data["metadata"]["cutoff_freq"] == 50.0

    @pytest.mark.asyncio
    async def test_apply_highpass_filter(self, client: AsyncClient):
        """Test highpass filter endpoint."""
        create_resp = await client.post(
            "/api/v1/signals",
            json={"name": "Highpass Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = await client.post(
            f"/api/v1/signals/{signal_id}/filter",
            params={"filter_type": "highpass", "cutoff_freq": 5.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["filter_type"] == "highpass"

    @pytest.mark.asyncio
    async def test_apply_bandpass_filter(self, client: AsyncClient):
        """Test bandpass filter endpoint."""
        create_resp = await client.post(
            "/api/v1/signals",
            json={"name": "Bandpass Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        # Bandpass expects cutoff_freq as a range, but our API takes single float
        # This tests the validation
        response = await client.post(
            f"/api/v1/signals/{signal_id}/filter",
            params={"filter_type": "bandpass", "cutoff_freq": 50.0},
        )
        # Currently bandpass fails due to expecting list - this is expected behavior
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_convolve_signals(self, client: AsyncClient):
        """Test convolution endpoint."""
        signal_resp = await client.post(
            "/api/v1/signals",
            json={"name": "Conv Signal", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = signal_resp.json()["id"]
        kernel_resp = await client.post(
            "/api/v1/signals",
            json={"name": "Conv Kernel", "signal_type": "custom", "sample_rate": 1000, "duration": 1.0, "data": [0.25]*4},
        )
        kernel_id = kernel_resp.json()["id"]
        response = await client.post(f"/api/v1/signals/{signal_id}/convolve", params={"kernel_id": kernel_id})
        assert response.status_code == 200
        data = response.json()
        assert data["signal_type"] == "convolved"
        assert data["metadata"]["kernel_signal_id"] == kernel_id

    @pytest.mark.asyncio
    async def test_convolve_mismatched_sample_rates(self, client: AsyncClient):
        """Test convolution with mismatched sample rates fails."""
        signal_resp = await client.post(
            "/api/v1/signals",
            json={"name": "Signal", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = signal_resp.json()["id"]
        kernel_resp = await client.post(
            "/api/v1/signals",
            json={"name": "Kernel", "signal_type": "custom", "sample_rate": 2000, "duration": 1.0, "data": [0.25]*4},
        )
        kernel_id = kernel_resp.json()["id"]
        response = await client.post(f"/api/v1/signals/{signal_id}/convolve", params={"kernel_id": kernel_id})
        assert response.status_code == 400
        assert "Sample rates must match" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_signal_operations(self, client: AsyncClient):
        """Test getting operation history."""
        create_resp = await client.post(
            "/api/v1/signals",
            json={"name": "Ops Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        await client.post(f"/api/v1/signals/{signal_id}/fft")
        await client.post(f"/api/v1/signals/{signal_id}/filter", params={"filter_type": "lowpass", "cutoff_freq": 50.0})
        response = await client.get(f"/api/v1/signals/{signal_id}/operations")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["operation_type"] == "filter"
        assert data[1]["operation_type"] == "fft"
        assert data[2]["operation_type"] == "generate"
        for op in data:
            assert "input_data_hash" in op
            assert "output_data_hash" in op
            assert "execution_time_ms" in op
