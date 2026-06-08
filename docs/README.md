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
| Benchmark results | `benchmark/results/` | Pre-calibration cells are provisional until `config/qa_thresholds.json` records human-label agreement. |
| Human artifact review | `docs/WAYS_ARTIFACT_REVIEW_LOG.md` | Human review overrides proxy metrics. |

## Benchmark status

All benchmark result cells populated before metric calibration are provisional. Do not treat CLIP/DINO/LPIPS-derived scores as pass/fail routing until calibration produces `config/qa_thresholds.json` plus a recorded human-label agreement rate.
