# Mantis v03 correction pass — artifact rejection and clean-motion lane

Generated: 2026-06-06

## Josh correction

> I have no idea what the artifacts on the frame are we need to remove those. I want movement in the frame like the shark video not things on frame moving and just doing Ken burns

## Decision

- `motion_graphic_rework_v02` is rejected and must not be surfaced again.
- The fast `clean_source_motion_v03_proxy` is also not acceptable for posting. It removed the drawn overlay/ring concept, but contact-sheet QA still shows ugly pixel/mesh artifacts and does not reach shark-template quality.

## Correct lane now

The only viable lane is the same approach as the shark video:

- clean, real-photo mantis source plates;
- Wan I2V generated in-frame motion;
- no overlays, no diagrams, no moving proof artifacts;
- no Ken Burns-only edit;
- no post-ready claim unless the rendered motion actually passes QA.

## What exists now

Clean source plates:

- `assets/wan_motion_v03_clean_plates/`
- Contact sheet: `outputs/gate2_plate_qc/mantis_wan_motion_v03_clean_plates_contact_sheet.jpg`

Wan config:

- `render_wan22_motion_v03_config.json`

First completed Wan clip:

- `outputs/wan_motion_v03_clean/clips/shot01_wan22_432x768_25f_seed728201.mp4`
- QA contact sheet: `outputs/wan_motion_v03_clean/qa/shot01_contact.jpg`

First Wan clip direction is cleaner: no overlay artifacts/text and more like the shark template, but it is only one short clip and not a complete video.

## Current status

Not ready to post. Continue true Wan clean-motion render/QA; reject proxy lanes if they create artifacts.
