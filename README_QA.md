# Local video QA proxy

First-pass QA for local Shorts/Reels/TikTok candidates. It creates review artifacts and a machine-readable gate report, but it never uploads or publishes anything.

## What it checks

- `ffprobe` specs: video codec, dimensions, FPS, duration, audio streams, sample rate.
- Duration alignment against either `--expected-duration` or a manifest with `shots[].duration` / `segments[].duration`.
- Audio presence by default (`--no-require-audio` if intentionally silent).
- Contact sheet generation for harsh visual review.
- Optional text/logo/artifact/anatomy scan through either:
  - `--vlm-command 'your_scanner --image {image}'`, where stdout is JSON, or
  - `--openai-vlm-url http://host:8000/v1 --vlm-model <model>` for an OpenAI-compatible vision server.
- Optional metric harness for animal/source shots with `--source-image`: CLIP image-embedding preservation, DINOv2 structure preservation, temporal consistency, optical-flow motion magnitude, and VLM-derived artifact flags. These metrics are advisory/report-only until a calibrated `--thresholds config/qa_thresholds.json` exists; without thresholds, the tool computes `qa_report.json` + `metrics_debug.json` but does not create metric blockers.

## Basic use

```bash
python3 tools/local_video_qa.py \
  --input test_cases/sharks_older_than_trees/outputs/wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_audio.mp4 \
  --expected-duration 23.916 \
  --outdir test_cases/sharks_older_than_trees/outputs/wan22_v27_animated_frames/qa_proxy
```

Outputs in `--outdir`:

- `qa_report.json` — score, blockers, warnings, parsed checks, VLM/source-preservation notes.
- `ffprobe.json` — raw ffprobe output.
- `contact_sheet.jpg` — sampled frame grid.
- `README_QA.md` — concise human review handoff.

Exit codes:

- `0`: no blockers.
- `1`: blockers found; do not publish.
- `2`: QA tooling error.

## Example VLM hook

```bash
python3 tools/local_video_qa.py \
  --input outputs/candidate.mp4 \
  --outdir outputs/candidate_qa \
  --openai-vlm-url http://host.docker.internal:8000/v1 \
  --vlm-model Qwen/Qwen2.5-VL-7B-Instruct
```

The VLM should be harsh about generated text, watermarks, UI, double captions, malformed animals, duplicated fins/limbs, melting, shimmer, jitter, and other publish blockers.

## Publish rule

This proxy is a gate, not a publisher. A pass means “ready for human/full-playback review,” not “auto-publish.”
