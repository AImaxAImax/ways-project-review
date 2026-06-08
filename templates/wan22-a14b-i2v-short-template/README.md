# Wan2.2 A14B I2V short template

This is the saved winning template from `sharks_older_than_trees` v27, approved by Josh as: “This is it! This is the model.”

## Use when

- We need a realistic short-form video base from still plates.
- We want actual I2V motion rather than Ken Burns/static zoom.
- Visual realism matters more than speed.
- Final polish/captions can happen downstream in CapCut or another editor.

## Proven project example

Source project:

`C:\dev\curious-shorts\test_cases\sharks_older_than_trees`

Winning output:

`outputs/wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_discord.mp4`

Master:

`outputs/wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_audio.mp4`

## Proven Comfy workflow

Comfy workflow:

`C:\dev\vj-engine\comfyui\workflows\wan2_2_a14b_gguf_lightning_i2v_smoke.json`

Important repair:

- Keep the original `WanImageToVideo` workflow.
- Set node `39.inputs.vae_name` to `wan_2.1_vae.safetensors`.
- Do **not** swap to the newer `wan2.2_vae.safetensors` in this WSL/Comfy install. It caused latent/channel mismatch failures.
- Do **not** use ad-hoc `Wan22ImageToVideoLatent` patches unless retested.

## Proven render settings

- Model lane: Wan2.2 A14B GGUF Lightning I2V smoke workflow
- Input aspect: 9:16 still plates
- I2V clip size: `432x768`
- I2V length: `25` frames
- Timeline FPS: `24`
- Output master: `1080x1920`, H.264, AAC audio
- Discord preview: `720x1280`, H.264, AAC audio
- Strategy: generate short true-motion Wan clips, stretch each clip to match VO beat duration, then mux VO.

## Prompt pattern

Positive prompt:

```text
premium [genre] image-to-video from the exact still. Preserve the exact subject, composition, colors, and realistic style. Add subtle true motion: camera creep, gentle parallax, particles, water/light shimmer, small subject motion where appropriate. Preserve anatomy and framing. No scene cut.
```

Negative prompt:

```text
text, subtitles, readable letters, watermark, logo, UI, hard cut, scene transition, horror, blood, attack, morphing animal anatomy, duplicated fins, distorted face, melted geometry, jitter, flicker, low quality, blurry, compression artifacts
```

## Batch structure

Each shot needs:

- `id`
- `source still path`
- `duration`
- `caption text` for final caption pass
- `seed`
- `I2V prompt`

Use sequential seeds so reruns are traceable, for example:

```text
627101, 627102, 627103...
```

## Assembly pattern

For each Wan clip:

1. Download Comfy output.
2. Stretch from `25 / 24 = 1.0417s` to the target beat duration using `setpts`.
3. Scale/crop to `1080x1920`.
4. Concatenate by frames.
5. Encode master with H.264 `crf 18`.
6. Mux VO with AAC `160k`, `48kHz`.
7. Produce Discord preview at `720x1280`, `crf 24`, AAC `96k`.
8. Generate contact sheet at `fps=1`, `scale=270:480`, `tile=6x4`.

## QA gate

Accept as template when:

- It has actual I2V motion, not just still zoom.
- No catastrophic morphing, anatomy melt, duplicated fins, or text artifacts.
- Contact sheet and full playback look coherent.
- Audio is present in ffprobe.
- Captions are either absent intentionally for base render or handled in final caption pass.

For publish-ready WAYS/shorts, still require final caption pass and 9/10 visual gate.

## Final-polish/caption lane

After this Wan template produces a clean base, run the final-polish lane rather than editing the base in place:

```bash
python3 tools/final_polish_pack.py \
  --input <clean_wan_master.mp4> \
  --manifest <wan_manifest.json> \
  --outdir <outputs/final_polish_slug> \
  --title <short-slug>
```

The lane preserves `clean_master_unmodified.mp4`, generates `.ass`/`.srt`, burns large centered captions with yellow key-word emphasis, normalizes audio, creates a 1080x1920 publish candidate, creates a 720x1280 Discord preview, writes ffprobe JSON, and produces a `PUBLISH_GATE.md` checklist. Use CapCut/Whisper word timestamps to upgrade the same pack when true active-word karaoke is required.

Full process: `docs/final-polish-lane.md`.

## Reusable harness

The generalized runner is:

```bash
python3 scripts/render_wan_harness.py test_cases/<topic>/render_wan22_harness_config.json
```

For config/preflight only, without Comfy or ffmpeg assembly:

```bash
python3 scripts/render_wan_harness.py test_cases/<topic>/render_wan22_harness_config.json --dry-run --no-assemble
```

For reassembling from already-rendered per-shot clips listed in the config:

```bash
python3 scripts/render_wan_harness.py test_cases/<topic>/render_wan22_harness_config.json --skip-wan
```

A new topic should only require editing/copying the JSON config: `project_root`, `slug`, `output_dir`, `voiceover`, `workflow`, render settings/overrides, and the `shots[]` list (`id`, `image`, `duration`, `caption`, `seed`, `prompt`, optional `clip`). Do not edit the Python harness for topic-specific paths.

## Saved files in this template folder

- `README.md` — this recipe
- `recipe.json` — machine-readable settings
- `render_harness_config.template.json` — copy/edit starter config for a new topic
- `run_v27_wan22_animated_frames.py` — copied winning batch script
- `wan2_2_a14b_gguf_lightning_i2v_smoke.json` — copied Comfy workflow snapshot
