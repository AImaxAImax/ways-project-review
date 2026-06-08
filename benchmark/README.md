# WAYS Local Video Model Benchmark Implementation

Protocol source: `docs/WAYS_MODEL_BENCHMARK_PROTOCOL.md`.

This directory implements the protocol as an agent-runnable benchmark scaffold. The current implementation is intentionally conservative: it will run the proven `wan22_i2v` lane and refuses unverified model lanes until Phase 0 confirms the right workflow/conditioning path. This avoids invalid scores from bypassed I2V conditioning.

## Files

- `benchmark/config/benchmark_manifest.json` — locked model/plate/seed manifest.
- `benchmark/plates/` — locked golden plate copies with SHA-256 hashes in the manifest.
- `benchmark/results/phase0_status.json` — Comfy/model/workflow inventory and confound checks.
- `benchmark/runs/` — per-cell generated configs, render outputs, QA reports, and result JSON.
- `benchmark/results/model_matrix.md` — auto-aggregated matrix skeleton.

## Commands

Refresh locked plates and manifest:

```bash
python3 scripts/setup_ways_model_benchmark.py
```

Run Phase 0 inventory/status:

```bash
python3 scripts/benchmark_phase0_status.py
```

Dry-run one proven Wan2.2 I2V cell:

```bash
python3 scripts/run_ways_model_benchmark.py --model wan22_i2v --category 1 --seeds 627101 --limit 1 --dry-run
```

Run one real Wan2.2 I2V render/score cell:

```bash
python3 scripts/run_ways_model_benchmark.py --model wan22_i2v --category 1 --seeds 627101 --limit 1 --report-only
```

Run the full Wan2.2 baseline grid after confirming compute budget:

```bash
python3 scripts/run_ways_model_benchmark.py --model wan22_i2v --seeds 627101,627102,627103,627104,627105 --report-only
```

Update matrix from results:

```bash
python3 scripts/analyze_ways_model_benchmark.py
```

## Phase 0 status from implementation pass

- ComfyUI reachable at `127.0.0.1:8188`.
- RTX 5090 detected.
- `wan22_i2v` preflight is ready: high/low GGUF refs found, `wan_2.1_vae.safetensors` available, dry-run passed.
- A real one-cell Wan render smoke succeeded after clearing/restarting ComfyUI. The smoke cell was `cat1_shark_a / wan22_i2v / seed_627101`, render time 679.9s, QA score 92, no blockers. See `benchmark/results/phase0_real_smoke_attempt.json`.
- `ltx23_fp8`, `ltx23_distilled`, and `wan22_t2v` have model files available but no verified benchmark workflow wired in this scaffold yet.
- `hunyuan15` workflow exists, but its required GGUF and VAE are missing, so it is not allowed into scoring yet.
- `wan22_i2v_hi` and `cogvideox15` are marked missing until downloaded and smoke-tested.

## Guardrails implemented

- T2V is listed only for Category 5.
- Wan higher-precision and native-res questions stay out of the cross-model matrix.
- Scoring uses `tools/local_video_qa.py` with `config/qa_thresholds.json`.
- Human blind phone review remains the final authority; the matrix does not auto-fill human scores.
- Unverified model IDs are deliberately refused by `run_ways_model_benchmark.py`.
