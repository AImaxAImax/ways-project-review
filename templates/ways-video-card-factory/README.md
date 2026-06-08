# WAYS video card factory templates/checkers

This folder operationalizes the schema and artifact contract in:

`ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md`

## Generate a new card skeleton

```bash
python3 tools/ways_factory.py create-card \
  --slug wombat_cube_poop \
  --hook "Wombats poop cubes." \
  --core-fact "Only known animal to produce cube-shaped scat." \
  --cohort-tag "batch1-animal" \
  --test-variable "hook_style_A" \
  --root test_cases
```

The generator creates:

- `idea_card.json`
- `script.md`
- `storyboard_manifest.json`
- `lane_map.json`
- `assets/accepted_stills/`
- `assets/rejected_stills/`
- `outputs/i2v_clips/`
- `outputs/motion_graphic_clips/`
- `outputs/PUBLISH_GATE.md`
- `outputs/youtube_draft_pack/youtube_metadata.json`
- `outputs/youtube_draft_pack/description_upload.txt`
- placeholder upload verification slots

Defaults are locked to the WAYS contract:

- `category_id: 28`
- `voice: elevenlabs_george`
- `privacy: private`
- required `cohort_tag`
- exactly one scalar `test_variable`

## Check artifact contract

Early contract check:

```bash
python3 tools/ways_factory.py check-artifacts test_cases/wombat_cube_poop
```

Ready-to-Publish gate check:

```bash
python3 tools/ways_factory.py check-artifacts test_cases/wombat_cube_poop --ready-to-publish
```

`--ready-to-publish` refuses the card if any required media/report/upload artifact is missing or empty, or if `outputs/PUBLISH_GATE.md` lacks a machine-readable JSON block with required gate results.

Gate result statuses accepted for Ready-to-Publish:

- Gate 1 Script: `pass`
- Gate 2 Plate QC human: `approved` or `pass`
- Gate 3 Render QA: `pass`
- Gate 4 Assembly QA: `pass`
- Gate 5 Human Final Review: `approved` or `pass`
- Gate 6 Publish Authorization: `hold`, `pending`, `private_only`, or `not_authorized`

Gate 6 is intentionally held/pending at Ready-to-Publish because public publishing requires explicit human authorization. Default upload privacy remains `private`.
