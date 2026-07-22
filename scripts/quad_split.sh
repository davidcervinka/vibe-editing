#!/usr/bin/env bash
# 2x2 split-screen ("quad") of four clips with thin white gridlines.
# Usage: ./quad_split.sh DURATION OUT.mp4  TL TL_START  TR TR_START  BL BL_START  BR BR_START
# Each cell plays DURATION seconds starting at its own START offset.
set -euo pipefail

D="$1"; OUT="$2"
TL="$3"; TLS="$4"; TR="$5"; TRS="$6"; BL="$7"; BLS="$8"; BR="$9"; BRS="${10}"

ffmpeg -v error -y \
  -ss "$TLS" -t "$D" -i "$TL" \
  -ss "$TRS" -t "$D" -i "$TR" \
  -ss "$BLS" -t "$D" -i "$BL" \
  -ss "$BRS" -t "$D" -i "$BR" \
  -filter_complex "\
[0:v]scale=960:540,fps=30,setsar=1,setpts=PTS-STARTPTS[a];\
[1:v]scale=960:540,fps=30,setsar=1,setpts=PTS-STARTPTS[b];\
[2:v]scale=960:540,fps=30,setsar=1,setpts=PTS-STARTPTS[c];\
[3:v]scale=960:540,fps=30,setsar=1,setpts=PTS-STARTPTS[d];\
[a][b][c][d]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[g];\
[g]drawbox=x=956:y=0:w=8:h=1080:color=white:t=fill,\
   drawbox=x=0:y=536:w=1920:h=8:color=white:t=fill[out]" \
  -map "[out]" -t "$D" -r 30 -pix_fmt yuv420p -c:v libx264 -crf 18 -an "$OUT"

echo "wrote $OUT"
