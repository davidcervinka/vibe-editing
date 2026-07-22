#!/usr/bin/env bash
# Apply a color grade (ASC-CDL mental model) to a clip. Grade PER-SEGMENT during extraction,
# never post-concat (post-concat re-encodes twice). See TECHNIQUES.md §4.
#   ./grade.sh IN.mp4 OUT.mp4 [preset|raw-ffmpeg-filter]
set -euo pipefail

IN="$1"; OUT="$2"; PRESET="${3:-subtle}"

case "$PRESET" in
  none)          VF="" ;;
  subtle)        VF="eq=contrast=1.03:saturation=0.98" ;;
  neutral_punch) VF="eq=contrast=1.06:saturation=1.0,curves=master='0/0 0.25/0.23 0.75/0.77 1/1'" ;;
  warm_cinematic)VF="eq=contrast=1.12:brightness=-0.02:saturation=0.88,\
colorbalance=rs=0.02:bs=-0.03:rm=0.04:bm=-0.02:rh=0.08:bh=-0.05,\
curves=master='0/0 0.25/0.22 0.75/0.78 1/1'" ;;
  *)             VF="$PRESET" ;;   # treat anything else as a raw ffmpeg filter chain
esac

if [ -z "$VF" ]; then
  ffmpeg -v error -y -i "$IN" -c copy "$OUT"
else
  ffmpeg -v error -y -i "$IN" -vf "$VF" -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a copy "$OUT"
fi
echo "graded ($PRESET) -> $OUT"
