"""Word timestamps -> karaoke-style ASS subtitles (burn with ffmpeg)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Word:
    text: str
    start: float
    end: float


def load_words(path: str | Path) -> list[Word]:
    data = json.loads(Path(path).read_text())
    return [Word(w["word"].strip(), float(w["start"]), float(w["end"])) for w in data["words"]]


def group_lines(words: list[Word], max_words: int = 4, max_chars: int = 24, max_gap: float = 0.6) -> list[list[Word]]:
    """Split words into on-screen lines by count, width and silence gaps."""
    lines: list[list[Word]] = []
    cur: list[Word] = []
    for w in words:
        if cur:
            too_long = len(" ".join(x.text for x in cur + [w])) > max_chars
            gap = w.start - cur[-1].end
            if len(cur) >= max_words or too_long or gap > max_gap:
                lines.append(cur)
                cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def ass_time(t: float) -> str:
    cs = max(0, round(t * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _line_text(line: list[Word]) -> str:
    parts, cursor = [], line[0].start
    for w in line:
        if w.start - cursor > 0.01:
            parts.append(f"{{\\k{round((w.start - cursor) * 100)}}}")
            cursor = w.start
        parts.append(f"{{\\kf{max(1, round((w.end - cursor) * 100))}}}{w.text} ")
        cursor = w.end
    return "".join(parts).rstrip()


def build_ass(words: list[Word], width: int = 1080, height: int = 1920, font: str = "Arial",
              font_size: int | None = None, highlight: str = "&H0000F0FF", base: str = "&H00FFFFFF",
              margin_v: int | None = None, upper: bool = True, **group_kw) -> str:
    """highlight/base are ASS &HAABBGGRR colours. Spoken words sweep base -> highlight."""
    font_size = font_size or round(height * 0.055)
    margin_v = margin_v if margin_v is not None else round(height * 0.18)
    if upper:
        words = [Word(w.text.upper(), w.start, w.end) for w in words]
    head = (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {width}\nPlayResY: {height}\nWrapStyle: 2\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding\n"
        f"Style: Default,{font},{font_size},{highlight},{base},&H00000000,&H80000000,"
        f"-1,0,0,0,100,100,0,0,1,{max(2, font_size // 14)},2,2,40,40,{margin_v},1\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    )
    events = [
        f"Dialogue: 0,{ass_time(l[0].start)},{ass_time(l[-1].end + 0.15)},Default,,0,0,0,,{_line_text(l)}"
        for l in group_lines(words, **group_kw)
    ]
    return head + "\n".join(events) + "\n"
