# WAYS Local Model Benchmark Handoff

> Historical pointer: the canonical operating and benchmark guidance now lives in `docs/WAYS_MASTER_REVIEW_AND_OPERATING_SPEC.md`. For runnable commands, use `benchmark/README.md`. If this file conflicts with either source, the master spec wins.

Last updated: 2026-06-08

## Purpose

This repo now contains the review-facing documentation and runnable scaffold for the WAYS local video model benchmark. The live render tree is still `/mnt/c/dev/curious-shorts`; this GitHub repo is the sanitized handoff bundle for reviewer/agent inspection.

## What is included for review

- `docs/WAYS_MODEL_BENCHMARK_PROTOCOL.md` - source benchmark protocol.
- `benchmark/README.md` - how to run/setup/analyze the benchmark.
- `benchmark/config/benchmark_manifest.json` - locked plates, seeds, model bracket, category coverage.
- `benchmark/results/model_matrix.md` - current model x category matrix.
- `benchmark/results/cat1_wan22_i2v_results.json` - current Cat 1 Wan2.2 I2V score table.
- `benchmark/results/phase0_status.json` - Comfy/model readiness snapshot.
- `benchmark/results/phase0_real_smoke_attempt.json` - Comfy restart and smoke result note.
- `scripts/setup_ways_model_benchmark.py`
- `scripts/benchmark_phase0_status.py`
- `scripts/run_ways_model_benchmark.py`
- `scripts/analyze_ways_model_benchmark.py`
- `docs/WAYS_ARTIFACT_REVIEW_LOG.md` - human artifact observations that automated QA does not catch.

Generated videos, model weights, cached media, and secrets are intentionally not committed.

## Current benchmark state

### Completed

Wan2.2 I2V Category 1:

- `cat1_shark_a`: seeds `627101-627105` complete.
- `cat1_octopus_b`: seeds `627101-627102` complete.

Current matrix summary:

```text
Cat 1 / wan22_i2v
n=7
CLIPmed=0.830
LPIPSmed=0.106
secmed=590.6
```

All completed cells returned QA score `92` and `blockers: []` from the calibrated local QA harness. Human artifact review is still authoritative.

### Known artifact requiring review

`cat1_octopus_b / wan22_i2v / seed_627102` appears to contain an extra or visually unattached tentacle. This is logged in `docs/WAYS_ARTIFACT_REVIEW_LOG.md` with metrics and evidence reference.

## Live artifact paths

The rendered files remain in the live tree:

```text
/mnt/c/dev/curious-shorts/benchmark/runs/
```

Example flagged video:

```text
/mnt/c/dev/curious-shorts/benchmark/runs/cat1/cat1_octopus_b/wan22_i2v/seed_627102/clips/shot01_wan22_432x768_25f_seed627102.mp4
```

## Review guidance

Do not treat automated score `92` as a pass by itself. For routing:

1. Check `docs/WAYS_ARTIFACT_REVIEW_LOG.md`.
2. Blind-review the video on a phone-size viewport.
3. Reject or downgrade cells with anatomy errors even when CLIP/DINO/LPIPS are strong.
4. Record artifacts before continuing model comparisons so the matrix reflects human quality, not just preservation metrics.

## Next benchmark work

Recommended next steps:

1. Finish `cat1_octopus_b` seeds `627103-627105`.
2. Fill human review notes for all Cat 1 cells.
3. Start LTX I2V Phase 0 workflow verification before comparing against Wan2.2.
4. Only expand to Category 2 after Cat 1 has both automated and human-review notes.
