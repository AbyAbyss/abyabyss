#!/usr/bin/env bash
# Render every scene of xyz_axes.py with manimgl (in parallel) and join them into one video.
#   ./render.sh          1080p (default)
#   ./render.sh -l       quick 480p preview
#   JOBS=2 ./render.sh   limit parallel renders (default: number of CPUs)
set -euo pipefail
cd "$(dirname "$0")"

QUALITY="${1:---hd}"
JOBS="${JOBS:-$(nproc)}"
SCENES=(Intro OneDimension TwoDimensions ThreeDimensions QuestionDrone QuestionHill QuestionWifi Outro)
OUT=xyz_in_the_real_world.mp4

# manimgl needs an OpenGL context. On a headless machine, start one virtual display
# and share it between all parallel renders (xvfb-run -a per process races for display numbers).
if [ -z "${DISPLAY:-}" ]; then
  Xvfb :99 -screen 0 1920x1080x24 >/dev/null 2>&1 &
  XVFB_PID=$!
  trap 'kill $XVFB_PID 2>/dev/null || true' EXIT
  export DISPLAY=:99
  sleep 1
fi

mkdir -p logs
printf '%s\n' "${SCENES[@]}" | xargs -P "$JOBS" -I{} sh -c \
  'echo "Rendering {} ..."; manimgl xyz_axes.py {} -w '"$QUALITY"' > logs/{}.log 2>&1 || { echo "FAILED {} (see logs/{}.log)"; exit 255; }'

: > videos_list.txt
for scene in "${SCENES[@]}"; do
  echo "file 'videos/$scene.mp4'" >> videos_list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i videos_list.txt -c copy "$OUT"
rm videos_list.txt
echo "Done: $(pwd)/$OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
