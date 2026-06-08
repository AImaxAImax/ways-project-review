# WAYS project handoff: crons, workflows, and philosophy

This is the human/context layer for external agents reviewing the WAYS repo.

## Repo

- GitHub: <https://github.com/AImaxAImax/ways-project-review>
- Local source review copy: `/mnt/c/dev/ways-project-review-github`
- Original live working tree: `/mnt/c/dev/curious-shorts`
- WAYS = **Wait, Are You Serious?**, a weird-fact short-form video factory for YouTube Shorts/Reels/TikTok-style vertical videos.

## What is in this review bundle

Included:

- Pipeline code and tests.
- Production packets, idea cards, lane maps, manifests, QA notes, and publish-gate docs.
- WAYS ops docs and Discord/Kanban contracts.
- Current local ComfyUI workflow JSON references.
- Reviewer docs under `docs/`.

Excluded intentionally:

- Generated videos, images, audio, contact sheets, and preview media.
- Model weights: `.gguf`, `.safetensors`, `.ckpt`, `.pt`, `.pth`.
- OAuth tokens, `.env` files, credential files, and credential-like filenames.
- Runtime caches and temporary files.

## Start-here docs for agents

1. `README.md`
2. `docs/AGENT_REVIEW_BRIEF.md`
3. `docs/CRONS_AND_AUTOMATION.md`
4. `docs/WORKFLOWS_AND_PHILOSOPHY.md`
5. `ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md`
6. `ops/ways-video-lab-discord/PLATE_QC_DASHBOARD_CONTRACT.md`
7. `ops/ways-video-lab-discord/DISCORD_QA_INTERACTION_CONTRACT.md`
8. `templates/wan22-a14b-i2v-short-template/README.md`

## Verification already run on the review bundle

- `PYTHONPATH=. pytest -q`
- Result at bundle creation: `33 passed`.
- Tracked heavy media/model file check: 0 tracked files with heavy media/model extensions.
- Literal secret-pattern scan: 0 hits for common literal key formats.

## Active Hermes crons snapshot

Snapshot was taken from `cronjob(action="list")` on 2026-06-08.

### WAYS-specific crons

#### `b7643810a233` — WAYS five-video automation floor

- State: enabled, scheduled.
- Schedule: every 120 minutes.
- Delivery: origin, the WAYS Discord project thread.
- Workdir: `/mnt/c/dev/curious-shorts`.
- Skill: `short-form-video-production`.
- Toolsets: terminal, file, skills.
- Purpose: operate the WAYS video factory and keep at least five WAYS videos active/ready across the pipeline.
- Last status in snapshot: ok.

#### `adcfddd15e55` — WAYS iterative still-frame builder until complete

- State: paused/disabled.
- Schedule: every 20 minutes.
- Repeat usage at snapshot: 7/30.
- Workdir: `/home/joshn/.hermes/shorts-autoresearch`.
- Skill: `short-form-video-production`.
- Toolsets: terminal, file, browser, vision.
- Purpose: continue an older WAYS image-first still-frame pipeline until queued stills are produced and strict-gated.
- Reason it is paused: WAYS production moved toward a more explicit board/QC workflow and local Wan2.2 I2V lane.

### Adjacent/system crons that affect WAYS

#### `c6944e2bb344` — Kanban board watcher, keep actionable boards moving

- State: enabled.
- Schedule: every 5 minutes.
- Mode: script-only, `no_agent=true`.
- Script: `kanban_board_watcher.py`.
- Purpose: safely runs Hermes Kanban dispatch so active boards keep moving.

#### `a41265792a9d` — Hindsight memory watchdog

- State: enabled.
- Schedule: every 5 minutes.
- Mode: script-only.
- Script: `hindsight_watchdog.py`.
- Purpose: keep local Hindsight memory services healthy.

#### `5a518e6aec61` — Discord to Hindsight daily incremental catch-up

- State: enabled.
- Schedule: daily at 03:15.
- Mode: script-only.
- Script: `discord_hindsight_incremental_catchup.py`.
- Purpose: persist durable Discord project context into Hindsight.

### Non-WAYS crons present in the same Hermes environment

#### `1ed2e6d776a7` — Gmail inbox cleanup

- State: enabled.
- Schedule: 07:00 and 19:00 daily.
- Last status in snapshot: ok.
- Note: had a Discord delivery error in the snapshot: Unknown Channel.

#### `b739b9b58991` — Weekly home/property second-brain check-in

- State: enabled.
- Schedule: Fridays at 09:00.

#### `babe8dbeffc0` — BroadcastBench 30-day indexation follow-up

- State: enabled, one-shot.
- Scheduled for 2026-06-15 09:00.

## WAYS operating philosophy

### Quality bar

- Private draft bar: **8-9/10**.
- Public publish bar: **9/10+ plus explicit Josh approval**.
- Default upload state is always **private**.
- Public publish requires explicit human authorization.
- Human phone-size review beats VLM scores, contact sheets, and agent confidence.

