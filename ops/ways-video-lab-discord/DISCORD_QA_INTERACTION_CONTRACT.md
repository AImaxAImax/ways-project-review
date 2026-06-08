# WAYS Discord QA Interaction Contract

This is the Discord-first route for WAYS human QA. Discord is the source-of-truth conversation layer. Human decision pings must include Discord-native, downscaled photo/video attachments so Josh can decide while away from the workstation; local file paths are audit-only fallback, not the review surface.

## Primary target

- Project discussion thread: `1512650920373256232`
- QA gate channel: `#ways-video-lab-qa-gates` / `1512649734769348690`
- Dashboard companion: `C:\dev\curious-shorts\dashboard\review.html`
- Decision ledger: `C:\dev\curious-shorts\dashboard\review_decisions.json`

## Human decision replies

Josh can reply in Discord using this syntax:

```text
QA <slug-or-plate-id> <action> score=<number> lane=<lane> notes="short reason"
```

Examples:

```text
QA sharks_older_than_trees approve-private score=8.5 notes="Good private draft, not public yet. Shot 4 is a little soft."
QA sharks_older_than_trees reject notes="Final beat does not read at phone size. Replace shot 6."
QA sharks_older_than_trees publish notes="Explicitly authorize public publish today."
QA mantis_shrimp__shot03 approve-plate lane=wan_i2v score=9 notes="Clean silhouette and caption-safe upper third."
QA mantis_shrimp__shot04 deny-plate notes="Generated label text visible; regenerate this one plate."
```

## Allowed actions

### Gate 2 — Plate QC

- `approve-plate` requires `lane=wan_i2v`, `lane=motion_graphic`, or `lane=still_motion`.
- `deny-plate` defaults downstream to regeneration.

### Gate 5 — Final phone-size video review

- `approve-private` means it clears the 8-9/10 private-draft bar.
- `approve-public-quality` means it looks 9/10+ and can move to publish authorization, but does not itself publish public.
- `reject` / `reject-rework` means rework the exact issue in `notes`.

### Gate 6 — Publish authorization

- `publish` / `authorize-public-publish` is the explicit public publish authorization.
- `keep-private` means keep the draft private and record the hold reason.

## Tooling

Build Discord review prompts from the latest QC report. This also prepares downscaled attachments under `ops/ways-video-lab-discord/discord_media/<slug>/` and emits `MEDIA:/absolute/path` lines in the outbox. Do not paste/send a decision card that only contains local file paths unless the media preparation failed and the failure is explicitly explained.

```bash
cd /mnt/c/dev/curious-shorts
python3 tools/ways_discord_qa.py outbox \
  --report ops/ways-video-lab-discord/ways_qc_report_latest.json \
  --out ops/ways-video-lab-discord/discord_qa_outbox.md
```

Parse and persist a Discord reply:

```bash
cd /mnt/c/dev/curious-shorts
python3 tools/ways_discord_qa.py parse 'QA sharks_older_than_trees approve-private score=8.5 notes="private draft OK"'
```

The parser writes to `dashboard/review_decisions.json` using the same decision ledger as the dashboard server, with `source: discord` and the WAYS thread ID attached.

## Dashboard role after this change

The dashboard should not be the place Josh goes to manage everything. It should only:

1. show media that Discord cannot show well enough inline;
2. expose the exact Discord reply command for each card;
3. optionally persist a click-based decision when Josh is already in the dashboard;
4. make clear that the Discord reply route is preferred.

## Agent follow-up rule

Before asking Josh for a WAYS decision in Discord:

- attach a downscaled contact sheet or image grid when the decision depends on photos/plates;
- attach a downscaled playable MP4 when the decision depends on motion/captions/timing;
- keep each attachment Discord-safe, currently capped at 24 MB by `tools/ways_discord_qa.py`;
- include local paths only after the attachments, as audit/debug references.

After a decision appears in Discord or `review_decisions.json`:

- approved plates can move into the selected render lane;
- rejected plates/videos move to the smallest rework unit, not a full rebuild by default;
- public publish only happens when `explicit_public_publish_authorization` is present;
- below-bar renders stay internal unless Josh explicitly asks to see a direction check.
