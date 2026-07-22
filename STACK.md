# The stack (in full)

Every tool involved in making these videos, and why it's there.

## Orchestration

- **[Claude Code](https://claude.com/claude-code)** — the agent that reads my intent, proposes a
  plan, runs *every* command below, inspects its own output, and iterates on feedback. Nothing here
  is a fixed template; it's assembled per-video from a conversation.
- **The `video-use` skill** — a Claude skill that encodes the editing discipline: *inventory → ask →
  confirm the plan in plain English → execute → self-evaluate → iterate → persist*. It also carries
  the "hard rules" (captions applied last, per-segment extract before concat, audio fades at cuts,
  cache transcripts, etc.).

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

- **HyperFrames** — author motion as HTML/CSS/GSAP, render deterministically to MP4/WebM.
- **[Remotion](https://www.remotion.dev/)** — the **React alternative** to HyperFrames. Write
  compositions as components, `remotion render` to MP4. Pick whichever authoring model you prefer;
  both output a clip you fold into the ffmpeg pipeline.

## Research / matching a vibe

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — pull a reference video whose look/music you like.
- **Python (`wave` / `audioop`)** — quick RMS/loudness analysis + `ffmpeg showwavespic` /
  `showspectrumpic` to read a track's build/drop structure, so a *generated* track can match it.

## Environment

- macOS + Homebrew for `ffmpeg` / `yt-dlp` (Linux works too).
- Standard `ffmpeg` sometimes ships **without libass/freetype** → no `subtitles`/`drawtext` filter.
  This repo's caption/text approach uses PIL + `overlay` so it works regardless. See
  [GOTCHAS.md](GOTCHAS.md).
