# WAYS Repo Code Review: Issues and Required Fixes

Repo reviewed: `AImaxAImax/ways-project-review` (review bundle, 2026-06-10)
Scope: `tools/`, `scripts/`, `tests/`, `config/`, `calib/`, `docs/`, `ops/`, `test_cases/`, `templates/`

Severity legend: **P0** = can put a bad video in front of a publish decision or hollow out governance. **P1** = structural debt actively costing you rework time. **P2** = hygiene, fix when touching the area.

-----

## P0-1: Automation fabricates the QA evidence the gate runner checks

**Where:** `tools/ways_auto_queue.py` (mantis promotion block, ~lines 268-305) feeding `tools/ways_qc_gate_runner.py`

**Issue:** `ways_auto_queue.py` hand-writes the exact fields that Gates 3 and 4 evaluate:

- Synthesizes `render.shot_reports` with `severity: "warn"`. The gate runner only blocks on `severity in {"block", "fail"}`, so fabricated “warn” passes Gate 3.
- Writes `assembly_qa` with `caption_readability: "pass"`, `double_captions: False`, `non_caption_text: False`. Gate 4 trusts these self-reported booleans without computing anything.
- Invents `draft_score = c.get("draft_score") or 8.0`. A score of 8.0 appears from nowhere.

The gate runner never independently verifies any of this. It reads board JSON that the automation itself wrote. The verdict pipeline is: agent writes verdicts → agent reads verdicts → agent reports “pass”.

**Fix:**

1. The gate runner must compute evidence, not read declarations. Gate 4 should run ffprobe itself against the actual publish candidate (it already has the file path), not load a pre-supplied ffprobe JSON that may not match the video.
1. Require all QA report files (`qa_report.json`, `vlm_plate_scores.json`, shot reports) to be produced by `local_video_qa.py`, and embed a SHA-256 of the source mp4 inside each report. Gate runner re-hashes the video and rejects reports whose hash does not match.
1. Board JSON carries pointers to evidence files, never verdicts. Delete every code path in `ways_auto_queue.py` that writes `assembly_qa`, `shot_reports`, `draft_score`, or any gate result field.

-----

## P0-2: The agent writes its own permission slip to skip human gates

**Where:** `tools/ways_auto_queue.py` line 222; `tools/ways_qc_gate_runner.py` `evaluate_human_gate()`

**Issue:** `ways_auto_queue.py` stamps `automation_policy = "auto_advance_internal_until_5_active_ready"` on every card it creates. The gate runner honors that exact string to bypass Gate 2 (Human Plate QC) and Gate 5 (Human Final Review). The same automation that wants to advance cards grants itself the exemption. Gate 6 remains human-only, but everything upstream of it can be auto-advanced with zero real checks (see P0-1), so the 9/10 publish gate is the only real gate left.

**Fix:**

1. Move the policy grant out of the automation’s reach. The policy should live in a human-owned config file (e.g. `config/automation_policy.json`) that auto_queue reads but never writes, or be set only via the review dashboard’s decision endpoint.
1. Even under the five-video-floor policy, “auto_internal” advancement should still require real computed evidence (per P0-1 fixes), not just the policy string plus any non-empty field like `lane_assigned`.
1. Add a pre-push or cron check that diffs board JSON and flags any change to `automation_policy` or `human_approved` not originating from a dashboard decision record.

-----

## P0-3: Custom column name escapes Gate 5 AND WIP limits (concrete bug)

**Where:** `tools/ways_auto_queue.py` (mantis block) sets `status_column = "Human Final Review - Mantis Wan v03 Candidate"`; `tools/ways_qc_gate_runner.py` `evaluate_human_gate()` and `WIP_LIMITS`

**Issue:** The gate runner matches `column == "Human Final Review"` exactly, and WIP limits count the exact column name `"Human Final Review"` (max 3). The decorated column string means the mantis card:

- Never gets the Gate 5 human-gate evaluation (no `blocked_advisory`, no `human_gate` entry).
- Is invisible to the Human Final Review WIP limit.

