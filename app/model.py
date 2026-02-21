import asyncio
import logging
from typing import Optional

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from .config import (
    MODEL_ID, HF_TOKEN, GPU_CONCURRENCY,
    CHUNK_LENGTH_S, BATCH_SIZE,
)

logger = logging.getLogger(__name__)

_pipe = None
_device: str = "cpu"
_semaphore: Optional[asyncio.Semaphore] = None


def load_model() -> None:
    global _pipe, _device, _semaphore

    _device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    logger.info("Loading model %s on %s (dtype=%s)", MODEL_ID, _device, torch_dtype)

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        MODEL_ID,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True,
        token=HF_TOKEN,
    )
    model.to(_device)

    processor = AutoProcessor.from_pretrained(MODEL_ID, token=HF_TOKEN)

    _pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        chunk_length_s=CHUNK_LENGTH_S,
        batch_size=BATCH_SIZE,
        torch_dtype=torch_dtype,
        device=_device,
    )

    _semaphore = asyncio.Semaphore(GPU_CONCURRENCY)
    logger.info("Model loaded successfully on %s", _device)


def is_loaded() -> bool:
    return _pipe is not None


def get_device() -> str:
    return _device


def get_vram_info() -> tuple[Optional[float], Optional[float]]:
    if not torch.cuda.is_available():
        return None, None
    used = torch.cuda.memory_allocated(0) / 1024**3
    total = torch.cuda.get_device_properties(0).total_memory / 1024**3
    return round(used, 2), round(total, 2)


def _run_transcribe(audio: dict, generate_kwargs: dict, return_timestamps: bool) -> dict:
    return _pipe(audio, generate_kwargs=generate_kwargs, return_timestamps=return_timestamps)


def _run_detect_language(samples, sample_rate: int) -> tuple[str, float]:
    """Use the model's detect_language method to identify language and probability."""
    model = _pipe.model
    feature_extractor = _pipe.feature_extractor
    tokenizer = _pipe.tokenizer

    max_samples = 30 * sample_rate
    input_features = feature_extractor(
        samples[:max_samples],
        sampling_rate=sample_rate,
        return_tensors="pt",
    ).input_features.to(_device).to(model.dtype)

    with torch.no_grad():
        lang_tokens, lang_probs = model.detect_language(input_features)

    # lang_tokens: list of strings like ["<|da|>"]
    # lang_probs: tensor of shape (batch_size,) with the top language probability
    lang_str = lang_tokens[0].strip("<|>") if lang_tokens else "unknown"

    if hasattr(lang_probs, "item"):
        prob = round(float(lang_probs.item()), 4)
    elif hasattr(lang_probs, "__getitem__"):
        prob = round(float(lang_probs[0]), 4)
    else:
        prob = 1.0

    return lang_str, prob


async def transcribe(
    samples,
    sample_rate: int,
    language: str = "da",
    task: str = "transcribe",
    return_timestamps: bool = True,
) -> dict:
    audio = {"array": samples, "sampling_rate": sample_rate}
    generate_kwargs = {
        "language": language,
        "task": task,
        "max_new_tokens": 448,
    }

    async with _semaphore:
        result = await asyncio.to_thread(
            _run_transcribe,
            audio,
            generate_kwargs,
            return_timestamps,
        )

    return result


async def detect_language(samples, sample_rate: int) -> tuple[str, float]:
    async with _semaphore:
        lang, prob = await asyncio.to_thread(_run_detect_language, samples, sample_rate)
    return lang, prob
