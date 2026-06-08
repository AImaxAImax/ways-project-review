# Local image generation setup — ComfyUI SDXL Turbo

Status: working.

## What is running
ComfyUI is running from the Windows venv, launched from WSL:

```bash
/mnt/c/Windows/System32/cmd.exe /C "cd /d C:\dev\ComfyUI && venv\Scripts\python.exe main.py --listen 127.0.0.1 --port 8188"
```

Health check:

```bash
curl http://127.0.0.1:8188/system_stats
```

Verified:
- OS: Windows Comfy process (`win32`)
- GPU: NVIDIA GeForce RTX 5090
- VRAM: ~32GB
- PyTorch: `2.11.0+cu130`

## Model installed
`C:\dev\ComfyUI\models\checkpoints\sd_xl_turbo_1.0_fp16.safetensors`

Downloaded from:
`https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors`

## Agent script
`test_cases/sharks_older_than_trees/scripts/comfy_sdxl_turbo_generate.py`

This queues a simple Comfy workflow:
- `CheckpointLoaderSimple`
- `CLIPTextEncode` positive/negative
- `EmptyLatentImage` 768×1344
- `KSampler` / euler / simple / 5 steps / cfg 1.5
- `VAEDecode`
- `SaveImage`

Outputs are downloaded into:
`test_cases/sharks_older_than_trees/assets/comfy_sdxl_turbo_v1/`

## First smoke/candidate outputs
- `assets/comfy_sdxl_turbo_v1/sharks_smoke_00001_.png`
- `assets/comfy_sdxl_turbo_v1/ancient_ocean_wide_00001_.png`
- `assets/comfy_sdxl_turbo_v1/hero_shark_calm_00001_.png`
- `assets/comfy_sdxl_turbo_v1/before_forests_awe_00001_.png`
- `outputs/comfy_sdxl_turbo_first_contact_sheet.jpg`

## Initial visual read
Best first usable candidate: **#4 / `before_forests_awe_00001_.png`**.

Major defects across candidates:
- Some anatomy is off, especially duplicated shark tails/fins.
- #3 is too sharp/teeth-forward and less kid-safe.
- #1 has a floating/tail-like artifact under the main shark.
- All are good enough to prove the pipeline, not final enough for brand lock.

## Next quality improvements
- Generate 8–12 candidates per shot and curate.
- Add consistency prompt terms: `same art direction, soft natural history museum animation, gentle ancient shark, no open mouth`.
- Consider SDXL base/refiner or a stronger still-image model later; Turbo is fast but less precise.
