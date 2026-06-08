# Local video QA: sharks_older_than_trees_v27_wan22_animated_audio.mp4

Generated: 2026-06-05T18:53:19
Verdict: **PASS_WITH_WARNINGS**
Score: **95/100**

## Blockers
- none

## Warnings
- visual scan warning: base render still needs caption/full-motion review before publish

## Artifacts
- JSON report: `qa_report.json`
- ffprobe: `ffprobe.json`
- Contact sheet: `contact_sheet.jpg`

## Required manual/human review before publish
- Play the full candidate at phone size; first 2 seconds must read instantly.
- Inspect contact sheet for generated text, logos, watermarks, UI, double captions, malformed animals, duplicated fins/limbs, melting, shimmer, or jitter.
- Verify captions are intentional, readable, and not colliding with platform UI.
- For animal/source-preservation shots, prefer CLIP/DINO or full-frame VLM review if this proxy only ran RGB similarity.

This QA proxy does not auto-publish.
