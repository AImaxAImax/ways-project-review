# WAYS Local Video Model Benchmark Protocol

**Goal:** Determine the best local model **per use case**, not in the abstract. Quality is the primary axis; render time and VRAM are tiebreakers only.
**Hardware:** RTX 5090, ComfyUI on `127.0.0.1:8188`.
**Output:** a model x use-case recommendation matrix that feeds directly into the kanban’s Gate 2 lane routing.
**Core principle:** change one variable (the model). Everything else is fixed. Each model still gets the per-model setup it needs to run *correctly* (VAE, dims, noise staging), and every such adaptation is documented, not hidden.

-----

## 1. Models under test

### Core bracket (already installed)

|ID               |Model                                                |Type|Role in test                                                                               |
|-----------------|-----------------------------------------------------|----|-------------------------------------------------------------------------------------------|
|`wan22_i2v`      |Wan2.2-I2V-A14B GGUF Q5_K_M (High+Low noise, 2-stage)|I2V |Reigning champion. The baseline everything is measured against.                            |
|`ltx23_fp8`      |LTX-2.3-22b-dev-fp8                                  |I2V |Cinematic-motion challenger.                                                               |
|`ltx23_distilled`|LTX-2.3-distilled Q4_K_M                             |I2V |Faster LTX; is the speed worth the quality cost?                                           |
|`wan22_t2v`      |Wan2.2 T2V 14B Q4_K_M (High+Low)                     |T2V |**No plate input.** Only eligible where no specific subject must be preserved (Category 5).|

### Challengers to download (5090 / 32GB is the relevant tier)

|ID            |Model                                                    |Type|Download rationale                                                                                                                                                                                                   |Enters categories         |
|--------------|---------------------------------------------------------|----|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
|`wan22_i2v_hi`|Wan2.2-I2V-A14B at **higher precision** (Q8, or fp8/fp16)|I2V |**Sleeper highest-value test.** Same trusted model, more bits. Determines whether quantization is the current quality ceiling. 50-series has hardware FP8/NVFP4 paths, so the cost is low.                           |1, 3 (quant ablation only)|
|`hunyuan15`   |HunyuanVideo 1.5 (~8.3B, quantized, with offload)        |I2V |The newer 1.5 runs on consumer VRAM and currently leads community rankings on motion realism and scene coherence. The old “wiring unproven” note predates it. The one model that might beat Wan where Wan is weakest.|2, 5                      |
|`cogvideox15` |CogVideoX-1.5-5B                                         |I2V |The consumer-GPU option for ~10-second clips. Tests the **longer-clip** bottleneck, not realism.                                                                                                                     |long-clip probe only      |

**Dropped from the bracket:** the old generic `hunyuan` workflow-files entry. Replaced by `hunyuan15`, which gets a proper Phase 0 smoke test before it earns bracket entry. If it won’t wire cleanly, drop it and note why.

### Two hard rules on scope

1. **T2V models cannot be scored on subject preservation.** They have no plate. They compete only in Category 5. Scoring a T2V clip against a source plate is a methodology error.
1. **Challengers enter only the categories where they could plausibly win** (see the “Enters categories” column). Do not run every model in every category. A 4-model core grid that stays finishable beats an 8-model grid that never completes. Challengers are sparse, targeted entries.

-----

## 2. Use-case taxonomy (the test categories)

These map to your real production lanes. Each category has its own winner.

|Cat|Name                              |What matters                               |Example plates                                        |
|---|----------------------------------|-------------------------------------------|------------------------------------------------------|
|1  |**Strong-prior realism hold**     |Identity must not drift; subtle motion only|octopus, axolotl, shark                               |
|2  |**Large controlled motion**       |Big movement *without* morphing            |owl head-turn ~270°, cuttlefish color ripple          |
|3  |**Subtle reveal / transformation**|Controlled change, not random drift        |flamingo grey to pink, platypus UV glow, reindeer eyes|
|4  |**Dynamic effect / payoff**       |Energy; tolerates more abstraction         |electric eel discharge, water flash                   |
|5  |**Cinematic establishing / scale**|Big camera motion, low anatomy constraint  |deep-time landscape, galaxy, forest-to-stars          |
|6  |**Process / concept** (probe)     |Known failure mode                         |internal-anatomy / diagram beat                       |

Category 5 is the only one where `wan22_t2v` and LTX get a fair shot at beating Wan I2V, because preservation isn’t the constraint. Category 6 is a single cheap probe to confirm no local model rescues photoreal process beats (settles whether MG-lane routing stays mandatory).

-----

## 3. Golden plate set (fixed inputs)

- Pick **2 plates per category** from accepted WAYS stills plus a few new ones. Lock them. **No regenerating plates mid-test.**
- Plates must clear the existing plate gate first (no text/logos, caption-safe negative space, phone read, realistic anatomy, animation-friendly).
- Store as `benchmark/plates/cat{N}_{slug}_{a,b}.png`. Record source plate hash so scoring can reference the exact original.
- For Category 5, “plate” for the T2V entry is just the text prompt; the I2V entries use the matching still.

