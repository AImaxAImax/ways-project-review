# Shark v27 next-lane benchmark — 2026-06-05

Task: compare next local/video lanes against the saved shark v27 Wan2.2 template, using benchmark artifacts rather than one cherry-picked shot. Do not replace the template unless clearly better.

## Benchmark baseline

Current template remains:

- Lane: `baseline_v27_wan22_a14b_i2v`
- Workflow: `/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json`
- Critical setting: original `WanImageToVideo` lane with `wan_2.1_vae.safetensors`
- Clip render: `432x768`, `25f`, `24fps`, assembled/upscaled to full short
- Artifacts:
  - `baseline_v27/contact_sheet_v27_wan22.jpg`
  - `baseline_v27/ffprobe_master.json`
  - source master: `../wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_audio.mp4`
  - source Discord preview: `../wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_discord.mp4`

Harsh QA: baseline has coherent real I2V movement across the 7-shot suite, no obvious generated text/logos in sampled frames, and enough subject/environment stability to remain the benchmark. Known blockers remain: source clips are only 432x768/25f and stretched, detail is soft after 1080x1920 upscale, and final publish still needs a caption/polish pass.

Decision: KEEP TEMPLATE.

## Lane 1 — A14B original VAE21 single-shot retest

- Lane id: `a14b_original_vae21_single_shot_retest`
- Representative shot: Shot 07 final predator
- Script: `scripts/run_v27_wan22_a14b_original_vae21_pilot.py`
- Workflow: `/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json`
- VAE: `wan_2.1_vae.safetensors`
- Seed: `627401`
- Output specs: 432x768 H.264, 25 frames, 1.041667s
- Artifacts:
  - clip: `../wan22_v27_animated_frames/pilot_a14b_original_vae21/shot07_wan22_a14b_original_vae21_432x768_25f_seed627401.mp4`
  - contact sheet: `pilot_a14b_retest/contact_sheet_a14b_retest_shot07.jpg`
  - ffprobe: `pilot_a14b_retest/ffprobe.json`

Harsh QA: visually coherent and premium enough for a final predator shot. No visible text/logos. Shark anatomy is mostly stable, but sampled frames show very little change: it reads as a restrained micro-motion pass, not a clearly stronger lane than v27. Also only one representative shot exists, so it cannot replace a 7-shot template.

Decision: HOLD / NO TEMPLATE CHANGE. Keep as useful shot-07 reference, not as a promoted lane.

## Lane 2 — A14B high-noise-only bypass smoke

- Lane id: `a14b_highnoise_only_bypass`
- Representative shot: Shot 01 ancient shark hook
- Script run: `scripts/run_v27_wan22_highonly_smoke.py`
- Workflow: `/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json`
- Bypass tested: decode high-noise latent directly by wiring node 8 samples to node 57; skip low-noise sampler
- VAE: `wan_2.1_vae.safetensors`
- Seed: `777101`
- Output specs: 432x768 H.264, 25 frames, 1.041667s
- Artifacts:
  - clip: `../wan22_v27_animated_frames/highonly_smoke/shot01_highonly_25f.mp4`
  - contact sheet: `highonly_bypass_smoke/contact_sheet_highonly_shot01.jpg`
  - ffprobe: `highonly_bypass_smoke/ffprobe.json`

Harsh QA: hard reject. Contact sheet is mostly colored noise/static with black remainder; no readable shark, no anatomy, no coherent scene, and no useful motion. This proves the bypass is not a viable shortcut around the low-noise stage.

Decision: REJECT / HOLD. Do not use this lane again except as a negative control.

## Lane 3 — Wan2.2 5B TI2V/I2V dependency check

- Lane id: `wan22_5b_ti2v_i2v`
- Requested representative shot: Shot 07 final predator
- Script run: `scripts/run_v27_wan22_5b_pilot.py`
- Workflow: `/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_ti2v_5b_i2v_smoke.json`
- Artifact:
  - `wan22_5b_ti2v_dependency_check/run_error.txt`

Run result: prompt validation failed before render. Node 37 `UNETLoader` requested `wan2.2_ti2v_5B_fp16.safetensors`, but Comfy reported available UNET choices as only `flux1-schnell-fp8.safetensors`.

Decision: HOLD / DEPENDENCY BLOCKED. Do not compare quality or promote until the exact 5B model is installed or the workflow is rewired to a known-good installed 5B asset.

## Overall promote/hold decision

No challenger clearly beats shark v27.

- Keep `wan22-a14b-i2v-short-template` as the current local-video template.
- Do not replace the template with high-noise-only bypass: it produces noise.
- Do not promote 5B TI2V yet: it is dependency-blocked, no render artifact.
- Keep A14B VAE21 shot-07 retest as a useful micro-motion shot reference, but it is not a full-suite replacement.

## Next benchmark recommendations

1. For 5B TI2V, install/verify `wan2.2_ti2v_5B_fp16.safetensors` or fetch a workflow that matches currently installed model files, then rerun a 4-shot suite: shots 01, 03, 06, 07.
2. Any future lane must render at least the 4 representative shots before promotion; a single nice final shark shot is not enough.
3. If a lane passes 3/4 shots, assemble a full 7-shot contact sheet and compare against v27 before touching the saved template.