Your hardcoded special case created a column that dodges your own governance. Any future “Column Name - note” pattern reproduces this silently.

**Fix:**

1. Stop encoding notes in column names. `status_column` must come from a closed enum; put the note in a `status_note` field.
1. In `normalize_column()`, validate against the known column set and either raise or map to `"Unknown"` with a board-level warning. Unknown columns should be a blocking report condition, not silently ignored.
1. Change WIP counting and human-gate matching to prefix/enum match only after the enum validation exists, never substring matching as a band-aid.

-----

## P0-4: VLM failure fails open

**Where:** `tools/local_video_qa.py` `run_vlm_command()` (~line 472)

**Issue:** If the VLM command exits nonzero, the function returns `severity: "warn"`. If output is not JSON, default severity is also “warn”. Gate 3 only blocks on block/fail, so a crashed or misconfigured QA model makes videos look cleaner than a working one. An Ollama outage silently disables your visual QC.

**Fix:**

1. VLM command failure or unparseable output → `severity: "block"` with reason `vlm_unavailable_or_invalid_output`, or at minimum a distinct `severity: "error"` that the gate runner treats as blocking.
1. Same treatment in `run_openai_vlm()` for HTTP errors and JSON parse failures.
1. Add a test: simulate VLM command exiting 1, assert the gate blocks.

-----

## P0-5: `fail_closed: true` flag does nothing while gates are advisory

**Where:** `config/qa_thresholds.json`

**Issue:** Config declares `"fail_closed": true` alongside `"blocking_enabled": false` and `"gate_mode": "advisory"`. The scoring harness currently blocks nothing. Holding it advisory until recalibration against approved source plates is a defensible call, and the config documents the rationale honestly (credit there). But the `fail_closed` flag is misleading decoration: anyone (human or agent) skimming the config will believe the metric gate is enforcing.

**Fix:**

1. Remove `fail_closed` until the harness is in blocking mode, or rename it `fail_closed_when_blocking` with a comment.
1. Add a single derived field the gate runner echoes into every report: `metric_gate_effective_mode: "advisory"`. Make the inert state loud.
1. Track the recalibration prerequisite (“rerun with approved explicit source plates per shot”) as a board card so it does not live only in a config comment.

-----

## P1-1: Topic-specific business logic baked into core tools

**Where:** `tools/ways_auto_queue.py` (mantis special case ~50 lines; `SEED_CARDS` containing full scripts/beats in code)

**Issue:** A generic queue tool contains hardcoded mantis filenames, rejection-history commentary, and promotion logic for one topic. Seed card content (hooks, beats, sources) lives in Python instead of data. Every new topic or policy change is a code edit to a governance-critical tool. This is the one-off sprawl problem invading core tooling, which is worse than sprawl in `test_cases/`.

**Fix:**

1. Move seed cards to data. You already have `ops/.../topic_queue_batch2/topic_queue_batch2.json`; make that the only source of card content.
1. Replace the mantis special case with a generic mechanism: a per-card override file (e.g. `<project>/card_overrides.json`) that auto_queue merges, with the gate runner still independently verifying everything (P0-1).
1. Acceptance test: `grep -rn "mantis\|wood_frog\|shark" tools/` returns zero hits.

-----

## P1-2: Version-suffix script disease (30 near-identical copies per topic)

**Where:** `test_cases/*/scripts/` — 104 Python files, 50 `build_*` scripts. Mantis alone has `build_mantis_say_dog_v04.py` through `v30`.

**Measured:** v29 vs v30 are 98.7% identical; wood frog v12 vs v13 are 88.3% identical.

**Issue:** Every caption bugfix, audio tweak, or spec change must be re-applied across dozens of copies. Iteration history is encoded in filenames instead of git. This is the single largest ongoing time tax in the repo.

**Fix:**

