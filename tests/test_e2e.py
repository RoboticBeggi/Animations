"""Real ffmpeg + librosa run on synthetic media. Skipped if deps are missing."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

try:
    import librosa  # noqa: F401
    HAVE = shutil.which("ffmpeg") is not None
except ImportError:
    HAVE = False


@unittest.skipUnless(HAVE, "needs ffmpeg and librosa")
class Montage(unittest.TestCase):
    def test_montage_matches_audio_length(self):
        from studio.captions import Word, build_ass
        from studio.ffmpeg import probe_duration
        from studio.video import beat_montage

        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            for n, src in (("a", "testsrc2"), ("b", "smptebars")):
                subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"{src}=size=640x360:rate=25:duration=3",
                                "-pix_fmt", "yuv420p", str(t / f"{n}.mp4")], check=True, capture_output=True)
            # 120 BPM click track, 8 s
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                            "aevalsrc='0.9*sin(2*PI*1000*t)*lt(mod(t,0.5),0.03)':s=44100:d=8",
                            str(t / "beat.wav")], check=True, capture_output=True)
            (t / "c.ass").write_text(build_ass([Word("hello", 0.5, 1.0), Word("world", 1.1, 1.8)], 540, 960))
            out = t / "out.mp4"
            segs = beat_montage([str(t / "a.mp4"), str(t / "b.mp4")], str(t / "beat.wav"), str(out),
                                every=4, size=(540, 960), fps=25, captions_ass=str(t / "c.ass"), jobs=2)
            self.assertGreaterEqual(len(segs), 3)
            self.assertAlmostEqual(probe_duration(out), 8.0, delta=0.3)


if __name__ == "__main__":
    unittest.main()
