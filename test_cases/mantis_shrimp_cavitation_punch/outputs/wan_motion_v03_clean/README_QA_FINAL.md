# Mantis shrimp cavitation punch Wan v03 QA

Generated: 2026-06-06

## Status

Candidate-review preview created. This is the first full clean Wan/no-overlay lane that is directionally aligned with the shark template.

Not public upload final yet. It still needs Josh phone-size review and any final polish/voice/caption approval before Gate 6.

## Outputs

- Clean master, no captions: `mantis_shrimp_cavitation_punch_wan22_master_1080.mp4`
- Clean 720 preview, no captions: `mantis_shrimp_cavitation_punch_wan22_preview_720.mp4`
- Captioned hook master: `mantis_shrimp_cavitation_punch_wan22_captioned_hook_v03_1080.mp4`
- Captioned Discord preview: `mantis_shrimp_cavitation_punch_wan22_captioned_hook_v03_720.mp4`
- Caption source: `captions_hook_v03.ass`
- Contact sheet, clean: `contact_sheet_mantis_shrimp_cavitation_punch.jpg`
- Contact sheet, captioned: `contact_sheet_captioned_hook_v03.jpg`
- ffprobe, master: `ffprobe_master.json`
- ffprobe, captioned preview: `ffprobe_captioned_preview.json`

## Verified specs

Captioned Discord preview:

- Video: 720x1280 H.264
- Audio: AAC 48 kHz
- Duration: ~31.34 seconds
- Size: ~5.5 MB

Master:

- Video: 1080x1920 H.264
- Audio: AAC 48 kHz
- Duration: ~31.32 seconds

## QA results

- Overlay/proof artifacts: pass. The rejected rings/proof/diagram lane is gone.
- Generated non-caption text/logos/UI: pass on contact sheet.
- Motion lane: pass for candidate review. The frames show generated in-frame water/subject motion rather than a pure Ken Burns/static slideshow.
- Mantis anatomy: candidate pass. Some AI softness remains, but no obvious severe extra-limb/text-logo blocker is visible on contact-sheet QA.
- Bubble/flash proof beat: candidate pass. The white bubble/flash is inside the image/video lane, not a separate diagram overlay.
- Caption readability: pass for review. Large centered WAYS-style text with yellow/white contrast is readable at contact-sheet/phone size.
- Shorts feed hook gate: improved. First caption now leads with the payoff: `THIS SHRIMP PUNCH / MAKES WATER FLASH`.

## Remaining risks before public upload

- Needs full-speed human review on phone, not just contact-sheet QA.
- The source/AI macro look is still stylized/soft in some beats. If Josh wants a 9/10 publish-final, the weakest bubble-collapse and final water-punch beats may need another narrow reroll.
- Voice and final caption timing need Gate 5 approval.
- Do not publish without explicit Gate 6 authorization.
