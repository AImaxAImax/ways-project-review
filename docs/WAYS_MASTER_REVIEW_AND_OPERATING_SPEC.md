# WAYS Master Review and Operating Spec

Single source of truth for the WAYS short-form video factory. Part I is the review of the public bundle (`github.com/AImaxAImax/ways-project-review`, inspected at commit on master, 3 commits, 33 tests passing). Part II is the consolidated operating spec that absorbs the kanban/gate, model-benchmark, and topic-queue work so they live in one place.

Review stance: direct, practical, evidence-based. The bar is “reliable agent-operated system that consistently ships impressive weird-fact shorts,” not “does the repo run.”

-----

# PART I: REVIEW

## 1. Executive summary

- The format works and the data proves it. Shark, frog, and shrimp each cleared cold start at roughly 1.3k views day one on a 5-subscriber channel; shark hit 102.8% average-viewed. The wombat (process-heavy, older voice) was throttled at 133 views on 43.87% retention. That is a clean natural experiment: the retention floor is real and the strong-prior animal lane is the wedge.
- The `tools/` layer is genuinely good. `ways_factory`, `ways_qc_gate_runner`, `ways_public_publish`, `ways_publish_review`, and `local_video_qa` are clean, single-responsibility modules with real unit tests. This is not a toy.
- The single biggest code problem is one-off script sprawl. `mantis_shrimp` alone has build scripts v04 through v30 (27 versions), sharks has generate_v6 through v22 plus eight run_v27 pilot variants, wood_frog has motion_v07 through v13. This is the maintainability and agent-confusion risk, not the library code.
- The most safety-critical file, `ways_public_publish.py`, has zero test coverage. The one script that can make a video public is the one script with no test.
- The publish boundary itself is well-designed: it refuses without a matching `authorize-public-publish` decision, defaults to dry-run, requires `--execute`, and runs a real preflight (category 28, made-for-kids false, caption present, processed). The design is right; it just is not tested.
- Quality gates are enforceable where they are numeric (ffprobe/spec) and not enforceable where they are taste-based (retention, novelty, pacing). The source-preservation check is self-described as lightweight RGB similarity and needs to become CLIP/DINO.
- Sanitization is strong on secrets (no keys, no tokens, solid `.gitignore`). Local username paths are scrubbed to `/home/<user>/...`, and `docs/SECRET_SCAN_REPORT.md` is present for the reviewer entrypoint.
- The auto-queue hardcodes its seed topics inside the tool and still feeds known-weak process lanes (wombat, saturn) into the five-video floor, which is at odds with the documented “do not let the wombat define the format” lesson.
- The mantis 30-version saga is the most important single piece of evidence in the repo: it is the dollar cost of discovering the process-shot failure mode after render instead of gating it before render.

## 2. Top risks (ordered by severity)

1. **Untested publish boundary.** `ways_public_publish.py` is the only path to public and has no test. A refactor or dependency bump could silently weaken the authorization or preflight check and nothing would catch it. Fix: add tests asserting it (a) raises without a matching Gate 6 authorization, (b) raises on each preflight failure, (c) does not flip privacy in dry-run, (d) only updates status with `--execute` plus authorization.
1. **One-off script sprawl.** ~50+ disposable `build_*_vNN.py` / `generate_vNN_*.py` scripts encode per-video work as code. A new agent cannot tell which script is current, and each is a copy-paste mutation of the last. Fix: collapse to one config-driven assembler driven by `beat_map.json` (the render-harness pattern already proves this works); archive the version scripts.
1. **Gate enforceability gap.** Numeric gates (ffprobe, dimensions, audio) are real. Taste gates (retention, pacing, novelty) and source preservation are not. `local_video_qa` preservation is RGB similarity by its own admission. An agent can advance a card by writing the right JSON fields without real evidence. Fix: bind QC fields to artifact-derived facts (parsed ffprobe, VLM JSON output) rather than hand-set values, and upgrade preservation to CLIP/DINO.
1. **Sanitization hygiene check.** Local user paths have been scrubbed to placeholders, and `scripts/pre_push_hygiene_check.py` should run before public pushes to fail on username/token/secret patterns and refresh `docs/SECRET_SCAN_REPORT.md` / `docs/SECRET_SCAN_HITS.json`.
1. **Auto-queue drift and weak-lane seeding.** `ways_auto_queue.py` hardcodes `SEED_CARDS` (six topics including wombat and saturn) inside the tool, duplicating `topic_queue_batch2.json`, and pushes process/scale-heavy topics into the always-on five-video floor. Drift risk plus it actively feeds the lane the data says underperforms. Fix: read seeds from the topic-queue JSON; tag process-heavy topics so the floor does not auto-advance them.

