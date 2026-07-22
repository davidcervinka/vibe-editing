#!/usr/bin/env python3
"""Animated end card: text (+ optional mascot) flies in, bounces, flies away, over a blurred bg,
then fades to white. Pure PIL for the animation + ffmpeg for the blur/overlay (no libass needed).

    python3 end_card.py --bg background.mp4 --line1 "Built with" --line2 "Claude Code" \
        --mascot assets/mascot.png --font path/to/Bold.ttf --out end.mp4

--bg may be a video (it gets blurred) or omitted for a plain white background.
"""
import argparse, math, subprocess, tempfile, pathlib
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--bg"); ap.add_argument("--out", default="end.mp4")
ap.add_argument("--line1", default="Built with"); ap.add_argument("--line2", default="Claude Code")
ap.add_argument("--mascot"); ap.add_argument("--font", required=True)
ap.add_argument("--dur", type=float, default=3.5); ap.add_argument("--fps", type=int, default=30)
a = ap.parse_args()

W, H, N = 1920, 1080, int(a.dur * a.fps)
IRIS, YELLOW = (25, 26, 36), (255, 231, 79)
font = ImageFont.truetype(a.font, 120)
frames = pathlib.Path(tempfile.mkdtemp())

# static text block (two centered lines, yellow highlight behind line 2)
block = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(block)
cy1, cy2 = H // 2 + 70, H // 2 + 205
def measure(t): b = bd.textbbox((0, 0), t, font=font); return b, b[2]-b[0], b[3]-b[1]
b1, w1, h1 = measure(a.line1); b2, w2, h2 = measure(a.line2)
bd.text(((W-w1)//2 - b1[0], cy1 - b1[1] - h1//2), a.line1, font=font, fill=IRIS + (255,))
x2 = (W-w2)//2; ry = cy2 - h2//2 - b2[1] + 18
bd.rounded_rectangle([x2-26, ry, x2+w2+26, ry+h2+30], radius=20, fill=YELLOW + (255,))
bd.text((x2 - b2[0], cy2 - b2[1] - h2//2), a.line2, font=font, fill=IRIS + (255,))

masc = None
if a.mascot:
    masc = Image.open(a.mascot).convert("RGBA")
    mw = 230; masc = masc.resize((mw, int(masc.height*mw/masc.width)), Image.NEAREST)
masc_cx, masc_cy = W // 2, H // 2 - 150

eo = lambda t: 1 - (1 - t) ** 3          # ease-out cubic (fly in)
ei = lambda t: t ** 3                     # ease-in cubic (fly away)
for i in range(N):
    t = i / a.fps
    if t <= 0.5:                          # fly in from below
        p = eo(t / 0.5); dy = int((1 - p) * 170); alpha = p; bob = 0
    elif t <= 2.5:                        # hold (mascot hops)
        dy = 0; alpha = 1.0; bob = int(-abs(math.sin((t - 0.5) * math.pi * 1.1)) * 16)
    elif t <= 3.3:                        # fly away up
        q = ei((t - 2.5) / 0.8); dy = int(-300 * q); alpha = 1 - q; bob = 0
    else:
        dy, alpha, bob = -300, 0.0, 0
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if alpha > 0:
        lay = block.copy(); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        fr.paste(lay, (0, dy), lay)
        if masc:
            m = masc.copy()
            if alpha < 1: m.putalpha(m.getchannel("A").point(lambda v: int(v * alpha)))
            fr.paste(m, (masc_cx - masc.width//2, masc_cy - masc.height//2 + dy + bob), m)
    fr.save(frames / f"f{i:04d}.png")

# background: blurred video, or plain white
if a.bg:
    bg = ["-i", a.bg]; bgv = "[0:v]scale=1920:1080,fps=30,gblur=sigma=24,drawbox=x=0:y=0:w=1920:h=1080:color=white@0.42:t=fill[bg]"
    txt_idx = 1
else:
    bg = ["-f", "lavfi", "-i", f"color=c=white:s=1920x1080:r=30"]; bgv = "[0:v]null[bg]"; txt_idx = 1

subprocess.run([
    "ffmpeg", "-y", "-v", "error", *bg, "-framerate", str(a.fps), "-i", str(frames / "f%04d.png"),
    "-filter_complex", f"{bgv};[bg][{txt_idx}:v]overlay=0:0,fade=t=out:st={a.dur-0.3:.2f}:d=0.3:color=white[v]",
    "-map", "[v]", "-t", str(a.dur), "-r", str(a.fps), "-pix_fmt", "yuv420p",
    "-c:v", "libx264", "-crf", "18", "-an", a.out], check=True)
print(f"wrote {a.out}")
