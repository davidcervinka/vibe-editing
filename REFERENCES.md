# Launch-video reference library

A curated set of **product-launch videos worth studying**, plus the archetypes and tone rules
distilled from them. This is where the "what should a launch video actually look like" decisions come
from before a single clip is cut.

> Method: a structural analysis of a major AI lab's public launch feed (`@claudeai` on X,
> ~133 posts across Feb–May 2026, with 10 launch videos pulled for duration/aspect/engagement).
> These are **public posts** linked for study — no video files are redistributed here. Durations and
> aspect ratios are verified from metadata; pacing/cut claims are inferences (see the caveat at the
> bottom). Refresh instructions are included so the patterns can be re-derived later.

---

## The reference films (study these)

The 10 launch videos analyzed in detail — each is a clean worked example of its archetype:

| # | Launch (paraphrased) | Dur | Aspect | Archetype | Views* | Link |
|---|---|---|---|---|---|---|
| 1 | Scheduled tasks land in the product | 0:25 | 16:9 | A single-feature demo | 8.2M | [x.com](https://x.com/claudeai/status/2026720870631354429) |
| 2 | Spreadsheet + slides sync context across files | 1:36 | 16:9 | B multi-step workflow | 12.5M | [x.com](https://x.com/claudeai/status/2031790754637717772) |
| 3 | Charts & diagrams in chat | 1:19 | 16:9 | B multi-step workflow | 11.8M | [x.com](https://x.com/claudeai/status/2032124273587077133) |
| 4 | Conference returns (teaser) | 0:11 | 1:1 | C event teaser | 1.9M | [x.com](https://x.com/claudeai/status/2034308517964956051) |
| 5 | Security feature (public beta) | 0:50 | 16:9 | A single-feature demo | 4.9M | [x.com](https://x.com/claudeai/status/2049898739783897537) |
| 6 | Livestream reminder | 0:18 | 4:5 | C event teaser | 1.6M | [x.com](https://x.com/claudeai/status/2050252933866930339) |
| 7 | Industry agent templates | 1:03 | 16:9 | B multi-step workflow | 13.6M | [x.com](https://x.com/claudeai/status/2051679629488865498) |
| 8 | "Tiny computers" compilation | 0:10 | 4:5 | D compilation showcase | 531K | [x.com](https://x.com/claudeai/status/2054257324278132893) |
| 9 | Self-hosted sandboxes (live from event) | 0:15 | 16:9 | E live-from-event | 2.3M | [x.com](https://x.com/claudeai/status/2056645485696315581) |
| 10 | Hackathon recruitment | 0:07 | 4:5 | C event teaser | 1.6M | [x.com](https://x.com/claudeai/status/2045248224659644654) |

\* Engagement at time of scrape — a rough signal of which formats carry, not a target.

Other high-signal launches in the window (image/text leads, no video, but good thread structure):
Opus model release ([13.9M](https://x.com/claudeai/status/2044785261393977612)), a design product by the
lab's research group ([63.7M](https://x.com/claudeai/status/2045156267690213649)), a compute-partnership
note ([23.9M, text-only](https://x.com/claudeai/status/2052060691893227611)).

---

## The five archetypes (aspect ↔ duration ↔ purpose)

Pick the archetype; it locks the spec.

| # | Archetype | Aspect | Duration | Cuts | Use when |
|---|---|---|---|---|---|
| **A** | Single-feature demo | 16:9 | 25–50s | 4–8 (~3–6s each) | One feature, one screen recording, one payoff |
| **B** | Multi-step workflow | 16:9 | 60–96s | 10–18 (~4–6s) | Cross-product story; a job finished end-to-end |
| **C** | Event teaser | 1:1 | 8–12s | few | Conference/livestream/hackathon — date + place + register |
| **D** | Compilation showcase | 4:5 | ~10s | many/fast | Multiple wins/outputs cut together — proof through variety |
| **E** | Live-from-event | 16:9 | 15–20s | few | Launching *on stage* — punchier than A |

**Two rules behind the matrix:**
1. **Horizontal (16:9) = demo. Vertical/square (1:1, 4:5) = event or showcase.** Don't mix — a demo in
   4:5 reads like a TikTok and undercuts the product; an event teaser in 16:9 reads like a webinar promo.
2. **Complexity → duration.** Single feature 25–30s · single feature + full demo 50s · cross-product
   workflow 60–90s · pure event/recruitment under 20s.

### Beat sheet — Archetype A (single-feature demo, ~35s default)
```
0–3s    Cold open: wordmark + the headline as one line of on-screen text (= the post's headline).
3–8s    Cut to real UI. Cursor moves like a person. Establish ONE context (no feature carousel).
8–18s   The setup: the user does the thing (clicks / types / uploads). Captions name it plainly.
18–28s  The payoff: the output appears. This is the freeze-frame that tells the whole story.
28–33s  Optional "you can also…" (only if budget; cutting at 28s is correct).
33–35s  Static end card: product name + availability + short URL. Same wordmark. No sting.
```

### Beat sheet — Archetype B (multi-step workflow, ~75s default)
```
0–10s   Setup: who is this, what job are they finishing, the "before" (tabs juggled, format stuck in).
10–25s  Step 1: first feature does its part — show input → immediate output (don't narrate).
25–40s  Step 2: handoff to the second surface — CONTEXT CARRIES (work doesn't restart). The proof point.
40–55s  Step 3: often an external surface (doc/deck/sheet/dashboard/export). Job approaches done.
55–65s  The "done" moment: deliverable appears, held ~3s so the viewer feels it.
65–75s  End card: products involved + availability + short URL.
```
**Unmissable rule for B:** the viewer must feel **context is preserved between steps** — the same
thread visible in the sidebar across cuts, data referenced from step 1 in step 2, a persistent
cursor. Without that signal you've made three short videos badly stuck together.

---

## Structural principles

- **The thread is the launch; the video is the headline image inside post 1.** Write the lead post as
  if no one sees the video — the news must be in the words. Replies do the telling: post 1 = opener +
  one-sentence news + video; post 2–3 = one concrete feature/number each; final = availability + CTA.
- **Videos usually carry no voice-over** — the post copy *is* the voice-over; captions carry the video.
- **One news per launch.** Two things shipping the same day = two threads, two hours apart, separate
  videos. (Exception: sub-features that only make sense together share a thread as replies.)
- **The product is the still life; the user is the cursor.** Don't give the product a personality/VO.
- **Static end cards.** Wordmark doesn't animate; no sting. Calm authority over flourish.

## Tone (the calm-declarative voice)

- **State the news, don't sell it.** Verbs that carry weight: *is, ships, runs, returns, opens, scans,
  syncs, connects, reads, writes, exports, imports, generates, schedules, watches, lets, gives,
  supports, includes, costs, takes [N minutes].* Avoid *unlocks / empowers / supercharges /
  revolutionises / reimagines / accelerates / enables* as headline verbs.
- **Concrete beats abstract.** "A 30-minute interview, a map, and a business case" > "process
  intelligence." If a line could be true of any vendor, it isn't carrying weight.
- **Numbers in the body, not the headline** — a declarative news beat, *then* the number as proof
  (unless the number *is* the news).
- **Almost zero emojis, zero hashtags.** One 🎉/🚀/✨ and it reads like every other AI startup —
  which is the whole thing calm-declarative avoids.
- **No hype adjectives in the lead** — strike *blazing, world-class, cutting-edge, next-gen,
  revolutionary, game-changing, seamless, intelligent, AI-powered, powerful, robust, enterprise-grade,
  end-to-end, comprehensive.* Keep an adjective only if it's literally load-bearing (*new, public,
  generally available, regulated, validated, board-ready*).
- **Brand the product, not the maker** — prefix the brand (`<Brand> Code`, `<Brand> Security`),
  lowercase code-named features ("auto mode", "routines"), and use a "by <Maker> Labs" sub-brand to
  signal something is early.

## Opener formulas (fill in your own product)

1. **`Introducing <Name>: <what it is in one clause>.`** — strongest; reserve for brand-new products.
2. **`New in <Product>: <feature>. <one sentence of user value>.`** — the workhorse for additions.
3. **`<Product> is now <available / GA / on plan X>. <what that unlocks>.`** — GA / expansion / rollout.
4. **`Live from <event>: <launch>.`** — on-stage/event launches (Archetype E).
5. Event teaser (C): just **date + place + register** — no product pitch.

Lead length target ~100–250 characters, and it must stand alone if the video doesn't autoplay.

---

## Where this reel fits

The reel in this repo is a **Compilation/showcase (D-ish) → single-product hybrid**: a split-screen of
four product-motion beats, a "type a request → it builds" demo beat, and a sign-off card. If you were
posting it as a formal launch, you'd wrap it in the four-part thread above and lead with a
calm-declarative one-liner.

---

## Refreshing the analysis (re-derive the patterns later)

The original data came from Apify actors against the public feed:
1. `apidojo/twitter-profile-scraper` — `twitterHandles=["<handle>"]`, a start/end window,
   `maxItems=200`, `getReplies=false`. Filter to top-level posts (`isReply=false`) = the lead posts.
2. Take the top 10–15 by views; run a video-metadata actor (e.g.
   `igview-owner/twitter-x-video-downloader`) on those URLs, ~10 at a time.
3. Re-derive the archetype matrix + opener distribution. If a new archetype appears (e.g. a 9:16
   vertical demo), add it as Archetype F.

**Caveat:** durations/aspect ratios are verified from metadata; the pacing, cut-count, and end-card
claims are inferences from duration-vs-complexity + the lab's consistent brand identity, not
frame-by-frame review. The tone rules are observation of public posts, not a published brand book —
re-check before adopting wholesale.
