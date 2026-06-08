# QA V17 ElevenLabs George VO Swap

Generated: 2026-06-07T03:48:32Z

## Voice
- Provider: ElevenLabs
- Voice: George - Warm, Captivating Storyteller
- Voice ID: JBFqnCBsd6RMkjVDRZzb
- Model: eleven_multilingual_v2
- Script: unchanged six-beat wood frog script from v16.
- Beat timing: each ElevenLabs segment tempo-fitted to the existing v16 caption/visual timings.

## Outputs
- Captioned 1080 master: `outputs/wan22_v17_elevenlabs_george/wood_frog_freeze_survival_v17_elevenlabs_george_captioned_1080.mp4`
- Clean 1080 master: `outputs/wan22_v17_elevenlabs_george/wood_frog_freeze_survival_v17_elevenlabs_george_clean_1080.mp4`
- Captioned 720 preview: `outputs/wan22_v17_elevenlabs_george/wood_frog_freeze_survival_v17_elevenlabs_george_captioned_720.mp4`
- Final VO audio: `outputs/wan22_v17_elevenlabs_george/final_voiceover_george_boosted.m4a`
- Render report: `outputs/wan22_v17_elevenlabs_george/final_vo_report.json`
- Spec probe: `outputs/wan22_v17_elevenlabs_george/ffprobe_captioned_master.json`

## Verified
- 1080 master: h264 video, 1080x1920, AAC audio at 48 kHz.
- Duration: 20.583333s.
- Audio volume: mean_volume -16.7 dB, max_volume -1.3 dB after +3.0 dB gain.
- Visuals/captions: inherited from v16, only audio swapped.
- No upload/public publish performed in this step.

## Publish gate
- Voice blocker cleared: now uses ElevenLabs George.
- Still requires final human Gate 6 approval before public publish.
