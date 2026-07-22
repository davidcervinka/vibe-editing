# Techniques

The reusable craft accumulated across many videos — cut craft, transcription, grading, audio/music,
voiceover, captions, and the compositing pipeline. Concrete values throughout; anonymized.

> Motion-graphics craft (easings, kinetic type, HyperFrames/Remotion) lives in **[MOTION.md](MOTION.md)**.
> The traps live in **[GOTCHAS.md](GOTCHAS.md)**.

---

## The core loop

`raw clip → transcribe (word-level) → cut on the transcript → generate VO + music → render
motion-graphic overlays → composite with ffmpeg → self-eval on sampled frames → iterate`.

A per-project `project.md` is durable memory ("current truth") a fresh session resumes from. **Keep
every prior render (`final_v1…vN`)** so you can diff/revert, and keep a "do not re-experiment with
approved patterns" note.

---

## 1. Seeing footage (the model reads video, it doesn't watch it)

The model never streams frames. Two layers instead:

1. **An always-loaded word-level transcript**, packed to ~12 KB markdown.
2. **On-demand visual composites** (a few PNGs) only at decision points.

Naïve frame-dumping ≈ 30,000 frames × ~1,500 tokens ≈ 45M tokens of noise. This approach is ~12 KB
text + a handful of images.

