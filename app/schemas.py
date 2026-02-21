from typing import List, Optional, Tuple
from pydantic import BaseModel


class Chunk(BaseModel):
    text: str
    timestamp: Tuple[float, Optional[float]]


class TranscribeResponse(BaseModel):
    text: str
    chunks: Optional[List[Chunk]] = None
    language: str
    duration_s: float
    model: str
    device: str


class DetectLanguageResponse(BaseModel):
    language: str
    language_probability: float
    model: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str
    vram_used_gb: Optional[float] = None
    vram_total_gb: Optional[float] = None
