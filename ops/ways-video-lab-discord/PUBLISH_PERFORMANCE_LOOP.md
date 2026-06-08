# WAYS publish/status follow-up loop

This folder implements the post-QA side of `WAYS_KANBAN_AND_QC_GATES.md`: private-draft upload packs, public-publish authorization checks, cadence planning, and 48-72h performance review records.

## Safe defaults

Use `tools/ways_publish_review.py draft-pack` to create the upload pack for a candidate:

```bash
python -m tools.ways_publish_review draft-pack \
  --outdir test_cases/<slug>/outputs/<pack>/youtube_draft_pack \
  --title "Title #Shorts" \
  --description-file test_cases/<slug>/outputs/<pack>/description_upload.txt \
  --video test_cases/<slug>/outputs/<pack>/publish_candidate_captioned.mp4 \
  --captions-srt test_cases/<slug>/outputs/<pack>/captions.srt \
  --thumbnail-candidate test_cases/<slug>/outputs/<pack>/thumbnail_candidate.jpg \
  --tags "Wait Are You Serious,science facts,shorts"
```

The generated `youtube_metadata.json` always uses:

- `categoryId: "28"` (Science & Technology)
- `privacyStatus: "private"`
- `selfDeclaredMadeForKids: false`

If code tries to create a non-private draft pack or mark it made-for-kids, the helper raises instead of writing a risky pack.

## Public publish gate

Public/scheduled publish remains blocked unless an authorization note explicitly says Josh approved/authorized public publish:

```bash
python -m tools.ways_publish_review authorize-public \
  --authorization "Josh approved public publish for <video_id>"
```

A draft upload, QA pass, or agent recommendation is not enough. Without that authorization, keep the video private.

## Cadence planner

Small backlog:

```bash
python -m tools.ways_publish_review schedule --start-date 2026-06-06 --ready-buffer-count 10 --count 7
```

This emits one slot/day.

Once the ready buffer is at least 50:

```bash
python -m tools.ways_publish_review schedule --start-date 2026-06-06 --ready-buffer-count 50 --count 7
```

This emits at most two slots/day, morning/evening UTC, with a hard minimum 6-hour spacing check.

## 48-72h performance review

Record YouTube performance after 48-72 hours:

```bash
python -m tools.ways_publish_review record-review \
  --outdir test_cases/<slug>/outputs/performance_reviews \
  --video-id <youtube_id> \
  --retention-pct-viewed 68.4 \
  --swipe-away-timestamp 2.4 \
  --storyboard-manifest test_cases/<slug>/storyboard_manifest.json \
  --lesson "If proof beat dips, cut fossil setup under 2 seconds."
```

The helper writes:

- `performance_reviews.jsonl`
- `performance_review_<video_id>.json`
- `mapped_beat_or_shot` from the storyboard segment covering the swipe-away timestamp

For class-level lessons that should survive beyond this one video, pass `--class-level --skill-path <SKILL.md>`. The helper refuses class-level reviews without a skill path so durable production lessons do not get stranded in task logs.
