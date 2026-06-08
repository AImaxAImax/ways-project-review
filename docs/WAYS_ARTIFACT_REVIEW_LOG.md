# WAYS Artifact Review Log

Human review observations for the local video model benchmark. This log exists because the automated QA harness can score preservation and motion, but it does not reliably catch anatomy errors, extra limbs, unattached appendages, or viewer-trust-breaking weirdness.

## Review scale

- `clean`: no visible issue.
- `minor`: visible but likely acceptable for quick edit or crop.
- `major`: likely reject or reroll.
- `fatal`: unusable.

## Current observations

### cat1_octopus_b / wan22_i2v / seed_627102

Status: `major`, needs human review before any pass/routing decision.

User observation:

> There seems to be an extra un attached tentecal.

Agent visual confirmation from contact sheet:

- The octopus subject is preserved overall.
- The right/lower-right tentacle cluster looks anatomically suspicious across sampled frames.
- There appears to be an extra or disconnected tentacle/appendage that does not read as cleanly attached to the body.
- This is not reflected as an automated blocker because CLIP/DINO preservation and motion metrics remain strong.

Evidence:

```text
benchmark/review_artifacts/cat1_octopus_b_seed627102/contact.jpg
```

Live video path:

```text
/mnt/c/dev/curious-shorts/benchmark/runs/cat1/cat1_octopus_b/wan22_i2v/seed_627102/clips/shot01_wan22_432x768_25f_seed627102.mp4
```

Automated metrics:

```text
QA score: 92
blockers: []
render_seconds: 561.584
CLIP min: 0.932542
DINO min: 0.953524
LPIPS: 0.128590
motion: 3.773810
warning: low resolution for Shorts: 432x768; preferred >= 720x1280
```

Decision note:

Do not count this cell as a clean pass until a human reviewer marks one of:

- `pass despite artifact`
- `reroll seed`
- `reject model/use-case cell`
- `crop/edit salvageable`

Recommended provisional routing:

```text
provisional_human_status: needs_review
provisional_quality_status: anatomy_artifact_major
matrix_effect: automated metrics retained, human pass withheld
```

## Open reviewer actions

- Review `cat1_octopus_b` seeds `627101` and `627102` side by side.
- Decide whether extra/unattached appendages should be a hard blocker for animal/creature realism plates.
- If yes, update Gate 2 routing rules so anatomy failures override CLIP/DINO pass.
