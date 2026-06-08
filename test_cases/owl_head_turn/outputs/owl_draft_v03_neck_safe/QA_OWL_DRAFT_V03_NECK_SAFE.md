# QA — owl_head_turn draft v03 neck-safe

## Purpose
Josh flagged v02 for neck artifacting. v03 intentionally removes generated neck-twist motion and uses clean still/source plates with subtle camera movement.

## Outputs
- Captioned master: `owl_head_turn_captioned_draft_v03_neck_safe.mp4`
- Discord preview: `owl_head_turn_discord_preview_v03_neck_safe.mp4`
- Contact sheet: `contact_sheet_owl_draft_v03_neck_safe.jpg`
- Clean edit: `owl_head_turn_neck_safe_clean_v03.mp4`

## Technical verification
- Master: 1080x1920, H.264 + AAC, 19.551s, 6.65 MB
- Preview: 540x960, H.264 + AAC, 19.551s, 1.41 MB

## Visual strategy
- No AI-generated neck rotation in final edit, so the v02 neck artifact class is avoided.
- Uses multiple clean owl plates showing over-shoulder/head-turn poses.
- Tradeoff: cleaner anatomy, but less impressive motion. This is safer for review, not a final publish-level motion solution.

## Visual QA
- Contact sheet confirms v02's generated neck-twist artifact class is avoided because v03 uses still/source plates with Ken Burns motion only.
- Captions are readable with strong outline.
- No black frames detected by `blackdetect`; 469 video frames at 24fps.
- Visual tradeoff is clear: safer anatomy and cleaner necks, but less impressive motion than a true head-turn shot.

## Gate recommendation
Internal review pass for artifact mitigation. For publish, render or source one longer clean wildlife-style head-turn shot before upload.