1. Build one assembly engine (`tools/ways_assemble.py`) that consumes a per-topic beat manifest (beats, plates, captions, VO file, lane per shot, timings).
1. Iterating a video = editing the manifest, committing, re-running the engine. The 30 mantis scripts collapse to one engine plus 30 small JSON diffs in git history.
1. Migrate forward only: next topic uses the engine; do not retrofit published topics. Freeze `test_cases/*/scripts/` as archive and exclude it from hygiene/lint scopes.
1. The `templates/wan22-a14b-i2v-short-template/run_v27_wan22_animated_frames.py` is the closest existing thing to the engine; promote and generalize it rather than starting fresh.

-----

## P1-3: Duplicated helpers across the codebase

**Where:** `as_float()` copy-pasted in `tools/local_video_qa.py` and `tools/ways_qc_gate_runner.py`; 9 separate `run()` subprocess wrappers; 9 caption-drawing helper implementations across `scripts/` and `test_cases/`.

**Issue:** Behavior drift between copies is guaranteed. A fix to fraction parsing or ffmpeg error handling in one place does not propagate.

**Fix:** Create `ways_lib/` package with `proc.py` (run/capture_json), `media.py` (ffprobe, contact sheets, as_float), `captions.py` (wrap/draw/ASS+SRT emit), `io.py` (atomic JSON read/write). Core tools import it; the assembly engine (P1-2) is its first big consumer.

-----

## P1-4: Gate runner trusts inputs structurally (beyond P0-1)

**Where:** `tools/ways_qc_gate_runner.py`

**Issues:**

- Gate 2 has zero automated artifact checks. It only inspects policy strings and `human_approved`. There is no verification that accepted plates, plate-QC contact sheets, or `vlm_plate_scores.json` exist or pass thresholds.
- `should_run_gate4()` only triggers when `assembly_qa`/`spec_qa` keys exist on the card, and those keys are written by the automation (P0-1). A card with the keys omitted skips Gate 4 silently when sitting in a non-matching column.
- Gate 4 reads a pre-supplied ffprobe JSON file rather than probing the actual publish candidate. The JSON can describe a different or older file.

**Fix:**

1. Gate 2 (automated portion): verify `assets/accepted_stills/` is non-empty, the plate QC contact sheet exists, and `vlm_plate_scores.json` exists with all selected plates above threshold. Human approval stays required on top.
1. Gates run by column position, period. A card in or past a gate’s column with missing evidence is a **block**, never a skip.
1. Gate 4 runs ffprobe directly on `publish_candidate_captioned` and compares to spec; the stored JSON becomes an artifact, not the source of truth.

-----

## P1-5: No adversarial tests for the auto_queue → gate_runner interaction

**Where:** `tests/` (43 tests, reasonable happy/blocking-path coverage)

**Issue:** The most dangerous interaction in the system is untested as a pair. Nothing asserts that a board produced by `ways_auto_queue.py` cannot pass gates without real evidence. The P0-3 column-escape bug and the P0-1 fabricated-evidence path would both have been caught by one integration test.

**Fix:** Add `tests/test_pipeline_adversarial.py`:

1. Run auto_queue against a tmp root with no real artifacts → pipe board into gate runner → assert every card blocks.
1. Card with fabricated `assembly_qa`/`shot_reports` but mismatched/missing video hash → assert block.
1. Card with `automation_policy` self-set but no dashboard decision record → assert human gates stay blocked_advisory.
1. Card in column `"Human Final Review - anything"` → assert it is treated as unknown/blocking and counted in WIP (after P0-3 fix).

-----

## P2-1: Hardcoded local paths in 118 files

**Where:** repo-wide (`C:\dev\curious-shorts`, `/mnt/c/dev/curious-shorts`); worst offender `tools/ways_public_publish.py` with hardcoded `ROOT` and token path.

**Fix:** One resolution function in `ways_lib`: `WAYS_ROOT` env var → `--root` flag → cwd, in that order. Token path via `WAYS_YT_TOKEN` env var. Add a hygiene-check rule that blocks new hardcoded absolute roots in `tools/` and `scripts/` (keep `test_cases/` exempt as archive).

-----

## P2-2: Ghost file references in docs (14 confirmed in this bundle)

