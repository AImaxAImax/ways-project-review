# QA V16 Final VO

## Candidate files

- Captioned 1080 master: `outputs/wan22_v16_final_vo/wood_frog_freeze_survival_v16_final_vo_captioned_1080.mp4`
- Captioned 720 Discord preview: `outputs/wan22_v16_final_vo/wood_frog_freeze_survival_v16_final_vo_captioned_720.mp4`
- Clean no-caption 1080 with final VO: `outputs/wan22_v16_final_vo/wood_frog_freeze_survival_v16_final_vo_clean_1080.mp4`
- Final VO audio: `outputs/wan22_v16_final_vo/final_voiceover_fitted.m4a`
- Captions: `outputs/wan22_v16_final_vo/captions.ass`
- Contact sheet: `outputs/wan22_v16_final_vo/contact_sheet_v16_final_vo_captioned.jpg`
- VO timing report: `outputs/wan22_v16_final_vo/final_vo_report.json`

## Spec verification

- 1080 captioned master: 1080x1920, H.264, AAC 48 kHz, 20.583333s, 16,481,498 bytes.
- 720 captioned preview: 720x1280, H.264, AAC 48 kHz, 20.583333s, 5,384,476 bytes.
- Audio loudness pass: measured input integrated loudness about -15.05 LUFS, true peak -0.94 dBTP.
- Final fitted VO duration: 20.600000s, aligned to the six caption/beat windows.

## Visual QA

- Contact sheet inspected.
- Captions are large, readable, centered, white with yellow emphasis and black outline.
- No unintended logos, UI, arrows, labels, or extra text beyond intended captions.
- Middle polish remains intact from v15: frost body beat, subtle heart glow, and cleaner sugar/cell protection beat.
- Last row black tiles are contact-sheet padding only, not part of the video ending.

## Voice note

- The final VO was generated and fitted using the currently configured Hermes TTS provider: Edge (`en-US-AriaNeural`).
- I did not find an available ElevenLabs API key in the environment/config search, so this is not verified as `elevenlabs_george` even though the WAYS card metadata requests that voice.
- If `elevenlabs_george` is a hard public-publish requirement, replace only the VO before upload. The visual/caption package is otherwise ready.

## Recommendation

- Ready as a final-VO review/upload candidate.
- Public posting is safe only after confirming the Edge VO is acceptable or replacing it with approved `elevenlabs_george`, plus explicit Gate 6 publish authorization.
