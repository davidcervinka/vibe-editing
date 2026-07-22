#!/usr/bin/env bash
# Extract a segment from a source and normalize it to a uniform spec so segments concat cleanly.
# Usage: ./extract_normalize.sh SOURCE START DURATION OUT.mp4
set -euo pipefail

SRC="$1"; START="$2"; DUR="$3"; OUT="$4"
W="${W:-1920}"; H="${H:-1080}"; FPS="${FPS:-30}"

# scale to fit, pad to exact WxH (white), force 30fps + square pixels, reset timestamps
NORM="scale=${W}:${H}:force_original_aspect_ratio=decrease,\
pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:color=white,\
fps=${FPS},setsar=1,setpts=PTS-STARTPTS"

ffmpeg -v error -y -ss "$START" -t "$DUR" -i "$SRC" \
  -vf "$NORM" -an -r "$FPS" -pix_fmt yuv420p -c:v libx264 -crf 18 "$OUT"

echo "wrote $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
