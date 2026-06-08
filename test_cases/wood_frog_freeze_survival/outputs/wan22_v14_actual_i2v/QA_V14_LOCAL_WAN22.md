# Wood frog v14 local Wan2.2 I2V QA

## Render lane
- Local ComfyUI Wan2.2 A14B GGUF Lightning I2V
- Workflow: `/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json`
- Config: `render_wan22_v14_config.json`
- Source stills: public-source frog photos plus clean local no-text proof plates
- Not Ken Burns: every shot was generated as Wan2.2 image-to-video clip before assembly.

## Outputs
- Captioned preview 720p: `wood_frog_freeze_survival_v14_wan22_captioned_720.mp4`
- Captioned master 1080p: `wood_frog_freeze_survival_v14_wan22_captioned_1080.mp4`
- Clean master 1080p: `wood_frog_freeze_survival_v14_wan22_master_1080.mp4`
- Contact sheet: `contact_sheet_wood_frog_freeze_survival_v14_captioned.jpg`

## Technical verification
- Duration: 20.583333s
- Preview: 720x1280, h264 + AAC audio, 6.25 MB
- Master: 1080x1920, h264 + AAC audio, 19.32 MB
- Motion delta sample: mean 20.16, min 2.34, max 89.88 across 2fps extracted frames

## Visual QA notes
- Captions are readable and timed from v13.
- No non-caption text/logo/UI detected in contact sheet.
- Frog shots show actual generated I2V changes instead of static pan/zoom.
- Sugar/cell shot is cleaner than the previous arrow-like source plate. It still reads as a stylized science plate, not microscope footage.
- Heart shot is cleaner after removing pause marks/UI rings, but it remains a proof visual rather than documentary footage.
- Overall: correct lane and a real motion candidate, but not yet an 8.5/10 publish-final. Best next micro-pass is to improve shot 02/03/04 source plates and prompts, then reroll only those shots.
