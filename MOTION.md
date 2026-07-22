# Motion graphics

How the animated overlays, kinetic type, UI mocks, and end cards are made — and folded back into the
ffmpeg cut. Engine-agnostic principles; recipes assume HTML/CSS/GSAP (HyperFrames) but the
easings/durations transfer to Remotion or a PIL PNG sequence.

> Cut/audio/caption craft is in **[TECHNIQUES.md](TECHNIQUES.md)**; the traps are in **[GOTCHAS.md](GOTCHAS.md)**.

---

## The laws

1. **One idea per beat; cut fast.** Avg scene ~1.5s. If a scene says two things, split it.
2. **Never parallel-reveal independent elements** — the eye can't track two new things at once. One
   thing, pause, next thing. Staggered reveals per region; a region resolves before the next moves.
3. **Camera never sleeps** — after a settle, apply a slow push-in for the whole hold (`scale 1→1.014,
   ease "none"`, on an *inner* wrapper so transforms don't fight). Static = death.
4. **Payoff-sync to narration** — a reveal lands *on* its spoken word: slot-local time =
   `master_word_start − slot_offset`, and start the tween `reveal_duration` earlier so it *lands* on
   the word. Lead ~0.2s ahead on punchlines.
5. **Hold the hero shot** — logo reveal ~1.5–2s of stillness; outro/CTA holds 4–6s. Kinetic chaos →
   calm = catharsis.
6. **Motion bridges cuts** — hard cuts with no motion feel cheap; give transitions a whip/blur trail,
   or a shared held background across the seam.
7. **Every timeline fills its slot** — end each GSAP timeline with a no-op anchor
   `tl.to({}, {duration: SLOT}, 0)`, or the framework black-flashes when `timeline.duration() < data-duration`.

---

## Easing & duration tokens

**Never `linear`** except a slow ambient drift.

```
--ease-reveal   power3.out     reveals (content pop, word reveal) — crisp decel
--ease-settle   expo.out       big fly-in settles — long decel, "lands flat"
--ease-exit     power2.in      exits/handoffs into a cut — accelerate away
--ease-snap     power4.out     short snappy entrances
--ease-spring   back.out(1.2–1.6)  deliberate overshoot (use sparingly)
--ease-glide    power2.inOut / power4.inOut   cursor glides, scene push/zoom
--ease-ambient  sine.inOut     loops/breathing;  "none" for constant drift

--dur-micro   0.15–0.20s      --dur-snap    0.30–0.50s
--dur-reveal  0.50–0.80s      --dur-settle  1.30–1.90s
--dur-exit    0.25–0.38s      --dur-ambient 2–4s (or WIN−2.4s)

stagger-char  0.04–0.08s      stagger-word  0.12–0.18s
type-speed    ~28ms/char (+ deterministic jitter, +0.05s after punctuation)
push-in       scale 1→1.014, ease none, whole hold
exit-lead     complete 0.05s BEFORE the window ends
```

PIL/PNG helper easings (for the no-browser path):
```python
def ease_out_cubic(t):     return 1 - (1 - t) ** 3            # single reveals
def ease_in_out_cubic(t):                                     # continuous draws
    return 4*t**3 if t < 0.5 else 1 - (-2*t + 2)**3 / 2
```

Use **≥3 different eases per scene**; velocity-match at beat seams (a velocity discontinuity reads as
a stall). Word-reveal "carrier" pattern: first word carries a 360px slide (`expo.out 0.33s`), tail
words decay `360→120→60→25→12px` (`power2.out 0.20s`). Snap tween end-times to `1/fps` multiples
(steep eases alias at sub-frame boundaries).

---

## Kinetic type & UI motion

- **Text reveal / glide** — per-word span fading up from an offset as spoken:
  `fromTo(word, {opacity:0, x:28}, {opacity:1, x:0, duration:0.28, ease:"power3.out"}, wordStart)`.
- **Skeleton → data pop** — `to(sk,{opacity:0,duration:0.28},T)` then
  `fromTo(real,{opacity:0,y:8},{opacity:1,y:0,duration:0.35,ease:"power3.out"},T+0.05)`.
- **Counters** — tween a proxy, format on update (deterministic, not wall-clock); set
  `font-variant-numeric: tabular-nums` so digits don't jitter width.
- **Typewriter — "center on the full string width" trick** (the fix for text sliding as it grows):
  1. Size the typed container to the **final string width** up front; each char is a `<span>` at
     `opacity:0`, revealed one at a time — text never reflows.
  2. Keep a **hidden, never-transformed measuring copy** off-screen; measure each char's rect there
     for caret positions (re-measure on `document.fonts.ready`).
  3. ~28 ms/char with **precomputed deterministic jitter** (e.g. `(((i*37)%7)-3)*0.0015`), + a
     `0.05s` pause after punctuation. Caret is a timeline-driven 2px block, not CSS animation.

**Anti-list (what looks bad):** linear easing (except drift); parallel reveals; text that reflows
while typing; digits that change width; full-screen gradients on dark (H.264 banding → use solid bg +
localized radial glow); the `transparent` keyword in gradients (use `rgba(r,g,b,0)`); hard cuts with
no bridging motion; frozen final frames; `Math.random()`/`Date.now()` in a render loop (breaks
determinism — seed it or precompute).

---

## Authoring engines — pick per slot

| Engine | Use when |
|---|---|
| **[HyperFrames](https://github.com/heygen-com/hyperframes)** (HTML/CSS/GSAP → deterministic capture) | **Default.** Paste real product HTML/CSS and animate it; agent-driven; no build step; alpha overlays. Apache-2.0, Node 22+. |
| **[Remotion](https://www.remotion.dev/)** (React/TSX) | You already have a React codebase/component library to reuse, or want its Lambda distributed rendering. |
| **PIL / NumPy PNG sequence** | Deterministic static plates, procedural backgrounds, or simple per-frame cards (counters, typewriter, bar reveals) with no browser. |
| **Manim** | Formal diagrams, equations, graph morphs. |

Hybrids are fine (PIL background plate under an HTML layer). None is mandatory.

**HyperFrames in one paragraph:** write `index.html` where the root has `data-composition-id`,
`data-start/width/height` and every timed element has `class="clip"` + `data-start`/`data-duration`/
`data-track-index` (`data-start` can reference other clips: `"intro + 2"`). Register **exactly one
paused GSAP timeline** per composition so the headless-Chrome engine can *seek* it frame-by-frame and
encode identical output every run. Loop: `lint`/`check` → live Studio preview → `render --quality
draft` → **pull a frame per scene and actually look** → `render --quality standard`. Render flags:
`--quality draft|standard|high` = CRF 28/18/15; `--format mp4|mov|webm` where **`mov` = ProRes 4444
with alpha, `webm` = VP9** (but on some toolchains WebM comes back `yuv420p` **without** alpha — use
`mov` for overlays). Apache-2.0, ships a registry (`hyperframes add <block>`).

---

## Folding rendered clips back into the cut

Each motion slot renders independently, then a **frame-exact overlay composite** places it at its
master offset over the base (avoids concat rounding drift; keeps visuals locked to the VO):

```python
# shift the slot's PTS to its master offset, gate to its window
f"[{i+1}:v]setpts=PTS-STARTPTS+{off:.3f}/TB,format=yuv420p[v{i}]"
f"[{prev}][v{i}]overlay=enable='between(t,{off:.3f},{end:.3f})'[o{i}]"
```
Encode with dense keyframes `-g 30 -keyint_min 30` so downstream seeks stay frame-accurate.
**Transparent titles/lower-thirds/callouts:** render the slot as **ProRes 4444 MOV (alpha)** and
`overlay` it straight onto graded talking-head footage — no black matte, alpha composites cleanly.

---

## UI-spec-from-code (faithful animated product mock)

Don't invent a fake UI — **point Claude Code directly at your product's codebase** (the repo, the
design-system package, the component library) and let it read the **real source**. It lifts the UI
elements straight from there and reproduces resolved values:

1. Extract resolved theme hexes (page/card/border/text/button/accent) and the **type scale** as real
   tokens (role → rem/weight/line-height), radii (`6/8/12/16/full`), spacing.
2. Capture component anatomy faithfully: exact padding, icon sizes (16/18/28px), status-pill
   semantics (e.g. "Completed" is a neutral **outline** pill, not green), empty states, real copy.
3. Inline the **real icon set's SVG paths** (e.g. lucide 24×24, stroke-width 2, `currentColor`).
4. **Scale for video:** render everything at a uniform factor inside a fixed card (e.g. a 1560×900
   card at ~1.55×) — keep proportions, multiply px.
5. Port any in-product canvas/particle widget to a **vanilla-canvas version driven off the timeline
   proxy** (deterministic seek), not its own rAF loop.

Result: a `UI-SPEC.md` that owns *content*; the motion spec references it and owns only *choreography*.

---

## Style system for video (a reusable pattern)

- **Two-font display/body split** — a Display cut for headlines/large numerals (≥~24px), a Body/UI
  font for everything smaller; load **locally via `@font-face`** (not a CDN) for deterministic
  offline renders. Counting numerals always `tabular-nums`.
- **Accent sparingly** — a tight symbolic palette (≤5 colors), one **hero accent** used only where it
  earns contrast (eyebrows, chip dots, karaoke fill, count-up highlights, payoff words); secondary
  accents reserved for "spark" moments (success/alert) only. Never neon-flood.
- **Depth without pure black** — shadows tinted toward the deep base, not `#000`; on dark surfaces cap
  element shadow at `rgba(0,0,0,0.35)` + a hairline light border (`0 0 0 1px rgba(light,0.08)`).
  Backgrounds: solid deep base + a few localized radial glows (no full-screen gradients).
- **Logo discipline** — three variants (dark-on-light default, light-on-dark, hero-accent for special
  moments only); never recolor/stretch; respect clearspace.

**Example placeholder palette — replace every value with your own brand:**
```css
/* placeholder values — swap for your brand tokens */
:root{
  --bg:#0E0F14; --surface:#181922; --card:#242634; --border:#363B57; --border-hi:#4A52A0;
  --text:#F4F6FB; --text-mute:#AAB6D2; --placeholder:#7183B8;
  --accent:#F5C84B;            /* HERO accent — sparingly */
  --spark-1:#59D6C4;           /* success / secondary spark */
  --spark-2:#F0705C;           /* alerts only */
}
```
