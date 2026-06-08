# WAYS Harness Calibration Runbook

Purpose: produce `config/qa_thresholds.json` from human-labeled clips before any benchmark cell is trusted as non-provisional.

Canonical rule: human phone-size review is authoritative until measured agreement proves the automated gate tracks the eye. If agreement is weak, keep the metric advisory and report human-blind rankings with automated metrics only as context.

## Preconditions

1. The slow real-model path has run green, not skipped:

   ```bash
   PYTHONPATH=. pytest -m slow -q tests/test_local_video_qa.py -rs
   ```

2. A calibration set of 15-20 clips exists in the live media tree (`curious-shorts`), with source plates where preservation is meaningful.
3. Each calibration clip has a human label recorded before fitting thresholds:
   - `human_verdict`: `pass` or `fail`
   - optional `human_score`: 1-10
   - brief failure label when failed: anatomy drift, identity drift, flicker, dead motion, bad motion, artifact, caption/format issue, etc.

## Build the labeled set

Use clips from accepted and rejected drafts, not only benchmark outputs. The set should include at least:

- strong animal realism holds that passed by eye
- identity/anatomy failures that metrics should catch
- low-motion/dead renders
- high-motion or flicker failures
- one or more borderline clips where disagreement is likely

Keep model identity hidden from the human reviewer when labels are assigned.

## Run report-only metrics

For each labeled clip, run `tools/local_video_qa.py` in report-only mode first. Example shape:

```bash
PYTHONPATH=. python3 tools/local_video_qa.py   --input <clip.mp4>   --source-image <approved_plate.png>   --outdir <qa_outdir>   --frame-sample-fps 6   --no-require-audio
```

Do not use threshold blocking while fitting thresholds. Capture each clip's `qa_report.json` and `metrics_debug.json` next to the label record.

## Fit thresholds

Fit thresholds to separate human pass/fail labels. Use the smallest set of blockers that materially improves agreement:

- `clip_preservation_min`
- `dino_structure_min`
- `temporal_consistency_min`
- `motion_magnitude_low`
- `motion_magnitude_high`

Record disagreements, not just the final agreement rate. Disagreements are calibration data.

## Write `config/qa_thresholds.json`

Write the threshold config in the live tree where media scoring runs. Minimum required metadata:

```json
{
  "version": "ways-qa-thresholds-v1",
  "fail_closed": true,
  "calibrated_against": "15-20 human-labeled clips",
  "agreement": "N/N = P% vs human pass/fail labels",
  "clip_preservation_min": 0.0,
  "dino_structure_min": 0.0,
  "temporal_consistency_min": 0.0,
  "motion_magnitude_low": 0.0,
  "motion_magnitude_high": 0.0
}
```

Use real fitted values, not the zero placeholders above.

## Prove the gate before trusting it

1. Run a known-bad calibration clip with thresholds and confirm a blocker fires.
2. Run a known-good calibration clip and confirm no blocker fires.
3. Re-run:

   ```bash
   PYTHONPATH=. pytest -q tests/test_local_video_qa.py
   PYTHONPATH=. pytest -m slow -q tests/test_local_video_qa.py -rs
   ```

4. Only after those checks pass may new benchmark cells be scored as calibrated.

## If agreement is weak

Do not force the metric into a blocker. Keep `fail_closed: true` for required metric availability, but keep the benchmark campaign taste-led:

- human blind median/best scores decide routing
- automated metrics are context columns
- every human-vs-metric disagreement feeds the next calibration pass

## Output

- `config/qa_thresholds.json` in the live tree
- calibration label table with human verdicts, metric values, gate verdicts, and disagreements
- a short note in `benchmark/results/model_matrix.md` or adjacent calibration results naming agreement rate and threshold version
