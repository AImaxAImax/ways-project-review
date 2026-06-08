# WAYS workflows, philosophy, and context for external review agents

This document captures project context that may not be obvious from code alone.

## Project identity

WAYS = **Wait, Are You Serious?** short-form educational video channel. The format is vertical Shorts/Reels/TikTok-style content built around weird, counterintuitive facts about animals/nature/science.

## Quality bar

- Private draft bar: **8-9/10**.
- Public publish bar: **9/10+ plus explicit Josh approval**.
- Never publish public by default. Default upload state is private.
- Human phone-size review is authoritative. Contact sheets, VLM scores, and agent judgments are advisory.
- Do not upload drafts unless they are strong enough for the gate.

## Core creative principle

Build the short as one retention system, not as separate script/video/caption pieces. The hook, VO, visual, motion, caption timing, and audio all need to reinforce one clear payoff.

Important language used in this project:

- **Say dog, see dog:** if the VO says a dog, the visual must literally show a dog or a clean obvious proxy. Do not hide the claim in abstract visuals.
- **Strong visual prior:** recognizable subjects like shark, owl, octopus, axolotl, crow. These are safest for local I2V.
- **Process-shot failure mode:** internal anatomy/process/diagram beats often fail photoreal I2V and should use motion graphics/compositing or be avoided.
- **One variable per cohort:** format experiments should vary one thing at a time so YouTube retention data is interpretable.

## Current model/lane philosophy

### Winning local video lane

The current best proven local Comfy lane for WAYS is:

- **Wan2.2 A14B GGUF Lightning I2V**
- Workflow: `external_workflows/comfyui/wan2_2_a14b_gguf_lightning_i2v_smoke.json`
- Original source outside this repo: `C:\devj-engine\comfyui\workflows\wan2_2_a14b_gguf_lightning_i2v_smoke.json`
- Important VAE override: use `wan_2.1_vae.safetensors`, not `wan2.2_vae.safetensors`, for this workflow in this local setup.
- The saved template is `templates/wan22-a14b-i2v-short-template/`.

Use this lane for source-preserving realistic I2V from premium still plates.

### Known alternatives

- LTX 2.3 exists locally and may be better for large cinematic T2V motion, but previous WAYS animal I2V tests smeared subject anatomy compared with Wan2.2.
- Hunyuan workflow files exist but are not a proven production lane in this local setup.
- Wan T2V 14B exists locally but is riskier for WAYS animal subjects because it does not preserve approved still plates as tightly.

## Production gate summary

The canonical gate spec is `ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md`.

1. Gate 1 — Script: automated/agent-authored. Hook lands in 1-2 seconds, one claim per beat, safe sourced fact.
2. Gate 2 — Plate QC: VLM advisory plus **human approve/deny**. This is the most important quality gate.
3. Gate 3 — Render QA: automated check for missing clips, morphing, generated text, lane failures.
4. Gate 4 — Spec/Assembly QA: automated ffprobe/contact sheet/caption/readability checks.
5. Gate 5 — Human Final Review: Josh reviews phone-size master and assigns draft/publish score.
6. Gate 6 — Publish Authorization: explicit human authorization required for public.

The agent can work unattended through automated gates but must halt at Gate 2, Gate 5, and Gate 6.

## Current Discord/project operating surface

Main project thread: `#ways-chat / Let’s use this Chan as the place I talk to you about this project`.
The dashboard is a companion review surface, but the Discord thread is the working decision log.

## Current YouTube OAuth context

YouTube Data + Analytics access is expected through `~/.hermes/youtube_token.json`, copied from the broader token at `~/.verticals/youtube_token.json`. The broader token has upload, force-ssl, readonly, and analytics scopes. Do not commit token files.

## Performance lessons so far

- Shark and frog style strong-prior animal/nature clips are the cleanest lane.
- Wombat-style process/internal/object precision is a known weak lane and should not define the format.
- The topic queue intentionally emphasizes recognizable animals and facts that can be shown literally.
- Plate quality matters more than prompt cleverness. I2V cannot reliably rescue a weak plate.

## Review request for another agent

Useful review questions:

1. Are the QC gates enforceable from the current code/artifacts?
2. Are any scripts unsafe around publish/public upload boundaries?
3. Are secrets properly excluded?
4. Is the factory state machine coherent enough to automate at volume?
5. Where should the project add tests before more automation?
6. Which parts should be split into reusable modules versus one-off scripts?
7. Are there places where generated media outputs are masking weak source/QA logic?
