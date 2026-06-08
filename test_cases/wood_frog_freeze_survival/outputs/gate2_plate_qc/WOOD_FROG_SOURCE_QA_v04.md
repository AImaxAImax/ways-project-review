# Wood Frog Source Acquisition QA v04

Generated: 2026-06-06T15:00:00Z

## Result
- Manifest now has 7 static assets: 4 public-source real wood frog stills + 3 deterministic no-AI proof/composite plates.
- Added beat 2 proof plate: `test_cases/wood_frog_freeze_survival/assets/source_stills/source_06_freeze_through_body_graphic.jpg`
- Added beat 3 proof plate: `test_cases/wood_frog_freeze_survival/assets/source_stills/source_07_heart_stop_graphic.jpg`
- New contact sheet: `test_cases/wood_frog_freeze_survival/outputs/gate2_plate_qc/wood_frog_source_contact_sheet_v04.jpg`
- Updated manifest: `test_cases/wood_frog_freeze_survival/assets/source_stills/source_manifest.json`
- Added machine-readable status: `test_cases/wood_frog_freeze_survival/outputs/gate2_plate_qc/gate2_source_status_v04.json`
- Repro script: `test_cases/wood_frog_freeze_survival/outputs/gate2_plate_qc/build_wood_frog_proof_plates_v04.py`

## What changed vs v03
- v03 blocker said beats 2-3 needed stronger literal freeze-through-body / heart-stop proof visuals.
- v04 adds two safe deterministic local plates using existing right-safe/public-source wood frog photos plus project-owned simple overlays:
  - Beat 2: translucent body/cutaway mask with branching ice crystals to imply ice through much of the frog body, not only surface frost.
  - Beat 3: frosted frog-body mask with frozen heart icon, pause marks, and fading pulse motif to imply temporary heartbeat stop.

## Rights / lane notes
- No paid/credit lane used.
- No AI image generation used.
- No video rendered.
- New plates contain no text/logos. They are proof graphics/composites, not documentary footage.

## Gate status
Partial Gate 2 progress only. Source plate count and beat-coverage are improved, but this is **not ready** and should not be sent as ready:
1. Approved `elevenlabs_george` VO is still not present (`outputs/auto_static_v01/voiceover.mp3` absent), so rendering with a wrong/unapproved voice remains blocked.
2. Beat 2 and beat 3 plates are stronger deterministic proof visuals, but should receive human Gate 2 plate review because they are composite graphics and beat 3 includes a pulse/heart motif that must be checked against the WAYS "no medical UI" sensitivity.
3. Public publish remains Gate 6 hold.

## Decision
Hold render. Hold public upload. Candidate advanced only by improving Gate 2 source/proof plates and status documentation.
