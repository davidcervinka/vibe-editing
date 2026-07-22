# Gotchas (things that cost real time)

Battle scars from building this pipeline, by area. Read before you run.

## ffmpeg / build

- **No `libass` / `freetype`** → the `subtitles`, `ass`, and `drawtext` filters don't exist
  (`No such filter: 'subtitles'`). Render text (captions, cards) as **PIL PNGs** + `overlay …
  enable='between(t,a,b)'`. Check: `ffmpeg -filters | grep -E 'subtitles|drawtext'`.
- **`force_style` commas break the filtergraph** — commas in `subtitles=...:force_style='...'` parse
  as filter separators. Generate a styled `.ass`, or skip libass entirely.
- **Concat needs identical specs** — `-c copy` concat only works if every segment shares
  codec/res/fps/timebase. Normalize all beats up front, including fps (60/25 → 30).
- **Concat rejects mixed SAR** — framework-rendered MP4s can carry SAR `169:160`; apply `setsar=1`
  to every input before concat.
- **Framework renders have no audio** — feed a matched-length
  `anullsrc=channel_layout=stereo:sample_rate=44100` per silent segment, or concat drops audio sync.
- **Overlays show the wrong frame** — reset with `setpts=PTS-STARTPTS+{offset}/TB` so the overlay's
  frame 0 lands at its window start.
- **HDR metadata survives an 8-bit export** — if the source is PQ/HLG, an SDR output still *carries*
  the transfer tag and blows out on some players. Tone-map explicitly (see TECHNIQUES §4).
- **Pixel-art scales blurry** — use `Image.NEAREST` (PIL) / `-sws_flags neighbor` (ffmpeg).

## Audio / music

- **ElevenLabs Music minimum length ~42 s** even if you request 24 s → trim afterward. And the track
  must be **≥ the video length**.
- **ElevenLabs Music 400 `bad_prompt`** if the prompt names a brand/artist to imitate — describe the
  *sound* (instruments, tempo, energy, build/drop), not "in the style of X".
- **`sidechaincompress` output = the shorter input** — a short VO key truncates the music. **Pad the
  VO key** (`apad`→`atrim`) to full length.
- **A filtergraph label is single-use** — reusing `[vo]` as sidechain key *and* mix input throws
  `Stream specifier ... matches no streams`. `asplit=2[key][mix]`.
- **Audio pops at cuts** — 30 ms fades at every segment boundary
  (`afade=t=in:d=0.03` + `afade=t=out:d=0.03`).
- Loudness: master to **−14 LUFS** (`loudnorm=I=-14:TP=-1.5`) for social; a limiter
  (`alimiter=limit=0.97`) catches peaks.

## Cutting

- **Cut on silence, snap to word boundaries** — `silencedetect=noise=-30dB:d=0.4`; pad edges
  30–200 ms (ASR drifts 50–100 ms); never cut inside a word.
- **Dissolves fight kinetic clips** — a crossfade over a typing/UI animation fades it mid-motion.
  For UI-motion montages, hard cuts read cleaner.
- **Don't span a source's internal cuts** — polished videos intercut every 1–3 s. Map with a contact
  sheet (`fps=2,tile=8x7`) and cut on clean boundaries; extend in/out to contain a beat's payoff.

## HTML `<video>` embeds (HyperFrames / browser render)

- **Sparse keyframes break seeking** — re-encode embedded clips with `-g 30 -keyint_min 30`
  (1 keyframe/sec) or frames go black near the clip end (`media_missing_data_start`).
- **Chromium caches video by filename** between renders — after re-encoding, **rename** the asset
  (`clip.mp4`→`clip_v2.mp4`) to force a reload.
- **`body{background:#000}` isn't captured as opaque pixels** in an alpha MOV — a slot that must
  cover the source needs a first-child `<div style="position:absolute;inset:0;background:#000">`.
- **Fonts need explicit `@font-face`** (lint `font_family_without_font_face`); vendor the TTF into the
  slot's own `assets/fonts/`. Absolute `@font-face` paths **with a comma in the filename** fail on
  the render server; the validate static server blocks `../../` traversal — keep assets self-contained.
- **Alpha:** `--format mov` (ProRes 4444) gives real alpha; **WebM may come back `yuv420p` without
  alpha** on some toolchains — use MOV for overlays.
- **Determinism:** no `Date.now()`, no unseeded `Math.random()`, no render-time fetches, no
  `repeat:-1`. Pre-render any raw-rAF/canvas widget to MP4 via a frame-stepper (virtualize the clock)
  and embed it as a `<video>`.

## GSAP / SVG

- **SVG `<g>` transforms are in user-space (viewBox) units, not CSS px.** With a 540px wrapper over a
  1924-unit viewBox (scale ≈0.281), moving ~208 CSS px means `x: 741` (=208/0.281), not `x:208`.
- **Don't add `transform-box:fill-box; transform-origin:50% 50%`** to an SVG element that already has
  a baked `transform="matrix(...)"` — it re-anchors the matrix and the element jumps/vanishes.
- **Center with GSAP `xPercent:-50, yPercent:-50`**, not CSS `translate(-50%,-50%)`, when the element
  also tweens y/x/scale — GSAP overwrites the whole transform (lint `gsap_css_transform_conflict`).
- **A parent scaling up drags an off-center child** — split into a modest grow during the slide
  (1→1.4) + the big grow in place after (1.4→4).
- **Validator contrast false positives** — it samples the light page bg, so light-on-dark text on a
  dark card reports ~1:1. Trust the rendered frame, not the lint.

## Process

- **Self-check the render, not the sources** — hidden captions, flashes, and pops only appear in the
  composited output. Sample frames at every cut boundary + waveform, from the *final* file.
- **Keep every prior render** (`final_v1…vN`) and a "current truth / don't re-experiment with approved
  patterns" note in `project.md`.
- **Trust frames over lint** — a clean lint pass is not a correct render.
