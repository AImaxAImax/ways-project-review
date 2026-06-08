# Wood frog source acquisition QA v01

Status: **partial internal source acquisition only**. Downloaded 2 public-source real wood frog stills before Wikimedia Commons returned HTTP 429. This is not enough for a Gate 2 all-beats plate pass or a say-dog-see-dog static draft.

What passes:
- Real wood frog identity/source lane started.
- Public-domain/CC0 licensing for the downloaded stills.
- Contact sheet generated for source QA.

Blockers before render/publish:
- Need at least 5 beat-mapped source plates or proof visuals for hook/freeze/heart/cell/thaw.
- Need approved `elevenlabs_george` VO file before `scripts/render_static_source_short.py` can render without template/voice drift.
- Static public-source photos alone do not literally show freeze-thaw/cell-protection motion; any first draft would be INTERNAL_QA/static-first only.

Artifacts:
- `test_cases/wood_frog_freeze_survival/assets/source_stills/source_manifest.json`
- `test_cases/wood_frog_freeze_survival/outputs/gate2_plate_qc/wood_frog_source_contact_sheet_v01.jpg`
