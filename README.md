# 🎬 Editing product videos by *talking* to Claude Code

No timeline. No editor UI. No keyframes by hand.

I describe the edit in plain English — *"cut these four clips into a split-screen, build the
Pulse dashboard reveal, add music that builds and drops, put a 'Built with Claude Code' card at
the end that flies away"* — and [Claude Code](https://claude.com/claude-code) drives **ffmpeg**,
**ElevenLabs**, and a little **Python/Pillow** to actually cut, score, caption, animate, and render
the video. Then it samples frames from its own output, checks the audio, and fixes what's wrong
before showing me.

This repo documents the **stack** and the **flow** so you can reproduce it. It ships the
(generalized) scripts — not my source footage or brand assets.

> ⚠️ This is a *method* repo. It contains no video/audio assets. Drop your own clips in and go.

---

## The result

A ~30s LinkedIn reel built entirely through conversation:

- a 2×2 **split-screen** hero of four product-motion clips
- a **"type a request → the dashboard builds itself"** beat
- kinetic **captions** burned in for silent autoplay
- an original **music bed** with a real build/drop
- a blurred **end card** with a mascot that flies in, bounces, and flies away

*(Add your own `demo.gif` / `demo.mp4` here.)*

---

## The stack

See **[STACK.md](STACK.md)** for the full list and *why* each tool. The short version:

| Layer | Tool | Role |
|---|---|---|
| Orchestration | **Claude Code** | Reads intent, plans, runs every command, self-reviews output |
| Editing skill | **`video-use`** skill | The conversational "ask → confirm → execute → iterate" workflow |
| Media engine | **ffmpeg / ffprobe** | Cut, scale, split-screen, overlay, blur, fade, concat, mux |
| Music | **ElevenLabs Music** | Original, licensing-clean background tracks (build/drop) |
| Voiceover | **ElevenLabs TTS** (+ voice cloning) | Narration when a reel needs it |
| Captions | **ElevenLabs Scribe** | Word-level transcription → styled subtitles |
| Graphics | **Python + Pillow (PIL)** | End cards, captions, mascot animation, frame compositing |
| Motion graphics | **HyperFrames** *(HTML/CSS/GSAP)* | Web-authored motion overlays — **alternative: [Remotion](https://www.remotion.dev/)** (React) |
| Research | **yt-dlp** + Python | Pull reference videos, analyze tempo/loudness to match a vibe |

---

## The flow

```mermaid
flowchart TD
    A[Drop raw clips in a folder] --> B[Inventory: ffprobe + sample frames]
    B --> C[Ask → propose a plain-English plan]
    C --> D{Confirm}
    D -->|yes| E[Extract & normalize each beat<br/>ffmpeg → 1080p@30]
    E --> F[Compose:<br/>quad split-screen · overlays · blur · end card]
    F --> G[Audio: ElevenLabs music/VO<br/>mix · duck · loudnorm]
    G --> H[Captions LAST<br/>Scribe → PIL/subtitles]
    H --> I[Self-eval:<br/>sample output frames · waveform · loudness]
    I -->|issues| F
    I -->|clean| J[Show me → I give notes]
    J -->|change X| C
    J -->|ship| K[Final render]
```

The loop that makes it work is **step I → J**: Claude renders, then *looks at its own frames*
(`ffmpeg -ss ... -frames:v 1`), checks the audio waveform/loudness, and only surfaces the cut once
it passes. Every note I give ("meta part isn't in full", "0:22–0:25 is too slow", "make the music
build") re-enters the same loop.

Full walkthrough in **[WORKFLOW.md](WORKFLOW.md)**.

---

## What's in `scripts/`

| Script | What it does |
|---|---|
| [`extract_normalize.sh`](scripts/extract_normalize.sh) | Per-segment extract → uniform 1080p@30 (the safe way to concat) |
| [`quad_split.sh`](scripts/quad_split.sh) | 2×2 split-screen of four clips via `xstack` |
| [`concat.sh`](scripts/concat.sh) | Lossless `-c copy` concat of segments |
| [`gen_music.py`](scripts/gen_music.py) | ElevenLabs Music → an original track (with build/drop) |
| [`gen_voiceover.py`](scripts/gen_voiceover.py) | ElevenLabs TTS voiceover (bring your own voice id) |
| [`transcribe.py`](scripts/transcribe.py) | ElevenLabs Scribe word-level transcript |
| [`build_captions.py`](scripts/build_captions.py) | Kinetic captions **without libass** — PIL PNGs + `overlay` |
| [`end_card.py`](scripts/end_card.py) | Animated end card: text + mascot fly-in → bounce → fly-away |
| [`blur_and_mux.sh`](scripts/blur_and_mux.sh) | Blurred background + music mix + `loudnorm` |

Read **[GOTCHAS.md](GOTCHAS.md)** before you run anything — it lists the traps that cost me time
(ffmpeg builds with no `libass`, ElevenLabs prompt ToS, `sidechaincompress` length, single-use
filter labels, etc.).

---

## Setup

```bash
# 1. tools
brew install ffmpeg yt-dlp        # macOS
python3 -m pip install pillow requests

# 2. key
cp .env.example .env              # then paste your ElevenLabs API key

# 3. fonts (any you like) — the scripts default to Inter / Inter Display
#    put a mascot/logo PNG in assets/ if your end card uses one
```

Everything reads paths and the API key from env / argv — no absolute paths baked in.

---

## HyperFrames vs. Remotion

For richer motion graphics (kinetic type, UI-to-video, animated overlays) you author a composition
and render it to MP4/WebM:

- **HyperFrames** — HTML/CSS/GSAP, browser-rendered, deterministic frame capture.
- **[Remotion](https://www.remotion.dev/)** — the React alternative. Same idea, component-based;
  great if you'd rather write JSX than HTML/CSS. `npx create-video@latest` → `remotion render`.

Both drop a rendered clip that you overlay/concat with the rest of the ffmpeg pipeline.

---

## Notes

- **Anonymized:** no source footage, brand assets, voice ids, or API keys are included.
- **Music & copyright:** *generate* your beds (licensing-clean) rather than ripping a track from
  someone's video. Reference tracks are for matching a *vibe*, not for shipping.
- **License:** [MIT](LICENSE) — do whatever, no warranty.

Built by talking to Claude Code. 🟧
