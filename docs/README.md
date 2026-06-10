# WAYS Review Docs Index

Canonical source on conflict: `docs/WAYS_MASTER_REVIEW_AND_OPERATING_SPEC.md`.

## Canonical doc per topic

| Topic | Canonical source | Notes |
|---|---|---|
| Overall review, operating priorities, gate philosophy | `docs/WAYS_MASTER_REVIEW_AND_OPERATING_SPEC.md` | Wins on conflicts. |
| Reviewer entrypoint | `docs/REVIEW_REQUEST.md` | Tells reviewers where to start and what to judge. |
| Full project/context handoff | `docs/WAYS_PROJECT_HANDOFF_FULL_RUNDOWN.md` | Narrative context only; defer to master spec for current priorities. |
| Automation and cron inventory | `docs/CRONS_AND_AUTOMATION.md` | Snapshot/handoff, not a live scheduler source. |
| Secret/sanitization scan | `docs/SECRET_SCAN_REPORT.md`, `docs/SECRET_SCAN_HITS.json`, `docs/SCAN_REPORT.md` | Keep current with `scripts/pre_push_hygiene_check.py`. |
| Runnable benchmark protocol | `docs/WAYS_MASTER_REVIEW_AND_OPERATING_SPEC.md` Part II and `benchmark/README.md` | Older benchmark docs are historical pointers. |
| Model testing execution order | `docs/WAYS_MODEL_TESTING_RUNDOWN.md` | Ordered do-this-now campaign sequence; calibration before Step 1. |
| Harness calibration runbook | `docs/WAYS_HARNESS_CALIBRATION_RUNBOOK.md` | Required before flipping benchmark cells out of provisional status. |
| Latest calibration run notes | `docs/WAYS_CALIBRATION_RUN_20260608.md` | Documents first-frame, explicit-source, and per-shot candidate runs copied from the live artifact tree. |
| Benchmark results | `benchmark/results/` | Pre-calibration cells are provisional until `config/qa_thresholds.json` records human-label agreement. |
| Human artifact review | `docs/WAYS_ARTIFACT_REVIEW_LOG.md` | Human review overrides proxy metrics. |
| Latest YouTube performance data | `ops/ways-video-lab-discord/WAYS_YOUTUBE_DATA_NOW_20260610.md` and `.raw.json` | Current public stats plus Analytics API rows through 2026-06-09; use to tune next videos. |
| Batch 2 topic queue | `ops/ways-video-lab-discord/topic_queue_batch2/WAYS_TOPIC_QUEUE_BATCH2.md` and `BATCH2_COHORT_PLAN.md` | Next topic cohort derived from shark/frog/shrimp/crow signals. |

## Benchmark status

All benchmark result cells populated before metric calibration are provisional. Do not treat CLIP/DINO/LPIPS-derived scores as pass/fail routing until calibration produces `config/qa_thresholds.json` plus a recorded human-label agreement rate.
