"""Signal domain models."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Signal(Base):
    """Signal entity for persistent storage."""

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    signal_type = Column(String(50), nullable=False)  # sine, square, sawtooth, noise, custom
    sample_rate = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)  # seconds
    frequency = Column(Float, nullable=True)  # Hz for periodic signals
    amplitude = Column(Float, default=1.0)
    phase = Column(Float, default=0.0)  # radians
    data = Column(JSON, nullable=False)  # array of samples
    metadata = Column(JSON, nullable=True)  # additional params
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    operations = relationship("SignalOperation", back_populates="signal", cascade="all, delete-orphan")


class SignalOperation(Base):
    """Audit log for signal processing operations."""

    __tablename__ = "signal_operations"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True)
    operation_type = Column(String(50), nullable=False)  # fft, filter, convolution, generate
    parameters = Column(JSON, nullable=True)  # operation-specific params
    input_data_hash = Column(String(64), nullable=True)  # SHA256 of input
    output_data_hash = Column(String(64), nullable=True)  # SHA256 of output
    execution_time_ms = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="completed")  # completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    signal = relationship("Signal", back_populates="operations")


class SignalCreate:
    """DTO for creating a signal."""

    def __init__(
        self,
        name: str,
        signal_type: str,
        sample_rate: int,
        duration: float,
        frequency: float | None = None,
        amplitude: float = 1.0,
        phase: float = 0.0,
        data: list[float] | None = None,
        metadata: dict | None = None,
    ):
        self.name = name
        self.signal_type = signal_type
        self.sample_rate = sample_rate
        self.duration = duration
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase
        self.data = data or []
        self.metadata = metadata or {}


class SignalResponse:
    """DTO for signal response."""

    def __init__(self, signal: Signal):
        self.id = signal.id
        self.name = signal.name
        self.signal_type = signal.signal_type
        self.sample_rate = signal.sample_rate
        self.duration = signal.duration
        self.frequency = signal.frequency
        self.amplitude = signal.amplitude
        self.phase = signal.phase
        self.data = signal.data
        self.metadata = signal.metadata
        self.created_at = signal.created_at
        self.updated_at = signal.updated_at


class SignalOperationResponse:
    """DTO for signal operation response."""

    def __init__(self, operation: SignalOperation):
        self.id = operation.id
        self.signal_id = operation.signal_id
        self.operation_type = operation.operation_type
        self.parameters = operation.parameters
        self.input_data_hash = operation.input_data_hash
        self.output_data_hash = operation.output_data_hash
        self.execution_time_ms = operation.execution_time_ms
        self.status = operation.status
        self.error_message = operation.error_message
        self.created_at = operation.created_at
