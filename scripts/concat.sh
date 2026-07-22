#!/usr/bin/env bash
# Lossless concat of pre-normalized segments (all must share codec/res/fps).
# Usage: ./concat.sh OUT.mp4 seg1.mp4 seg2.mp4 seg3.mp4 ...
set -euo pipefail

OUT="$1"; shift
LIST="$(mktemp).txt"
for f in "$@"; do printf "file '%s'\n" "$(cd "$(dirname "$f")"; pwd)/$(basename "$f")" >> "$LIST"; done

ffmpeg -v error -y -f concat -safe 0 -i "$LIST" -c copy "$OUT"
rm -f "$LIST"
echo "wrote $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