## 3. Highest-leverage improvements

- **Build the CLIP/DINO/VLM scoring harness once.** It has three payoffs from one build: it upgrades `local_video_qa`’s RGB preservation proxy into a real Gate 3 check, it unlocks the model-benchmark Phase 0, and it is the precondition for any autonomous optimization loop. This is the single highest-leverage thing on the board.
- **Enforce lane routing at Gate 2.** Score plate animation-friendliness before render so process beats route to motion-graphics and never consume an I2V render. The mantis 30-version history is exactly what this prevents.
- **One config-driven assembler.** Kills the script sprawl, makes every video reproducible from a manifest, and makes the pipeline legible to a fresh agent.
- **Test the publish boundary.** Lowest effort, highest safety return in the repo.

## 4. What to delete or simplify

- The ~50 per-version `build_*_vNN.py` scripts. Keep the `beat_map_vNN.json` files as the record of what was tried; delete the scripts once the assembler exists.
- Duplicate runner checklists: `WAYS_QC_GATE_RUNNER_CHECKLIST.md` and `WAYS_QC_RUNNER_CHECKLIST.md` are two near-identically named docs. Keep one.
- Hardcoded `SEED_CARDS` in `ways_auto_queue.py`. Replace with a read from the topic queue.
- Saturn and wombat as anything resembling format anchors. They are useful as MG-lane stress tests, not as floor-fillers.
- The paused still-frame cron (`adcfddd15e55`) if the Wan2.2 I2V lane has fully replaced it; a paused cron that will never resume is just confusion.

## 5. Agent handoff gaps

- **No single runbook of commands.** There is no `Makefile` or `RUNBOOK.md` that says, in order, “to take a card from Script Locked to Ready to Publish, run these commands.” Commands are scattered across READMEs and docstrings. A fresh agent has to reconstruct the sequence.
- **No publish-boundary test** (see Risk 1), so an agent cannot trust a refactor.
- **Secret scan artifacts** are generated at `docs/SECRET_SCAN_REPORT.md` and `docs/SECRET_SCAN_HITS.json`; refresh them with the hygiene scan before public pushes.
- **No documented rollback** for a public publish that should not have gone out. There is an append-only event log but no revert-to-private command.
- **The scoring harness does not exist yet**, which blocks Gate 3 source preservation, the benchmark, and any loop. It is the missing keystone.

## 6. Content-quality critique (can this ship 8/10+ shorts?)

Yes, for the strong-prior animal lane, and the live data confirms it. The gate philosophy (say-dog-see-dog, plate-first, one-variable cohorts) is sound and the three winners validate it. The system reliably produces 8/10-class output when the subject is a recognizable animal whose fact can be shown literally.

It does not reliably hit the bar on process, scale, or internal-anatomy topics. The wombat throttled at 133 on 43.87% retention, the mantis needed 30 versions, and saturn/tardigrade are scale/process-heavy. The docs know this, but the auto floor still seeds those topics, which means the factory can spend real effort manufacturing its known failure mode.

The biggest content risk at scale is not any single video: it is that you are about to 10x a fixed AI format, and the only thing keeping you on the right side of YouTube’s low-effort-content scrutiny is watch-through. You do not yet have a numeric retention proxy, so the watch-through floor in the spec is currently human judgment at Gate 5, not an enforced gate. Building that proxy is both a quality lever and a safety lever.

