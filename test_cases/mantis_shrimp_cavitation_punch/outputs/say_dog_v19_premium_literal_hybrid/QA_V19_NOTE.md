# v19 premium literal hybrid QA

## What changed from v17

- Kept the v17c premium no-text abstract water/VFX mechanism frames because they were the cleanest local ComfyUI output.
- Added a restrained project-owned mechanism layer: stylized club geometry, hard target, vapor bubble growth, first impact glow, and bubble collapse/shock texture.
- Avoided AI-generated mantis bodies, labels, arrows, diagram cards, UI, and non-caption text.

## Verification

- Preview: `mantis_say_dog_v19_captioned_720.mp4`
- Master: `mantis_say_dog_v19_captioned_1080.mp4`
- Contact sheet: `contact_sheet_mantis_say_dog_v19.jpg`
- ffmpeg decode check passed with no errors.
- ffprobe preview: 720x1280 H.264 video + AAC audio, 31.33s, ~8.8 MB.

## Harsh QA

Score: ~7.7/10 direction candidate, not a clean publish 8/10.

Improvements:
- Cleaner than v18. v18 was more literal but too flat/schematic.
- Slightly more literal than v17 because the mechanism beats now include a visible club/target/bubble layer.
- Maintains v17's stronger polish and zero-text cleanliness.

Remaining blockers:
- The mechanism overlay is intentionally subtle; at phone/contact-sheet size it may still read as premium splash/VFX more than unmistakable mantis club → cavitation bubble → collapse proof.
- The real-source animal beats still repeat the same mantis closeup and source style.
- The mechanism section is still illustrated/fallback proof, not real high-speed footage.
- The style jump between real mantis footage and mechanism plates is reduced versus v18, but still present.

Recommendation: v19 is the best current local route candidate. Next high-confidence step is either stronger licensed/right-safe high-speed footage, or a dedicated 3D/illustration render lane with a real modeled club/bubble sequence rather than prompt-generated splash plates.
