# WAYS shark v26 final-predator replacement QA

Created: 2026-06-05

## Inputs
- New manual GPT Image 2 frame saved as `assets/gpt_image_2_manual_v23/04_final_predator_got_here_first.png`
- Replaced prior final weak survivor/split-world still with the new predator frame.
- Render script: `scripts/render_v26_final_predator_audio.py`
- Voice: `outputs/voice_auditions/01_warm_older_brother_uncle.mp3`

## Outputs
- Master: `outputs/motion_probe_v26_final_predator_audio/sharks_older_than_trees_v26_final_predator_audio.mp4`
- Discord preview: `outputs/motion_probe_v26_final_predator_audio/sharks_older_than_trees_v26_final_predator_audio_discord.mp4`
- Contact sheet: `outputs/motion_probe_v26_final_predator_audio/contact_sheet_v26.jpg`
- Specs: `ffprobe_master.json`, `ffprobe_discord.json`

## Verified specs
- Master: 1080x1920, H.264, AAC audio, 23.916s, 24.56 MB.
- Discord preview: 720x1280, H.264, AAC audio, 23.936s, 4.56 MB.

## Harsh gate
Result: HOLD, not a 9/10 publish/upload pass.

Estimated whole-cut score: ~8.2 to 8.5/10.

What improved:
- Final predator still itself is the best final image so far: realistic shark, premium deep ocean, good caption-safe top third, no visible text/logos/UI.
- The final beat now lands much stronger than the prior weak final image.
- Captions are readable and not clipped in the contact sheet.
- Export specs and audio stream verified.

Remaining blockers:
- Still-plate fatigue remains: the cut is visibly static-first with several long repeated holds per plate.
- Style cohesion is improved but not fully premium-final: fossil/tooth, object-gag, geological split, and final shark are from different visual grammars.
- The midsection still feels like a polished storyboard/plate reel rather than true nature-doc motion.
- Caption system is readable but not the preferred full creator-style karaoke treatment.

Decision:
- Keep the new final predator frame as accepted/promoted.
- Do not upload or present this as 9/10 final.
- Next pass should either add real/I2V motion for the accepted plates or rebuild only the weakest midsection style-mismatch beats before another gate.