## 7. Technical and code critique

- **Architecture:** good separation. `tools/` holds reusable modules, `scripts/` holds build/render helpers, `test_cases/` holds per-topic packets. The render harness is correctly config-driven, the VAE override is documented in the workflow, and the preflight in `ways_public_publish` is thorough.
- **Tests:** real unit tests, not smoke. `test_ways_factory` asserts the schema and that `check-artifacts --ready-to-publish` refuses when artifacts are missing. `test_ways_publish_review` and `test_ways_qc_gate_runner` exercise the gate logic. 33 passing is meaningful. The coverage is skewed, though: the safety-critical publish path and the auto-queue idempotency are the two least-tested, highest-consequence areas.
- **Sprawl:** the per-test_case `scripts/` directories are where maintainability breaks down. The library is clean; the per-video work is not.
- **QC runner:** `ways_qc_gate_runner.py` correctly mirrors the kanban WIP limits (5 / 5 / 3, buffer target 10, warn below 5) and normalizes multiple board vocabularies. Solid. Its weakness is that it trusts card-reported fields.

## 8. Recommended next 7 days (ordered by impact)

1. **Test the publish boundary.** Highest safety return, lowest effort. Cover authorization-refusal, each preflight failure, dry-run, and execute-with-auth.
1. **Build and calibrate the CLIP/DINO/VLM scoring harness.** Replace the RGB proxy in `local_video_qa`. Hand-label ~15-20 clips and confirm the metric tracks your eye. This unblocks everything downstream.
1. **Keep the hygiene gate mandatory.** Run `scripts/pre_push_hygiene_check.py` before public pushes so username/token/secret patterns do not regress.
1. **Repoint `ways_auto_queue` at the topic-queue JSON** and stop seeding process-heavy topics into the five-video floor.
1. **Ship the next 2-3 strong-prior animal videos** (owl head-turn, octopus, cuttlefish) on the validated pattern, keeping cadence. Owl is the cleanest first test because the motion is the whole video.

## 9. Recommended next 30 days (after the 7-day fixes work)

1. **Config-driven assembler.** One builder that takes `beat_map.json`; archive the v04-v30 scripts.
1. **Run the model benchmark** now that the scoring harness exists. Produce the per-use-case routing table and feed it into Gate 2 lane routing.
1. **Bind QC gate fields to artifact-derived facts** so gates cannot be passed by writing JSON.
1. **Turn on the autoresearch loop** for per-shot prompt and seed optimization, gated by the calibrated metric, surfacing finalists for phone review. Not before calibration is measured.
1. **Close the retention feedback loop:** pull 48-72h retention into the queue and weight the next cohort toward what held the 70% line.

## 10. Open questions for Josh (only implementation-changing ones)

- Is TikTok cross-post in scope now? If later, archive `cdp_tiktok_helper.py` / `tiktok_crosspost_two.py` rather than maintaining them.
- What is the hard ceiling on paid Higgsfield credits per video? It should be a config value the gate enforces, not a convention.
- Do you want an automatic revert-to-private if a public-publish verification fails, built into `ways_public_publish`?
- Target daily output once the 50 land: 1 or 2 per day? This sets the WIP limits and the buffer math.

-----

# PART II: CONSOLIDATED OPERATING SPEC

This section folds in the three working specs from this session so they live in one place. The canonical in-repo gate doc is `ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md`; this is the reconciled summary plus the model and topic decisions.

## A. North star and quality bars

- WAYS = Wait, Are You Serious? Vertical weird-fact shorts. Kid-friendly, not kid-targeted. Category 28. George (ElevenLabs) voice.
- Private draft bar: 8-9/10. Public bar: 9/10+ and explicit human authorization.
- Human phone-size review is authoritative. VLM and contact sheets are advisory.
- Production is the bottleneck, not posting. Keep a reserve, never ship sub-bar to fill a slot.

## B. The board and the six gates

Columns: Idea Pool, Script Locked, Plate Generation, Plate QC, Render, Assembly and Caption, Auto-QA, Human Final Review, Ready to Publish, Published, Performance Review.

