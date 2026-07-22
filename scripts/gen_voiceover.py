#!/usr/bin/env python3
"""Generate a voiceover via ElevenLabs Text-to-Speech.

Bring your own voice id (a stock voice, or a voice you cloned in the ElevenLabs dashboard).

    ELEVENLABS_API_KEY=... ELEVENLABS_VOICE_ID=... python3 gen_voiceover.py "script text" out.mp3
"""
import os, sys, json, subprocess, urllib.request

KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE = os.environ.get("ELEVENLABS_VOICE_ID")
if not KEY or not VOICE:
    sys.exit("set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID")

text = sys.argv[1] if len(sys.argv) > 1 else "This whole reel was built by talking to Claude Code."
out = sys.argv[2] if len(sys.argv) > 2 else "vo.mp3"
MODEL = os.environ.get("ELEVENLABS_TTS_MODEL", "eleven_multilingual_v2")

body = json.dumps({
    "text": text,
    "model_id": MODEL,
    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True},
}).encode()
req = urllib.request.Request(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
    data=body, method="POST",
    headers={"xi-api-key": KEY, "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=300) as r, open(out, "wb") as f:
    f.write(r.read())

dur = subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]).strip().decode()
print(f"wrote {out} ({dur}s)")
