"""studio <command>: one entry point for the whole pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="studio", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("transcribe", help="Whisper word timestamps -> JSON")
    p.add_argument("audio"); p.add_argument("out"); p.add_argument("--model", default="base"); p.add_argument("--language")

    p = sub.add_parser("captions", help="word JSON -> karaoke ASS")
    p.add_argument("words_json"); p.add_argument("out"); p.add_argument("--size", type=int, nargs=2, default=[1080, 1920])
    p.add_argument("--font", default="Arial"); p.add_argument("--max-words", type=int, default=4)

    p = sub.add_parser("beats", help="print BPM and beat times")
    p.add_argument("audio")

    p = sub.add_parser("montage", help="cut clips to the beat of an audio track")
    p.add_argument("audio"); p.add_argument("out"); p.add_argument("clips", nargs="+")
    p.add_argument("--every", type=int, default=4); p.add_argument("--size", type=int, nargs=2, default=[1080, 1920])
    p.add_argument("--fps", type=int, default=30); p.add_argument("--captions"); p.add_argument("--jobs", type=int, default=4)

    p = sub.add_parser("stems", help="Demucs stem separation")
    p.add_argument("audio"); p.add_argument("out_dir"); p.add_argument("--all", action="store_true", help="4 stems instead of vocals/no_vocals")

    p = sub.add_parser("tts", help="ElevenLabs text-to-speech")
    p.add_argument("text"); p.add_argument("out"); p.add_argument("--voice", default="21m00Tcm4TlvDq8ikWAM")

    p = sub.add_parser("mix", help="duck music under voice")
    p.add_argument("voice"); p.add_argument("music"); p.add_argument("out"); p.add_argument("--music-db", type=float, default=-6.0)

    p = sub.add_parser("loudnorm", help="normalise loudness")
    p.add_argument("src"); p.add_argument("dst"); p.add_argument("--lufs", type=float, default=-14.0)

    p = sub.add_parser("comfy", help="run a ComfyUI API workflow")
    p.add_argument("workflow"); p.add_argument("out_dir"); p.add_argument("--set", action="append", default=[], metavar="NODE.input=value")

    p = sub.add_parser("capture", help="Playwright deterministic frame capture -> video")
    p.add_argument("url"); p.add_argument("out"); p.add_argument("--duration", type=float, required=True)
    p.add_argument("--fps", type=int, default=30); p.add_argument("--size", type=int, nargs=2, default=[1920, 1080])
    p.add_argument("--alpha", action="store_true")

    a = ap.parse_args(argv)

    if a.cmd == "transcribe":
        from .audio import transcribe
        print(f"{len(transcribe(a.audio, a.out, a.model, a.language)['words'])} words -> {a.out}")
    elif a.cmd == "captions":
        from .captions import build_ass, load_words
        Path(a.out).write_text(build_ass(load_words(a.words_json), a.size[0], a.size[1], font=a.font, max_words=a.max_words))
        print(f"captions -> {a.out}")
    elif a.cmd == "beats":
        from .beats import detect_beats
        bpm, beats = detect_beats(a.audio)
        print(json.dumps({"bpm": round(bpm, 1), "beats": [round(b, 3) for b in beats]}))
    elif a.cmd == "montage":
        from .video import beat_montage
        segs = beat_montage(a.clips, a.audio, a.out, a.every, tuple(a.size), a.fps, a.captions, a.jobs)
        print(f"{len(segs)} cuts -> {a.out}")
    elif a.cmd == "stems":
        from .audio import separate_stems
        print(separate_stems(a.audio, a.out_dir, None if a.all else "vocals"))
    elif a.cmd == "tts":
        from .audio import synthesize_speech
        print(synthesize_speech(a.text, a.out, a.voice))
    elif a.cmd == "mix":
        from .ffmpeg import duck_music
        duck_music(a.voice, a.music, a.out, a.music_db)
    elif a.cmd == "loudnorm":
        from .ffmpeg import normalize_loudness
        normalize_loudness(a.src, a.dst, a.lufs)
    elif a.cmd == "comfy":
        from .comfyui import run_workflow
        for f in run_workflow(a.workflow, a.out_dir, a.set):
            print(f)
    elif a.cmd == "capture":
        import tempfile
        from .capture import capture_frames, encode_frames
        with tempfile.TemporaryDirectory() as tmp:
            capture_frames(a.url, tmp, a.duration, a.fps, tuple(a.size), a.alpha)
            encode_frames(tmp, a.out, a.fps, a.alpha)
        print(f"-> {a.out}")


if __name__ == "__main__":
    main()
