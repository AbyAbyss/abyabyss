"""
manim_kit: battle-tested helpers for narrated math explainer videos in manimgl (3b1b/manim).

Copy this file next to your scene file, then:

    from manim_kit import *          # also re-exports everything from manimlib

    class MyScene(KitScene):
        def construct(self):
            self.say("Narration starts now.")    # voice plays while the next animations run
            self.play(Write(Tex(R"x^2")))
            self.wait_voice()                     # hold until the sentence is finished

Every helper here exists because the plain manimgl approach broke in practice;
the comments say what went wrong.
"""
import hashlib
import os
import textwrap
from pathlib import Path

from manimlib import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
# Convention in math, CAD and most 3D software: x = red, y = green, z = blue
X_COL, Y_COL, Z_COL = RED_C, GREEN_C, BLUE_C
ANS_COL = YELLOW
# manimgl's Text() default font isn't installed on most Linux boxes and falls back to an ugly
# wide monospace that overflows the frame. Inter (fonts-inter) is clean and widely available.
FONT = os.environ.get("MANIM_FONT", "Inter")

# Render with `-r 1080x1920` for Shorts/Reels: manimgl then uses a 4.5 x 8 frame (9:16).
# Apps cover roughly the top 15% and bottom 20% of a vertical video with buttons and text,
# so in portrait the kit keeps headings and captions inside the middle of the screen.
PORTRAIT = FRAME_WIDTH < FRAME_HEIGHT


def T(text, **kwargs):
    """Text with a sane default font. Use T(...) everywhere instead of Text(...)."""
    kwargs.setdefault("font", FONT)
    return Text(text, **kwargs)


def tex(source, color=None, **kwargs):
    """Tex that actually honours color: manimgl 1.7 silently ignores Tex(..., color=...)."""
    mob = Tex(source, **kwargs)
    if color is not None:
        mob.set_color(color)
    return mob


def color_symbols(mob, mapping=None):
    """Color every occurrence of the given symbols in a Tex, e.g. {"x": RED}. Defaults to x/y/z."""
    mob.set_color_by_tex_to_color_map(mapping or {"x": X_COL, "y": Y_COL, "z": Z_COL})
    return mob


def caption(text, size=None, color=WHITE):
    """Subtitle-style line pinned to the bottom of the screen (stays put while the 3D camera moves).
    In portrait it wraps onto up to three lines and sits above the apps' bottom UI."""
    if PORTRAIT:
        text = "\n".join(textwrap.wrap(text, 26))
        size = size or 30
    cap = T(text, font_size=size or 34, color=color)
    cap.set_backstroke(BLACK, 6)
    cap.set_max_width(FRAME_WIDTH - (0.5 if PORTRAIT else 0.8))   # shrink rather than run off-screen
    cap.to_edge(DOWN, buff=1.7 if PORTRAIT else 0.45)
    cap.fix_in_frame()
    return cap


def heading(text, size=44):
    if PORTRAIT:
        text = "\n".join(textwrap.wrap(text, 18))
    head = T(text, font_size=size, weight=BOLD)
    head.set_backstroke(BLACK, 6)
    head.set_max_width(FRAME_WIDTH - (0.5 if PORTRAIT else 0.8))
    head.to_edge(UP, buff=1.2 if PORTRAIT else 0.35)
    head.fix_in_frame()
    return head


def fit(mob, margin=0.4):
    """Shrink a mobject (never enlarge) so it fits the frame width. Vital in portrait, where the frame is 4.5 wide."""
    return mob.set_max_width(FRAME_WIDTH - 2 * margin)


def formula_block(lines, size=42, corner=UL, shift=0.3 * DOWN, buff=0.22):
    """A stack of left-aligned Tex lines pinned to a screen corner (use for worked steps in 3D scenes).
    In portrait it sits centred under the heading instead. Returns (group, background_box).
    Write the lines one by one: self.play(Write(group[i]))."""
    group = VGroup(*(Tex(l, font_size=size) if isinstance(l, str) else l for l in lines))
    group.arrange(DOWN, aligned_edge=LEFT, buff=buff)
    if PORTRAIT:
        fit(group)
        group.to_edge(UP, buff=2.3)
    else:
        group.to_corner(corner).shift(shift)
    group.fix_in_frame()
    box = BackgroundRectangle(group, buff=0.2, fill_opacity=0.85).fix_in_frame()
    return group, box


