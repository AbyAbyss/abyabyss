# x, y, z in the real world (manim video)

A short explainer video made with [3Blue1Brown's manim](https://github.com/3b1b/manim) (the `manimgl` package). It shows what the x, y and z axes mean in everyday situations, then works through three practice questions.

Finished video: [`xyz_in_the_real_world.mp4`](xyz_in_the_real_world.mp4) (1080p, 30 fps, 2 min 52 s, 5.8 MB)

## What's in it

| Scene | What it shows |
| --- | --- |
| `Intro` | x, y, z as three questions: left/right, forward/back, up/down |
| `OneDimension` | A car on a straight road only needs x |
| `TwoDimensions` | A city map: coffee shop at (4, 3), distance √(x² + y²) = 5 blocks |
| `ThreeDimensions` | A drone at (4, 3, 2), distance √(x² + y² + z²) ≈ 5.39 m, then the camera swings around in 3D |
| `QuestionDrone` | Q1: drone flies from A(1, 2, 0) to B(4, 6, 12). Answer: 13 m |
| `QuestionHill` | Q2: hill height z = 4 − (x² + y²)/4, hiker at (2, 2). Answer: z = 2 (200 m) |
| `QuestionWifi` | Q3: router range 5 m, phone at (3, 4, 1). 9 + 16 + 1 = 26 > 25, so just out of range |
| `Outro` | Real uses (GPS, 3D printers, games, CAD, physics) and the four formulas |

Each question shows a "pause and try it" card before the answer is animated.

## Rendering it yourself

```bash
# System libraries (Debian/Ubuntu): Pango/Cairo for text, LaTeX for formulas, ffmpeg for video
sudo apt-get install libpango1.0-dev libcairo2-dev pkg-config ffmpeg \
  texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra \
  texlive-science dvisvgm cm-super

pip install manimgl
pip install audioop-lts   # only on Python 3.13+, where the audioop module was removed

./render.sh       # 1080p, writes xyz_in_the_real_world.mp4
./render.sh -l    # fast 480p preview
```

To work on a single scene, render just that one, for example `manimgl xyz_axes.py QuestionHill -w -l`. Drop `-w` to open an interactive window instead of writing a file.

On a machine without a display (a server or CI), `render.sh` runs manimgl inside `xvfb-run` automatically, since manimgl renders with OpenGL.

## Things I hit while building it

- `manimgl` 1.7.2 ignores `Tex(..., color=...)` on multi-character formulas, so the code calls `.set_color()` after creating them.
- Labels in 3D are re-rotated every frame (`XYZScene.label3d`) so they always face the camera, even while it moves.
- Markers that sit inside or behind a translucent surface (the hiker on the hill, the phone outside the Wi-Fi sphere) use `deactivate_depth_test()` so they stay visible.
