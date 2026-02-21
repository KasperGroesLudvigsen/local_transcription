import asyncio
import logging
import time
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from . import model as model_module
from .audio import decode_audio
from .config import MAX_FILE_SIZE_MB, MODEL_ID
from .schemas import (
    Chunk,
    DetectLanguageResponse,
    HealthResponse,
    TranscribeResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading model at startup...")
    await asyncio.to_thread(model_module.load_model)
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Local Transcription API",
    description="Speech-to-text via Hviske v3 (syvai/hviske-v3-conversation)",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health():
    vram_used, vram_total = model_module.get_vram_info()
    return HealthResponse(
        status="ok",
        model_loaded=model_module.is_loaded(),
        device=model_module.get_device(),
        vram_used_gb=vram_used,
        vram_total_gb=vram_total,
    )


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    language: str = Form("da"),
    task: str = Form("transcribe"),
    return_timestamps: bool = Form(True),
):
    if not model_module.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_FILE_SIZE_MB}MB)",
        )

    try:
        samples, sample_rate = await decode_audio(contents, file.filename or "audio")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Audio decode failed: {e}")

    duration_s = len(samples) / sample_rate
    t0 = time.monotonic()

    try:
        result = await model_module.transcribe(
            samples,
            sample_rate,
            language=language,
            task=task,
            return_timestamps=return_timestamps,
        )
    except Exception as e:
        logger.exception("Inference error")
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

    logger.info(
        "Transcribed %.1fs audio in %.1fs", duration_s, time.monotonic() - t0
    )

    chunks = None
    if return_timestamps and "chunks" in result:
        chunks = [
            Chunk(
                text=c["text"],
                timestamp=(
                    c["timestamp"][0] if c["timestamp"][0] is not None else 0.0,
                    c["timestamp"][1],
                ),
            )
            for c in result["chunks"]
        ]

    return TranscribeResponse(
        text=result["text"],
        chunks=chunks,
        language=language,
        duration_s=round(duration_s, 2),
        model=MODEL_ID,
        device=model_module.get_device(),
    )


@app.post("/detect-language", response_model=DetectLanguageResponse)
async def detect_language(file: UploadFile = File(...)):
    if not model_module.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_FILE_SIZE_MB}MB)",
        )

    try:
        samples, sample_rate = await decode_audio(contents, file.filename or "audio")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Audio decode failed: {e}")

    try:
        lang, prob = await model_module.detect_language(samples, sample_rate)
    except Exception as e:
        logger.exception("Language detection error")
        raise HTTPException(status_code=500, detail=f"Language detection failed: {e}")

    return DetectLanguageResponse(
        language=lang,
        language_probability=prob,
        model=MODEL_ID,
    )
