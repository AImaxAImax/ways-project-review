# WAYS source Gate 2 check-in

Time: 2026-06-06T10:08:53Z

This check-in advanced source/plate QC work only. No videos rendered. No old candidates re-promoted.

## Saturn Hexagon Storm

Artifacts:

- Raw source sheet v2: `test_cases/saturn_hexagon_storm/outputs/gate2_plate_qc/source_acquisition_contact_sheet_v2.jpg`
- Source manifest: `test_cases/saturn_hexagon_storm/assets/source_nasa/source_manifest.json`

Gate 2 state: **partial pass for source acquisition, plate build still needed.**

Visual QA:

- NASA Cassini sources are zero-text in the image pixels; contact-sheet labels are outside the source images.
- Best source candidates: PIA17122 for strong hexagon/storm read; PIA21052 for closer storm texture; PIA14646 for hexagon plus rings/context.
- PIA20507 is clean but weaker for hexagon read, likely texture/reference only.
- New Earth proxy acquired: Apollo 17 Blue Marble `AS17-148-22727_blue_marble_orig.jpg`.

Remaining blocker before render:

- Need build real 9:16 proof plates from these sources, including a tasteful non-text Earth scale composite, then run phone-size/OCR visual QC.

## Octopus Three Hearts

Artifacts:

- Raw source sheet: `test_cases/octopus_three_hearts/outputs/gate2_plate_qc/source_acquisition_contact_sheet.jpg`
- Source manifest: `test_cases/octopus_three_hearts/assets/source_rework/source_manifest.json`

Gate 2 state: **blocked/partial.**

Visual QA:

- Candidate 2 and 5 are the best real octopus plates for baseline/crawl beats.
- Candidate 1 is too murky/low-read.
- Candidate 3 and 4 include human hand/finger interaction and should not be primary final plates.
- No right-safe text-free anatomy diagram was found for the three-heart claim.

Safe next approach:

- Use real octopus source plates plus simple agent-created pulse-dot/ring overlay after plate QC, not a fake or labeled anatomy diagram.
- Must still pass rights/attribution recheck and phone-size contact-sheet QC.

## Tardigrade Survival Mode

Artifacts:

- Raw source sheet: `test_cases/tardigrade_survival_mode/outputs/gate2_plate_qc/source_acquisition_contact_sheet.jpg`
- Video frame sheet: `test_cases/tardigrade_survival_mode/outputs/gate2_plate_qc/video_frame_contact_sheet.jpg`
- Source manifest: `test_cases/tardigrade_survival_mode/assets/source_rework/source_manifest.json`

Gate 2 state: **partial pass with precise beat gap.**

Visual QA:

- C005 is the best active/hero plate: clean, real-looking microscope tardigrade, no visible text.
- C003/C004 are credible SEM active/tun references. Good for tun/dormancy if the style shift is acceptable.
- C008/C009 are diagram/text-heavy and fail zero-text final plate gate.
- C010 has panel labels/scale bars and fails zero-text final plate gate unless cropped very aggressively, likely reference only.
- C002 research video has a real desiccation/tun/rehydration sequence, but sampled frames include title/label text at some points; usable only after extracting clean no-text frames/segments.
- C007 is poor phone-size microscope footage and not premium enough.

Remaining blocker before render:

- Need select clean C002 time ranges without embedded labels/text, or adjust the script to say tun → active after water returns without pretending a visible droplet/flow shot exists.

## Current rule

No WAYS video goes back to Josh as ready until Gate 2 source/plate QC, approved voice/template, and per-shot say-dog-see-dog all pass.


## Saturn proof plates v01 update - 2026-06-06T10:11:11Z

Created 5 no-text proof plates and contact sheet:

- `test_cases/saturn_hexagon_storm/outputs/gate2_plate_qc/proof_plates_v01/`
- `test_cases/saturn_hexagon_storm/outputs/gate2_plate_qc/saturn_proof_plates_v01_contact_sheet.jpg`
- QC: `test_cases/saturn_hexagon_storm/outputs/gate2_plate_qc/PLATE_QC.md`

Verdict: **blocked, do not render yet.** Sources are right-safe and text-free, but plates score roughly 6-7/10 and are not premium/say-dog-see-dog enough.
