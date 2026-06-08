# WAYS Scoring Harness Build Spec

Agent build task. This is the keystone the project is blocked on: it upgrades the placeholder source-preservation check into a real metric, becomes Phase 0 of the model benchmark, and is the precondition for any autonomous optimization loop. Build it as an extension of the existing `tools/local_video_qa.py`, not a new tool.

## Why this exists

`tools/local_video_qa.py` currently scores source preservation with “lightweight RGB similarity” by its own README admission, and its taste/quality signals are not numeric. Three workstreams depend on fixing that: Gate 3 render QA, the model benchmark (`WAYS_MODEL_BENCHMARK_PROTOCOL.md`), and the per-shot autoresearch loop. One build, three payoffs.

## Hard constraints

- It is a gate, never a publisher. A pass means “ready for human phone-size review,” not “auto-publish.” Preserve the existing exit-code contract: 0 = no blockers, 1 = blockers, 2 = tooling error.
- Human phone-size review stays authoritative. Every number this produces is advisory until calibration proves agreement (see Calibration).
- No paid/metered calls. Runs locally on the 5090. CPU fallback allowed but may be slow.
- Do not hardcode pass thresholds. Thresholds are loaded from a calibrated config file produced by the calibration step.

## What to compute

Add these metrics alongside the existing ffprobe/contact-sheet checks. All operate on the clean master (pre-caption) plus the source plate when provided.

|Metric                |Purpose                         |Method                                                                               |Library                            |
|----------------------|--------------------------------|-------------------------------------------------------------------------------------|-----------------------------------|
|`clip_preservation`   |Subject identity vs source plate|Cosine of CLIP image embeddings: source plate vs sampled frames. Report min and mean.|`open_clip_torch`                  |
|`dino_structure`      |Structural/pose preservation    |Cosine of DINOv2 embeddings, source vs frames                                        |`torch.hub` facebookresearch/dinov2|
|`temporal_consistency`|Flicker / jitter                |Mean frame-to-frame LPIPS; higher = more flicker                                     |`lpips`                            |
|`motion_magnitude`    |Enough motion, not chaos        |Mean optical-flow magnitude across frames; want a band, not a max                    |`opencv` (Farneback) or RAFT       |
|`artifact_flags`      |Text/logo/anatomy failures      |Existing VLM hook (`--vlm-command` or `--openai-vlm-url`); keep harsh prompt         |existing                           |

Replace the RGB `--source-image` proxy with `clip_preservation` + `dino_structure`. Keep `--source-image` as the flag name for backward compatibility; just change what it computes.

Do not use SSIM for preservation. SSIM rewards static frames and misses semantic drift. This is a known project lesson.

## CLI contract (extends current flags)

```
python3 tools/local_video_qa.py \
  --input <clean_master.mp4> \
  --source-image <approved_plate.png> \
  --thresholds config/qa_thresholds.json \
  --outdir <out> \
  [--openai-vlm-url http://host:8000/v1 --vlm-model <model>] \
  [--frame-sample-fps 4]
```

New outputs in `--outdir`, additive to the current ones:

- `qa_report.json` gains a `metrics` block: `{clip_preservation:{min,mean}, dino_structure:{min,mean}, temporal_consistency, motion_magnitude, artifact_flags:[...]}` and a `thresholds_used` echo.
- `metrics_debug.json`: per-frame values for inspection.

## Thresholds config

`config/qa_thresholds.json`, produced by calibration, not hand-guessed:

```json
{
  "clip_preservation_min": 0.0,
  "dino_structure_min": 0.0,
  "temporal_consistency_max": 0.0,
  "motion_magnitude_low": 0.0,
  "motion_magnitude_high": 0.0,
  "calibrated_against": "n labeled clips",
  "agreement": "report agreement vs human labels here"
}
```

A blocker fires when a metric crosses its threshold. Until the file exists, the harness runs in `--report-only` mode: it computes and prints metrics but raises no blockers, so nobody trusts an uncalibrated gate.

## Calibration (do this before the gate is trusted)

1. Pull 15-20 already-human-reviewed clips spanning good and bad (the mantis say_dog versions and the four published videos are ideal: they have known outcomes).
1. Record each clip’s existing human verdict (pass/fail, and the draft score if present).
1. Run the harness in report-only mode over all of them.
1. Find thresholds that best separate the human pass/fail set. Record the agreement rate (how often the gate verdict matches the human verdict).
1. Write `config/qa_thresholds.json` with those thresholds and the measured agreement.
1. Only then enable blocking. If agreement is weak, keep it advisory and flag for tuning; do not ship a gate that disagrees with the eye.

This is the calibrate-before-gating rule. It is also exactly Phase 0 of the model benchmark, so this step does double duty.

## Tests to add (tests/test_local_video_qa.py)

- Report-only mode never returns exit code 1, regardless of metric values.
- With a thresholds file, a clip below `clip_preservation_min` returns exit code 1 and lists the blocker.
- A clip with zero motion (`motion_magnitude` below `low`) flags a dead-render warning.
- Missing source plate skips preservation metrics without crashing.
- Malformed thresholds file returns exit code 2, not a false pass.

## How it plugs into the system

- **Gate 3 (Render QA):** call the harness on each clean master; a preservation/temporal blocker parks the card in Rework with the failing metric as the reason.
- **Benchmark Phase 0/1:** the same harness produces the Tier-1 quantitative scores in the model matrix. No second tool.
- **Autoresearch loop:** once calibrated, the loop uses the harness score as its keep/discard signal. Until agreement is measured, the loop stays off.

## Definition of done

- `local_video_qa.py` computes the five metrics, reads thresholds from config, defaults to report-only when no config exists.
- `config/qa_thresholds.json` exists with a recorded agreement rate against the labeled set.
- New tests pass and the existing 33 still pass.
- One paragraph in `README_QA.md` documents the new metrics and the report-only-until-calibrated behavior.

## Out of scope (do not do yet)

- Wiring this into autonomous keep/discard. That waits on the measured agreement rate.
- Any change to the publish boundary. This tool never touches privacy state.