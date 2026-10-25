"""Deterministic frame capture of any web animation with Playwright.

Contract: the page must expose `window.seek(timeSeconds)` that renders that exact
moment (synchronously, or returning a Promise). Three.js, canvas, GSAP and Lottie
timelines all fit this. Frames are then encoded with ffmpeg.
"""
from __future__ import annotations

from pathlib import Path

from .ffmpeg import run


def capture_frames(url: str, out_dir: str, duration: float, fps: int = 30,
                   size: tuple[int, int] = (1920, 1080), transparent: bool = False) -> int:
    from playwright.sync_api import sync_playwright  # lazy

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    n = int(round(duration * fps))
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": size[0], "height": size[1]})
        page.goto(url)
        page.wait_for_function("typeof window.seek === 'function'", timeout=30000)
        for i in range(n):
            page.evaluate("t => window.seek(t)", i / fps)
            page.screenshot(path=str(out / f"frame_{i:06d}.png"), omit_background=transparent)
        browser.close()
    return n


def encode_frames(frames_dir: str, out: str, fps: int = 30, alpha: bool = False) -> None:
    pattern = str(Path(frames_dir) / "frame_%06d.png")
    if alpha:  # ProRes 4444 keeps transparency for compositing
        run(["ffmpeg", "-y", "-framerate", str(fps), "-i", pattern, "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", out])
    else:
        run(["ffmpeg", "-y", "-framerate", str(fps), "-i", pattern, "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out])
