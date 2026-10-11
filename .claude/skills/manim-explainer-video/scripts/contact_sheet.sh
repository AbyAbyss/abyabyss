#!/usr/bin/env bash
# Tile evenly spaced frames of a video into one PNG so you can inspect a whole scene in a single image.
# This is how you catch overflowing captions, labels hidden behind surfaces, off-frame objects
# and overlapping text without watching the video.
#   contact_sheet.sh video.mp4 [out.png] [cols] [rows] [skip_seconds]
set -euo pipefail
IN="$1"; OUT="${2:-${IN%.mp4}_sheet.png}"; C="${3:-3}"; R="${4:-3}"; SKIP="${5:-0}"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
N=$((C * R))
ffmpeg -v error -y -ss "$SKIP" -i "$IN" \
  -vf "fps=$N/($D-$SKIP),scale=640:-1,tile=${C}x${R}" -frames:v 1 "$OUT"
echo "$OUT"
