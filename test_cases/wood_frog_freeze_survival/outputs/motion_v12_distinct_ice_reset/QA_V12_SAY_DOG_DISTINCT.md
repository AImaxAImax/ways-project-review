# Wood frog freeze survival — v12 say-dog-see-dog / shot variation QA

Date: 2026-06-07

## User request

Josh asked for:

- More **say dog, see dog**: every spoken/captioned claim should have a matching visual proof.
- More difference between shots so the cut does not feel like the same frog frame repeated.

## What changed from v08

v08 was artifact-clean but too samey: real frog stills plus clean deterministic motion.

v12 adds stronger beat-level visual resets:

1. **A frog can freeze solid**
   - Cold real frog macro with frost creep.
2. **Ice forms through its body**
   - Starts on real frog body, then hard-resets into a blue inside-body ice-network proof shot.
3. **Its heart can stop**
   - Frog close-up with organic red heart glow fading/stilling. No ECG, no UI.
4. **Sugar helps protect cells**
   - Clean cell/protection visual. Second half resets to a closer/more crowded protective-fluid view.
5. **Spring warms it back to life**
   - Cold frog transitions to warm frog/leaf scene with thaw/warmth motion.
6. **Not magic / survival chemistry**
   - Warm frog hero plus chemistry-like protective particles, then different warm close crop for the ending.

## Artifact / caption QA

Passes:

- Caption backslash/slash artifact from v09 is fixed.
- No visible non-caption text.
- No logos, watermarks, UI, arrows, or labels.
- Captions are readable on the contact sheet.
- More visual variety than v08/v10/v11.
- 2s vs 4s now has a meaningful reset: real frog body -> blue internal ice network.
- 8s vs 10s has a more visible macro/protection reset.
- 16s vs 18s now uses a different warm crop/source rather than a near-identical hold.

Remaining weaknesses:

- This is still deterministic/source-preserving motion, not true live frog-body movement or I2V.
- The internal ice and cell scenes are clean proof graphics, not documentary footage.
- Temporary TTS is still not verified as approved `elevenlabs_george`, so this remains internal only.

## Specs verified

- Master: `wood_frog_motion_v12_captioned_1080.mp4`
- Resolution: 1080x1920
- Video codec: H.264
- Audio codec: AAC, 48 kHz
- Duration: 20.60s
- Contact sheet: `contact_sheet_wood_frog_motion_v12.jpg`
- Motion delta report: `motion_delta_report_v12.json`

Motion delta mean sampled every 0.5s: **19.72 / 255**, confirming frame-to-frame motion/reset rather than a frozen slideshow.

## Score

**7.9/10 internal candidate**

Better than v08-v11 on the user's specific critique: more literal proof visuals and more shot-to-shot difference.

## Decision

Use v12 as the current best wood frog internal candidate.

Next improvement if pushing toward 8.5-9/10:

1. Replace temporary TTS with approved `elevenlabs_george` VO.
2. Add one real/I2V thaw movement shot for `back to life` so the frog visibly moves rather than only thawing via grade/pan/particles.
3. If available, acquire actual wood-frog freeze/thaw footage or a premium generated mechanism lane for the heart/ice-cell beats.
