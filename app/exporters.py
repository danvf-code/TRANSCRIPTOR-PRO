"""Exportadores de transcripciones: TXT, SRT, VTT y JSON."""
import json


def stamp(seconds: float, sep: str = ",") -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def to_txt(segments, timestamps=True) -> str:
    if not timestamps:
        return " ".join(s["text"] for s in segments)
    return "\n".join(f"[{stamp(s['start'], '.')[:8]}] {s['text']}" for s in segments)


def to_srt(segments) -> str:
    return "\n".join(
        f"{i}\n{stamp(s['start'])} --> {stamp(s['end'])}\n{s['text']}\n"
        for i, s in enumerate(segments, 1)
    )


def to_vtt(segments) -> str:
    body = "\n".join(
        f"{stamp(s['start'], '.')} --> {stamp(s['end'], '.')}\n{s['text']}\n" for s in segments
    )
    return "WEBVTT\n\n" + body


def to_json(job) -> str:
    keys = ("filename", "language", "duration", "model", "segments")
    return json.dumps({k: job[k] for k in keys}, ensure_ascii=False, indent=2)
