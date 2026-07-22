# The stack (in full)

Every tool involved in making these videos, and why it's there.

## Orchestration

- **[Claude Code](https://claude.com/claude-code)** — the agent that reads my intent, proposes a
  plan, runs *every* command below, inspects its own output, and iterates on feedback. Nothing here
  is a fixed template; it's assembled per-video from a conversation.
- **The [video-use](https://github.com/browser-use/video-use) skill** — a Claude skill (install it
  first) that encodes the editing discipline: *inventory → ask → confirm the plan in plain English →
  execute → self-evaluate → iterate → persist*. It carries the "hard rules" (captions applied last,
  per-segment extract before concat, audio fades at cuts, cache transcripts, etc.) and its own
  helpers (transcribe / grade / render / timeline-view). Needs ffmpeg + an ElevenLabs key.

## Media engine

- **ffmpeg / ffprobe** — the workhorse. Used for:
  - `ffprobe` inventory + `-frames:v 1` frame sampling (how Claude "sees" the footage)
  - per-segment extract + scale/pad to a uniform `1920×1080@30`
  - `xstack` 2×2 split-screen
  - `overlay` (with `enable='between(t,a,b)'`) for captions/graphics when the build has no libass
  - `gblur` blurred backgrounds, `drawbox` scrims, `fade` (incl. fade-to-white)
  - `-c copy` lossless concat, `sidechaincompress` ducking, `loudnorm` mastering

## Audio & voice — ElevenLabs

- **Music** (`music_v1`) — original background tracks generated from a text prompt. Prompt for
  structure ("atmospheric intro → build → drop → resolve") to avoid a flat, generic bed.
- **Text-to-Speech** (+ **voice cloning**) — narration. Clone a consistent narrator voice, or use a
  stock voice id.
- **Scribe** — word-level speech-to-text. Word timings drive caption chunking so captions land on
  the beat.

## Graphics & compositing

- **Python 3 + [Pillow (PIL)](https://python-pillow.org/)** — everything hand-drawn:
  - animated end cards (fly-in / bounce / fly-away with cubic easing)
  - kinetic caption PNG sequences (when the ffmpeg build lacks `drawtext`/`subtitles`)
  - mascot/logo compositing, yellow highlight bars, etc.
- **Fonts** — [Inter / Inter Display](https://rsms.me/inter/) by default (swap for your brand type).

## Motion graphics (optional, for richer overlays)

- **[HyperFrames](https://github.com/heygen-com/hyperframes)** — author motion as HTML/CSS/GSAP,
  render deterministically to MP4/WebM (alpha). Apache-2.0, needs Node.js 22+ and FFmpeg. Install:
  `npx skills add heygen-com/hyperframes --full-depth` (agents) or `npx hyperframes init`.
- **[Remotion](https://www.remotion.dev/)** — the **React alternative** to HyperFrames. Write
  compositions as components, `remotion render` to MP4. Pick whichever authoring model you prefer;
  both output a clip you fold into the ffmpeg pipeline.

## AI b-roll (footage you don't have)

- **[Higgsfield](https://higgsfield.ai/)** — via **MCP**, so the agent calls it in-conversation:
  `generate_image` / `generate_video` / `motion_control` / `reframe` / `upscale_video`.
- **[RunwayML](https://runwayml.com/)** — REST **API** (image→video, Gen-4/Gen-3) for scripted
  pipelines → [`scripts/gen_broll_runway.py`](scripts/gen_broll_runway.py).
- See **[BROLL.md](BROLL.md)** for the flow and how generated shots are normalized into the cut.

## Audio surgery

- **[Demucs](https://github.com/adefossez/demucs)** — two-stem source separation: pull a clean
  **vocals** stem (to clone a voice from existing footage) *and* a ready-made **instrumental** bed
  (the `no_vocals` stem) from the same clip.
- **ffmpeg audio filters** — `silencedetect` (cut on speech gaps), `sidechaincompress` (duck),
  `loudnorm` (master to −14 LUFS), `alimiter`, `atempo` (time-stretch a bed to fit).

## Research / matching a vibe

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — pull a reference video whose look/music you like.
- **Python (`wave` / `audioop`)** — quick RMS/loudness analysis + `ffmpeg showwavespic` /
  `showspectrumpic` to read a track's build/drop structure, so a *generated* track can match it.
- **ffmpeg `signalstats`** — luma/saturation probes for auto-grading and for finding hard
  cuts / black frames in a source.

## Environment

- macOS + Homebrew for `ffmpeg` / `yt-dlp` (Linux works too).
- Standard `ffmpeg` sometimes ships **without libass/freetype** → no `subtitles`/`drawtext` filter.
  This repo's caption/text approach uses PIL + `overlay` so it works regardless. See
  [GOTCHAS.md](GOTCHAS.md).
