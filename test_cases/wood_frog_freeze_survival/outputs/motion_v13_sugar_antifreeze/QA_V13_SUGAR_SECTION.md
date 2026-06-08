# Wood frog freeze survival — v13 sugar-section fix QA

Date: 2026-06-07

## User request

Josh asked to fix the `SUGAR HELPS / PROTECT CELLS` section with something more fitting.

## Change made

Replaced the prior generic cell/bubble section with a clearer antifreeze-chemistry visual:

- cold blue tissue-fluid environment
- white ice crystals advancing from the sides/top
- intact teal cells
- gold glucose-like protective halos around the cells
- gold fluid streams crossing the frame
- second-half macro reset so the 8s and 10s samples differ more

No labels, arrows, text, UI, or molecular diagrams were added.

## QA result

### Passes

- The sugar section now better matches the line: `SUGAR HELPS / PROTECT CELLS`.
- The gold protective halos clearly imply protection instead of random bubbles.
- Blue/white ice crystals surrounding, but not destroying, the cells makes the antifreeze idea more readable.
- 8s and 10s are visually different enough: wide cell field -> macro protected-cell view.
- No visible non-caption text, logos, UI, labels, or arrows on the contact sheet.
- Captions remain readable at phone/contact-sheet size.
- Specs verified: 1080x1920 H.264 master, AAC 48 kHz audio, 20.60s duration.
- Motion delta mean sampled every 0.5s: 19.25 / 255, so the render remains animated/static-motion rather than frozen.

### Remaining weaknesses

- The sugar section is still a stylized proof graphic, not microscope/documentary footage.
- It is clean and more fitting, but not a premium 3D/biology render.
- Temporary TTS is still not verified as approved `elevenlabs_george`, so this remains internal only.

## Score

**8.0/10 internal candidate**

This is better than v12 specifically on the sugar/cell beat and keeps the improved say-dog-see-dog structure.

## Current best

Use v13 as the current wood frog internal candidate.
