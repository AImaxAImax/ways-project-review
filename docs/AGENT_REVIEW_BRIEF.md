# Agent review brief

## What this repo is

A sanitized review copy of the WAYS short-form video production system. It is built around producing high-quality weird-fact vertical videos with a human-gated factory workflow.

## What is intentionally missing

- Generated `.mp4`, `.jpg`, `.png`, `.wav`, `.mp3`, etc.
- Model files and ComfyUI model weights.
- OAuth tokens, credentials, and secret files.
- Runtime caches.

## Main areas

- `tools/` — factory/QC/publish helpers.
- `scripts/` — build/render helpers and one-off pipeline scripts.
- `ops/ways-video-lab-discord/` — operating spec, QC gates, Discord/kanban contracts, status reports.
- `templates/wan22-a14b-i2v-short-template/` — current winning local Wan2.2 I2V recipe.
- `test_cases/` — topic-specific production packets, scripts, QA notes, manifests.
- `dashboard/` — dashboard/review state files and contracts.
- `external_workflows/comfyui/` — selected external Comfy workflows needed to understand local lanes.

## What to review first

1. `ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md`
2. `tools/ways_qc_gate_runner.py`
3. `tools/ways_factory.py`
4. `tools/ways_public_publish.py`
5. `tools/ways_publish_review.py`
6. `templates/wan22-a14b-i2v-short-template/README.md`
7. `docs/WORKFLOWS_AND_PHILOSOPHY.md`
8. `docs/CRONS_AND_AUTOMATION.md`

## Safety expectations

- Public publish must require explicit human authorization.
- Default upload state must stay private.
- Metered/paid generation must not run without approval.
- Tokens must remain outside the repo.
- Human phone-size review is required before any finalist/publish claim.
