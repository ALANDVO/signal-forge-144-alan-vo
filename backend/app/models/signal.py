"""Signal domain models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Signal(Base):
    """Signal entity for persistent storage."""

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    signal_type = Column(String(50), nullable=False)
    sample_rate = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)
    frequency = Column(Float, nullable=True)
    amplitude = Column(Float, default=1.0)
    phase = Column(Float, default=0.0)
    data = Column(JSON, nullable=False)
    signal_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    operations = relationship("SignalOperation", back_populates="signal", cascade="all, delete-orphan")


class SignalOperation(Base):
    """Audit log for signal processing operations."""

    __tablename__ = "signal_operations"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True)
    operation_type = Column(String(50), nullable=False)
    parameters = Column(JSON, nullable=True)
    input_data_hash = Column(String(64), nullable=True)
    output_data_hash = Column(String(64), nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="completed")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    signal = relationship("Signal", back_populates="operations")


class SignalCreate(BaseModel):
    """DTO for creating a signal."""

    name: str
    signal_type: str
    sample_rate: int
    duration: float
    frequency: Optional[float] = None
    amplitude: float = 1.0
    phase: float = 0.0
    data: Optional[list[float]] = None
    metadata: Optional[dict] = None


class SignalResponse(BaseModel):
    """DTO for signal response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    signal_type: str
    sample_rate: int
    duration: float
    frequency: Optional[float] = None
    amplitude: float
    phase: float
    data: list[float]
    metadata: Optional[dict] = Field(default=None, validation_alias="signal_metadata")
    created_at: datetime
    updated_at: datetime


class SignalOperationResponse(BaseModel):
    """DTO for signal operation response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    signal_id: int
    operation_type: str
    parameters: Optional[dict] = None
    input_data_hash: Optional[str] = None
    output_data_hash: Optional[str] = None
    execution_time_ms: Optional[float] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
