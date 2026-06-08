# WAYS Video Lab Kanban Bootstrap

Board slug: `ways-video-lab`

Purpose: move from one-off local wins into a repeatable automated short-video production pipeline.

## Board columns used by Hermes

- `triage` — vague ideas needing specification
- `todo` — specified work, not ready for worker execution
- `ready` — unblocked, can be claimed
- `running` — claimed/in progress
- `blocked` — waiting on human action or external blocker
- `done` — verified completion

The production factory spec uses a domain-level flow over these Hermes statuses:

1. Idea Pool
2. Script Locked
3. Plate Generation
4. Plate QC — human gate
5. Render
6. Assembly & Caption
7. Auto-QA
8. Human Final Review — human gate
9. Ready to Publish
10. Published / Scheduled
11. Performance Review

Canonical spec: `C:\dev\curious-shorts\ops\ways-video-lab-discord\WAYS_KANBAN_AND_QC_GATES.md`

## Initial task groups

### Milestones

- Lock shark v27 as current local-video benchmark.
- Create Discord hub and seed posts.
- Convert shark v27 script into reusable render harness.
- Build QA automation layer.
- Add candidate dashboard.
- Benchmark next local/video lanes against v27.

### Automation acceptance criteria

A run is not “automated” until it can:

1. Preflight Comfy server and required workflow/model files.
2. Validate all source stills and voiceover files exist.
3. Render or resume all shot clips.
4. Assemble master + preview.
5. Generate contact sheet + ffprobe/spec files.
6. Run at least basic artifact checks.
7. Write manifest + README_QA.
8. Surface only human-review candidates that pass hard blockers.

## Human gates

- Discord channel/category creation requires Discord admin action from Josh or a server admin because the current Hermes gateway session cannot create channels.
- Plate QC requires Josh approve/deny and lane confirmation before render.
- Human Final Review requires Josh phone-size review; 8-9/10 can become private draft, 9/10+ is eligible for public.
- Publishing public requires explicit Josh authorization. Default upload is always private.
