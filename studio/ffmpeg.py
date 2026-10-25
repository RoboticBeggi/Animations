"""Thin, dependency-free ffmpeg helpers."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f"{' '.join(cmd[:3])}... failed:\n{proc.stderr[-2000:]}")


def probe_duration(path: str | Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def normalize_loudness(src: str, dst: str, target_lufs: float = -14.0, true_peak: float = -1.0) -> None:
    """Single-pass EBU R128 loudness normalisation (-14 LUFS = streaming standard)."""
    run(["ffmpeg", "-y", "-i", src, "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA=11", dst])


def duck_music(voice: str, music: str, dst: str, music_gain_db: float = -6.0) -> None:
    """Mix music under voice; music is sidechain-compressed whenever the voice speaks."""
    graph = (
        f"[1:a]volume={music_gain_db}dB[m];[0:a]asplit=2[v][sc];"
        "[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[d];"
        "[v][d]amix=inputs=2:duration=longest:normalize=0[out]"
    )
    run(["ffmpeg", "-y", "-i", voice, "-i", music, "-filter_complex", graph, "-map", "[out]", dst])


def crossfade_audio(a: str, b: str, dst: str, seconds: float = 2.0) -> None:
    run(["ffmpeg", "-y", "-i", a, "-i", b, "-filter_complex", f"acrossfade=d={seconds}", dst])
