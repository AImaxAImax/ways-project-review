# Wan2.2 ComfyUI recovery status

Updated: 2026-06-05

## What is fixed

- ComfyUI is reachable at `http://127.0.0.1:8188` from WSL.
- Active server is Windows `C:\dev\ComfyUI` using `C:\Users\<user>\miniconda3\envs\env_uma\python.exe`.
- Required nodes are present:
  - `UnetLoaderGGUF`
  - `WanImageToVideo`
  - `VHS_VideoCombine` / `SaveVideo`
- A14B GGUF model lane is available:
  - `HighNoise\Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf`
  - `LowNoise\Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf`
- The current repair for the A14B I2V workflow is to keep the original `WanImageToVideo` node and use `wan_2.1_vae.safetensors` instead of `wan2.2_vae.safetensors`.

## Verified output

A real Wan2.2 A14B I2V pilot completed and landed here:

`outputs/wan22_v27_animated_frames/pilot_a14b_original_vae21/shot07_wan22_a14b_original_vae21_432x768_25f_seed627401.mp4`

ffprobe verified:

- H.264 video
- 432x768
- 24 fps
- duration `1.041667s`
- no audio stream

QA contact sheet:

`outputs/wan22_v27_animated_frames/pilot_a14b_original_vae21/shot07_contact.jpg`

Visual QA: shark anatomy stays coherent and the frame shows actual I2V drift/motion rather than pure Ken Burns, though it is short and subtle.

## Current run

A fresh ComfyUI restart was performed and the same repaired final-predator pilot was relaunched to confirm the lane still runs from a clean server.

Current background process:

`proc_209290bd20b5`

Current Comfy prompt id:

`b46f2b9e-806e-41b3-922d-c11b007b035c`

Observed GPU state during render:

- GPU utilization: 99%
- VRAM: ~31.9 GB / 32.6 GB used

So this is not idle. It is actively rendering, but the fresh-run low-noise sampler is much slower than the first successful pilot.

## Batch script repaired

`sections/run_v27_wan22_animated_frames.py` equivalent path:

`scripts/run_v27_wan22_animated_frames.py`

Patch applied:

- `WAN_LEN = 25`
- VAE set to `wan_2.1_vae.safetensors`
- comments added documenting the 2.2 VAE / latent mismatch pitfall

## Next actions when current prompt completes

1. Verify output with `ffprobe`.
2. If current clean-start pilot lands, launch the 7-shot repaired batch.
3. If it continues to take too long per shot, use the already proven pilot as the evidence that plumbing is fixed but do not burn a full 7-shot batch blindly. Downshift to shorter/lower-res I2V or selectively animate the strongest shark shots first.
