"""
Offline narration for manimgl scenes, using the Kokoro text-to-speech model.

    class MyScene(VoiceoverMixin, Scene):
        def construct(self):
            self.say("A car on a straight road only needs one number.")
            self.play(...)          # animations run while the voice plays
            self.wait_voice()       # hold until the sentence is finished

Each sentence is synthesized once and cached as a .wav keyed on (text, voice, speed),
so re-rendering after a visual tweak costs nothing extra.

Model files (about 120 MB) are looked up in $KOKORO_DIR, default ~/.cache/kokoro:
    kokoro-v1.0.int8.onnx, voices-v1.0.bin
from https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
"""
import hashlib
import os
from pathlib import Path

import soundfile as sf
from pydub import AudioSegment

VOICE = os.environ.get("VOICE", "af_heart")
SPEED = float(os.environ.get("VOICE_SPEED", "1.0"))
MODEL_DIR = Path(os.environ.get("KOKORO_DIR", Path.home() / ".cache" / "kokoro"))
CACHE_DIR = Path(__file__).resolve().parent / "voice_cache"

_kokoro = None


def _model():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(str(MODEL_DIR / "kokoro-v1.0.int8.onnx"), str(MODEL_DIR / "voices-v1.0.bin"))
    return _kokoro


def synthesize(text: str, voice: str = VOICE, speed: float = SPEED) -> tuple[Path, float]:
    """Return (wav path, duration in seconds) for one narration line, using the cache when possible."""
    CACHE_DIR.mkdir(exist_ok=True)
    key = hashlib.sha1(f"{voice}|{speed}|{text}".encode()).hexdigest()[:16]
    path = CACHE_DIR / f"{key}.wav"
    if not path.exists():
        samples, rate = _model().create(text, voice=voice, speed=speed, lang="en-us")
        tmp = path.with_suffix(".tmp.wav")
        sf.write(tmp, samples, rate)
        tmp.replace(path)  # atomic, so parallel renders never read a half-written file
    return path, sf.info(path).duration


class VoiceoverMixin:
    voice_gap = 0.3  # breathing room after each sentence

    def say(self, text: str):
        """Start speaking now. Animations played afterwards overlap with the voice."""
        path, duration = synthesize(text)
        self.add_sound(str(path))
        self.voice_end = self.get_time() + duration
        return duration

    def wait_voice(self, extra: float = 0.0):
        """Wait until the current sentence (plus a short gap) has finished."""
        remaining = getattr(self, "voice_end", 0) - self.get_time() + self.voice_gap + extra
        if remaining > 0.05:
            self.wait(remaining)

    def tear_down(self):
        # manimgl leaves the audio track shorter than the video when the scene ends on silence.
        # Pad it, otherwise joining scenes with `ffmpeg -c copy` drifts the voice out of sync.
        writer = self.file_writer
        if getattr(writer, "includes_sound", False):
            gap = self.get_time() - writer.audio_segment.duration_seconds
            if gap > 0:
                writer.add_audio_segment(AudioSegment.silent(int(gap * 1000) + 1))
        super().tear_down()
