#!/usr/bin/env bash
# Render every scene of xyz_axes.py with manimgl and join them into one video.
#   ./render.sh          1080p (default)
#   ./render.sh -l       quick 480p preview
set -euo pipefail
cd "$(dirname "$0")"

QUALITY="${1:---hd}"
SCENES=(Intro OneDimension TwoDimensions ThreeDimensions QuestionDrone QuestionHill QuestionWifi Outro)

# manimgl needs an OpenGL context; on a headless machine run it inside a virtual display
RUN=(manimgl)
if [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null; then
  RUN=(xvfb-run -a -s "-screen 0 1920x1080x24" manimgl)
fi

: > videos_list.txt
for scene in "${SCENES[@]}"; do
  echo "Rendering $scene ..."
  "${RUN[@]}" xyz_axes.py "$scene" -w "$QUALITY" > /dev/null
  echo "file 'videos/$scene.mp4'" >> videos_list.txt
done

ffmpeg -v error -y -f concat -safe 0 -i videos_list.txt -c copy xyz_in_the_real_world.mp4
rm videos_list.txt
echo "Done: $(pwd)/xyz_in_the_real_world.mp4"
