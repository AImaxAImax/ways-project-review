# WAYS Video Factory: Kanban Board + QC Gate Spec

**Channel:** Wait, Are You Serious? (WAYS)
**Board name:** `ways-video-lab`
**Purpose:** Turn the WAYS pipeline into a repeatable factory that churns out videos at volume without dropping below the quality bar, with QC enforced by automated gates and human review reserved for the two decisions only a human should make.
**Owner:** Josh (human-final on plate approval and publish authorization)
**Agent role:** Run every card through every automated gate unattended; halt and queue for human only at the two human gates.

-----

## 0. Operating principles

1. **Production is the bottleneck, not posting.** The board exists to keep a steady supply of finished videos in reserve, not to maximize throughput at the cost of quality.
1. **Two gates need a human; everything else is automated.** Human touches: (a) plate approve/deny, (b) final phone-size review + publish authorization. The agent does not claim “finalist” or publish public without human sign-off.
1. **One asset/step at a time.** No batch-claiming a whole video as done. Each shot/plate clears its own gate.
1. **Quality bar is non-negotiable.** Private draft bar = 8-9/10. Public publish bar = 9/10+ AND human-approved.
1. **Route shots by visual register, not by model.** Strong-prior subjects (animals, recognizable objects) go to the Wan2.2 I2V lane. Process/concept/diagram beats go to the stylized motion-graphics lane. Photoreal I2V on texture-heavy process shots is a known failure mode and must be gated out *before* render.
1. **Premium plate lane is default.** Higgsfield Unlimited for plate generation. Never spend metered credits without approval.
1. **No finalist claim without human visual review at phone size.** Contact sheets and VLM scores are advisory, not authority.

-----

## 1. Board columns (left to right)

|# |Column                   |What lives here                                     |Owner of the move-out action|
|--|-------------------------|----------------------------------------------------|----------------------------|
|0 |**Idea Pool**            |Raw fact ideas, backlog hooks, research notes       |Agent (triage)              |
|1 |**Script Locked**        |Idea card + locked script that cleared Gate 1       |Agent                       |
|2 |**Plate Generation**     |Active Higgsfield plate generation, hero frame first|Agent                       |
|3 |**Plate QC**             |Plates awaiting VLM score + human approve/deny      |**Human** (Gate 2)          |
|4 |**Render**               |Lane-routed I2V + motion-graphics rendering         |Agent                       |
|5 |**Assembly & Caption**   |Stretch, concat, mux George VO, burn captions       |Agent                       |
|6 |**Auto-QA**              |ffprobe hard checks + VLM contact-sheet gate        |Agent (Gate 3 + 4)          |
|7 |**Human Final Review**   |Phone-size human review against 8-9 / 9+ bar        |**Human** (Gate 5)          |
|8 |**Ready to Publish**     |Approved private draft, scheduled slot assigned     |Agent                       |
|9 |**Published / Scheduled**|Live or queued in YouTube                           |Agent                       |
|10|**Performance Review**   |48-72h retention pulled back, lessons logged        |Agent                       |

### WIP limits (enforce these)

- **Plate Generation + Render combined: max 3 videos in flight.** Quality degrades when too many are mid-render.
- **Plate QC: max 5 plates waiting.** If it backs up past 5, stop generating and clear the human queue first.
- **Human Final Review: max 3 waiting.** Same logic.
- **Ready to Publish buffer target: 10 videos.** This is the reserve that protects the posting streak. Do not let it drop below 5 without flagging Josh.

-----

## 2. Card schema

Every card is one video. Fields:

```yaml
slug: wombat_cube_poop            # unique, matches project folder
hook: "Wombats poop cubes."
core_fact: "Only known animal to produce cube-shaped scat..."
status_column: "Plate QC"
cohort_tag: "batch1-animal"       # for format A/B testing, see §5
test_variable: "hook_style_A"     # the ONE thing this card tests
category_id: 28                   # Science & Technology, standardized
voice: "elevenlabs_george"
lane_map:                         # per-shot lane assignment from Gate 2
  shot01: wan_i2v
  shot04: motion_graphic
draft_score: null                 # filled at Gate 5
publish_score: null
youtube_video_id: null
privacy: private
retention_pct_viewed: null        # filled at column 10
artifact_folder: "project_slug/"  # the artifact contract, see §6
blocking_gate: null               # which gate failed, if parked
```