- **`ffprobe` every source** for duration and `color_transfer` (detect HDR — see grading).
- **Sample frames** at timestamps: `ffmpeg -ss <t> -i src -frames:v 1 -q:v 4 -vf scale=320:-2 out.jpg`.
- **Contact sheet** to map a fast-intercut source: `-vf "fps=2,scale=240:-1,tile=8x7"` gives a
  0.5s-per-cell grid so you can read off clean windows (and spot the source's own internal cuts).
- **Filmstrip + waveform + word labels** at a decision point (a "timeline view"): extract N evenly
  spaced frames into a strip, draw a windowed-RMS waveform ribbon below, overlay transcript words
  (only ≥120ms, min 28px apart), shade silence gaps ≥400ms. **Use at decision points, never in a
  scan loop.**
- **Packed transcript** (`takes_packed.md`): one markdown file, each take a list of phrase-level
  lines `[start-end] Sx text`, phrases broken on **silence ≥0.5s or speaker change**. ~1 hr of takes
  at ~1/10 the tokens of raw JSON, with word-boundary precision from text alone. This is what you
  point at to choose cuts.

---

## 2. Transcription

**Hosted word-level ASR** (e.g. ElevenLabs Scribe `scribe_v1`) — see [`scripts/transcribe.py`](scripts/transcribe.py):

- Extract mono 16 kHz PCM first (`-vn -ac 1 -ar 16000 -c:a pcm_s16le`).
- Request `timestamps_granularity=word`, `diarize=true`, `tag_audio_events=true`; optional
  `num_speakers` improves diarization; omit `language_code` to auto-detect.
- **Why word-level verbatim, never SRT/phrase:** SRT loses sub-second gap data (needed for cut
  candidates); normalized output drops fillers/false-starts (editorial signal); word-level lets cuts
  snap to boundaries and captions re-time to the output timeline.
- **Cache per source stem** and never re-transcribe (immutable output of immutable input). Batch with
  ~4 parallel workers.

---

## 3. Cut craft

**Find cut points from audio, not by eye.**

- Speech onsets/silences: `ffmpeg -af "silencedetect=noise=-30dB:d=0.4" -f null -`. Cutting *just
  before* a detected onset leaves a breathing buffer (e.g. cut at 73.0s when onset is 73.5s → the
  line plays cleanly in the *next* segment).
- Detect hard cuts / black frames in a source with a luma probe (`signalstats` `YAVG`): a jump
  16→181 across two frames = a cut. A black frame is ~8 KB as a PNG vs ~400 KB for real UI — file
  size finds cut-to-black.
- **Never cut inside a word** — snap to a word boundary. **Pad every edge 30–200 ms** (ASR drifts
  50–100 ms). Shipped example: 50 ms before the first kept word, 80 ms after the last.
- Silences **≥400 ms** are the cleanest cut targets; 150–400 ms usable with a visual check; <150 ms
  unsafe. Speaker-handoff air **400–600 ms** (less for fast-paced, more for cinematic).
- **Preserve peaks** — extend past laughs/punchlines to include the reaction (the laugh *is* the beat).

**Montage / UI-motion specifics:**

- **Include a clip's signature motion, not its middle.** A card that cut at 2.2–4.6s stopped *before*
  its payoff (text glides aside, a card slides in at ~5–7.7s); re-extracting 4.0–7.9s captured the
  whole gesture. Extend in/out to contain the beat's resolve.
- Normalize mixed frame rates (25/60 → 30) before cutting.
- **Hard cuts read cleaner than dissolves for UI-motion montages** — a crossfade over a typing
  animation makes it fade mid-keystroke. Reverting all `xfade` to hard cuts fixed it.
- **Seamless "invisible" cut:** make the outgoing last frame and incoming first frame identical (both
  land on the same full-bleed color) → the hard cut reads as one continuous dip.
- **Speed-ramp** a too-slow beat with `setpts=PTS/1.5`; prefer trimming to a shorter natural-pace
  window over a visible ramp.

---

## 4. Color grading

**Mental model = ASC CDL.** Per channel `out = (in*slope + offset)**power`, then global saturation.
`slope`→highlights, `offset`→shadows, `power`→midtones. Look at a frame, fix one thing, look again.
→ [`scripts/grade.sh`](scripts/grade.sh)

**Apply per-segment during extraction, never post-concat** (post-concat re-encodes twice).

**Auto mode (default — data-driven, bounded ±8%, no creative shift):** sample frames via
`signalstats`, read `YAVG/YMIN/YMAX/SATAVG` normalized by bit depth; emit a small `eq=...` that only
fixes underexposure/flatness/mild desaturation:
- contrast target luma range ≈0.72 (clamp `[0.94,1.08]`, never reduce)
- gamma target luma mean ≈0.48 (clamp `[0.94,1.10]`)
- saturation target ≈0.25, default `0.98` (most consumer video is slightly over-saturated; clamp `[0.94,1.06]`)
- drop adjustments <0.005. "Clean without looking graded."

**Named presets (actual chains):**
```
subtle          eq=contrast=1.03:saturation=0.98
neutral_punch   eq=contrast=1.06:saturation=1.0,curves=master='0/0 0.25/0.23 0.75/0.77 1/1'
warm_cinematic  eq=contrast=1.12:brightness=-0.02:saturation=0.88,
                colorbalance=rs=0.02:bs=-0.03:rm=0.04:bm=-0.02:rh=0.08:bh=-0.05,
                curves=master='0/0 0.25/0.22 0.75/0.78 1/1'
none            (straight copy — default when nobody asked)
```
`warm_cinematic` is opt-in only (too strong for talking heads). **Never go aggressive without
checking skin tones.**

**HDR → SDR** (prepend when `color_transfer` is `smpte2084`/PQ or `arib-std-b67`/HLG — otherwise an
8-bit output still carries the transfer metadata and blows out on some players):
```
zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,
tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p
```

---

## 5. Audio & music

### Generate the bed (ElevenLabs Music) — [`scripts/gen_music.py`](scripts/gen_music.py)

Two prompt *structures*, chosen by the video's energy:

- **(a) Flat "carpet" bed** (VO-led films): *"Warm, minimal, modern product-film instrumental… one
  consistent relaxed groove the whole way through — **NO drops, NO risers, NO build, no EDM**… subtle
  2s fade-in, graceful thinning in the last 6s to a single held chord."*
- **(b) Dynamic arc** (montage/launch): structure the prompt as *intro → build → peak on the hero
  beat → sustained drive → resolve*, then **verify the rendered loudness curve** matches (e.g.
  −25 dB intro → −11 dB peak → −34 dB tail).

**Music API gotchas:** minimum length floor **~42 s** (request more, trim); **HTTP 400
`bad_prompt`** if you name a brand/artist to imitate — describe the *sound* instead; the track must
be **≥ the video length**.

### Mix (VO + ducked bed) — the canonical filtergraph

```
[1:a]atrim=0:{L},asetpts=PTS-STARTPTS,volume=0.30,
     afade=t=in:st=0:d=1.5,afade=t=out:st={L-2.0}:d=2.0[mus];
[mus][0:a]sidechaincompress=threshold=0.045:ratio=7:attack=5:release=280[mduck];
[0:a][mduck]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.97[out]
```

- **Bed levels (linear volume):** `0.30` warm-minimal bed / under-VO reel · `0.24` for a ~5.6 dB
  hotter dynamic track · `0.42` for a demucs-extracted instrumental · `0.9` when music-only.
- **Duck:** `threshold=0.045:ratio=7:attack=5:release=280` (films); a punchier reel used
  `threshold=0.035:ratio=9`.
- **Fades:** music in `st=0:d=1.5`, out `st=(len−2):d=2.0`. **30 ms fades at every source-segment
  boundary** to kill cut pops (`afade=t=in:d=0.03` + `afade=t=out:d=0.03`).
- **Master:** `alimiter=limit=0.97`; deliverables `loudnorm=I=-14:TP=-1.5:LRA=11` (−14 LUFS social
  standard).
- **Sidechain pitfalls:** its output length = the **shorter** of main/key → **pad the VO key** to
  full length or the music truncates; and a filtergraph label is **single-use** → `asplit` the VO
  into `[key][mix]`. (See [`scripts/blur_and_mux.sh`](scripts/blur_and_mux.sh).)

### VO placement / gaps

Concatenate per-beat VO with **explicit silence before each beat**, sized to the visual-only action
it covers. Real 8-beat, ~57 s plan (silence before each): `2.30` (logo pre-roll) · `1.40` · `1.70` ·
**`4.60` (typing plays visual-only)** · **`3.20` (build animation)** · `1.60` · `1.70` · `2.40`; tail
`2.80`. Write a `vo_timeline.json` the compositor reads so audio + visuals stay frame-locked.

**Music-only mux:** no captions to burn → stream-copy the video (`-c copy`, no re-encode). Crossfades
force a full re-encode; `xfade` offset for the *k*-th transition = `cumulative_duration − k·T` (`T=0.30s`).

---

## 6. Voiceover

**Engine:** ElevenLabs `eleven_multilingual_v2`. → [`scripts/gen_voiceover.py`](scripts/gen_voiceover.py)

**Voice settings (tune per project):**

| Use | stability | similarity_boost | style | speaker_boost |
|---|---|---|---|---|
| Warm narrator (film) | 0.55 | 0.75 | 0.0 | true |
| Premium launch read | 0.45 | 0.80 | 0.15 | true |

Lower `stability` + a little `style` = more expressive; higher `stability`, `style 0` = calmer.

- **Karaoke timings:** call the `…/with-timestamps` endpoint (returns character-level
  `character_end_times_seconds`) or transcribe the finished VO with Scribe for word-level JSON.
- **Clone a source voice:** demucs two-stem split → take the vocals stem → cut a clean
  single-speaker sample → ElevenLabs Instant Voice Clone → use the returned voice id. Bonus: the
  demucs `no_vocals` stem is a ready instrumental bed (`atempo` to fit).
- **Per-beat scripting:** write VO as named beats, generate each individually so gaps/timing are
  controllable and beats regenerate in isolation.
- **Pacing:** premium reads ~**2 words/sec** with deliberate holds (~62 words ≈ 33 s). Insert a beat
  with SSML `<break time="0.8s"/>`.
- **Never print or commit the API key.**

---

## 7. Captions

- **Word-timed karaoke:** each word reveals at its exact `spoken_start` (`opacity 0→1, y 6→0,
  ~220 ms power3.out`). Every word span sits in its **final position from t=0** (opacity 0) so the
  line never reflows. Card exits when the last word finishes (`y 0→-60, 250 ms power2.in`).
- **Chunked kinetic captions:** ~2–3 words/cue, break on punctuation, right-to-left word reveal
  (`translateX 28→0, 280 ms power3.out`), container crossfade 250 ms with adjacent chunks on
  alternating tracks so they overlap on handoff. Drop captions over b-roll/logo beats via skip-ranges.
- **Legibility on varied backgrounds:** over unpredictable light footage, white gets swallowed → use
  **dark text + white outline** (e.g. a near-black `#17181F` fill + 7px white outline + soft shadow,
  bold, lower third). Over dark/cream films, a charcoal `#1a1a1a` text.
- **Sizing:** longer phrase → smaller (72px for a 9-word two-liner, 80px for a 5-word line, 88px for
  a short card). Keep a caption band (y≈440–640) clear in any motion beneath.
- **`MarginV`** is a safe-zone rule, not taste: vertical-video UI covers the bottom ~25–30%. With
  libass auto-scaling against `PlayResY=288`, `MarginV=90` lands ~30% up on any aspect.
- **No-libass fallback:** if your ffmpeg lacks `subtitles`/`drawtext`, render caption PNGs with PIL
  and `overlay … enable='between(t,s,e)'` → [`scripts/build_captions.py`](scripts/build_captions.py).

---

## 8. Compositing pipeline (ffmpeg)

Strict order (each is a [GOTCHAS.md](GOTCHAS.md) hard rule):

1. **Per-segment extract** (grade + 30 ms fades baked in) → 2. **HDR tone-map** if needed →
3. **lossless `-c copy` concat** → 4. **build master SRT** on the output timeline
   (`out = word.start − seg_start + seg_offset`) → 5. **overlays** (each `setpts=PTS-STARTPTS+{off}/TB`,
   gated `overlay=enable='between(t,off,end)'`, chained) → 6. **subtitles LAST** → 7. **loudnorm**.

Overlay/composite encode: `libx264 -crf 18..20 -preset medium -pix_fmt yuv420p -g 30 -keyint_min 30
-c:a aac -b:a 192k`.

- **Alpha overlays:** `format=yuva420p`, `overlay … eof_action=pass`. Extend a base past source with
  `tpad=stop_mode=add:stop_duration=N` + `apad=pad_dur=N` for an outro runway.
- **Concat of framework-rendered MP4s:** apply `setsar=1` to every input (some renders carry SAR
  `169:160` which concat rejects); framework renders have **no audio** → feed a matched-length
  `anullsrc=channel_layout=stereo:sample_rate=44100` per silent segment.
- **HTML `<video>` embeds:** re-encode the source clip with **tight keyframes `-g 30 -keyint_min 30`**
  (default sparse keyframes break per-frame `currentTime` seeking → black frames near clip end). And
  **rename the file after re-encoding** (`clip.mp4`→`clip_v2.mp4`) — Chromium caches by filename.

---

## 9. Self-evaluate (before showing anyone)

On the **rendered output** (not sources): sample frames at **every cut boundary** (±1.5s) and look
for a flash/jump, a caption hidden behind an overlay, or an overlay showing the wrong frame; render
the **waveform** + check **loudness** for pops/clipping; `ffprobe` the **duration** vs the plan.
Cap at 3 fix→re-render→re-eval passes, then flag what's left rather than looping.
