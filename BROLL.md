# AI b-roll (generative video)

When you need footage you don't have — a cinematic product shot, an abstract transition, an
establishing scene — generate it. Two routes, both fold a rendered clip back into the ffmpeg
pipeline exactly like any other segment.

## Route A — Higgsfield (via MCP)

[Higgsfield](https://higgsfield.ai/) exposes an **MCP server**, so Claude Code can call it directly
in-conversation (no glue code). Relevant tools:

- `generate_image` — a still to seed a shot (or a standalone graphic)
- `generate_video` — text/image → video (the core b-roll tool)
- `generate_audio` — SFX / music beds
- `motion_control` — recast / puppeteer / motion-transfer onto an existing clip
- `reframe` — change a clip's aspect ratio (16:9 ⇄ 9:16 ⇄ 1:1)
- `upscale_video` — enhance to 2K/4K
- `generate_3d`, `outpaint_image`, `remove_background` — supporting ops

**Flow in practice:** ask Claude for the shot → it calls `generate_image` (seed) → `generate_video`
→ downloads the result → you `extract_normalize.sh` it to `1080p@30` → it's just another beat in
the EDL. Because it's MCP, "make me a 4s cinematic push-in on a running shoe on wet asphalt" is a
sentence, not a script.

> Enable the Higgsfield MCP connector in your Claude settings; then it's available to the agent
> like any other tool.

## Route B — RunwayML (via API)

[RunwayML](https://runwayml.com/) has a REST API for image-to-video (Gen-4 / Gen-3). Use it when
you want b-roll in a scripted/headless pipeline. → [`scripts/gen_broll_runway.py`](scripts/gen_broll_runway.py)

```bash
export RUNWAYML_API_SECRET=...
# still + motion prompt → 5s clip
python3 scripts/gen_broll_runway.py seed.png "slow cinematic push-in, shallow depth of field" broll.mp4
```

Minimal REST flow the script implements:
1. `POST /v1/image_to_video` `{model, promptImage, promptText, ratio, duration}` → `{id}`
2. poll `GET /v1/tasks/{id}` until `status == "SUCCEEDED"`
3. download `output[0]`

Runway's video models are **image-to-video** — seed with a real frame, a product still, or a
generated image (`/v1/text_to_image`, model `gen4_image`). Check
[docs.dev.runwayml.com](https://docs.dev.runwayml.com) for the current model ids and version header.

## Which to use

| | Higgsfield (MCP) | Runway (API) |
|---|---|---|
| Invocation | In-conversation, no code | Scripted / headless |
| Best for | Fast iteration, motion-transfer, reframe, upscale | Repeatable pipelines, image-to-video |
| Extras | 3D, outpaint, bg-removal, SFX | text-to-image, character performance |

## Making generated b-roll match the cut

- **Normalize** it (`extract_normalize.sh`) to your `1920×1080@30` spec so it concats cleanly.
- **Grade** it toward the rest of the reel (see [TECHNIQUES.md](TECHNIQUES.md) → grading) — generated
  footage often reads too saturated/clean next to product UI.
- **Keep it short** — 2–4s per generative shot; treat it as an accent, not the story.
- **Match motion direction** — if your cut pushes in, don't cut to a shot that pushes out.
