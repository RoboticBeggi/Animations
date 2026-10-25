"""Beat-synced montage rendering with ffmpeg (parallel per-segment encode)."""
from __future__ import annotations

import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .beats import Segment, cut_points, detect_beats, plan_cuts
from .ffmpeg import probe_duration, run


def _render_segment(seg: Segment, clip: str, out: Path, w: int, h: int, fps: int) -> None:
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
          f"fps={fps},setsar=1,format=yuv420p")
    run(["ffmpeg", "-y", "-stream_loop", "-1", "-ss", str(seg.src_start), "-t", str(seg.duration),
         "-i", clip, "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)])


def beat_montage(clips: list[str], audio: str, out: str, every: int = 4, size: tuple[int, int] = (1080, 1920),
                 fps: int = 30, captions_ass: str | None = None, jobs: int = 4) -> list[Segment]:
    """Cut `clips` to the beat of `audio`, mux the audio, optionally burn ASS captions."""
    total = probe_duration(audio)
    _, beats = detect_beats(audio)
    segs = plan_cuts(cut_points(beats, total, every), [probe_duration(c) for c in clips])
    w, h = size
    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = Path(tmp)
        parts = [tmp_p / f"seg{i:04d}.mp4" for i in range(len(segs))]
        with ThreadPoolExecutor(jobs) as ex:
            list(ex.map(lambda a: _render_segment(a[0], clips[a[0].clip], a[1], w, h, fps), zip(segs, parts)))
        listing = tmp_p / "list.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in parts))
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-i", audio]
        if captions_ass:
            cmd += ["-vf", f"ass={captions_ass}", "-c:v", "libx264", "-preset", "medium", "-crf", "18"]
        else:
            cmd += ["-c:v", "copy"]
        run(cmd + ["-c:a", "aac", "-b:a", "192k", "-map", "0:v", "-map", "1:a", "-shortest", out])
    return segs
