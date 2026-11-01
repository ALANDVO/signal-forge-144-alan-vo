"""Tests for signal service."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.database import Base
from app.models.signal import SignalCreate
from app.services.signal_service import SignalService


@pytest_asyncio.fixture
async def engine():
    """Create in-memory test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """Create test session."""
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def signal_service(session: AsyncSession):
    """Create signal service with test session."""
    return SignalService(session)


class TestSignalGeneration:
    """Tests for signal generation."""

    @pytest.mark.asyncio
    async def test_generate_sine_wave(self, signal_service: SignalService):
        """Test sine wave generation."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test Sine", signal_type="sine", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        assert signal.id is not None
        assert signal.name == "Test Sine"
        assert signal.signal_type == "sine"
        assert signal.sample_rate == 1000
        assert signal.duration == 1.0
        assert signal.frequency == 10.0
        assert len(signal.data) == 1000  # 1000 samples at 1000 Hz for 1 second

    @pytest.mark.asyncio
    async def test_generate_square_wave(self, signal_service: SignalService):
        """Test square wave generation."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test Square", signal_type="square", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        assert signal.signal_type == "square"
        assert len(signal.data) == 1000
        # Square wave should have values at +/- amplitude
        assert all(abs(x) == 1.0 for x in signal.data)

    @pytest.mark.asyncio
    async def test_generate_sawtooth_wave(self, signal_service: SignalService):
        """Test sawtooth wave generation."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test Sawtooth", signal_type="sawtooth", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        assert signal.signal_type == "sawtooth"
        assert len(signal.data) == 1000

    @pytest.mark.asyncio
    async def test_generate_noise(self, signal_service: SignalService):
        """Test noise generation."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test Noise", signal_type="noise", sample_rate=1000, duration=1.0)
        )
        assert signal.signal_type == "noise"
        assert len(signal.data) == 1000
        # Noise should have variation
        assert max(signal.data) > min(signal.data)

    @pytest.mark.asyncio
    async def test_generate_custom_signal(self, signal_service: SignalService):
        """Test custom signal generation."""
        custom_data = [0.0, 0.5, 1.0, 0.5, 0.0, -0.5, -1.0, -0.5]
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test Custom", signal_type="custom", sample_rate=8, duration=1.0, data=custom_data)
        )
        assert signal.signal_type == "custom"
        assert signal.data == custom_data

    @pytest.mark.asyncio
    async def test_generate_sine_requires_frequency(self, signal_service: SignalService):
        """Test that sine wave requires frequency."""
        with pytest.raises(ValueError, match="Frequency required"):
            await signal_service.generate_signal(
                SignalCreate(name="Test", signal_type="sine", sample_rate=1000, duration=1.0)
            )


class TestSignalRetrieval:
    """Tests for signal retrieval."""

    @pytest.mark.asyncio
    async def test_get_signal(self, signal_service: SignalService):
        """Test retrieving a signal by ID."""
        created = await signal_service.generate_signal(
            SignalCreate(name="Test Get", signal_type="sine", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        retrieved = await signal_service.get_signal(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Get"
        assert retrieved.data == created.data

    @pytest.mark.asyncio
    async def test_get_nonexistent_signal(self, signal_service: SignalService):
        """Test retrieving non-existent signal returns None."""
        retrieved = await signal_service.get_signal(999)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_list_signals(self, signal_service: SignalService):
        """Test listing signals."""
        await signal_service.generate_signal(
            SignalCreate(name="Signal 1", signal_type="sine", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        await signal_service.generate_signal(
            SignalCreate(name="Signal 2", signal_type="square", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        signals = await signal_service.list_signals()
        assert len(signals) == 2
        # Most recent first
        assert signals[0].name == "Signal 2"
        assert signals[1].name == "Signal 1"


class TestSignalProcessing:
    """Tests for signal processing operations."""

    @pytest.mark.asyncio
    async def test_compute_fft(self, signal_service: SignalService):
        """Test FFT computation."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test FFT", signal_type="sine", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        fft_signal = await signal_service.compute_fft(signal.id)
        assert fft_signal.signal_type == "fft"
        assert len(fft_signal.data) == len(signal.data)
        assert fft_signal.metadata["source_signal_id"] == signal.id
        assert "frequencies" in fft_signal.metadata

    @pytest.mark.asyncio
    async def test_apply_lowpass_filter(self, signal_service: SignalService):
        """Test lowpass filter application."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test Filter", signal_type="sine", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        filtered = await signal_service.apply_filter(signal.id, "lowpass", 50.0)
        assert filtered.signal_type == "filtered"
        assert len(filtered.data) == len(signal.data)
        assert filtered.metadata["filter_type"] == "lowpass"
        assert filtered.metadata["cutoff_freq"] == 50.0

    @pytest.mark.asyncio
    async def test_apply_highpass_filter(self, signal_service: SignalService):
        """Test highpass filter application."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test Highpass", signal_type="sine", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        filtered = await signal_service.apply_filter(signal.id, "highpass", 5.0)
        assert filtered.metadata["filter_type"] == "highpass"

    @pytest.mark.asyncio
    async def test_convolve_signals(self, signal_service: SignalService):
        """Test signal convolution."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test Signal", signal_type="sine", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        kernel = await signal_service.generate_signal(
            SignalCreate(name="Test Kernel", signal_type="custom", sample_rate=1000, duration=1.0, data=[0.25]*4)
        )
        convolved = await signal_service.convolve(signal.id, kernel.id)
        assert convolved.signal_type == "convolved"
        assert len(convolved.data) == len(signal.data)
        assert convolved.metadata["kernel_signal_id"] == kernel.id

    @pytest.mark.asyncio
    async def test_convolve_mismatched_sample_rates(self, signal_service: SignalService):
        """Test convolution fails with mismatched sample rates."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Signal", signal_type="sine", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        kernel = await signal_service.generate_signal(
            SignalCreate(name="Kernel", signal_type="custom", sample_rate=2000, duration=1.0, data=[0.25]*4)
        )
        with pytest.raises(ValueError, match="Sample rates must match"):
            await signal_service.convolve(signal.id, kernel.id)


class TestOperationAuditLog:
    """Tests for operation audit logging."""

    @pytest.mark.asyncio
    async def test_operation_log_created(self, signal_service: SignalService):
        """Test that operations are logged."""
        signal = await signal_service.generate_signal(
            SignalCreate(name="Test Log", signal_type="sine", sample_rate=1000, duration=1.0, frequency=10.0)
        )
        await signal_service.compute_fft(signal.id)
        await signal_service.apply_filter(signal.id, "lowpass", 50.0)
        operations = await signal_service.get_operations(signal.id)
        assert len(operations) == 3
        # Most recent first
        assert operations[0].operation_type == "filter"
        assert operations[1].operation_type == "fft"
        assert operations[2].operation_type == "generate"
        # Check hash fields
        for op in operations:
            assert op.input_data_hash is not None
            assert op.output_data_hash is not None
            assert op.execution_time_ms is not None
            assert op.status == "completed"