-----

## 4. Fixed vs varied parameters

**FIXED across all runs:**

- The golden plate set.
- Target clip duration and the timeline fps (24).
- Output resolution and the upscale path (hold the 432x768 to 1080x1920 path constant). If you want to test native higher-res, that is a **separate documented variable**, run as its own pass, never mixed in.
- Prompt semantics per plate (same meaning; model-appropriate syntax allowed and logged).
- The seed bank.
- The VLM scorer, its calibration, and the human review protocol.

**VARIED:** the model only.

**Per-model required setup (document each, this is correctness not cheating):**

- `wan22_i2v` / `wan22_t2v` / `wan22_i2v_hi`: use `wan_2.1_vae.safetensors`. **Do not** swap to the 2.2 VAE (caused latent/channel mismatch). High-noise to low-noise 2-stage as in the shark v27 template.
- `ltx23_*`: dimensions must be **/32-clean**. And **verify the I2V conditioning path is actually active** before scoring (see confound checklist). A bypassed conditioning path silently turns LTX I2V into T2V and invalidates every preservation number.
- `hunyuan15`: quantized weights + offload to fit 32GB; confirm clean I2V conditioning in Phase 0 before bracket entry.
- `cogvideox15`: run at its native clip length for the long-clip probe; do not force it into the short-clip realism categories.

**SEED PROTOCOL:** run the **same bank of 5 seeds** per (model x plate). Report **median and best**, never a single seed. A model judged on one lucky or unlucky seed tells you nothing. Suggested bank: reuse `627101-627105`.

### Two ablations run as their own labeled passes (not mixed into the main grid)

- **Quant ablation:** `wan22_i2v_hi` vs `wan22_i2v` on Categories 1 and 3 only, identical plates/seeds/prompts. The only variable is precision. This answers “is quantization my quality ceiling?” and is the highest-value, lowest-effort test in the whole protocol.
- **Native-resolution ablation:** Wan2.2 I2V at a higher native resolution vs the 432x768-then-upscale path, same plates. Isolates how much fine detail the upscale path is costing you, separately from model choice.

Keep both ablations out of the cross-model winner matrix. They are within-model questions, reported separately.

-----

## 5. Scoring rubric

Quality is weighted heaviest, per the brief. Three tiers.

### Tier 1: Automated quantitative (calibrated first, see Phase 0)

- **Subject preservation:** CLIP cosine (source plate vs generated frames) and DINOv2 structural cosine. **Use CLIP/DINO, not SSIM** (SSIM rewards static frames and misses semantic drift). Applies to Categories 1-4 only.
- **Temporal consistency:** frame-to-frame LPIPS and a flicker score. Lower is better.
- **Motion presence:** mean optical-flow magnitude. You want a healthy band: not zero (dead Ken-Burns), not chaotic (morphing).
- **Artifact / anatomy:** VLM (gemma3:12b) flags for generated text/logos, extra or melting limbs, texture shimmer, repeated-still fatigue.

### Tier 2: Human blind review (FINAL AUTHORITY)

- Review every clip **on a phone**, 1-10, ranked **within each (category x plate) bracket**.
- **Blind it.** Anonymize the model-to-clip mapping before review. You already have a stated bias toward Wan (“This is it!”); blinding is what makes the result trustworthy.
- When human score and automated score disagree, the human wins **and** the disagreement is logged to recalibrate the VLM.

### Tier 3: Cost (tiebreaker only)

- Render time per clip, peak VRAM, max stable clip length and fps.

-----

## 6. Decision rule

For each category:

> Winner = highest **median human blind score**, among models clearing the category’s preservation threshold (Cat 1-4). Render cost breaks ties only when human scores are within ~0.5.

Quality first. Speed never beats a clearly better-looking clip; it only chooses between near-equals. Output the matrix in section 8, then promote the result into the SKILL.md and the kanban Gate 2 routing rules.

-----

## 7. Execution phases (agent-runnable)

**Phase 0 — Calibration, downloads, and smoke tests (do not skip).**

1. Lock the golden plate set.
1. Download challengers: higher-precision Wan2.2, HunyuanVideo 1.5, CogVideoX-1.5-5B.
1. Smoke-test each model runs *correctly*: Wan VAE correct and 2-stage firing; LTX /32 dims and **conditioning path confirmed active**; `hunyuan15` wires cleanly with offload (if not, drop it and note why); `cogvideox15` produces a clean long clip.
1. Calibrate the VLM scorer: hand-label ~15-20 clips, tune the VLM until its flags track your labels. Calibrate **before** trusting any automated number. (This is the calibration-before-gating rule.)

**Phase 1 — I2V preservation bracket (Categories 1-4).**

- Core: `wan22_i2v`, `ltx23_fp8`, `ltx23_distilled`.
- Challenger entry: `hunyuan15` enters **Category 2 only** (its motion-realism strength).
- 2 plates x category x model x 5 seeds. Score Tiers 1-3.

