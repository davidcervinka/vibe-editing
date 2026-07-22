#!/usr/bin/env python3
"""Generate AI b-roll via the RunwayML API (image-to-video), poll, and download the clip.

Runway's video models are image-to-video, so give it a still (a real frame, a product shot, or a
generated image) + a motion prompt. For text-only b-roll, generate an image first (Runway
`/v1/text_to_image`, or any image model) and pass it here.

    RUNWAYML_API_SECRET=... python3 gen_broll_runway.py PROMPT_IMAGE "motion prompt" out.mp4

PROMPT_IMAGE may be a public URL or a local file (encoded to a data URI automatically).
Docs (check for current model names / version header): https://docs.dev.runwayml.com
"""
import os, sys, json, time, base64, mimetypes, urllib.request

KEY = os.environ.get("RUNWAYML_API_SECRET")
if not KEY:
    sys.exit("set RUNWAYML_API_SECRET")

BASE = "https://api.dev.runwayml.com"
VERSION = os.environ.get("RUNWAY_API_VERSION", "2024-11-06")   # check docs for the current value
MODEL = os.environ.get("RUNWAY_MODEL", "gen4_turbo")           # or gen3a_turbo
HEADERS = {"Authorization": f"Bearer {KEY}", "X-Runway-Version": VERSION,
           "Content-Type": "application/json"}

img = sys.argv[1]
prompt = sys.argv[2] if len(sys.argv) > 2 else "slow cinematic push-in, subtle parallax"
out = sys.argv[3] if len(sys.argv) > 3 else "broll.mp4"

# local image -> data URI
if os.path.exists(img):
    mime = mimetypes.guess_type(img)[0] or "image/png"
    b64 = base64.b64encode(open(img, "rb").read()).decode()
    prompt_image = f"data:{mime};base64,{b64}"
else:
    prompt_image = img  # already a URL

def post(path, body):
    r = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), method="POST", headers=HEADERS)
    with urllib.request.urlopen(r, timeout=120) as resp:
        return json.loads(resp.read())

def get(path):
    r = urllib.request.Request(BASE + path, headers=HEADERS)
    with urllib.request.urlopen(r, timeout=120) as resp:
        return json.loads(resp.read())

task = post("/v1/image_to_video", {
    "model": MODEL, "promptImage": prompt_image, "promptText": prompt,
    "ratio": os.environ.get("RUNWAY_RATIO", "1280:720"), "duration": int(os.environ.get("RUNWAY_DURATION", "5")),
})
tid = task["id"]
print(f"task {tid} — polling…")

while True:
    time.sleep(5)
    t = get(f"/v1/tasks/{tid}")
    st = t.get("status")
    if st == "SUCCEEDED":
        url = t["output"][0]
        urllib.request.urlretrieve(url, out)
        print(f"wrote {out}")
        break
    if st in ("FAILED", "CANCELLED"):
        sys.exit(f"generation {st}: {t.get('failure') or t}")
    print(f"  … {st}")
