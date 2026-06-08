# Wood frog freeze survival — v08 motion/artifact QA

Date: 2026-06-07

## User instruction

Josh asked to keep building, with two explicit constraints:

1. Avoid frame artifacts.
2. Create motion like the other videos.

## What was built

Built `v08_no_artifact_transition`, a deterministic source-preserving motion candidate:

- real/public-source frog bases only for animal frames
- no AI-generated frog bodies
- no paid video credits
- no non-caption text/logos/UI
- large centered WAYS captions
- per-beat push-in/pan plus animated frost/thaw/cell overlays
- clean transition replacing v07's artifact-looking split/oval thaw moment

## Outputs

- Captioned master: `wood_frog_motion_v08_captioned_1080.mp4`
- Discord preview: `wood_frog_motion_v08_captioned_720.mp4`
- Clean no-caption master: `wood_frog_motion_v08_clean_1080.mp4`
- Contact sheet: `contact_sheet_wood_frog_motion_v08.jpg`
- Motion delta report: `motion_delta_report_v08.json`
- Captions: `captions.ass`, `captions.srt`
- Specs: `ffprobe_captioned_master.json`

## Specs verified

From ffprobe:

- 1080x1920 H.264 video
- AAC audio, 48 kHz mono
- duration: 20.60s
- master size: 26.5 MB

## Motion check

A frame-delta report sampled every 0.5s shows real frame-to-frame change from deterministic camera moves and animated overlays. This is not a single frozen still. Motion types:

- opening frost creep + push-in
- freeze/body frost motion + push-in
- subtle pulse/freeze motion on the heart-stop beat
- animated cells/droplets/protection halos
- cold-to-warm thaw crossfade + warm light sweep
- final warm hero push-in

Caveat: this is still **source-preserving static motion**, not true animal-body movement from I2V. It is closer to the deterministic WAYS fallback lane than the mantis Higgsfield/I2V lane.

## Contact sheet QA

### Passes

- No visible non-caption text.
- No logos, UI, labels, arrows, or diagram cards.
- v07's weird translucent oval/split artifact is removed.
- Captions are readable at contact-sheet/phone size.
- First frame opens on the payoff: `A FROG CAN / FREEZE SOLID`.
- Visual resets by ~2.4s, then again at each beat.
- Frog anatomy comes from real/public source photos, not generated animal bodies.
- The hook and freeze-body beats are immediately understandable.

### Remaining weaknesses

- The `SUGAR HELPS / PROTECT CELLS` scene is clean but graphic/abstract rather than documentary proof.
- The `ITS HEART / CAN STOP` beat relies heavily on caption + subtle pulse/frost, not literal physiological footage.
- Because this uses deterministic motion, it may still feel less alive than true I2V/footage if judged against the mantis or shark motion benchmark.
- Voice is temporary internal TTS from the available provider; it is **not verified as approved `elevenlabs_george`**, so this cannot be publish-final.

## Score

**7.4/10 internal motion candidate**

Better than v06/v07 for artifact cleanliness. Good enough to show as an internal candidate and continue polishing from, but not publish-final.

## Decision

Keep v08 as the current wood frog internal candidate.

Next best improvements:

1. Replace/approve VO in `elevenlabs_george` lane.
2. If we want a higher score, add one true motion source or I2V pass for frog thaw/movement while preserving real frog anatomy.
3. Keep the v08 no-artifact transition approach. Do not return to the split/oval thaw plate.