WIP limits (enforced by `ways_qc_gate_runner`): Plate Generation + Render combined max 5; Plate QC max 5; Human Final Review max 3; Ready-to-Publish buffer target 10, warn below 5.

Gates (four automated, two human):

1. Script: hook in first 2s, one claim per beat, say-dog-see-dog, sourced fact.
1. Plate QC (human approve/deny + VLM advisory): the highest-leverage gate. Includes the animation-friendliness score that routes process beats to motion-graphics before render.
1. Render QA (automated): all clips present, no morphing (CLIP/DINO, not SSIM), no generated text, lane clips clean.
1. Spec/Assembly QA (automated): 1080x1920, 24fps, AAC 48k, audio not clipped, captions readable, visual reset every 2-3s.
1. Human Final Review (phone-size): assigns draft/publish score.
1. Publish Authorization (human): explicit, default private. Enforced by `ways_public_publish.py` requiring a matching decision.

Automation boundary: the agent runs unattended through the automated gates and halts at Gate 2, Gate 5, Gate 6. It never spends paid credits or publishes public without explicit approval.

## C. Model routing and benchmark (condensed)

Run a controlled, per-use-case benchmark; the deliverable is a routing table, not a single winner. Full protocol in `WAYS_MODEL_BENCHMARK_PROTOCOL.md`.

- Core models: Wan2.2 I2V A14B (champion), LTX-2.3 fp8, LTX-2.3 distilled, Wan2.2 T2V (Category 5 only).
- Challengers to download, entered only where they can win: higher-precision Wan2.2 (quant ablation, the sleeper test), HunyuanVideo 1.5 (motion realism, Categories 2 and 5), CogVideoX-1.5-5B (long-clip probe only).
- Use-case categories: realism hold, large controlled motion, reveal/transformation, dynamic effect, cinematic/scale, process (probe).
- Non-negotiables: T2V never scored on preservation; LTX I2V conditioning path verified active; Wan uses `wan_2.1_vae.safetensors`; same 5-seed bank per cell, report median; blind the human review; calibrate the VLM before gating.
- Phase 0 (calibration) gates everything. The scoring harness is the missing keystone (see Part I, Risk 3 and the 7-day plan).
- The autoresearch loop (per-shot prompt/seed optimization) turns on only after Phase 0 metric agreement is measured.

The repo already shows a `lane_benchmark_20260605` start and a `hunyuan15_i2v_gguf_smoke.json` workflow, so this is partly in flight.

## D. Topic queue and cohort strategy (condensed)

Full queue in `WAYS_TOPIC_QUEUE_BATCH2.md` / `topic_queue_batch2.json`. Pattern: one counterintuitive fact about a recognizable subject, hook in 2s, shown literally, no process-diagram beat as the core visual.

- Anchor with strong-prior animals (octopus, axolotl, owl, cuttlefish, etc.). These are most of the next two weeks.
- Restrict process/scale topics to a deliberate MG-lane test cohort. Do not let them fill the floor.
- Vary one thing per cohort so retention data is interpretable. Tag every card with `cohort_tag` and a single `test_variable`.
- The wombat is a confounded data point; do not let it decide the format.

## E. Definition of done (artifact contract)

A finished card ships: `idea_card.json`, `script.md`, `storyboard_manifest.json`, `lane_map.json`, accepted/rejected stills, i2v and motion-graphic clips, clean master, captioned candidate, captions (ass/srt), contact sheet, `ffprobe_publish.json`, `audio_report.txt`, `vlm_plate_scores.json`, `PUBLISH_GATE.md` with all gate results, and the youtube draft pack (category 28, made-for-kids false). A card is not done if any artifact or gate result is missing.

## F. The throughline

The system is one good build away from being trustworthy at volume: the scoring harness. It upgrades Gate 3, calibrates the benchmark, and unlocks the optimization loop. Pair it with testing the publish boundary and collapsing the script sprawl, and the factory becomes something a fresh agent can operate safely while you keep the only two jobs that should stay human: approving plates and authorizing publishes.