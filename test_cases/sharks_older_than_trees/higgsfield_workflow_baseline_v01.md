# Higgsfield-first short-form workflow baseline v01

## What changed

Higgsfield MCP is now connected and authenticated. Available account state at setup time:

- Plan: Ultra
- Credits: ~2996.72
- MCP tools discovered: 24
- Recommended video models for our use case:
  - `seedance_2_0` — reference-driven video, strong identity preservation, 4–15s, 9:16, image/start/end/video/audio refs.
  - `kling3_0` — cinematic multi-shot, motion transfer, audio sync, 3–15s, 9:16, start/end image refs.
  - `minimax_hailuo` — natural physics/emotion, 6/10s, useful challenger lane.
  - `seedance_1_5` / `kling2_6` — backup/challenger lanes.
- Useful MCP primitives:
  - `models_explore` — choose/check model constraints before generating.
  - `media_upload` + `media_confirm` — upload local stills/video/audio into Higgsfield.
  - `generate_image` — premium still generation/polish when local/ChatGPT/manual lane is not enough.
  - `generate_video` — actual image-to-video motion.
  - `job_status` / `job_display` / `show_generations` — poll, inspect, and reuse results.
  - `show_reference_elements` — persistent reusable environments/props/characters per workspace.
  - `show_characters` — trained Soul identities only when we explicitly need reusable human/character identity.
  - `balance` / `transactions` — credit discipline.

## New operating principle

Do not use Higgsfield to blindly make a whole video. Use it as the premium motion + polish lane after the story and literal visual payload are locked.

The baseline is now:

1. Script and shot map first.
2. Literal visual payload per beat: “say dog, see dog.”
3. Still frames/style frames must be distinct before motion.
4. Upload only held frames to Higgsfield.
5. Run a small model bakeoff on hard shots.
6. Select a house motion model/preset.
7. Batch only after the winning lane proves itself.
8. Assemble locally with narration, captions, sound, and final pacing.

## Standard project folder structure

```text
project/
  production_brief.md
  script_v##_recommended.txt
  shot_map_v##.md
  prompts_and_metadata.json
  assets/
    stills_raw/
    stills_selected/
    higgsfield_uploads/
    higgsfield_downloads/
  outputs/
    rough_cuts/
    contact_sheets/
    final_exports/
  reviews/
    still_reviews/
    motion_reviews/
  scripts/
    upload_to_higgsfield.py
    render_rough_cut.py
    make_contact_sheet.py
```

## Stage 0 — Creative lock

Inputs:
- topic
- target runtime
- audience/tone
- script

Output:
- `script_v##_recommended.txt`
- `shot_map_v##.md`

Rules:
- Every line gets a visible noun/action/setting.
- If a line says shark, fossil, tree, apple, squirrel, kid, aquarium, timeline, etc., the frame must literally show it or show its deliberate absence.
- Avoid seven variations of the same hero subject.

For the sharks short, the revised shot jobs are:

1. Ancient ocean shark — hook.
2. Fossil proof close-up — evidence.
3. Apple/squirrel/nut gag — future things, not here yet.
4. Deep-time rock/timeline — age scale.
5. First weird forests/land plants — later arrival.
6. Modern kid at aquarium — today connection.
7. Lone survivor shark — emotional close.

## Stage 1 — Still frame lane

Goal: make each shot visually distinct before any motion spend.

Preferred hierarchy:

1. Use existing strong GPT Image/selected frames if they already clear the bar.
2. Use Higgsfield `generate_image` for premium polish or missing frames.
3. Use local ComfyUI only for controlled tests, masks, guides, or layout probes.

Acceptance bar for still frames:
- 9:16 mobile readable.
- One clear idea per frame.
- Premium enough that motion would be worth spending credits on.
- Distinct setting/composition from adjacent shots.
- No caption needed to understand the main visual beat.

## Stage 2 — Upload + reference registry

For held stills:

