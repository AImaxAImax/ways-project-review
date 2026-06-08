# v09 generated hybrid QA note

Generated-frame experiment completed.

## Outputs
- Preview: `/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch/outputs/say_dog_v09_generated_hybrid/mantis_say_dog_v09_captioned_720.mp4`
- Master: `/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch/outputs/say_dog_v09_generated_hybrid/mantis_say_dog_v09_captioned_1080.mp4`
- Contact sheet: `/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch/outputs/say_dog_v09_generated_hybrid/contact_sheet_mantis_say_dog_v09.jpg`

## Verified specs
- 720×1280 preview
- Duration: 31.333s
- Size: 6,662,868 bytes (~6.7 MB)
- Video: H.264
- Audio: AAC 48 kHz
- Integrated loudness: -15.1 LUFS
- True peak: -0.9 dBFS

## Generated frame QA
- Pure txt2img mantis frames were rejected: they looked premium at thumbnail size but had bad mantis anatomy and fake appendages.
- No-animal shell/bubble mechanism frames were rejected: clean/no text, but too beach/shell/generic and not connected to mantis shrimp.
- The selected v09 route uses low-denoise img2img from real Wikimedia stills. This keeps better subject continuity than txt2img, but the generated imagery is still not a true 9/10 solution.

## Harsh verdict
Useful experiment, but keep internal as a v09 test rather than treating as the new publish candidate.

Why:
- Say-dog-see-dog is clearer for flash/collapse than v08, but the generated frames add repeated cropped close-ups and do not convincingly show true high-speed cavitation physics.
- Some frames still feel AI-smoothed / embellished around the head and club.
- Anatomy is less broken than txt2img, but still risky for a science/nature short.
- v08 remains cleaner/right-safer because it uses real sources, even if it lacks the ideal cavitation footage.

## Recommendation
Next step should be one of:
1. Use generated frames only as quick placeholders while hunting rights-safe real high-speed strike/cavitation footage.
2. If generating is required, use real stills/video frames as strict controls and generate only subtle bubble/flash overlays, not the animal itself.
3. Build v10 from v08 plus procedural/controlled bubble overlays on real frames, avoiding AI animal re-synthesis.
