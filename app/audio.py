import asyncio
import subprocess
import tempfile
import os
from pathlib import Path


async def decode_audio(input_bytes: bytes, filename: str) -> tuple[any, int]:
    """Decode any audio format to 16kHz mono float32 array using ffmpeg."""
    suffix = Path(filename).suffix or ".audio"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
        tmp_in.write(input_bytes)
        tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path + ".wav"
    try:
        await asyncio.to_thread(_run_ffmpeg, tmp_in_path, tmp_out_path)
        samples, sample_rate = await asyncio.to_thread(_load_wav, tmp_out_path)
        return samples, sample_rate
    finally:
        os.unlink(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)


def _run_ffmpeg(input_path: str, output_path: str) -> None:
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            output_path,
        ],
        capture_output=True,
        check=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.decode()}")


def _load_wav(path: str) -> tuple:
    import soundfile as sf
    samples, sample_rate = sf.read(path, dtype="float32")
    return samples, sample_rate
