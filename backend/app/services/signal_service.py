"""Signal processing service with generation, FFT, filtering, and convolution."""

import hashlib
import time
import math
import numpy as np
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.signal import Signal, SignalOperation, SignalCreate, SignalResponse, SignalOperationResponse


class SignalService:
    """Service for signal generation and processing operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _hash_data(self, data: list[float]) -> str:
        """Compute SHA256 hash of signal data."""
        return hashlib.sha256(str(data).encode()).hexdigest()

    def _log_operation(
        self,
        signal_id: int,
        operation_type: str,
        parameters: dict,
        input_data: list[float],
        output_data: list[float],
        execution_time_ms: float,
        status: str = "completed",
        error_message: Optional[str] = None,
    ) -> SignalOperation:
        """Log an operation to audit trail."""
        operation = SignalOperation(
            signal_id=signal_id,
            operation_type=operation_type,
            parameters=parameters,
            input_data_hash=self._hash_data(input_data),
            output_data_hash=self._hash_data(output_data),
            execution_time_ms=execution_time_ms,
            status=status,
            error_message=error_message,
        )
        self.session.add(operation)
        return operation

    async def generate_signal(self, signal_create: SignalCreate) -> SignalResponse:
        """Generate a signal based on type."""
        start_time = time.perf_counter()

        num_samples = int(signal_create.sample_rate * signal_create.duration)
        t = np.linspace(0, signal_create.duration, num_samples, endpoint=False)

        if signal_create.signal_type == "sine":
            if signal_create.frequency is None:
                raise ValueError("Frequency required for sine wave")
            data = signal_create.amplitude * np.sin(
                2 * np.pi * signal_create.frequency * t + signal_create.phase
            ).tolist()
        elif signal_create.signal_type == "square":
            if signal_create.frequency is None:
                raise ValueError("Frequency required for square wave")
            data = signal_create.amplitude * np.sign(
                np.sin(2 * np.pi * signal_create.frequency * t + signal_create.phase)
            ).tolist()
        elif signal_create.signal_type == "sawtooth":
            if signal_create.frequency is None:
                raise ValueError("Frequency required for sawtooth wave")
            data = signal_create.amplitude * 2 * (
                (t * signal_create.frequency + signal_create.phase / (2 * np.pi)) % 1 - 0.5
            ).tolist()
        elif signal_create.signal_type == "noise":
            data = signal_create.amplitude * np.random.normal(0, 1, num_samples).tolist()
        elif signal_create.signal_type == "custom":
            if not signal_create.data:
                raise ValueError("Data required for custom signal")
            data = signal_create.data
        else:
            raise ValueError(f"Unknown signal type: {signal_create.signal_type}")

        execution_time = (time.perf_counter() - start_time) * 1000

        signal = Signal(
            name=signal_create.name,
            signal_type=signal_create.signal_type,
            sample_rate=signal_create.sample_rate,
            duration=signal_create.duration,
            frequency=signal_create.frequency,
            amplitude=signal_create.amplitude,
            phase=signal_create.phase,
            data=data,
            signal_metadata=signal_create.metadata,
        )
        self.session.add(signal)
        await self.session.flush()

        self._log_operation(
            signal_id=signal.id,
            operation_type="generate",
            parameters={
                "signal_type": signal_create.signal_type,
                "frequency": signal_create.frequency,
                "amplitude": signal_create.amplitude,
                "phase": signal_create.phase,
            },
            input_data=[],
            output_data=data,
            execution_time_ms=execution_time,
        )

        await self.session.commit()
        await self.session.refresh(signal)
        return SignalResponse(signal)

    async def get_signal(self, signal_id: int) -> Optional[SignalResponse]:
        """Retrieve a signal by ID."""
        result = await self.session.execute(select(Signal).where(Signal.id == signal_id))
        signal = result.scalar_one_or_none()
        return SignalResponse(signal) if signal else None

    async def list_signals(self, skip: int = 0, limit: int = 100) -> list[SignalResponse]:
        """List signals with pagination."""
        result = await self.session.execute(
            select(Signal).offset(skip).limit(limit).order_by(Signal.created_at.desc())
        )
        signals = result.scalars().all()
        return [SignalResponse(s) for s in signals]

    async def compute_fft(self, signal_id: int) -> SignalResponse:
        """Compute FFT of a signal."""
        start_time = time.perf_counter()

        result = await self.session.execute(select(Signal).where(Signal.id == signal_id))
        signal = result.scalar_one_or_none()
        if not signal:
            raise ValueError("Signal not found")

        data = np.array(signal.data, dtype=np.float64)
        n = len(data)

        # Compute FFT
        fft_result = np.fft.fft(data)
        magnitudes = np.abs(fft_result).tolist()
        frequencies = np.fft.fftfreq(n, 1 / signal.sample_rate).tolist()
        phases = np.angle(fft_result).tolist()

        # Only keep positive frequencies
        pos_mask = np.array(frequencies) >= 0
        pos_frequencies = [f for f, m in zip(frequencies, pos_mask) if m]
        pos_magnitudes = [m for m, mask in zip(magnitudes, pos_mask) if mask]
        pos_phases = [p for p, mask in zip(phases, pos_mask) if mask]

        execution_time = (time.perf_counter() - start_time) * 1000

        # Create FFT result signal
        fft_signal = Signal(
            name=f"{signal.name} (FFT)",
            signal_type="fft",
            sample_rate=signal.sample_rate,
            duration=signal.duration,
            frequency=None,
            amplitude=1.0,
            phase=0.0,
            data=pos_magnitudes,
            signal_metadata={
                "source_signal_id": signal.id,
                "frequencies": pos_frequencies,
                "phases": pos_phases,
                "original_length": n,
            },
        )
        self.session.add(fft_signal)
        await self.session.flush()

        self._log_operation(
            signal_id=signal.id,
            operation_type="fft",
            parameters={"output_signal_id": fft_signal.id},
            input_data=signal.data,
            output_data=pos_magnitudes,
            execution_time_ms=execution_time,
        )

        await self.session.commit()
        await self.session.refresh(fft_signal)
        return SignalResponse(fft_signal)

    async def apply_filter(
        self,
        signal_id: int,
        filter_type: str,
        cutoff_freq: float,
        order: int,
    ) -> SignalResponse:
        """Apply a digital filter to a signal."""
        start_time = time.perf_counter()

        result = await self.session.execute(select(Signal).where(Signal.id == signal_id))
        signal = result.scalar_one_or_none()
        if not signal:
            raise ValueError("Signal not found")

        from scipy.signal import butter, filtfilt

        nyquist = signal.sample_rate / 2
        if cutoff_freq >= nyquist:
            raise ValueError(f"Cutoff frequency must be less than Nyquist frequency ({nyquist} Hz)")

        normalized_cutoff = cutoff_freq / nyquist

        if filter_type == "lowpass":
            b, a = butter(order, normalized_cutoff, btype="low")
        elif filter_type == "highpass":
            b, a = butter(order, normalized_cutoff, btype="high")
        elif filter_type == "bandpass":
            # For bandpass, cutoff_freq is treated as center frequency, bandwidth = cutoff_freq
            low = max(0.001, (cutoff_freq - cutoff_freq / 2) / nyquist)
            high = min(0.999, (cutoff_freq + cutoff_freq / 2) / nyquist)
            if low >= high:
                raise ValueError("Invalid bandpass frequency range")
            b, a = butter(order, [low, high], btype="band")
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")

        data = np.array(signal.data, dtype=np.float64)
        filtered_data = filtfilt(b, a, data).tolist()

        execution_time = (time.perf_counter() - start_time) * 1000

        filtered_signal = Signal(
            name=f"{signal.name} ({filter_type})",
            signal_type=f"filtered_{filter_type}",
            sample_rate=signal.sample_rate,
            duration=signal.duration,
            frequency=signal.frequency,
            amplitude=signal.amplitude,
            phase=signal.phase,
            data=filtered_data,
            signal_metadata={
                "source_signal_id": signal.id,
                "filter_type": filter_type,
                "cutoff_freq": cutoff_freq,
                "order": order,
            },
        )
        self.session.add(filtered_signal)
        await self.session.flush()

        self._log_operation(
            signal_id=signal.id,
            operation_type="filter",
            parameters={
                "filter_type": filter_type,
                "cutoff_freq": cutoff_freq,
                "order": order,
                "output_signal_id": filtered_signal.id,
            },
            input_data=signal.data,
            output_data=filtered_data,
            execution_time_ms=execution_time,
        )

        await self.session.commit()
        await self.session.refresh(filtered_signal)
        return SignalResponse(filtered_signal)

    async def convolve(self, signal_id: int, kernel_id: int) -> SignalResponse:
        """Convolve two signals."""
        start_time = time.perf_counter()

        result = await self.session.execute(select(Signal).where(Signal.id == signal_id))
        signal = result.scalar_one_or_none()
        if not signal:
            raise ValueError("Signal not found")

        result = await self.session.execute(select(Signal).where(Signal.id == kernel_id))
        kernel = result.scalar_one_or_none()
        if not kernel:
            raise ValueError("Kernel signal not found")

        if signal.sample_rate != kernel.sample_rate:
            raise ValueError("Signals must have the same sample rate for convolution")

        data = np.array(signal.data, dtype=np.float64)
        kernel_data = np.array(kernel.data, dtype=np.float64)

        # Full convolution
        convolved_data = np.convolve(data, kernel_data, mode="full").tolist()
        # Duration of convolved signal
        convolved_duration = len(convolved_data) / signal.sample_rate

        execution_time = (time.perf_counter() - start_time) * 1000

        convolved_signal = Signal(
            name=f"{signal.name} * {kernel.name}",
            signal_type="convolved",
            sample_rate=signal.sample_rate,
            duration=convolved_duration,
            frequency=None,
            amplitude=1.0,
            phase=0.0,
            data=convolved_data,
            signal_metadata={
                "source_signal_id": signal.id,
                "kernel_signal_id": kernel.id,
            },
        )
        self.session.add(convolved_signal)
        await self.session.flush()

        self._log_operation(
            signal_id=signal.id,
            operation_type="convolution",
            parameters={
                "kernel_signal_id": kernel.id,
                "output_signal_id": convolved_signal.id,
            },
            input_data=signal.data,
            output_data=convolved_data,
            execution_time_ms=execution_time,
        )

        await self.session.commit()
        await self.session.refresh(convolved_signal)
        return SignalResponse(convolved_signal)

    async def get_operations(self, signal_id: int) -> list[SignalOperationResponse]:
        """Get operation history for a signal."""
        result = await self.session.execute(
            select(SignalOperation).where(SignalOperation.signal_id == signal_id).order_by(SignalOperation.created_at)
        )
        operations = result.scalars().all()
        return [SignalOperationResponse(op) for op in operations]

