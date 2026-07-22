#!/usr/bin/env python3
"""Kinetic captions WITHOUT libass — render styled PNGs with PIL, overlay them on time windows.

Works on any ffmpeg build (no subtitles/drawtext filter needed). Dark text + white outline so it
reads on light UI footage. Reads a Scribe JSON (from transcribe.py) for word timings.

    python3 build_captions.py transcript.json in.mp4 out.mp4 [offset_seconds]
"""
import sys, json, subprocess, pathlib, re, tempfile
from PIL import Image, ImageDraw, ImageFont

TRANSCRIPT, VIDEO, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
OFFSET = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
FONT = pathlib.Path(sys.argv[5]) if len(sys.argv) > 5 else None  # a bold .ttf; falls back to default
MAX_WORDS = 3
W, H = 1920, 1080

font = ImageFont.truetype(str(FONT), 62) if FONT else ImageFont.load_default()
words = [w for w in json.load(open(TRANSCRIPT))["words"] if w.get("type") == "word"]

# group into short cues, break on punctuation
cues, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) >= MAX_WORDS or re.search(r"[.?!,]$", w["text"]):
        cues.append(cur); cur = []
if cur:
    cues.append(cur)

tmp = pathlib.Path(tempfile.mkdtemp())
overlays = []
for i, grp in enumerate(cues):
    text = re.sub(r"[.?!,]+$", "", " ".join(x["text"].strip() for x in grp)).upper()
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), text, font=font, stroke_width=7)
    x = (W - (bb[2] - bb[0])) // 2 - bb[0]
    y = H - 96 - (bb[3] - bb[1]) - bb[1]                 # lower third
    d.text((x, y), text, font=font, fill=(25, 26, 36, 255),
           stroke_width=7, stroke_fill=(255, 255, 255, 255))
    p = tmp / f"c{i:03d}.png"; img.save(p)
    overlays.append((p, grp[0]["start"] + OFFSET, grp[-1]["end"] + OFFSET))

# chain one overlay per cue, gated by enable='between(t,start,end)'
inputs, chain, prev = [], [], "[0:v]"
for i, (p, s, e) in enumerate(overlays):
    inputs += ["-i", str(p)]
    out = f"[v{i}]" if i < len(overlays) - 1 else "[vout]"
    chain.append(f"{prev}[{i+1}:v]overlay=0:0:enable='between(t,{s:.2f},{e:.2f})'{out}")
    prev = out

subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", VIDEO, *inputs,
                "-filter_complex", ";".join(chain),
                "-map", "[vout]", "-map", "0:a?", "-c:v", "libx264", "-crf", "18",
                "-c:a", "copy", "-pix_fmt", "yuv420p", OUT], check=True)
print(f"wrote {OUT} ({len(cues)} caption cues)")
