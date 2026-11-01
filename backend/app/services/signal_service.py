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
            metadata=signal_create.metadata,
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
            select(Signal).order_by(Signal.created_at.desc()).offset(skip).limit(limit)
        )
        signals = result.scalars().all()
        return [SignalResponse(s) for s in signals]

    async def compute_fft(self, signal_id: int) -> SignalResponse:
        """Compute FFT of a signal."""
        start_time = time.perf_counter()

        signal = await self.session.get(Signal, signal_id)
        if not signal:
            raise ValueError(f"Signal {signal_id} not found")

        input_data = signal.data
        fft_result = np.fft.fft(input_data)
        magnitudes = np.abs(fft_result).tolist()
        frequencies = np.fft.fftfreq(len(input_data), 1 / signal.sample_rate).tolist()

        output_data = magnitudes

        execution_time = (time.perf_counter() - start_time) * 1000

        result_signal = Signal(
            name=f"{signal.name} (FFT)",
            signal_type="fft",
            sample_rate=signal.sample_rate,
            duration=signal.duration,
            frequency=None,
            amplitude=1.0,
            phase=0.0,
            data=output_data,
            metadata={
                "source_signal_id": signal.id,
                "frequencies": frequencies,
                "operation": "fft",
            },
        )
        self.session.add(result_signal)
        await self.session.flush()

        self._log_operation(
            signal_id=signal.id,
            operation_type="fft",
            parameters={},
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time,
        )

        await self.session.commit()
        await self.session.refresh(result_signal)
        return SignalResponse(result_signal)

    async def apply_filter(
        self,
        signal_id: int,
        filter_type: str,
        cutoff_freq: float,
        order: int = 4,
    ) -> SignalResponse:
        """Apply a digital filter to a signal."""
        start_time = time.perf_counter()

        signal = await self.session.get(Signal, signal_id)
        if not signal:
            raise ValueError(f"Signal {signal_id} not found")

        from scipy import signal as scipy_signal

        input_data = signal.data
        nyquist = signal.sample_rate / 2
        normalized_cutoff = cutoff_freq / nyquist

        if filter_type == "lowpass":
            b, a = scipy_signal.butter(order, normalized_cutoff, btype="low")
        elif filter_type == "highpass":
            b, a = scipy_signal.butter(order, normalized_cutoff, btype="high")
        elif filter_type == "bandpass":
            if not isinstance(cutoff_freq, (list, tuple)) or len(cutoff_freq) != 2:
                raise ValueError("Bandpass requires [low, high] cutoff frequencies")
            b, a = scipy_signal.butter(order, [c / nyquist for c in cutoff_freq], btype="band")
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")

        output_data = scipy_signal.filtfilt(b, a, input_data).tolist()

        execution_time = (time.perf_counter() - start_time) * 1000

        result_signal = Signal(
            name=f"{signal.name} ({filter_type})",
            signal_type="filtered",
            sample_rate=signal.sample_rate,
            duration=signal.duration,
            frequency=signal.frequency,
            amplitude=signal.amplitude,
            phase=signal.phase,
            data=output_data,
            metadata={
                "source_signal_id": signal.id,
                "filter_type": filter_type,
                "cutoff_freq": cutoff_freq,
                "order": order,
                "operation": "filter",
            },
        )
        self.session.add(result_signal)
        await self.session.flush()

        self._log_operation(
            signal_id=signal.id,
            operation_type="filter",
            parameters={
                "filter_type": filter_type,
                "cutoff_freq": cutoff_freq,
                "order": order,
            },
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time,
        )

        await self.session.commit()
        await self.session.refresh(result_signal)
        return SignalResponse(result_signal)

    async def convolve(self, signal_id: int, kernel_id: int) -> SignalResponse:
        """Convolve two signals."""
        start_time = time.perf_counter()

        signal = await self.session.get(Signal, signal_id)
        kernel = await self.session.get(Signal, kernel_id)
        if not signal or not kernel:
            raise ValueError("Signal or kernel not found")

        if signal.sample_rate != kernel.sample_rate:
            raise ValueError("Sample rates must match for convolution")

        input_data = signal.data
        kernel_data = kernel.data
        output_data = np.convolve(input_data, kernel_data, mode="same").tolist()

        execution_time = (time.perf_counter() - start_time) * 1000

        result_signal = Signal(
            name=f"{signal.name} * {kernel.name}",
            signal_type="convolved",
            sample_rate=signal.sample_rate,
            duration=signal.duration,
            frequency=signal.frequency,
            amplitude=signal.amplitude,
            phase=signal.phase,
            data=output_data,
            metadata={
                "source_signal_id": signal.id,
                "kernel_signal_id": kernel.id,
                "operation": "convolution",
            },
        )
        self.session.add(result_signal)
        await self.session.flush()

        self._log_operation(
            signal_id=signal.id,
            operation_type="convolution",
            parameters={"kernel_signal_id": kernel.id},
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time,
        )

        await self.session.commit()
        await self.session.refresh(result_signal)
        return SignalResponse(result_signal)

    async def get_operations(self, signal_id: int) -> list[SignalOperationResponse]:
        """Get operation history for a signal."""
        result = await self.session.execute(
            select(SignalOperation).where(SignalOperation.signal_id == signal_id).order_by(SignalOperation.created_at.desc())
        )
        operations = result.scalars().all()
        return [SignalOperationResponse(op) for op in operations]
