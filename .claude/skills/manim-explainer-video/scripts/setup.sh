#!/usr/bin/env bash
# One-shot, idempotent setup for rendering narrated manimgl videos on Debian/Ubuntu.
# Safe to re-run: every step checks before installing. Takes ~5 min the first time (mostly LaTeX).
#   bash setup.sh            full setup (manim + LaTeX + voice)
#   NO_VOICE=1 bash setup.sh skip the text-to-speech model
set -uo pipefail

SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
ok()   { echo "  [ok] $*"; }
step() { echo "==> $*"; }

step "System packages (Pango/Cairo for text, LaTeX for formulas, ffmpeg, Xvfb for headless OpenGL)"
PKGS=(libpango1.0-dev libcairo2-dev pkg-config python3-dev ffmpeg xvfb
      libgl1-mesa-dri libegl1
      texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra
      texlive-science dvisvgm cm-super fonts-inter)
MISSING=()
for p in "${PKGS[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || MISSING+=("$p"); done
if [ ${#MISSING[@]} -gt 0 ]; then
  $SUDO apt-get update -qq
  # fonts-inter may not exist on older distros; install the rest regardless
  $SUDO apt-get install -y -qq "${MISSING[@]}" >/dev/null 2>&1 || \
    $SUDO apt-get install -y -qq $(printf '%s\n' "${MISSING[@]}" | grep -v fonts-inter) >/dev/null
fi
# manimgl's default LaTeX template needs dsfont.sty (texlive-fonts-extra). Without it every Tex() fails.
kpsewhich dsfont.sty >/dev/null && ok "LaTeX + dsfont" || echo "  [!!] dsfont.sty missing: install texlive-fonts-extra"

step "Python packages"
PIP="pip install -q"
python3 -c "import manimlib" 2>/dev/null || $PIP manimgl
# Python 3.13 removed audioop; pydub (used by manimgl for sound) needs the backport.
python3 -c "import audioop" 2>/dev/null || $PIP audioop-lts
python3 -c "import setuptools" 2>/dev/null || $PIP setuptools
ok "manimgl $(python3 -c 'import importlib.metadata as m; print(m.version("manimgl"))')"

if [ -z "${NO_VOICE:-}" ]; then
  step "Kokoro text-to-speech (offline, ~120 MB, hosted on GitHub releases)"
  python3 -c "import kokoro_onnx, soundfile" 2>/dev/null || $PIP kokoro-onnx soundfile
  KDIR="${KOKORO_DIR:-$HOME/.cache/kokoro}"; mkdir -p "$KDIR"
  BASE=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
  for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do
    [ -s "$KDIR/$f" ] || curl -sSL --fail -o "$KDIR/$f" "$BASE/$f" || echo "  [!!] could not download $f (network policy?)"
  done
  [ -s "$KDIR/voices-v1.0.bin" ] && ok "voice model in $KDIR"
fi

step "Smoke test: render one frame headless"
TMP=$(mktemp -d)
cat > "$TMP/smoke.py" <<'EOF'
from manimlib import *
class Smoke(Scene):
    def construct(self):
        self.add(Tex(R"\sqrt{x^2 + y^2}"), Text("ok").shift(DOWN))
EOF
RUN="manimgl"; [ -z "${DISPLAY:-}" ] && RUN="xvfb-run -a -s '-screen 0 1280x720x24' manimgl"
# -w matters: without it manimgl opens an interactive window and waits forever, even under Xvfb
if (cd "$TMP" && timeout 180 bash -c "$RUN smoke.py Smoke -w -s -l" >"$TMP/log" 2>&1); then
  ok "manimgl renders (Tex + Text + OpenGL)"
else
  echo "  [!!] smoke test failed:"; tail -5 "$TMP/log"
fi
rm -rf "$TMP"
echo "Setup finished."
