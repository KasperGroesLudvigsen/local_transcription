FROM nvcr.io/nvidia/pytorch:25.05-py3

ENV TORCH_CUDA_ARCH_LIST="12.0 12.1"

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Base image already provides: torch, transformers, fastapi, uvicorn, soundfile, accelerate
RUN pip install --no-cache-dir \
    python-multipart \
    aiofiles \
    soundfile

COPY app/ /app/app/

ENV MODEL_ID="syvai/hviske-v3-conversation" \
    GPU_CONCURRENCY=1 \
    MAX_FILE_SIZE_MB=500 \
    CHUNK_LENGTH_S=30 \
    BATCH_SIZE=16 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
