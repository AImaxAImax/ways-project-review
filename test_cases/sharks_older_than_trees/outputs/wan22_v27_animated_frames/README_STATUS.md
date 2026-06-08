# v27 Wan2.2 animation status

Goal: animate the accepted shark still frames using the same local Wan2.2-style motion lane used for the Wombat pass.

## What I attempted

- Built a 7-shot Wan2.2 runner: `scripts/run_v27_wan22_animated_frames.py`
- Used current accepted frame set from `scripts/render_v26_final_predator_audio.py`
- Targeted local ComfyUI at `http://127.0.0.1:8188`
- Confirmed ComfyUI is running on RTX 5090 and queue was idle before testing
- Started with a 25-frame true-motion pass per plate, intended to stretch/interpolate into the final edit like the Wombat v2 workflow

## Blocker found

The live ComfyUI/Wan plumbing is not currently rendering the older Wombat-style workflow cleanly.

Observed failures:

1. A14B GGUF workflow with original `WanImageToVideo` node:
   - `expected input ... to have 36 channels, but got 64 channels instead`

2. A14B GGUF workflow patched to `Wan22ImageToVideoLatent`:
   - with `wan2.2_vae.safetensors`: latent format size mismatch
   - with `wan_2.1_vae.safetensors`: start-image latent size mismatch

3. 5B TI2V fallback workflow:
   - blocked because `wan2.2_ti2v_5B_fp16.safetensors` is not installed in current ComfyUI; only `flux1-schnell-fp8.safetensors` is available to `UNETLoader`.

## Decision

Do not hand back a fake/static-motion pass as “animated like Wombat.” The right next step is to repair/restore the Wan2.2 Comfy workflow/model set, then run a one-shot pilot on the final predator frame and only batch all seven shots after a real MP4 lands.

## Useful artifacts

- Batch runner scaffold: `scripts/run_v27_wan22_animated_frames.py`
- A14B fixed pilot attempts:
  - `scripts/run_v27_wan22_a14b_fixed_pilot.py`
  - `scripts/run_v27_wan22_a14b_fixed_pilot_vae21b.py`
  - `scripts/run_v27_wan22_a14b_fixed_pilot_halfsource.py`
- 5B fallback pilot: `scripts/run_v27_wan22_5b_pilot.py`
