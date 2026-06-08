# WAYS Model Testing Rundown: Finding the Best Route Forward

Execution playbook for the local video-model campaign. The full method is in `WAYS_MODEL_BENCHMARK_PROTOCOL.md`; this is the ordered “do this now” sequence, with the decision each step unlocks. Goal: a per-use-case routing table you can trust, not a wall of numbers.

## The one hard gate before any scored comparison

**Calibration comes first. Nothing scored is trustworthy until it exists.** The benchmark results already in the repo (`benchmark/results/cat1_wan22_i2v_results.json`) are correctly marked `provisional: true` because they were produced before the metric was calibrated. Do not flip any cell to non-provisional, and do not make any routing decision, until `config/qa_thresholds.json` exists with a recorded human-label agreement rate.

Precondition checklist before scoring anything:

1. The slow real-model test runs green (not skipped) on the 5090. This proves CLIP/DINO/LPIPS/flow actually execute. A skipped test does not count.
1. Calibration run complete per `WAYS_HARNESS_CALIBRATION_RUNBOOK.md`: 15-20 human-labeled clips, thresholds fitted, agreement rate recorded.
1. `config/qa_thresholds.json` written, in the live tree (`curious-shorts`), where the media is.

If agreement is weak, the metric stays advisory and the campaign produces ranked human-blind scores only, with automated metrics as context. That is still useful; it just means the routing table is taste-led, not metric-gated.

## Phase order (by decision value, not by category number)

### Step 1: Quant ablation (the sleeper, do this first)

**Question:** is quantization your quality ceiling?
**Run:** higher-precision Wan2.2 (Q8 or fp8/fp16) vs the current Q5_K_M, same plates, same 5 seeds, Categories 1 and 3 only.
**Why first:** if Q8 clearly beats Q5 by eye, every later phase should run on Q8, so you need this answer before the rest. It is also the cheapest high-value test: same model, more bits, no new architecture.
**Decision unlocked:** which Wan precision is the baseline for everything downstream.

### Step 2: Realism-hold bracket (Categories 1, 3, 4)

**Question:** does anything beat Wan2.2 I2V where identity must not drift?
**Run:** Wan2.2 I2V (winning precision from Step 1) vs LTX-2.3 fp8 vs LTX-2.3 distilled. 2 plates x category x 5 seeds. Score preservation (CLIP/DINO), temporal, motion, plus blind human.
**Decision unlocked:** the default model for your bread-and-butter animal shots. Expectation: Wan holds. If it does, that is a confirmation, not a non-result.

### Step 3: Large-motion + cinematic bracket (Categories 2, 5)

**Question:** where does Wan lose, and to what?
**Run:** add HunyuanVideo 1.5 here (the smoke workflow `hunyuan15_i2v_gguf_smoke.json` is already in the repo). Category 2 is large controlled motion (owl head-turn), Category 5 is cinematic/scale where Wan2.2 T2V also competes because preservation is not required.
**Decision unlocked:** whether you route big-motion and establishing shots to a different model than your realism shots. This is the most likely place the routing table splits.

### Step 4: Long-clip probe (Category, separate)

**Question:** does a single longer generation beat stretched short clips?
**Run:** CogVideoX-1.5-5B vs Wan2.2 I2V on one plate at ~10s.
**Decision unlocked:** whether the “longer clips” bottleneck has a model answer or stays a stitching problem.

### Step 5: Process-beat probe (Category 6)

**Question:** does any local model rescue photoreal process shots, or does MG-lane routing stay mandatory?
**Run:** one plate, best 2 models, few seeds.
**Decision unlocked:** confirm (almost certainly) that process beats stay in motion-graphics. Settles the mantis-saga question with data.

## Non-negotiables (carry over from the protocol)

- T2V is scored only in Category 5. Never against a source plate.
- LTX I2V conditioning path verified active before scoring; /32-clean dims.
- Wan uses `wan_2.1_vae.safetensors`; 2-stage high-to-low noise.
- Same 5-seed bank per cell; report median and best, never a single seed.
- Human blind review is authoritative and the model identity is anonymized before review.
- Fixed compute budget per cell so no model wins on extra compute.
- Challengers enter only the categories listed; do not run every model everywhere.

## Reporting format

Fill `benchmark/results/model_matrix.md` per cell as `median_human / best_human | CLIP | flicker | sec_per_clip | VRAM`. Keep `provisional: true` on every cell until calibration exists, then re-score and flip. Log seed variance and every human-vs-metric disagreement; those disagreements feed metric recalibration.

## What the campaign produces

Not “the best model.” A routing table:

- Realism-critical categories: likely Wan2.2 I2V (at the precision Step 1 picks).
- Large-motion / cinematic: possibly HunyuanVideo 1.5 or LTX, decided by Step 3.
- Long single clips: CogVideoX only if Step 4 says so.
- Process beats: motion-graphics lane, confirmed by Step 5.

That table drops straight into Gate 2 lane routing. Once it exists and the metric is calibrated, the autoresearch loop can take over per-shot prompt/seed optimization on the chosen model, surfacing finalists for phone review.

## Sequencing note

Do not start this campaign in parallel with the open correctness fixes. Calibration depends on the scoring harness being trustworthy, and the harness work is what the recent commits have been about. Finish: fix the secret-scan references, run the slow test green on the 5090, complete calibration. Then Step 1. Running the campaign on an uncalibrated metric just manufactures more provisional cells.
