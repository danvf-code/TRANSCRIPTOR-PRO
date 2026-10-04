"""API de Transcriptor Pro (FastAPI)."""
import os
import shutil
import tempfile
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from . import exporters, transcriber

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

STATIC = Path(__file__).parent / "static"
WORKDIR = Path(tempfile.gettempdir()) / "transcriptor-pro"
WORKDIR.mkdir(exist_ok=True)
MODELS = {"whisper-large-v3-turbo", "whisper-large-v3"}

app = FastAPI(title="Transcriptor Pro", version="1.1.0")
JOBS: dict[str, dict] = {}


def run_job(job_id: str, src: Path) -> None:
    job = JOBS[job_id]
    work = WORKDIR / job_id
    work.mkdir(exist_ok=True)
    try:
        transcriber.api_key()
        job["stage"] = "Preparando audio"
        parts = transcriber.prepare(src, work)
        offset = 0.0
        for i, part in enumerate(parts, 1):
            job["stage"] = f"Transcribiendo ({i}/{len(parts)})"
            res = transcriber.transcribe_part(part, job["model"], job["lang_req"])
            for s in res.get("segments", []):
                text = s["text"].strip()
                if text:
                    job["segments"].append(
                        {"start": round(offset + s["start"], 2), "end": round(offset + s["end"], 2), "text": text}
                    )
            offset += float(res.get("duration") or 0)
            job.update(
                duration=round(offset, 2),
                language=job["lang_req"] or res.get("language"),
                progress=min(99, round(i / len(parts) * 100, 1)),
            )
        job.update(status="done", progress=100, stage="Completado")
    except Exception as exc:  # noqa: BLE001
        job.update(status="error", error=str(exc))
    finally:
        src.unlink(missing_ok=True)
        shutil.rmtree(work, ignore_errors=True)


@app.post("/api/transcribe")
def create_job(
    file: UploadFile = File(...),
    model: str = Form("whisper-large-v3-turbo"),
    language: str = Form(""),
):
    if model not in MODELS:
        raise HTTPException(400, "Modelo no válido.")
    job_id = uuid.uuid4().hex[:12]
    src = WORKDIR / f"{job_id}{Path(file.filename or 'media').suffix}"
    with src.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    JOBS[job_id] = dict(
        status="processing", stage="En cola", progress=0, error=None, segments=[],
        filename=file.filename, model=model, lang_req=language, language=None, duration=0,
    )
    threading.Thread(target=run_job, args=(job_id, src), daemon=True).start()
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str, since: int = 0):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Trabajo no encontrado.")
    out = {k: job[k] for k in ("status", "stage", "progress", "error", "language", "duration")}
    out["segments"] = job["segments"][since:]
    return out


@app.get("/api/jobs/{job_id}/export")
def export(job_id: str, format: str = "txt", timestamps: bool = True):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Trabajo no encontrado.")
    seg = job["segments"]
    builders = {
        "txt": lambda: exporters.to_txt(seg, timestamps),
        "srt": lambda: exporters.to_srt(seg),
        "vtt": lambda: exporters.to_vtt(seg),
        "json": lambda: exporters.to_json(job),
    }
    if format not in builders:
        raise HTTPException(400, "Formato no válido.")
    name = Path(job["filename"] or "transcripcion").stem
    return PlainTextResponse(
        builders[format](),
        headers={"Content-Disposition": f'attachment; filename="{name}.{format}"'},
    )


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
