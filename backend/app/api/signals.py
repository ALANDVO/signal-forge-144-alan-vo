"""Signal processing API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_session
from app.models.signal import SignalCreate, SignalResponse, SignalOperationResponse
from app.services.signal_service import SignalService

router = APIRouter(prefix="/signals", tags=["signals"])


def get_signal_service(session: AsyncSession = Depends(get_session)) -> SignalService:
    return SignalService(session)


@router.post("", response_model=SignalResponse, status_code=201)
async def create_signal(
    signal: SignalCreate,
    service: SignalService = Depends(get_signal_service),
):
    """Create a new signal (generate or custom)."""
    try:
        return await service.generate_signal(signal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[SignalResponse])
async def list_signals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SignalService = Depends(get_signal_service),
):
    """List all signals with pagination."""
    return await service.list_signals(skip=skip, limit=limit)


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal(
    signal_id: int,
    service: SignalService = Depends(get_signal_service),
):
    """Get a signal by ID."""
    signal = await service.get_signal(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal


@router.post("/{signal_id}/fft", response_model=SignalResponse)
async def compute_fft(
    signal_id: int,
    service: SignalService = Depends(get_signal_service),
):
    """Compute FFT of a signal."""
    try:
        return await service.compute_fft(signal_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{signal_id}/filter", response_model=SignalResponse)
async def apply_filter(
    signal_id: int,
    filter_type: str = Query(..., pattern="^(lowpass|highpass|bandpass)$"),
    cutoff_freq: float = Query(..., gt=0),
    order: int = Query(4, ge=1, le=10),
    service: SignalService = Depends(get_signal_service),
):
    """Apply a digital filter to a signal."""
    try:
        return await service.apply_filter(signal_id, filter_type, cutoff_freq, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{signal_id}/convolve", response_model=SignalResponse)
async def convolve_signals(
    signal_id: int,
    kernel_id: int,
    service: SignalService = Depends(get_signal_service),
):
    """Convolve two signals."""
    try:
        return await service.convolve(signal_id, kernel_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{signal_id}/operations", response_model=list[SignalOperationResponse])
async def get_signal_operations(
    signal_id: int,
    service: SignalService = Depends(get_signal_service),
):
    """Get operation history for a signal."""
    return await service.get_operations(signal_id)
