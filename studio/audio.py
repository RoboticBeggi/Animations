"""Transcription (Whisper), stem separation (Demucs), TTS (ElevenLabs)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path


def transcribe(audio: str, out_json: str, model: str = "base", language: str | None = None) -> dict:
    """Word-level timestamps via openai-whisper. Output: {"text", "words":[{word,start,end}]}."""
    import whisper  # lazy

    result = whisper.load_model(model).transcribe(audio, word_timestamps=True, language=language)
    words = [
        {"word": w["word"].strip(), "start": float(w["start"]), "end": float(w["end"])}
        for seg in result["segments"] for w in seg.get("words", [])
    ]
    payload = {"text": result["text"].strip(), "language": result.get("language"), "words": words}
    Path(out_json).write_text(json.dumps(payload, indent=2))
    return payload


def separate_stems(audio: str, out_dir: str, two_stems: str | None = "vocals", model: str = "htdemucs") -> Path:
    """Run Demucs. With two_stems='vocals' you get vocals.wav + no_vocals.wav."""
    cmd = [sys.executable, "-m", "demucs", "-n", model, "-o", out_dir]
    if two_stems:
        cmd += ["--two-stems", two_stems]
    subprocess.run(cmd + [audio], check=True)
    return Path(out_dir) / model / Path(audio).stem


def synthesize_speech(text: str, out_path: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM",
                      model_id: str = "eleven_multilingual_v2") -> str:
    """ElevenLabs REST text-to-speech (needs ELEVENLABS_API_KEY)."""
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps({"text": text, "model_id": model_id}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
    )
    with urllib.request.urlopen(req) as r, open(out_path, "wb") as f:
        f.write(r.read())
    return out_path
