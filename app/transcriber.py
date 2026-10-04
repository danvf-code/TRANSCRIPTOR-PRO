"""Preparación del audio (ffmpeg, opcional) y transcripción con Whisper vía API de Groq."""
import os
import shutil
import subprocess
from pathlib import Path

import httpx

API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MAX_BYTES = 24 * 1024 * 1024  # límite del plan gratuito: 25 MB por archivo
CHUNK_SECONDS = 900


def api_key() -> str:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or key.startswith("pega_"):
        raise RuntimeError("Falta la clave GROQ_API_KEY. Crea el archivo .env (ver .env.example).")
    return key


def prepare(src: Path, workdir: Path) -> list[Path]:
    """Devuelve archivos listos para enviar: audio mono comprimido y troceado cada 15 min."""
    if shutil.which("ffmpeg"):
        pattern = workdir / "parte_%03d.mp3"
        cmd = [
            "ffmpeg", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "32k",
            "-f", "segment", "-segment_time", str(CHUNK_SECONDS), "-reset_timestamps", "1", str(pattern),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            parts = sorted(workdir.glob("parte_*.mp3"))
            if parts:
                return parts
        except subprocess.CalledProcessError:
            raise RuntimeError("No se pudo leer el archivo. Verifica que sea audio o video válido.")
        except OSError:
            pass  # ffmpeg bloqueado o inaccesible: se intenta enviar el archivo tal cual
    if src.stat().st_size > MAX_BYTES:
        raise RuntimeError("El archivo supera 24 MB y ffmpeg no está disponible para comprimirlo.")
    return [src]


def transcribe_part(path: Path, model: str, language: str | None) -> dict:
    data = {"model": model, "response_format": "verbose_json", "timestamp_granularities[]": "segment"}
    if language:
        data["language"] = language
    with path.open("rb") as fh:
        resp = httpx.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key()}"},
            data=data,
            files={"file": (path.name, fh)},
            timeout=600,
        )
    if resp.status_code != 200:
        try:
            msg = resp.json()["error"]["message"]
        except Exception:  # noqa: BLE001
            msg = resp.text[:200]
        raise RuntimeError(f"Error de la API ({resp.status_code}): {msg}")
    return resp.json()
