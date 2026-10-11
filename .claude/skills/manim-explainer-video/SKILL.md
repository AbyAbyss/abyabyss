---
name: manim-explainer-video
description: Make narrated animated explainer videos (3Blue1Brown style) with manimgl, the 3b1b/manim Python library, for math, physics, technology, geography, history, finance or any topic that can be shown with diagrams, maps, charts, formulas and 3D shapes. Includes offline AI voiceover, worked examples, practice questions, and YouTube (16:9) or Shorts/Reels (9:16) output as a single MP4. Use this whenever someone wants an animated or whiteboard-style explainer video, a YouTube or Instagram educational video made from a script, mentions manim / manimgl / 3blue1brown, or asks to add narration to a manim video, even if they don't name the library.
---

# Narrated explainer videos with manimgl

Works for any topic you can draw: math, science, tech, maps, timelines, money. It is the wrong
tool for live action, realistic people or character cartoons.

This skill packages what it took to ship a real 5-minute narrated 3D explainer, so the next
video skips the hours lost to installs, manimgl quirks and layout bugs. The workflow is:
**setup → script → scenes → preview + inspect → final render**.

Bundled files (paths relative to this skill's folder):
- `scripts/setup.sh`: installs and smoke-tests everything (idempotent, about 5 min the first time).
- `assets/manim_kit.py`: helpers and narration. Copy it next to your scene file.
- `assets/example_scenes.py`: working 2D, 3D and practice-question scenes (16:9) to copy from.
- `assets/example_short.py`: the same ideas laid out for a vertical Short (9:16).
- `scripts/render.sh`: renders scenes in parallel and joins them into one MP4.
- `scripts/contact_sheet.sh`: tiles frames of a video into one PNG for visual QA.

## 1. Setup (run first, in the background while you script)

```bash
bash <skill>/scripts/setup.sh          # NO_VOICE=1 to skip the TTS model
```

It installs system libraries, LaTeX (including `dsfont.sty`, which manimgl's template needs),
`manimgl`, the Python 3.13 `audioop` backport that pydub needs, and the Kokoro voice model
(about 120 MB from GitHub releases). It ends with a headless render test. If the model download
fails, the network probably blocks GitHub release assets; ask the user, or render silently with `NO_VOICE=1`.

Start it with `run_in_background` and write the script while it runs.

## 2. Write the narration script before any code

Plan scenes as a list of **beats**: one spoken sentence plus what appears on screen during it.
The narration sets the pacing, so the timing comes for free later. Good structure for a lesson:
hook → simplest case → build up one idea per scene → 2 to 3 worked questions → real-world uses → recap.

Write narration for the ear, not the eye. TTS reads symbols badly:
- "the square root of twenty-nine", not "√29"; "four, three, two", not "(4,3,2)"
- "x squared plus y squared", not "x^2+y^2"; spell out units ("metres")
- Short sentences. One idea each.

Pick numbers that come out clean (3-4-5, 2-3-6 → 7, 1-2-2 → 3, 3-4-12 → 13). Viewers can follow
integer answers, and a mistake is obvious when one appears. Check every answer before animating it.

## 3. Build scenes from the kit

```bash
cp <skill>/assets/manim_kit.py <skill>/assets/example_scenes.py <project>/
```

Use one `KitScene` subclass per scene (each 20 to 60 s). Separate scenes render in parallel, and
a fix only re-renders one of them. The core pattern:

```python
self.say("Sentence the viewer hears.")   # starts the voice now
self.play(...)                            # animations run during the sentence
self.wait_voice()                         # hold until it finishes; never hand-tune wait(n)
```

Kit helpers and the problem each one solves (all observed in practice):

| Use | Instead of | Why |
| --- | --- | --- |
| `T("...")` | `Text("...")` | The default font is missing on Linux, and the wide monospace fallback overflows the frame |
| `tex(src, color=C)` or `.set_color(C)` | `Tex(src, color=C)` | manimgl 1.7 silently drops `color=` on multi-glyph Tex |
| `caption()`, `heading()` | raw text | Shrink to fit the frame and stay fixed while the 3D camera moves |
| `self.label3d()`, `self.axis_labels3d()`, `self.axis_numbers3d()` | `axes.add_axis_labels()`, `add_numbers()` | Plain labels lie flat on the floor and are unreadable once the camera tilts. These face the camera every frame |
| `ball(p)` | `Dot(p)` in 3D | A flat dot disappears when seen edge-on |
| `always_on_top(m, ...)` | nothing | Markers inside or behind translucent surfaces (a point on a hill, a phone near a sphere) get hidden by the depth test |
| `formula_block(lines, corner=...)` | free-floating Tex | Keeps worked steps pinned to a screen corner in 3D |
| `KitScene.tear_down` (automatic) | nothing | Pads each scene's audio to its video length. Otherwise joined scenes drift out of sync |

3D rules of thumb:
- Set `self.frame.reorient(theta, phi, 0, center=<middle of content>, height=6.5 to 9)` **before**
  creating camera-facing labels. Too large a `height` leaves the content tiny. Center on the content, not the origin.
- Put formula blocks in the corner opposite the busy part of the 3D view, and keep axis labels away from that corner.
- Unicode emoji don't render (no emoji font). Use words or simple shapes.
- manimgl doesn't add the script's folder to `sys.path`. Keep the `sys.path.insert` line from the example.

## Shorts and Reels (9:16)

Render with `RES=1080x1920` (see step 5). manimgl then uses a frame 4.5 units wide and 8 tall,
and the kit switches to portrait: headings and captions wrap and move into the safe zone, question
cards re-wrap, and `formula_block` centres under the heading.

What the kit can't do is re-flow a scene designed for 16:9. Axes 6 units wide or side-by-side
layouts get clipped. Write Shorts as their own scenes, starting from `example_short.py`:
- Stack vertically: heading, visual, formula or number, caption. Size diagrams to `FRAME_WIDTH - 0.9`.
- Wrap anything that might be wide in `fit(mob)`.
- In 3D, use `self.frame_on(theta, phi, center=..., width=<content width>)` instead of
  `reorient`. It fits the content to the narrow frame and lifts it above the caption.
- Hook in the first 3 seconds, one idea, 30 to 60 s total, font size 40 or more.

## 4. Preview fast, inspect visually, fix, repeat

```bash
NO_VOICE=1 bash <skill>/scripts/render.sh scenes.py "SceneA SceneB" -l   # seconds, silent, estimated timing
bash <skill>/scripts/contact_sheet.sh videos/SceneA.mp4                  # then Read the PNG
```

Look at **every** scene's contact sheet before the final render. That's how you catch overflowing
captions, labels colliding with formulas, content off-frame after a camera move, or hidden markers.
You can't watch the video, so these images are your eyes. Use `skip_seconds` (5th arg) to zoom in
on a moment. Re-render only the scenes you changed.

Do the first voiced preview (`-l` without `NO_VOICE`) once the visuals are settled. It synthesizes
all narration once at about 1.4× real time on CPU, and later renders reuse `voice_cache/`.

Checks worth automating before you call it done:
```bash
for v in videos/*.mp4; do ffprobe -v error -show_entries stream=codec_type,duration -of csv=p=0 $v; done  # audio == video per scene
ffmpeg -i final.mp4 -af volumedetect -vn -f null - 2>&1 | grep mean_volume   # about -20 to -26 dB means speech is present
```

## 5. Final render and delivery

```bash
bash <skill>/scripts/render.sh scenes.py "Intro A B C Outro" --hd final.mp4
RES=1080x1920 bash <skill>/scripts/render.sh short.py "Hook Point" --hd short.mp4   # vertical
```

Measured on 4 CPUs, rendering in parallel: a 5 min 34 s narrated video took **19 min at `--hd`**
(1080p30, about 3.5× the video length) and **9 min at `-l`** (480p, including first-time voice
synthesis). Scenes with large translucent surfaces (spheres, hills) are the slowest, at around
3 frames per second. Iterate at `-l`, use `-m` (720p) when a mid-quality check is needed, and
render `--hd` once, in the background, while you do other work. Commit the source, the kit and the MP4. Ignore `videos/`,
`voice_cache/` and `logs/`.

## Timing from the reference project

| Step | First time | With this skill |
| --- | --- | --- |
| Environment setup | ~25 min of trial and error | ~5 min unattended |
| Fixing layout and quirk bugs | 4 full re-render cycles | mostly avoided by the kit |
| Final 1080p render | 14 min for a 2:52 silent video, one scene at a time | 19 min for a 5:34 narrated video, scenes in parallel |

The render itself is CPU-bound and can't drop to zero. Most of the savings come from not hitting
the same bugs twice and from QA with contact sheets instead of full renders.

## Voices

Kokoro voices: `af_heart` (default, warm US female), `am_michael` (US male), `bf_emma` and
`bm_george` (UK). Set `VOICE=am_michael`, and `VOICE_SPEED=0.95` for a slower pace. Changing
voice or speed re-synthesizes, because the cache key includes both.
