#!/usr/bin/env python3
"""Word-level transcription via ElevenLabs Scribe -> JSON. Word timings drive caption chunking.

    ELEVENLABS_API_KEY=... python3 transcribe.py input.(mp4|wav|mp3) out.json
"""
import os, sys, json, subprocess, tempfile, urllib.request, mimetypes, uuid

KEY = os.environ.get("ELEVENLABS_API_KEY")
if not KEY:
    sys.exit("set ELEVENLABS_API_KEY")

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else "transcript.json"

# extract audio to wav (works for video or audio input)
wav = tempfile.mktemp(suffix=".wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ar", "16000", "-ac", "1", wav], check=True)

# multipart/form-data upload
boundary = uuid.uuid4().hex
with open(wav, "rb") as f:
    audio = f.read()

def field(name, value):
    return (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n').encode()

parts = field("model_id", "scribe_v1") + field("timestamps_granularity", "word")
parts += (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\n'
          f'Content-Type: audio/wav\r\n\r\n').encode() + audio + f'\r\n--{boundary}--\r\n'.encode()

req = urllib.request.Request(
    "https://api.elevenlabs.io/v1/speech-to-text", data=parts, method="POST",
    headers={"xi-api-key": KEY, "Content-Type": f"multipart/form-data; boundary={boundary}"})
with urllib.request.urlopen(req, timeout=600) as r:
    data = json.loads(r.read())

json.dump(data, open(out, "w"), indent=2)
words = [w for w in data.get("words", []) if w.get("type") == "word"]
print(f"wrote {out} ({len(words)} words)")
