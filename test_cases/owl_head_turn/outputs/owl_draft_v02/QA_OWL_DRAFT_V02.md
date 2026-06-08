# QA — owl_head_turn draft v02

## Outputs
- Captioned master: `owl_head_turn_captioned_draft_v02.mp4`
- Discord preview: `owl_head_turn_discord_preview_v02.mp4`
- Contact sheet: `contact_sheet_owl_draft_v02.jpg`
- Clean sequence: `owl_head_turn_clean_sequence_v02.mp4`

## Technical verification
- Master: 1080x1920, H.264 + AAC, 19.551s, 7.24 MB
- Preview: 540x960, H.264 + AAC, 19.551s, 1.47 MB

## Edit changes from v01
- Uses both Wan2.2 I2V head-turn candidates instead of one single repeated loop.
- Adds a slow plate hold during the anatomy/blood-vessel explanation.
- Uses slower/interpolated motion and reverse passes to reduce obvious one-second cycling.
- Re-recorded VO is more natural and closer to the 20s WAYS educational beat.

## Visual QA
- Contact sheet shows one owl throughout; no duplicate heads or extra owls visible.
- No black frames detected by `blackdetect`; 469 video frames at 24fps.
- Captions are readable on the dark forest background with strong outline.
- v02 is better than v01 because it alternates side/front positions and uses two I2V candidates instead of one obvious 1-second loop.
- Remaining issue: motion still reads like a cleverly edited/looped generated clip, not a fully natural long wildlife shot. The first caption phrase also holds a partial thought briefly, but it is understandable with VO.

## Gate recommendation
Improved internal review draft. Not publish-approved yet under the 8-9/10 WAYS gate. Publish-level next pass should render a longer true head-turn clip or use an approved higher-end video lane.