1. `media_upload` with filenames.
2. PUT local bytes to presigned upload URLs.
3. `media_confirm(type='image', media_ids=[...])`.
4. Store returned media IDs in `prompts_and_metadata.json`.

For reusable items:
- Use `show_reference_elements(action='create')` for recurring props/environments/characters if the video series will reuse them.
- Use `show_characters(action='train')` only for reusable identity models with 5–20 refs, not for one-off animals/props.

## Stage 3 — Motion bakeoff, not full batch

Run the first bakeoff on 3–4 hard shots only:

- Shot 1: ancient shark swimming through prehistoric ocean.
- Shot 3: apple/squirrel/nut gag, minimal hallucinated forest risk.
- Shot 6: kid at aquarium, reflections/water motion.
- Shot 7: final survivor shark, cinematic closer.

Default test settings:

### Lane A — Seedance 2.0

Use when identity preservation and restrained reference-driven motion matter most.

- `model: seedance_2_0`
- `aspect_ratio: 9:16`
- `duration: 4` or `5` seconds for tests
- media role: `start_image` or `image`
- prompt: concise physical motion, preserve composition, no morphing.

### Lane B — Kling 3.0

Use as cinematic challenger when shot needs bolder natural motion or multi-shot feel.

- `model: kling3_0`
- `aspect_ratio: 9:16`
- `duration: 5` seconds
- media role: `start_image`
- `sound: off` unless explicitly testing native audio.

### Lane C — Minimax Hailuo

Use as natural-physics challenger for water, animals, subtle environmental motion.

- `model: minimax_hailuo`
- start image only unless end frame is deliberately designed.

## Stage 4 — Motion prompt template

```text
Preserve the exact image identity, composition, subject design, and art style.
Create subtle natural motion only: [specific motion].
Camera: [locked / slow push / gentle drift].
Keep all important objects visible and stable.
Do not add new trees, humans, logos, text, extra animals, gore, attack behavior, or surreal morphing.
No warping, melting, flicker, or changing anatomy.
Vertical 9:16 cinematic educational short.
```

Example shark prompt:

```text
Preserve the exact prehistoric shark design and ancient ocean composition from the reference image. The shark glides forward slowly with subtle tail and fin movement. Tiny particles drift in the water, light rays ripple gently, and the camera makes a very slow cinematic push-in. Keep the shark calm and majestic, not attacking. Do not add modern objects, divers, text, gore, extra animals, or trees. No morphing, melting, flicker, or anatomy changes. Vertical 9:16 premium natural-history short.
```

## Stage 5 — Review rubric

Each generated clip gets scored 1–5:

1. Identity preserved from still.
2. Motion is real and specific, not just Ken Burns.
3. No AI wobble/melting/flicker.
4. Literal beat still reads on mute/mobile.
5. Premium enough for final channel quality.
6. No forbidden additions.

Decision rule:
- 3/4 bakeoff clips score 4+ → use Higgsfield as primary motion lane.
- 2/4 score 4+ → use Higgsfield selectively for hero shots only.
- <2/4 score 4+ → return to still-frame motion/local compositing and sound design.

## Stage 6 — Final assembly

Higgsfield makes clips; local pipeline still owns the final edit.

Local assembly responsibilities:
- narration
- captions
- timing
- sound design
- music bed
- clip trims
- transitions
- final 1080×1920 export
- contact sheet/QA

No final should be accepted until:
- ffprobe verifies duration/resolution/fps.
- captions are not cropped.
- first 2 seconds hook visually reads.
- every shot is visually distinct.
- user can watch once without needing explanation.

## Immediate next move for current sharks short

1. Upload the four bakeoff stills: Shot 1, Shot 3, Shot 6, Shot 7.
2. Generate one Seedance 2.0 clip for each.
3. Generate one Kling 3.0 challenger for the best/hardest two shots.
4. Build a side-by-side motion review sheet/video.
5. Pick the house model for the rest of the short.

Do not animate all seven shots until the bakeoff proves the motion lane.