-----

## 3. The QC gates

Six gates. Four automated, two human. A card cannot advance past a gate it failed; it moves to a **Parked / Rework** swimlane with `blocking_gate` set.

### Gate 1 — Script (automated check + agent-authored)

**Between:** Idea Pool → Script Locked
**Automated checks:**

- Hook payoff lands in first 1-2 seconds (first caption line is the claim).
- One spoken claim per beat; no filler beats.
- Every beat is say-dog-see-dog: if the VO names a thing, a shot can literally show that thing or a clean symbolic proxy.
- Fact has a citable source; safe/exact wording locked (no sensational or false claim).
- Kid-friendly language, not childish.
  **Pass:** all true. **Fail action:** return to Idea Pool with notes.

### Gate 2 — Plate QC (VLM auto-score + HUMAN approve/deny) ⬅ human gate

**Between:** Plate Generation → Render
**VLM auto-score (gemma3:12b via local Ollama), advisory, per plate:**

- Hard block: any detected text, label, number, logo, UI, watermark.
- Caption-safe negative space present.
- Phone-size concept read passes.
- Realistic anatomy, kid-friendly awe (no horror/gore).
- **Animation-friendliness score:** texture density, boundary clarity, register match. Low score = route to motion-graphics lane, NOT Wan I2V.
  **Human action (approve/deny dashboard):** Josh approves each plate and confirms its lane assignment. VLM score is advisory only. Dashboard contract/reference implementation: `ops/ways-video-lab-discord/PLATE_QC_DASHBOARD_CONTRACT.md` and `scripts/plate_qc_dashboard_server.py`.
  **Pass:** human-approved with lane assigned. **Fail action:** regenerate that single plate (Higgsfield), do not proceed with a weak plate.
  **This is the highest-leverage gate. The plate determines final quality; I2V cannot fix a weak plate.**

### Gate 3 — Render QA (automated)

**Between:** Render → Assembly (runs as a mid-run watchdog too)

- All expected clips present for every beat.
- No catastrophic morphing / anatomy dissolution (CLIP/DINO semantic similarity, not SSIM).
- No generated on-frame text or logos.
- Motion-graphic lane clips render clean (no I2V texture artifact on process shots).
  **Pass:** all clips clean. **Fail action:** re-render the failing shot only; if a Wan animal shot still shimmers after a free tuning pass (lower motion, upscaled source, RIFE), escalate that single shot to the paid lane with explicit approval.

### Gate 4 — Spec / Assembly QA (automated, hard checks)

**Between:** Assembly & Caption → Auto-QA exit

- `1080x1920`, vertical 9:16, H.264, 24 fps.
- AAC audio, 48 kHz, present and not clipped (mean ~-15 dB, peak < -0.5 dB).
- Duration within target Shorts range.
- Captions readable at phone size; no double captions; zero non-caption on-screen text.
- Visual reset every 2-3 seconds (no repeated-still fatigue).
- ffprobe JSON + contact sheet generated.
  **Pass:** all hard checks green. **Fail action:** back to Assembly.

### Gate 5 — Human Final Review (HUMAN, phone-size) ⬅ human gate

**Between:** Auto-QA → Ready to Publish

- Josh reviews the captioned master **on a phone**, not desktop.
- Scores against the bar: **8-9/10 = approved as private draft; 9/10+ = eligible for public publish.**
- Confirms each shot maps to its spoken claim, anatomy holds, hook lands in 2s.
  **Pass:** score recorded, approved. **Fail action:** specific shot/caption rejected, returns to the relevant upstream column (not a full rebuild).

### Gate 6 — Publish Authorization (HUMAN)

**Between:** Ready to Publish → Published

- Explicit human “publish public” required. Default upload is `private`.
- Pre-publish checklist: category 28, `selfDeclaredMadeForKids: false`, George voice, mobile caption read, thumbnail (or accept auto-thumbnail if 403).
  **Pass:** Josh authorizes. **Fail action:** stays private draft.

-----