### Core creative principle

Build each short as a retention system, not as disconnected script/video/caption pieces. The hook, VO, visual, motion, caption timing, and audio should all reinforce one clear payoff.

Key phrase: **say dog, see dog**. If the VO names a dog, the visual must literally show a dog or a clean, obvious proxy. Do not hide the claim in abstract visuals.

### Topic/lane philosophy

The safest WAYS topics have strong visual priors:

- shark
- owl
- octopus
- axolotl
- crow
- frog
- jellyfish
- other recognizable animals or natural phenomena

Known weak lane:

- internal anatomy
- process shots
- diagrammatic explanations
- precision mechanisms that require exact visual logic

Those should either be avoided, handled with motion graphics/compositing, or treated as a deliberate cohort test, not as the main factory lane.

### Current best local ComfyUI lane

Current best proven local lane:

- **Wan2.2 A14B GGUF Lightning I2V**.
- Template: `templates/wan22-a14b-i2v-short-template/`.
- Workflow included in the review bundle: `external_workflows/comfyui/wan2_2_a14b_gguf_lightning_i2v_smoke.json`.
- Important local setting: the working recipe uses `wan_2.1_vae.safetensors` for this lane in the local setup.
- Use for source-preserving realistic I2V from strong still plates.

Known alternatives:

- LTX 2.3 exists locally and may be stronger for cinematic T2V motion, but previous WAYS animal I2V tests smeared subject anatomy compared with Wan2.2.
- Hunyuan workflow files exist but are not a proven production lane for WAYS here.
- Wan T2V 14B exists locally but is riskier for animal subjects because it does not preserve approved source plates as tightly.

## Gate model

Canonical spec: `ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md`.

### Gate 1 — Script

Agent/automated. The hook must land in the first 1-2 seconds. One spoken claim per beat. Safe sourced fact. Kid-friendly, not childish.

### Gate 2 — Plate QC

Human gate. VLM score is advisory. Josh approves/denies each plate and confirms lane assignment.

This is the highest-leverage gate because plate quality determines final video quality. I2V cannot reliably rescue a weak plate.

### Gate 3 — Render QA

Automated. Checks for expected clips, catastrophic morphing, anatomy dissolution, generated text/logos, and lane failures.

### Gate 4 — Spec/Assembly QA

Automated. Checks vertical spec, H.264/AAC, duration, caption readability, no double captions, no non-caption text, visual reset, ffprobe JSON, contact sheet.

### Gate 5 — Human final review

Human gate. Josh reviews a phone-size master, scores against the 8-9/10 private draft bar and 9/10+ public publish bar.

### Gate 6 — Public publish authorization

Human gate. Explicit human “publish public” required. Private is default.

## Agent boundaries

Agents can run unattended through:

- Gate 1 script work.
- Plate generation until Gate 2 queue.
- Render and assembly after plate approval.
- Gate 3 and Gate 4 automated checks.

Agents must halt for:

- Gate 2 plate approve/deny and lane confirmation.
- Gate 5 phone-size final review.
- Gate 6 public publish authorization.

Agents must never:

- Spend metered/paid credits without explicit approval.
- Mark a video “finalist” without human phone-size review.
- Publish public without explicit human authorization.
- Substitute I2V trickery for weak plates.

## Current performance lessons

- Strong-prior animal/nature clips are the clearest lane.
- Shark/frog/shrimp style learnings are more useful than wombat for current format direction.
- Wombat-style process/internal-object precision is a known weak lane and should not define the channel format.
- Topic queues intentionally emphasize recognizable animals and facts that can be shown literally.

## Review questions for external agents

1. Are the QC gates enforceable from the current code and artifacts?
2. Are any scripts unsafe around public publish boundaries?
3. Are secrets and generated media properly excluded?
4. Is the factory state machine coherent enough to automate at volume?
5. Where should tests be added before more automation?
6. Which one-off scripts should be promoted into reusable modules?
7. Are there places where generated media outputs are masking weak source or QA logic?
8. Is the WAYS automation strict enough to prevent low-quality uploads?

## Suggested review prompt

```text
Review this repo as an external engineering/automation agent.

Start with:
- docs/AGENT_REVIEW_BRIEF.md
- docs/CRONS_AND_AUTOMATION.md
- docs/WORKFLOWS_AND_PHILOSOPHY.md
- docs/WAYS_PROJECT_HANDOFF_FULL_RUNDOWN.md
- ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md
- tools/ways_qc_gate_runner.py
- tools/ways_factory.py
- tools/ways_public_publish.py
- templates/wan22-a14b-i2v-short-template/README.md

Focus on:
1. Are the QC gates enforceable from the current code/artifacts?
2. Are publish/public-upload boundaries safe?
3. Are secrets and generated media properly excluded?
4. Is the state machine coherent enough to automate at volume?
5. Which scripts should be modularized or tested before scaling?
6. Where could generated media artifacts hide weak source/QA logic?
7. What should be changed to make this a reliable WAYS video factory?
```
