import os

MODEL_ID = os.getenv("MODEL_ID", "syvai/hviske-v3-conversation")
HF_TOKEN = os.getenv("HF_TOKEN", None)
GPU_CONCURRENCY = int(os.getenv("GPU_CONCURRENCY", "1"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
CHUNK_LENGTH_S = int(os.getenv("CHUNK_LENGTH_S", "30"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "16"))
PORT = int(os.getenv("PORT", "8000"))