## 4. Automation boundaries (what the agent does solo)

**Agent runs unattended through:** Gate 1 → Plate Generation → (halt at Gate 2) → Render → Assembly → Gate 3 → Gate 4 → (halt at Gate 5).

**Agent halts and queues for human at:**

- Gate 2 (plate approve/deny + lane confirm)
- Gate 5 (phone-size final review)
- Gate 6 (publish authorization)

**Agent never:**

- Spends metered/paid credits (Higgsfield paid lane, escalated paid shots) without explicit approval.
- Marks a video “finalist” or publishes public without human sign-off.
- Replaces a weak plate with I2V trickery instead of regenerating it.
- Publishes to `public`; default is always `private` until Gate 6.

**Overnight loop:** the agent should be able to take everything currently in Script Locked, generate plates, and park them in Plate QC for a morning human review session, then after approval run renders/assembly/auto-QA and park in Human Final Review for an evening session. Two human sessions a day keep the line moving.

-----

## 5. Cohort tagging for format validation (the 50)

The first ~20 published videos are a format test, not just output. Tag every card with a `cohort_tag` and a single `test_variable` so retention data is interpretable.

- **Vary ONE thing per cohort** (hook style, pacing, subject family, caption style). If you randomize everything, the retention data is noise.
- Publish a cohort, pull retention at 48-72h (column 10), weight the next cohort toward what held the ~70% percentage-viewed line.
- **Confounded-video flag:** the wombat is a poor format test (it has the known process-shot history and shipped on the older voice/version). Do not let its numbers decide the format. The shark is the cleaner first read (single weak plate, not three process shots).

Suggested first cohorts:

- `animal-strong-prior` (wombat, shark, mantis shrimp): pure Wan I2V lane, your safest visual register.
- `process-heavy` (anything needing diagram/process beats): tests the motion-graphics lane.
- Keep cohorts from mixing variables.

-----

## 6. Artifact contract (definition of done for a finished card)

Every video card, when it reaches Ready to Publish, must have shipped this folder:

```text
project_slug/
  idea_card.json
  script.md
  storyboard_manifest.json
  lane_map.json
  assets/
    accepted_stills/
    rejected_stills/
  outputs/
    i2v_clips/
    motion_graphic_clips/
    clean_master.mp4
    publish_candidate_captioned.mp4
    discord_preview_captioned.mp4
    captions.ass
    captions.srt
    contact_sheet.jpg
    ffprobe_publish.json
    audio_report.txt
    vlm_plate_scores.json
    PUBLISH_GATE.md          # records draft_score, publish_score, gate results
    youtube_draft_pack/
      youtube_metadata.json   # category 28, made_for_kids false
      description_upload.txt
      thumbnail_candidate.jpg
      youtube_upload_result.json
      youtube_verification.json
```

A card is **not** Done if any artifact is missing or any gate result is absent from `PUBLISH_GATE.md`.

-----

## 7. Posting cadence (column 9 rules)

- **Now (small backlog): 1 public video/day.** Consistency beats burst-then-gap.
- **Once the 50-buffer exists: up to 2/day**, spaced (one morning peak, one evening peak), never two within an hour.
- **Hold a 10-video reserve.** The buffer is what lets you keep a steady cadence without ever shipping a sub-bar video to fill a slot.
- **Schedule, don’t hand-post.** Batch-set publish times in Studio so daily posting is one weekly sit-down.
- **Quality floor:** never publish a video the retention model predicts below ~50% watch-through. A video nobody watches is worse than not posting.

-----

## 8. Performance review loop (column 10)

For each published video at 48-72h:

- Pull average percentage-viewed (target 70%+) and the swipe-away timestamp.
- Map any dip to the beat/shot at that timestamp.
- Log the lesson. Durable lessons (lane routing, plate register, caption style) get promoted into the production SKILL.md, not left in an ephemeral task log.
- Feed the winning format back into the next cohort’s plate generation.

-----

## 9. Parked / Rework swimlane

Any card that fails a gate moves here with `blocking_gate` set, plus a one-line reason. The agent works the rework queue at the granularity of the failing asset (one plate, one shot, one caption), never a full rebuild, unless human review explicitly rejects the whole concept.