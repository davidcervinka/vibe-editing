#!/usr/bin/env bash
# Mux a music bed onto a (silent) video: trim/pad to length, fade in/out, master with loudnorm.
# Optionally duck under a voiceover via sidechaincompress.
#
#   ./blur_and_mux.sh VIDEO.mp4 MUSIC.(mp3|wav) OUT.mp4 [VO.mp3]
set -euo pipefail

VIDEO="$1"; MUSIC="$2"; OUT="$3"; VO="${4:-}"
DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO")"
FO="$(python3 -c "print(f'{max(0,$DUR-2.0):.3f}')")"

if [ -z "$VO" ]; then
  # music only
  ffmpeg -v error -y -i "$VIDEO" -i "$MUSIC" -filter_complex "\
[1:a]apad,atrim=0:${DUR},asetpts=PTS-STARTPTS,\
afade=t=in:st=0:d=0.3,afade=t=out:st=${FO}:d=2.0,\
loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest "$OUT"
else
  # music ducked under VO. NOTE: pad+split the VO or the sidechain truncates the music (see GOTCHAS)
  ffmpeg -v error -y -i "$VIDEO" -i "$MUSIC" -i "$VO" -filter_complex "\
[1:a]apad,atrim=0:${DUR},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.3,afade=t=out:st=${FO}:d=2.0,volume=0.30[m];\
[2:a]adelay=800|800,apad,atrim=0:${DUR},asetpts=PTS-STARTPTS,volume=1.4,asplit=2[v1][v2];\
[m][v1]sidechaincompress=threshold=0.035:ratio=9:attack=5:release=320[mc];\
[mc][v2]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest "$OUT"
fi

echo "wrote $OUT"