def question_card(number, lines, size=36):
    if PORTRAIT:  # re-wrap for the narrow frame
        lines = textwrap.wrap(" ".join(lines), 24)
    tag = T(f"Question {number}", font_size=44, weight=BOLD, color=ANS_COL)
    body = VGroup(*(T(l, font_size=size) for l in lines)).arrange(DOWN, buff=0.25)
    hint = T("Pause the video and try it!", font_size=28, color=GREY_B, slant=ITALIC)
    return fit(VGroup(tag, body, hint).arrange(DOWN, buff=0.6))


def make_axes(x_range=(0, 5, 1), y_range=(0, 5, 1), z_range=(0, 4, 1),
              width=None, height=None, depth=None, numbers=True):
    """Colored ThreeDAxes. For x/y tick numbers in 3D prefer KitScene.axis_numbers3d (camera-facing)."""
    axes = ThreeDAxes(
        x_range=x_range, y_range=y_range, z_range=z_range,
        width=width, height=height, depth=depth,
        axis_config=dict(include_tip=True, tick_size=0.06),
    )
    axes.x_axis.set_color(X_COL)
    axes.y_axis.set_color(Y_COL)
    axes.z_axis.set_color(Z_COL)
    if numbers:
        axes.x_axis.add_numbers(font_size=20, excluding=[0])
        axes.y_axis.add_numbers(font_size=20, excluding=[0])
    return axes


def ball(point, color=ANS_COL, radius=0.1):
    """A point marker that looks right from every 3D angle (a flat Dot vanishes edge-on)."""
    return Sphere(radius=radius, color=color).move_to(point)


def always_on_top(*mobs):
    """Markers inside/behind translucent surfaces get hidden by the depth test. Draw them on top."""
    for m in mobs:
        m.deactivate_depth_test()
    return mobs


# ---------------------------------------------------------------------------
# Narration (Kokoro offline text-to-speech)
# ---------------------------------------------------------------------------
VOICE = os.environ.get("VOICE", "af_heart")          # also good: am_michael, bf_emma, bm_george
VOICE_SPEED = float(os.environ.get("VOICE_SPEED", "1.0"))
KOKORO_DIR = Path(os.environ.get("KOKORO_DIR", Path.home() / ".cache" / "kokoro"))
VOICE_CACHE = Path(os.environ.get("VOICE_CACHE", Path.cwd() / "voice_cache"))
NO_VOICE = bool(os.environ.get("NO_VOICE"))          # silent mode: timing estimated from word count

_kokoro = None


def synthesize(text, voice=None, speed=None):
    """Return (wav_path, seconds). Cached by (voice, speed, text): edits to visuals never re-synthesize."""
    import soundfile as sf
    global _kokoro
    voice, speed = voice or VOICE, speed or VOICE_SPEED
    VOICE_CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(f"{voice}|{speed}|{text}".encode()).hexdigest()[:16]
    path = VOICE_CACHE / f"{key}.wav"
    if not path.exists():
        if _kokoro is None:
            from kokoro_onnx import Kokoro
            _kokoro = Kokoro(str(KOKORO_DIR / "kokoro-v1.0.int8.onnx"), str(KOKORO_DIR / "voices-v1.0.bin"))
        samples, rate = _kokoro.create(text, voice=voice, speed=speed, lang="en-us")
        tmp = path.with_suffix(".tmp.wav")
        sf.write(tmp, samples, rate)
        tmp.replace(path)  # atomic: parallel renders never read a half-written file
    return path, sf.info(path).duration


