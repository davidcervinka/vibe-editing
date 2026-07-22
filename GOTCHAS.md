# Gotchas (things that cost real time)

Battle scars from building this pipeline. Read before you run.

### ffmpeg with no `libass` / `freetype`

Many `ffmpeg` builds ship **without** libass and freetype, so the `subtitles`, `ass`, and
`drawtext` filters simply **don't exist** (`No such filter: 'subtitles'`). Rather than fight it,
render all text (captions, end cards) as **PIL PNGs** and composite with `overlay` +
`enable='between(t,a,b)'`. That's why [`build_captions.py`](scripts/build_captions.py) and
[`end_card.py`](scripts/end_card.py) exist. Check yours with `ffmpeg -filters | grep -E 'subtitles|drawtext'`.

### `force_style` commas break the filtergraph

Even *with* libass, commas inside `subtitles=...:force_style='Fontname=X,Fontsize=Y'` get parsed as
filter separators. Generate a styled `.ass` file instead, or (better here) skip libass entirely.

### ElevenLabs Music rejects brand names

Prompting `"...in the style of <BrandName>"` returns **HTTP 400 – "prompt violated our Terms of
Service."** Describe the *sound* (instruments, tempo, energy, build/drop), not a brand or artist.

### `sidechaincompress` output length = the shorter input

Ducking music under a shorter VO truncates the music to the VO's length. **Pad the VO/key input**
(`apad` → `atrim` to the full duration) before the sidechain, or your bed cuts out early.

### A filtergraph label can only be consumed once

Reusing `[vo]` as both the sidechain key *and* the mix input throws
`Stream specifier ... matches no streams`. **`asplit`** the stream first: `[vo]asplit=2[key][mix]`.

### Concat needs identical segment specs

`-c copy` concat only works if every segment shares codec/resolution/fps/timebase. Normalize *all*
beats to the same spec up front (see [`extract_normalize.sh`](scripts/extract_normalize.sh)),
including fps (e.g. a 60fps or 25fps source → `fps=30`).

### Don't span a source's internal cuts

Polished marketing videos intercut every 1–3s. Blindly grabbing a 3s window can straddle an internal
cut and look broken. Map the source first with a **contact sheet**
(`ffmpeg -vf "fps=2,scale=240:-1,tile=8x7"`) and cut on clean boundaries.

### Captions are white → invisible on light UI

If your footage is light (product UIs often are), white captions vanish. Use **dark text with a
white outline** (or a scrim) so they read on both light frames and dark buttons.

### Pixel-art assets: scale with NEAREST

Upscaling a small pixel mascot/logo with the default (bilinear) blurs it. Use
`Image.NEAREST` in PIL (or `-sws_flags neighbor` in ffmpeg) to keep it crisp.

### Overlays: shift PTS to the window start

An overlay clip started mid-window shows its *middle* frame. Reset with `setpts=PTS-STARTPTS`
(+ offset) so the animation's frame 0 lands at the overlay's start.

### Self-check the render, not the sources

Bugs (hidden caption, flash at a cut, audio pop) only appear in the *composited output*. Always
sample frames + waveform from the **final file**, at the cut boundaries, before shipping.
