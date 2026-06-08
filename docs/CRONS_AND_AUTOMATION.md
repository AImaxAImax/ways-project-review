# Active Hermes crons and automation context

Snapshot taken: 2026-06-08 from `cronjob(action="list")`.

## WAYS-specific jobs

### `b7643810a233` — WAYS five-video automation floor
- State: enabled, scheduled
- Schedule: every 120 minutes
- Deliver: origin, in this project thread
- Workdir: `/mnt/c/dev/curious-shorts`
- Skill: `short-form-video-production`
- Toolsets: terminal, file, skills
- Purpose: operate the WAYS video factory and keep at least five WAYS videos active/ready across the pipeline.
- Last status in snapshot: ok
- Next run in snapshot: 2026-06-08 11:07:29 -0700

### `adcfddd15e55` — WAYS iterative still-frame builder until complete
- State: paused/disabled
- Schedule: every 20 minutes, repeat 7/30 used
- Workdir: `/home/<user>/.hermes/shorts-autoresearch`
- Skill: `short-form-video-production`
- Toolsets: terminal, file, browser, vision
- Purpose: continue WAYS image-first still-frame pipeline until queued stills are produced and strict-gated.
- Note: Paused because the factory moved to more explicit WAYS board/QC workflows and local Wan2.2 I2V lanes.

## Adjacent/system jobs that affect the project

### `c6944e2bb344` — Kanban board watcher, keep actionable boards moving
- State: enabled, scheduled
- Schedule: every 5 minutes
- Mode: script-only (`no_agent=true`)
- Script: `kanban_board_watcher.py`
- Purpose: run `hermes kanban dispatch` safely so active boards keep moving.

### `a41265792a9d` — Hindsight memory watchdog
- State: enabled, scheduled
- Schedule: every 5 minutes
- Mode: script-only
- Script: `hindsight_watchdog.py`
- Purpose: keep Hindsight memory services healthy.

### `5a518e6aec61` — Discord to Hindsight daily incremental catch-up
- State: enabled, scheduled
- Schedule: daily at 03:15
- Mode: script-only
- Script: `discord_hindsight_incremental_catchup.py`
- Purpose: persist durable Discord project context into Hindsight.

## Non-WAYS jobs currently present

### `1ed2e6d776a7` — Gmail inbox cleanup
- State: enabled, scheduled
- Schedule: 07:00 and 19:00 daily
- Last status: ok, but delivery error in snapshot: Discord Unknown Channel.

### `b739b9b58991` — weekly home/property second-brain check-in
- State: enabled, scheduled
- Schedule: Fridays 09:00

### `babe8dbeffc0` — BroadcastBench 30-day indexation follow-up
- State: enabled, one-shot scheduled for 2026-06-15 09:00

## Recently referenced one-shot

### `b4653ee1b8c9` — WAYS shark public publish 60h performance review
- Not present in active cron list in the snapshot.
- Interpreted as completed one-shot.
- Performance record: `ops/ways-video-lab-discord/PUBLISH_PERFORMANCE_REVIEW_sharks_older_than_trees_KLwp-KbIr9I_20260608.md`.
