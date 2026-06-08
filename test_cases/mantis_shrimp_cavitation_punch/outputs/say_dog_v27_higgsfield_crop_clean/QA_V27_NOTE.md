# WAYS mantis shrimp — v27 Higgsfield crop-clean QA

Date: 2026-06-06

## Build summary

v27 uses the downloaded silent Higgsfield 480p mechanism clip as the real-motion base for the three proof beats:

- cavitation / bubble formation
- first impact
- bubble collapse / water impact

It keeps the rest of the v25 scaffold: real/source mantis footage for context beats, large creator captions, no labels, no arrows, no diagram cards, no non-caption text.

Outputs:

- Preview: `mantis_say_dog_v27_higgsfield_crop_clean_captioned_720.mp4`
- Master: `mantis_say_dog_v27_higgsfield_crop_clean_captioned_1080.mp4`
- Contact sheet: `contact_sheet_mantis_say_dog_v27_higgsfield_crop_clean.jpg`
- Specs: `ffprobe_preview.json`
- Build script: `scripts/build_mantis_say_dog_v27_higgsfield_crop_clean.py`

## Verified specs

Preview ffprobe from build:

- 720x1280 H.264
- AAC audio, 48 kHz
- Duration: 31.333s
- Size: 9,365,410 bytes
- Bitrate: ~2.39 Mbps

## Contact-sheet QA

Score: **7.3/10 internal candidate**

### What improved

- The Higgsfield section is more cinematic and readable than the earlier pure-procedural mechanism passes.
- Bubble / flash / impact read is stronger at phone-contact-sheet size.
- Captions remain readable and creator-style.
- No non-caption text is visible.
- No labels, arrows, diagram cards, or bottom-caption blocks.
- The route confirms that a real-motion plate plus caption/mechanism emphasis is the right direction.

### What still blocks publish / Josh-review-ready status

1. **Crab-claw / pincer risk remains.**
   - The Higgsfield plate still reads like a large orange crab/lobster pincer more than a mantis shrimp raptorial club.
   - v27 tighter crop improves bubble visibility but does **not** solve the anatomy read.

2. **Repeated-shot fatigue.**
   - The three proof beats reuse the same Higgsfield plate window too heavily.
   - It is clear enough for mechanism direction, but not premium enough as final say-dog-see-dog coverage.

3. **Mechanism proof is visual but not exact.**
   - The clip shows bubble/flash/impact, but not a scientifically clean mantis club strike.
   - Captions can carry the concept, but the visual itself still does not fully prove club -> bubble -> collapse.

4. **Source fidelity blocker remains.**
   - Further crop/polish cannot fix the wrong-appendage read.
   - The next upgrade needs either a better generated source plate or acquired/licensed high-speed mechanism footage / purpose-built 3D mechanism.

## Decision

**Keep v27 as best-current internal direction proof, not final publish candidate.**

Recommended next route:

- Do **not** spend more credits blindly.
- If continuing this exact Higgsfield route, do one narrow 480p reroll only, with the hard prompt target: `mantis shrimp raptorial club, not crab claw, no pincer, no full creature body, close macro club strike, clear cavitation bubble collapse`.
- Alternative better route: purpose-built 3D / illustrated no-text mechanism shot with real mantis reference plates, or licensed high-speed footage if available.

## Bottom line

v27 validates the hybrid strategy, but the Higgsfield source plate is still the limiting factor. Editing cannot turn the pincer-looking plate into a 9/10 WAYS science proof shot.
