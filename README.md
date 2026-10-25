# Animations: Creative Studio Stack

Free frameworks and libraries for programmatic video, motion graphics, audio and automated editing.

## Setup

```bash
sudo scripts/install-system.sh          # ffmpeg, ImageMagick, GStreamer, Blender, Synfig, OpenToonz
npm install && npm run setup:browsers   # Remotion, Three.js, Framer Motion, Lottie, Playwright
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt         # core Python tools
pip install -r requirements-ml.txt      # optional: GPU / ML stack
pip install -r requirements-orchestration.txt   # optional: Ray, Prefect
pip install -r requirements-3d.txt      # optional: bpy
scripts/setup-comfyui.sh                # optional: ComfyUI + LivePortrait (cloned to ./external)
cp .env.example .env                    # add API keys
```

Airflow: install with its constraints file, e.g.
`pip install "apache-airflow==2.10.*" --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.10.3/constraints-3.11.txt`

A GPU container is in `docker/` (`docker compose -f docker/docker-compose.yml build`).

## Scripts

Install the CLI with `pip install -e .`, then use `studio <command>` (or `python -m studio`).

| Command | What it does |
|---|---|
| `studio transcribe voice.wav words.json` | Whisper word-level timestamps |
| `studio captions words.json caps.ass` | Karaoke-style ASS captions (word sweep, grouped lines) |
| `studio beats track.mp3` | BPM and beat times (Librosa) |
| `studio montage track.mp3 out.mp4 a.mp4 b.mp4 --every 4 --captions caps.ass` | Cuts clips to the beat, muxes audio, burns captions; segments encode in parallel |
| `studio stems song.mp3 stems/` | Demucs vocal / music split (`--all` for 4 stems) |
| `studio tts "script" voice.mp3` | ElevenLabs text-to-speech |
| `studio mix voice.mp3 music.mp3 mix.wav` | Music sidechain-ducked under speech |
| `studio loudnorm in.wav out.wav` | Normalise to -14 LUFS |
| `studio comfy workflow_api.json out/ --set 6.text="a fox" --set 3.seed=42` | Patch and run a ComfyUI API workflow, download outputs |
| `studio capture http://localhost:3000 out.mp4 --duration 5 [--alpha]` | Frame-exact Playwright capture; page must expose `window.seek(t)` |

Other entry points:
- `npm run remotion:studio` / `npm run remotion:render`: React kinetic-caption composition (`remotion/src`). Pass a Whisper `words` array as props, e.g. `--props=words.json` (wrap as `{"words": [...]}`).
- `blender -b -P scripts/blender_scene.py -- --out renders/scene_ --frames 120 --engine CYCLES`: headless procedural scene with animated camera.

Typical short-form pipeline:
```bash
studio tts "$(cat script.txt)" voice.mp3
studio loudnorm voice.mp3 voice_n.wav
studio mix voice_n.wav music.mp3 audio.wav
studio transcribe voice_n.wav words.json && studio captions words.json caps.ass
studio montage audio.wav final.mp4 clips/*.mp4 --captions caps.ass
```

Tests: `python -m unittest discover tests` (the e2e test needs ffmpeg + librosa and skips otherwise).

**Verification status:** captions and cut planning are unit-tested, and the beat-montage path (ffmpeg, Librosa, ASS burn-in) passes an end-to-end run on synthetic media. Whisper, Demucs, ElevenLabs, ComfyUI, Playwright capture, Blender and Remotion code was written to each tool's documented API but has **not** been run in this environment (no GPU, keys or installs).

## Catalog

Install key: **npm** = `package.json`, **pip** = a `requirements*.txt`, **sys** = `scripts/install-system.sh`, **api** = key in `.env`, **manual** = not automated.

### 1. Video animation and motion graphics
| Tool | Install |
|---|---|
| Remotion | npm |
| Three.js | npm |
| Framer Motion | npm |
| Lottie-Web | npm |
| Blender Python API | sys (blender) / pip `requirements-3d.txt` (bpy) |
| Synfig Studio | sys |
| OpenToonz | sys (Flatpak) |
| Manim | pip |
| HyperFrames | manual, see note below |
| Videowright | manual, see note below |

### 2. Audio
| Tool | Install |
|---|---|
| Whisper | pip (local) |
| Demucs | pip `requirements-ml.txt` |
| Librosa | pip |
| Pydub | pip |
| FFmpeg audio filters | sys |
| Web Audio API | built into browsers, no install |
| ElevenLabs API | pip + api |
| Openverse API | api (`OPENVERSE_*`) |
| Suno / Udio API | api (`SUNO_API_KEY`; Udio has no official public API) |
| Clack | manual, see note below |

### 3. Augmentation and automated editing
| Tool | Install |
|---|---|
| Playwright | npm |
| OpenCV | pip |
| Rembg | pip |
| ImageMagick | sys |
| FFmpeg filter_complex | sys |
| LivePortrait | `scripts/setup-comfyui.sh` |
| GIPHY API | api |
| EbSynth | manual (closed-source desktop app) |
| OpenFilm / Open Video Edit | manual, see note below |
| CapCut Schema Builder | manual, see note below |

### 4. Production layer
| Tool | Install |
|---|---|
| ComfyUI | `scripts/setup-comfyui.sh` |
| Ray | pip `requirements-orchestration.txt` |
| GStreamer | sys |
| MediaPipe | pip |
| Taichi | pip |
| PyTorch Geometric | pip `requirements-ml.txt` |
| MoviePy | pip |
| Docker GPU containers | `docker/` |
| Hugging Face Diffusers | pip `requirements-ml.txt` |
| Airflow / Prefect | pip `requirements-orchestration.txt` (Airflow needs constraints) |

## Notes on items I could not install automatically

I could not match these names to a verified, installable open-source project, so they are not wired in. Please send repo URLs if you have them:

- **HyperFrames, Videowright, Clack, OpenFilm / Open Video Edit, CapCut Schema Builder**
- **Suno / Udio**: neither has an official public API, so the `.env` key assumes a third-party wrapper.
- **Free vs. paid**: ElevenLabs, Suno, GIPHY (rate-limited) and Openverse (registration) need accounts or keys. Whisper local, Demucs and the rest run offline.
- **Licenses**: EbSynth and Blender-adjacent tools have their own terms; check before commercial use.
