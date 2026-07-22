#!/usr/bin/env python3
"""Generate an original background track via the ElevenLabs Music API.

Prompt for STRUCTURE (intro -> build -> drop -> resolve) and concrete instruments/tempo — that's
what stops the result from sounding generic. Describe a *sound*, never a brand/artist (that 400s).

    ELEVENLABS_API_KEY=... python3 gen_music.py "prompt..." out.mp3 [length_ms]
"""
import os, sys, json, subprocess, urllib.request

KEY = os.environ.get("ELEVENLABS_API_KEY")
if not KEY:
    sys.exit("set ELEVENLABS_API_KEY")

prompt = sys.argv[1] if len(sys.argv) > 1 else (
    "Uplifting modern electronic anthem with a clear build and drop, 32 seconds. Short atmospheric "
    "intro with warm pads and a bright piano melody; a rising build with a riser; then a satisfying "
    "drop into a driving section with a punchy kick, shimmering arpeggios and a memorable synth lead "
    "over warm sub bass. Premium and hi-fi, melodic and dynamic, clean resolve. Not flat, not ambient."
)
out = sys.argv[2] if len(sys.argv) > 2 else "music.mp3"
length_ms = int(sys.argv[3]) if len(sys.argv) > 3 else 32000

body = json.dumps({"prompt": prompt, "music_length_ms": length_ms, "model_id": "music_v1"}).encode()
req = urllib.request.Request(
    "https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128",
    data=body, method="POST",
    headers={"xi-api-key": KEY, "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=600) as r, open(out, "wb") as f:
    f.write(r.read())

dur = subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]).strip().decode()
print(f"wrote {out} ({dur}s)")
