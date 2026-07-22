# 🎬 vibe-editing

**Vibe coding, but for video.** I don't open a video editor anymore — I talk to
[Claude Code](https://claude.com/claude-code).

No timeline. No keyframes. No editor UI. I describe the video in plain English — the cut, the
pacing, the music, the captions, the motion — and Claude Code drives **ffmpeg**, **ElevenLabs**,
**HyperFrames**, and a little **Python/Pillow** to cut, score, caption, animate, and render it.
Then it samples frames from its own output, checks the audio, and fixes what's wrong before
showing me.

And not just short clips — this flow ships **any kind of video**:

| | Example (real, published) | Kind |
|---|---|---|
| 🚀 | [Build Live Dashboards in Seconds](https://youtu.be/cabvIEcUqtk) | Full **product launch film** — VO, music, motion graphics |
| 🎪 | [Hackathon Aftermovie — Prague Builder Day](https://youtu.be/37AsBM02eNI) | **Event aftermovie** — interviews, montage, music-driven cut |
| 🧑‍💻 | [MCP & CLI](https://youtu.be/QxL-jAuKGU8) | **Feature walkthrough** — screen capture + kinetic type |
| 📱 | the reel below ↓ | ~30s **social reel** — split-screen, beat cuts, animated end card |

![demo](demo.gif)

That reel was built entirely through conversation:

- a 2×2 **split-screen** hero of four product-motion clips
- a **"type a request → the dashboard builds itself"** beat
- an original **music bed** with a real build/drop
- a blurred **end card** with a mascot that flies in, bounces, and flies away

This repo documents the **stack** and the **flow** so you can reproduce it — for launch films,
aftermovies, walkthroughs, reels, motion pieces, whatever. It ships the (generalized) scripts —
not source footage or brand assets.

> ⚠️ Method repo: no video/audio assets inside. Drop your own clips in and go.

---

## The stack

See **[STACK.md](STACK.md)** for the full list and *why* each tool. The short version:

| Layer | Tool | Role |
|---|---|---|
| Orchestration | **Claude Code** | Reads intent, plans, runs every command, self-reviews output |
| Editing skill | **[video-use](https://github.com/browser-use/video-use)** (Claude skill) | The conversational "ask → confirm → execute → iterate" workflow — **install this first** |
| Media engine | **ffmpeg / ffprobe** | Cut, scale, split-screen, overlay, blur, fade, concat, mux |
| Music | **ElevenLabs Music** | Original, licensing-clean background tracks (build/drop) |
| Voiceover | **ElevenLabs TTS** (+ voice cloning) | Narration when a reel needs it |
| Captions | **ElevenLabs Scribe** | Word-level transcription → styled subtitles |
| Graphics | **Python + Pillow (PIL)** | End cards, captions, mascot animation, frame compositing |
| Motion graphics | **[HyperFrames](https://github.com/heygen-com/hyperframes)** *(HTML/CSS/GSAP)* | Web-authored motion overlays — **alternative: [Remotion](https://www.remotion.dev/)** (React) |
| AI b-roll | **[Higgsfield](https://higgsfield.ai/)** (MCP) / **[RunwayML](https://runwayml.com/)** (API) | Generate footage you don't have (image→video) — see [BROLL.md](BROLL.md) |
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

Full walkthrough in **[WORKFLOW.md](WORKFLOW.md)**. Deep technique reference (cut craft, grading,
audio mixing, motion) in **[TECHNIQUES.md](TECHNIQUES.md)** and **[MOTION.md](MOTION.md)**.
Generative footage in **[BROLL.md](BROLL.md)**.

Need a shot you don't have? Generate it — **Higgsfield** (in-conversation via MCP) or **RunwayML**
(API) produce b-roll that gets normalized and folded into the same pipeline.

> 💡 **Pro tip — point Claude Code straight at your product's codebase.** The most faithful product
> visuals don't come from screenshots: give Claude Code access to your product repo / design-system
> source and it pulls the **real UI elements** — resolved design tokens (colors, type scale, radii),
> component anatomy, actual icon SVGs, even real copy strings — and rebuilds the UI as a
> pixel-faithful *animated* mock. Motion you could never screen-record, with zero brand drift.
> How-to: [MOTION.md → UI-spec-from-code](MOTION.md#ui-spec-from-code-faithful-animated-product-mock).

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
| [`grade.sh`](scripts/grade.sh) | ASC-CDL color grade (per-segment presets + raw filters) |
| [`blur_and_mux.sh`](scripts/blur_and_mux.sh) | Blurred background + music mix (+ VO duck) + `loudnorm` |
| [`gen_broll_runway.py`](scripts/gen_broll_runway.py) | AI b-roll via the RunwayML API (image→video) |

### Docs

| Doc | What's in it |
|---|---|
| [STACK.md](STACK.md) | Every tool + why |
| [WORKFLOW.md](WORKFLOW.md) | The ask → confirm → execute → self-eval → iterate loop |
| [TECHNIQUES.md](TECHNIQUES.md) | Cut craft · transcription · grading · audio/music/VO · captions · compositing |
| [MOTION.md](MOTION.md) | Motion laws · easing tokens · kinetic type · engines · UI-spec-from-code · style system |
| [REFERENCES.md](REFERENCES.md) | Launch-video reference library — real films to study + archetypes/tone distilled from them |
| [BROLL.md](BROLL.md) | Generative footage — Higgsfield (MCP) & RunwayML (API) |
| [GOTCHAS.md](GOTCHAS.md) | The traps, by area |

Read **[GOTCHAS.md](GOTCHAS.md)** before you run anything — it lists the traps that cost me time
(ffmpeg builds with no `libass`, ElevenLabs prompt ToS, `sidechaincompress` length, single-use
filter labels, etc.).

---

## Setup

This repo is the *method* + helper scripts. The two engines that do the heavy lifting —
**video-use** (the editing skill) and **HyperFrames** (motion graphics) — are separate open-source
projects you install first. Neither is bundled here.

### 1. video-use — the editing skill (install first)

The conversational editing workflow, as a Claude Code skill →
**[github.com/browser-use/video-use](https://github.com/browser-use/video-use)**

```bash
# Easiest: paste this line into Claude Code and let it do the setup —
#   "Set up https://github.com/browser-use/video-use for me."

# Or manually:
git clone https://github.com/browser-use/video-use ~/Developer/video-use
ln -sfn ~/Developer/video-use ~/.claude/skills/video-use
cd ~/Developer/video-use && uv sync        # or: pip install -e .
```

### 2. HyperFrames — motion graphics (install when you need animated overlays)

HTML/CSS/GSAP → deterministic MP4/WebM → **[github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)**
(needs **Node.js 22+**). Or use **[Remotion](https://www.remotion.dev/)** instead.

```bash
# With Claude Code / agents (recommended):
npx skills add heygen-com/hyperframes --full-depth
# Manual CLI:
npx hyperframes init my-video && cd my-video && npx hyperframes preview   # → npx hyperframes render
```

### 3. System tools + keys (for the scripts in this repo)

```bash
brew install ffmpeg yt-dlp                 # macOS (Linux: your package manager)
python3 -m pip install pillow requests
pipx install demucs                        # optional — voice cloning / stem split
cp .env.example .env                       # then paste your ElevenLabs (and Runway) keys
```

Fonts: any you like — the scripts default to Inter / Inter Display; pass `--font path/to/Bold.ttf`.
Drop a mascot/logo PNG in `assets/` if your end card uses one. Everything reads paths and keys from
env / argv — no absolute paths baked in.

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