**Phase 1b — Quant + native-res ablations (within-model).**

- `wan22_i2v_hi` vs `wan22_i2v` on Cat 1 and 3. Native-res vs upscale pass on Wan. Reported separately from the cross-model matrix.

**Phase 2 — Cinematic / scale bracket (Category 5).**

- Models: all I2V entries **plus** `wan22_t2v` and `hunyuan15`. Preservation not scored; judge motion quality, coherence, awe.

**Phase 3 — Process-beat probe (Category 6) + long-clip probe.**

- Process beat: one plate, best 2 models, few seeds. Confirm (or refute) that MG-lane routing stays mandatory.
- Long-clip: `cogvideox15` vs `wan22_i2v` on one plate at ~10s. Does a longer single generation beat stretched short clips?

**Phase 4 — Analysis.**

- Fill the matrix. Log seed variance. Write disagreements back into VLM calibration. Update SKILL.md + Gate 2.

**Phase 5 — autoresearch loop (ONLY after Phase 0 calibration is trusted).**

- Scope: not model selection (that’s done above). This loop optimizes **per-shot prompt, motion strength, conditioning strength, and seed** for the chosen winning model on a specific plate.
- Mechanism (mirrors karpathy/autoresearch): the agent edits a single params/workflow file (the `train.py` analog), generates one candidate under a **fixed compute budget**, scores it with the calibrated metric, keeps or discards, repeats ~100x overnight. You edit a `program.md` defining the search space and guardrails; you never touch the generation code directly.
- **Hard precondition:** the calibrated metric’s agreement with your eye must be measured and acceptable. An autonomous keep/discard loop on an uncalibrated proxy optimizes the proxy, not the video (Goodhart). If Phase 0 agreement is weak, Phase 5 stays off and optimization stays manual.
- Output: top ~5 candidates per plate surfaced for your morning phone-size review. The loop proposes; you dispose.

-----

## 8. Results matrix (template the agent fills)

|Category         |wan22_i2v|ltx23_fp8|ltx23_distilled|wan22_t2v|hunyuan15|Winner|Notes                |
|-----------------|---------|---------|---------------|---------|---------|------|---------------------|
|1 Realism hold   |         |         |               |n/a      |n/a      |      |                     |
|2 Large motion   |         |         |               |n/a      |         |      |hunyuan15 enters here|
|3 Reveal         |         |         |               |n/a      |n/a      |      |                     |
|4 Effect         |         |         |               |n/a      |n/a      |      |                     |
|5 Cinematic/scale|         |         |               |         |         |      |full field           |
|6 Process (probe)|         |         |               |n/a      |n/a      |      |                     |

`n/a` = model deliberately not entered in that category (sparse-by-design, not missing data). `cogvideox15` and the quant/native-res ablations are reported in their own sub-tables, not here.

Per cell, record: `median_human / best_human | CLIP | flicker | sec_per_clip | VRAM`.

-----

## 9. Confound checklist (the traps that invalidate results)

- [ ] **LTX I2V conditioning path verified active.** If bypassed, LTX is secretly doing T2V and every preservation score is garbage. This is the exact bug from the prior conditioning-strength sweep.
- [ ] **LTX dimensions /32-clean.** Off-grid dims degrade LTX output.
- [ ] **Wan uses `wan_2.1_vae.safetensors`**, not the 2.2 VAE. 2-stage high to low noise confirmed firing.
- [ ] **T2V scored only in Category 5.** Never against a source plate.
- [ ] **Preservation scored with CLIP/DINO, not SSIM.**
- [ ] **Same 5-seed bank per cell;** report median, not cherry-picked best.
- [ ] **Upscale path held constant** (or native-res tested as a separate, labeled pass).
- [ ] **Human review blinded** to model identity.
- [ ] **VLM calibrated to human labels before** any automated gating.
- [ ] **Challengers entered sparsely**, only in categories where they could win.
- [ ] **Quant ablation kept separate** from the cross-model matrix (within-model question).
- [ ] **Phase 5 autoresearch stays off until Phase 0 metric agreement is measured and acceptable.**

-----

## 10. What this produces

A defensible, per-use-case model recommendation grounded in your plates and your hardware, with variance and cost documented. The likely outcome is not “one model wins everything” but a routing table: Wan2.2 I2V for realism-critical categories, HunyuanVideo 1.5 or LTX possibly taking Category 5 cinematic motion, T2V only where no subject must survive, CogVideoX considered only if long single-generation clips beat stretched short ones, and a hard confirmation that process beats stay in the motion-graphics lane. Plus two within-model answers: whether quantization is your quality ceiling, and how much the upscale path costs you.

That routing table drops straight into Gate 2. And once the calibrated metric exists, Phase 5 turns the same infrastructure into an overnight per-shot optimizer, which is where the autoresearch pattern actually pays off.