# QA — owl_head_turn draft v01

## Outputs
- Captioned master: `owl_head_turn_captioned_draft_v01.mp4`
- Discord preview: `owl_head_turn_discord_preview_v01.mp4`
- Contact sheet: `contact_sheet_owl_draft_v01.jpg`
- I2V source: `../wan22_owl_head_turn_v01/shot02_owl_head_turn_wan22_432x768_25f_seed812702.mp4`

## Technical verification
- Master: 1080x1920, H.264 + AAC, 15.232s, 9.53 MB
- Preview: 540x960, H.264 + AAC, 15.232s, 1.96 MB
- Source I2V candidates: 2 local Wan2.2 clips, each 432x768, 25 frames, 1.042s

## Visual QA from contact sheets
- One owl preserved; no extra owl in the selected I2V loop.
- No visible text, logo, watermark, UI, labels, arrows, or anatomy cutaway in the source imagery.
- No obvious duplicate-head failure in sampled frames.
- Head motion reads as owl rotating from/front-to-side across the loop. It is clean but repetitive because the local I2V clip is only ~1 second and looped to match VO.
- Captions are readable with good outline and bottom placement. Safe enough for Discord preview.

## Gate recommendation
This is a **review draft, not publish-approved**.

Keep as a fast v01 to judge hook/caption/VO fit. For publish-level, next pass should either:
1. Render a longer/more varied I2V head-turn clip, or
2. Use a paid/approved video lane if Josh explicitly approves metered spend.

Current blocker: visual loop repetition. Core owl anatomy and caption system are acceptable for internal review.
