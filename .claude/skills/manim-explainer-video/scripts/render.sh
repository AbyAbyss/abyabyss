#!/usr/bin/env bash
# Render scenes of a manimgl file in parallel and join them, in order, into one MP4.
#   render.sh scenes.py "Intro Part1 Part2 Outro" [quality] [output.mp4]
#   quality: -l (480p15, fast preview) | -m (720p30) | --hd (1080p30, default) | --uhd
#   JOBS=2 render.sh ...   limit parallel renders (default: number of CPUs)
set -euo pipefail

FILE="$1"; SCENES=($2); QUALITY="${3:---hd}"
OUT="${4:-$(basename "${FILE%.py}").mp4}"
JOBS="${JOBS:-$(nproc)}"
cd "$(dirname "$FILE")"; FILE="$(basename "$FILE")"

# manimgl renders with OpenGL and needs a display. Headless: start ONE Xvfb and share it;
# separate `xvfb-run -a` per process races for display numbers when run in parallel.
if [ -z "${DISPLAY:-}" ]; then
  Xvfb :97 -screen 0 1920x1080x24 >/dev/null 2>&1 &
  XVFB_PID=$!; trap 'kill $XVFB_PID 2>/dev/null || true' EXIT
  export DISPLAY=:97; sleep 1
fi

mkdir -p logs
START=$(date +%s)
printf '%s\n' "${SCENES[@]}" | xargs -P "$JOBS" -I{} sh -c \
  'manimgl "'"$FILE"'" {} -w '"$QUALITY"' > logs/{}.log 2>&1 && echo "  done {}" || { echo "  FAILED {} (tail logs/{}.log)"; exit 255; }'

LIST=$(mktemp)
for s in "${SCENES[@]}"; do echo "file '$PWD/videos/$s.mp4'" >> "$LIST"; done
ffmpeg -v error -y -f concat -safe 0 -i "$LIST" -c copy "$OUT"
rm "$LIST"
echo "Wrote $PWD/$OUT: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s of video in $(( $(date +%s) - START ))s"
