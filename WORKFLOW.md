# The flow, step by step

How a raw folder of clips becomes a finished reel — entirely through conversation.

## 0. Drop clips in a folder

No naming convention required. Sources stay untouched; all output goes to an `edit/` folder.

## 1. Inventory

Claude runs `ffprobe` on every source and samples frames (`ffmpeg -ss <t> -frames:v 1`) to *see*
what's in each clip and at what timestamps. For talking-head footage it also transcribes
(ElevenLabs Scribe) so it can cut on word boundaries.

## 2. Ask → propose a plan

Instead of guessing, it asks the few questions that actually change the edit (aspect ratio, music
vs. VO, structure) and then writes the plan back in plain English:

> *"2×2 split-screen hero → Pulse types a request and the dashboard builds → capture text glides in
> → … → blurred 'Built with Claude Code' end card that flies away. ~30s, 1080p, original music with
> a build/drop."*

Nothing gets cut until I confirm.

## 3. Extract & normalize each beat

Every beat is extracted to an **identical** spec (`1920×1080@30`, same codec) so segments concat
cleanly later. Cut points are chosen off the frame samples (and word boundaries for speech).
→ [`scripts/extract_normalize.sh`](scripts/extract_normalize.sh)

## 4. Compose the visuals

- **Split-screen** via `xstack` → [`scripts/quad_split.sh`](scripts/quad_split.sh)
- **Overlays / captions / graphics** composited on top (PIL PNG sequences + `overlay`)
- **End card** — blurred background + animated text/mascot → [`scripts/end_card.py`](scripts/end_card.py)
- **Lossless concat** of the beats → [`scripts/concat.sh`](scripts/concat.sh)

## 5. Score & voice

- **Music** generated to fit the arc (intro → build → drop → resolve) →
  [`scripts/gen_music.py`](scripts/gen_music.py)
- **Voiceover** if needed → [`scripts/gen_voiceover.py`](scripts/gen_voiceover.py)
- Mixed, ducked under VO, and mastered with `loudnorm` →
  [`scripts/blur_and_mux.sh`](scripts/blur_and_mux.sh)

## 6. Captions LAST

Captions/subtitles are applied **after** every overlay so nothing hides them. Word timings come
from Scribe; chunks are rendered as styled PNGs and overlaid on their time windows →
[`scripts/build_captions.py`](scripts/build_captions.py)

## 7. Self-evaluate (the important part)

Before showing me anything, Claude:

- samples output frames at **every cut boundary** and mid-beat, and looks at them for flashes,
  wrong frames, or hidden captions
- renders the **waveform** (`showwavespic`) and checks **loudness** (`volumedetect` / `loudnorm`)
  for clipping or dead air
- confirms the **duration** matches the plan

If anything's off → back to step 4. It caps the loop and flags anything it can't fix rather than
looping forever.

## 8. Iterate on feedback

Every note re-enters the loop:

| I say… | It does… |
|---|---|
| "the meta part isn't in full" | finds a cleaner source window where the UI is fully settled |
| "0:22–0:25 is too slow" | speeds up / trims just that beat |
| "the music is too generic" | analyzes a reference track's build/drop and regenerates to match |
| "add an end card that flies away" | builds a PIL fly-in/out animation over a blurred background |

## 9. Persist

Each session's decisions (cut windows, grades, music prompts, gotchas) are appended to a
`project.md` so the next session picks up with full context.