class KitScene(Scene):
    voice_gap = 0.3  # pause after each sentence

    # -- narration --------------------------------------------------------
    def say(self, text):
        """Start speaking now; animations played next overlap with the voice. Returns duration."""
        if NO_VOICE:
            duration = 0.38 * len(text.split()) + 0.3   # ~160 words/min, for fast silent previews
        else:
            path, duration = synthesize(text)
            self.add_sound(str(path))
        self.voice_end = self.get_time() + duration
        return duration

    def wait_voice(self, extra=0.0):
        """Hold until the current sentence (plus a short gap) is done. Replaces hand-tuned wait(n)."""
        remaining = getattr(self, "voice_end", 0) - self.get_time() + self.voice_gap + extra
        if remaining > 0.05:
            self.wait(remaining)

    def tear_down(self):
        # manimgl leaves the audio shorter than the video when a scene ends on silence. Joining
        # such scenes with `ffmpeg -c copy` then drifts the voice later and later. Pad to full length.
        writer = self.file_writer
        if getattr(writer, "includes_sound", False):
            from pydub import AudioSegment
            gap = self.get_time() - writer.audio_segment.duration_seconds
            if gap > 0:
                writer.add_audio_segment(AudioSegment.silent(int(gap * 1000) + 1))
        super().tear_down()

    # -- camera -------------------------------------------------------------
    def frame_on(self, theta, phi, center, width, height=None):
        """Point the 3D camera at `center` so content about `width` units wide (and `height` tall)
        fits on screen in either orientation. Pass the visible extent of your axes or objects."""
        need = max(height or 0, width * FRAME_HEIGHT / FRAME_WIDTH) * 1.1
        self.frame.reorient(theta, phi, 0, center=center, height=need)
        if PORTRAIT:
            # Lift the content into the upper-middle so the bottom caption never covers it
            camera_up = self.frame.get_orientation().as_matrix()[:, 1]
            self.frame.shift(-0.14 * need * camera_up)

    # -- labels in 3D -----------------------------------------------------
    def label3d(self, source, point, size=32, offset=0.35 * UP, color=WHITE):
        """Tex pinned to a 3D point that keeps facing the camera, even while the camera moves.
        Plain Tex lies flat in the xy-plane and becomes unreadable once the view tilts.
        `offset` is in screen directions (UP/RIGHT...), not world directions."""
        mob = Tex(source, font_size=size).set_color(color)
        mob.set_backstroke(BLACK, 4)
        rot = self.frame.get_orientation().as_matrix()   # camera space -> world space
        mob.move_to(offset)
        mob.apply_matrix(rot, about_point=ORIGIN)
        mob.shift(point)
        mob.last_rot = rot

        def keep_facing(m):
            new = self.frame.get_orientation().as_matrix()
            if not np.allclose(new, m.last_rot):
                # rotate by the change only, so per-glyph colors set later survive
                m.apply_matrix(new @ m.last_rot.T, about_point=point)
                m.last_rot = new

        mob.add_updater(keep_facing)
        return mob

    def axis_labels3d(self, axes, size=44, names=("x", "y", "z")):
        """Camera-facing x/y/z labels just past each axis tip. Call AFTER setting the camera angle."""
        out = VGroup()
        for name, axis, col in zip(names, axes.axes, (X_COL, Y_COL, Z_COL)):
            tip = axis.get_end() + 0.45 * normalize(axis.get_vector())
            out.add(self.label3d(name, tip, size=size, offset=ORIGIN, color=col))
        return out

    def axis_numbers3d(self, axes, axis_index, values, size=24, offset=0.3 * LEFT):
        """Camera-facing tick numbers (axis.add_numbers() renders flat and rotated in 3D)."""
        out = VGroup()
        for v in values:
            coords = [0, 0, 0]
            coords[axis_index] = v
            out.add(self.label3d(str(v), axes.c2p(*coords), size=size, offset=offset))
        return out

    def path_legs(self, axes, p, dashed=True, width=5):
        """Dashed x-then-y-then-z path from the origin to p: the clearest way to show what (x, y, z) means."""
        x, y, z = p
        pts = [axes.c2p(0, 0, 0), axes.c2p(x, 0, 0), axes.c2p(x, y, 0), axes.c2p(x, y, z)]
        line = DashedLine if dashed else Line
        return VGroup(*(line(a, b, color=c, stroke_width=width)
                        for a, b, c in zip(pts, pts[1:], (X_COL, Y_COL, Z_COL))))