**Where:** e.g. `test_cases/sharks_older_than_trees/outputs/wan22_v27_animated_frames/README_STATUS.md` references `scripts/run_v27_wan22_animated_frames.py`, `scripts/run_v27_wan22_a14b_fixed_pilot.py`, `scripts/render_v26_final_predator_audio.py` and others that do not exist in the repo. 14 of 124 checked references are dead.

**Issue:** Either the export/bundling script drops files (then the export is broken) or docs are stale (the recurring ghost-file problem). Agents reading these docs will chase nonexistent scripts.

**Fix:** Add a link checker to `scripts/pre_push_hygiene_check.py`: scan markdown for backticked repo paths and fail on missing targets. Run it once now and either restore the files to the bundle or delete the references.

-----

## P2-3: Documentation sprawl with overlapping sources of truth

**Where:** 210 markdown files; at least four overlapping operating specs (`WAYS_MASTER_REVIEW_AND_OPERATING_SPEC.md`, `WAYS_PROJECT_HANDOFF_FULL_RUNDOWN.md`, `WORKFLOWS_AND_PHILOSOPHY.md`, `WAYS_KANBAN_AND_QC_GATES.md`) plus dated check-in/status files accumulating in `ops/ways-video-lab-discord/`.

**Issue:** The `docs/README.md` conflict-winner rule is a band-aid on the symptom. Every doc an agent might read is a doc that can contradict the spec.

**Fix:** Collapse to three living docs: `OPERATING_SPEC.md` (gates, schema, contracts), `RUNBOOK.md` (how to run everything), `DECISIONS.md` (append-only durable decisions like the wombat MG-lane ruling). Dated check-ins move to `ops/log/YYYY-MM/` or get deleted; git history is the archive.

-----

## P2-4: Broad exception swallowing (66 `except Exception` blocks)

**Where:** repo-wide; notable silent ones: `read_json()` in `scripts/review_dashboard_server.py` returns default on corrupt JSON; `selected_count` in auto_queue → 0 on parse failure.

**Fix:** In governance-path code (gate runner, auto_queue, publish tools), a corrupt JSON file is a blocking error, not a default value. Log-and-continue is acceptable only in dashboards/reporting. Sweep the 66 sites when touching each file; do not do a big-bang refactor.

-----

## P2-5: `shell=True` with templated command in local_video_qa

**Where:** `tools/local_video_qa.py` line 474 (`run_vlm_command`)

**Issue:** `{image}` is shlex-quoted, which mitigates the injection risk, but the command template itself is interpolated into a shell. Acceptable for a single-operator tool; fragile the moment Hermes constructs the template string.

**Fix:** Accept the VLM command as an argv list in config (JSON array) and run with `shell=False`. Keep the string form only as a deprecated fallback.

-----

## What is already good (keep these patterns)

- `ways_qc_gate_runner.py` core is clean, typed, readable.
- Dashboard server: binds 127.0.0.1, atomic JSON writes, path traversal guarded via `resolve()` + `relative_to()`.
- `ways_public_publish.py`: dry-run by default, refuses to execute without a matching `authorize-public-publish` decision record.
- Pre-push hygiene hook self-tests known-bad samples and fails closed.
- Preserved-blocker logic in the gate runner (artifact existence cannot silently clear a known blocker).
- Calibration config documents its own limitations honestly.

-----

## Recommended execution order

|Step|Item                                     |Why first                                     |
|----|-----------------------------------------|----------------------------------------------|
|1   |P0-1 computed evidence + video hashing   |Removes the fabrication channel entirely      |
|2   |P0-3 column enum validation              |One-line-class bug, escapes two controls today|
|3   |P0-2 policy grant moved out of automation|Closes the self-permission loop               |
|4   |P0-4 VLM fail-closed                     |Small diff, big safety win                    |
|5   |P1-5 adversarial test suite              |Locks in steps 1-4 against regression         |
|6   |P1-1 strip topic logic from auto_queue   |Unblocks clean batch-2 onboarding             |
|7   |P1-2 assembly engine + manifests         |Biggest ongoing time savings                  |
|8   |P1-3 / P1-4 shared lib + gate hardening  |Ride along with engine work                   |
|9   |P2-x hygiene items                       |As you touch each area                        |