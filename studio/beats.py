"""Beat detection and cut planning."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Segment:
    clip: int           # index into the clip list
    src_start: float    # in-point inside the source clip
    duration: float
    timeline_start: float


def detect_beats(audio_path: str) -> tuple[float, list[float]]:
    """Return (bpm, beat times in seconds) using librosa."""
    import librosa  # lazy: heavy import

    y, sr = librosa.load(audio_path, sr=None, mono=True)
    tempo, frames = librosa.beat.beat_track(y=y, sr=sr, units="frames")
    times = librosa.frames_to_time(frames, sr=sr)
    return float(getattr(tempo, "item", lambda: tempo)()), [float(t) for t in times]


def cut_points(beats: list[float], total: float, every: int = 4, min_len: float = 0.4) -> list[float]:
    """Pick a cut every `every` beats, always starting at 0 and ending at `total`."""
    pts = [0.0]
    for t in beats[::every]:
        if t - pts[-1] >= min_len and total - t >= min_len:
            pts.append(float(t))
    pts.append(total)
    return pts


def plan_cuts(points: list[float], clip_durations: list[float]) -> list[Segment]:
    """Round-robin clips over the cut points, advancing each clip's in-point so
    footage is not repeated until the clip is exhausted (then it wraps)."""
    if not clip_durations:
        raise ValueError("need at least one clip")
    cursors = [0.0] * len(clip_durations)
    segs: list[Segment] = []
    for i, (a, b) in enumerate(zip(points, points[1:])):
        c = i % len(clip_durations)
        dur = b - a
        # Slot longer than the remaining footage: restart from the top (the
        # renderer loops the input, so the segment length always matches the beat).
        if cursors[c] + dur > clip_durations[c]:
            cursors[c] = 0.0
        segs.append(Segment(c, round(cursors[c], 3), round(dur, 3), round(a, 3)))
        cursors[c] = (cursors[c] + dur) % clip_durations[c]
    return segs
