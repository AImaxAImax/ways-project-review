# WAYS next-four render QA - 2026-06-06

Source workflow: shark/Wan22 A14B I2V short template adapted per project. All four were rendered end-to-end to 1080x1920 H.264 MP4 with AAC 48 kHz audio, captioned final polish, Discord preview, and contact sheet.

## Gate definition
- Target: >=8/10 all-around before surfacing as a publish candidate.
- If a video misses the gate after iteration, it is blocked with exact failing shots.

## Results

### saturn_hexagon_storm - PASS after v2 iteration
- Final: `test_cases/saturn_hexagon_storm/outputs/final_polish_wan22_template_v02_plain/publish_candidate_captioned.mp4`
- Preview: `test_cases/saturn_hexagon_storm/outputs/final_polish_wan22_template_v02_plain/discord_preview_captioned.mp4`
- Contact sheet: `test_cases/saturn_hexagon_storm/outputs/final_polish_wan22_template_v02_plain/contact_sheet_final_polish.jpg`
- ffprobe: 1080x1920, H.264, AAC 48k, duration 17.8s.
- QA: v1 failed due Wan hallucinated unreadable non-caption text/logos and template marks. v2 rerender removed graphic/text source overlays. Final visual scores are approximately 8.0-8.5 across beats. Captions readable, visuals match narration, no non-caption text visible.

### wombat_cube_poop - BLOCKED, needs source rebuild
- Current render: `test_cases/wombat_cube_poop/outputs/final_polish_wan22_template_v01/publish_candidate_captioned.mp4`
- Preview: `test_cases/wombat_cube_poop/outputs/final_polish_wan22_template_v01/discord_preview_captioned.mp4`
- Contact sheet: `test_cases/wombat_cube_poop/outputs/final_polish_wan22_template_v01/contact_sheet_final_polish.jpg`
- ffprobe: 1080x1920, H.264, AAC 48k, duration 18.9s.
- QA scores by beat: opening wombat 8, front wombat/pellet setup 7.5, internal cube-scatter macro 5.5, ground pellet/corner shot 6, closing wombat 8.
- Blockers: middle "THE SHAPE FORMS INSIDE" looks like cereal/toy cubes with holes, not wombat scat; "CORNERS BEFORE LANDING" looks like white rocks/cubes, not believable scat; factual visual believability below WAYS gate.
- Next rebuild brief: use real wombat footage/photos plus macro of irregular brown cuboid pellets, no perfect toy cubes, no holes, no cereal texture.

### octopus_three_hearts - PASS candidate
- Final: `test_cases/octopus_three_hearts/outputs/final_polish_wan22_template_v01/publish_candidate_captioned.mp4`
- Preview: `test_cases/octopus_three_hearts/outputs/final_polish_wan22_template_v01/discord_preview_captioned.mp4`
- Contact sheet: `test_cases/octopus_three_hearts/outputs/final_polish_wan22_template_v01/contact_sheet_final_polish.jpg`
- ffprobe: 1080x1920, H.264, AAC 48k, duration 16.0s.
- QA: approximate beat scores 8.0-8.5. Captions readable, underwater premium look, no visible generated text/logos. Anatomy is stylized but arms remain connected enough for a short-form pass. Watch risk: not a documentary-perfect common octopus, but clears 8 for current WAYS bar.

### tardigrade_survival_mode - PASS candidate
- Final: `test_cases/tardigrade_survival_mode/outputs/final_polish_wan22_template_v01/publish_candidate_captioned.mp4`
- Preview: `test_cases/tardigrade_survival_mode/outputs/final_polish_wan22_template_v01/discord_preview_captioned.mp4`
- Contact sheet: `test_cases/tardigrade_survival_mode/outputs/final_polish_wan22_template_v01/contact_sheet_final_polish.jpg`
- ffprobe: 1080x1920, H.264, AAC 48k, duration 19.1s.
- QA: approximate beat scores 8.0-8.5. Captions readable, no non-caption text/logos, strong premium macro style. Watch risk: stylized/cute tardigrade anatomy, but the concept is clear and passes for WAYS educational short.

## Overall
- Rendered: 4/4 complete.
- Passed >=8 all-around: 3/4 (Saturn v2, Octopus, Tardigrade).
- Blocked below gate: 1/4 (Wombat, exact failing shots above).
