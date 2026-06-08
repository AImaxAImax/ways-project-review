# WAYS Backlog Status and Next Operating Cut

Generated: 2026-06-06

## Public-publish test candidate

Candidate: **Sharks Are Older Than Trees #Shorts**

- YouTube video ID: `KLwp-KbIr9I`
- URL: `https://youtu.be/KLwp-KbIr9I`
- Studio: `https://studio.youtube.com/video/KLwp-KbIr9I/edit`
- Current verification: private, processed, HD, captions attached, category 28, selfDeclaredMadeForKids=false
- Safe public-publish helper: `tools/ways_public_publish.py`

Required Discord Gate 6 authorization before publish:

```text
QA sharks_older_than_trees/final_polish_v27_captioned publish notes="Josh authorizes public publish for KLwp-KbIr9I"
```

After that, publish command is:

```bash
cd /mnt/c/dev/curious-shorts
python3 tools/ways_discord_qa.py parse 'QA sharks_older_than_trees/final_polish_v27_captioned publish notes="Josh authorizes public publish for KLwp-KbIr9I"'
python3 tools/ways_public_publish.py --slug sharks_older_than_trees --video-id KLwp-KbIr9I --execute
```

## Backlog snapshot

Latest QC report: `ops/ways-video-lab-discord/ways_qc_report_latest.json`
Regenerated: 2026-06-06T03:36:13+00:00

- Cards evaluated: 53
- Blocked cards: 1 (Gate 6 public-publish authorization only)
- Render/Plate Generation WIP: 0/3, clear
- Human Final Review WIP: 0/3, clear
- Plate QC: 0/5, clear
- Ready to Publish buffer: 1/10, warning, below the 5-video alert line

Kanban ops board status after verification:

- `ways-video-lab`: 12/12 infrastructure/ops tasks are now done
- Production cutline executed: duplicate/superseded shark variants were moved out of active Render/Human Final Review via status/metadata only; no media was deleted.
- Preserved active shark records: canonical final candidate `sharks_older_than_trees/final_polish_v27_captioned`; Wan2.2 template benchmark `sharks_older_than_trees/lane_benchmark_20260605/benchmark`.
- Remaining bottleneck is Ready-to-Publish inventory depth and explicit Gate 6 authorization, not WIP overload.

## What this means

The historical shark WIP overload is collapsed. Treat `final_polish_v27_captioned` as the only active shark publish candidate and `lane_benchmark_20260605/benchmark` as the preserved Wan2.2 template benchmark. Everything else is parked unless explicitly reactivated.

1. Publish or hold the current shark private draft via Gate 6.
2. Start the next production batch from the revised First-10 list, with max 3 videos in Plate Generation+Render at once.
3. Keep shark variants parked; do not regenerate or spend paid generation on sharks without a new cutline.

## Next production order

Use the revised First-10 order and keep WIP tight:

1. `002_mantis_shrimp_cavitation_punch` — motion-led, strongest animation payoff.
2. `080_saturn_hexagon_storm` — cosmic/still-led, easier source/animation risk.
3. `005_wombat_cube_poop` — known channel benchmark topic, but anatomy/object semantics need harsh gating.

Keep the next batch limited to three active videos. Everything else stays parked until one of those clears Gate 5 or is killed.
