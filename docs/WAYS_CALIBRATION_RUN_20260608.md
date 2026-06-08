# WAYS Calibration Run Notes - 2026-06-08

This documents the live calibration work copied from `/mnt/c/dev/curious-shorts` into this review repo. The live tree is **not** a git repo, so lightweight code/config/results were copied here to make the run auditable without tracking heavy media.

## What was run

1. Advisory first-frame calibration generated `config/qa_thresholds.json`.
2. Candidate explicit-source calibration generated `config/qa_thresholds_explicit_candidate.json`.
3. Candidate per-shot explicit-source calibration generated `config/qa_thresholds_per_shot_candidate.json` and `calib/ways_scoring_harness_20260608/calibration_results_per_shot_candidate.json`.

No model campaign was started and no uploads/publishing happened.

## Current status

| Run | Agreement | Blocking | Decision |
| --- | ---: | --- | --- |
| Explicit primary/canonical source candidate | 5/5 (100.0%) | false | advisory |
| Per-shot source candidate | 14/16 (87.5%) | false | advisory |

The per-shot run stayed advisory because the labels are candidate-grade and agreement is below the quality bar.

## Per-shot candidate results

| slug | human | predicted | match | clip_min | dino_min | temporal | motion | shots |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| shark_v27 | pass | pass | yes | 0.888449 | 0.857369 | 0.504805 | 6.828149 | 7 |
| frog_v17 | pass | pass | yes | 0.658824 | 0.597337 | 0.521761 | 5.555588 | 6 |
| frog_v16 | pass | pass | yes | 0.658824 | 0.597337 | 0.521761 | 5.555588 | 6 |
| frog_v15 | pass | pass | yes | 0.658824 | 0.597337 | 0.521761 | 5.555588 | 6 |
| mantis_v30 | pass | pass | yes | 0.403516 | 0.013949 | 0.566823 | 3.625355 | 8 |
| owl_v03 | pass | pass | yes | 0.944787 | 0.988426 | 0.353906 | 3.154538 | 5 |
| owl_v04 | pass | pass | yes | 0.834465 | 0.872876 | 0.305652 | 3.003716 | 4 |
| octopus_v01 | pass | pass | yes | 0.948443 | 0.950256 | 0.582238 | 9.600125 | 5 |
| wombat_v01 | fail | pass | NO | 0.916607 | 0.940571 | 0.547925 | 9.412724 | 5 |
| tardigrade_v01 | fail | pass | NO | 0.909701 | 0.97023 | 0.402018 | 5.482888 | 5 |
| saturn_v01 | fail | fail | yes | 0.22818 | 0.720229 | 0.386161 | 1.829402 | 5 |
| saturn_v02 | fail | fail | yes | 0.761618 | 0.507654 | 0.434932 | 1.722284 | 5 |
| mantis_v04 | fail | fail | yes | 0.285965 | 0.002301 | 0.265632 | 0.860504 | 8 |
| mantis_v11 | fail | fail | yes | 0.441828 | 0.215168 | 0.638517 | 6.041937 | 8 |
| mantis_v17 | fail | fail | yes | 0.436315 | 0.024847 | 0.62377 | 5.919415 | 8 |
| mantis_v25 | fail | fail | yes | 0.410092 | -0.009794 | 0.574874 | 3.55985 | 8 |

## Disagreements

- `wombat_v01`: human `fail`, predicted `pass`, reasons `[]`
- `tardigrade_v01`: human `fail`, predicted `pass`, reasons `[]`

## Files added for auditability

- `scripts/calibrate_ways_qa_harness.py`
- `tools/local_video_qa.py`
- `config/qa_thresholds.json`
- `config/qa_thresholds_explicit_candidate.json`
- `config/qa_thresholds_per_shot_candidate.json`
- `calib/ways_scoring_harness_20260608/labels*.json`
- `calib/ways_scoring_harness_20260608/calibration_results*.json`

Heavy generated media, extracted shot segment MP4s, contact sheets, and per-shot image outputs are intentionally not tracked.

## Next step before blocking

Human-review the per-shot source map, especially wombat/tardigrade/mantis/owl. Only rerun with `--enable-blocking` after reviewed source labels and higher agreement.
