# WAYS Video Lab Discord Hub

Purpose: dedicated Discord space for building, testing, QAing, and automating the Wait, Are You Serious? short-video pipeline.

Status: the WAYS Video Lab category and channels exist. This thread (`1512650920373256232`) is the preferred project discussion and QA-decision surface; the dashboard is now the companion media-review surface, not the primary workflow.

## Recommended Discord category

**WAYS Video Lab**

## Channels to create

1. `#ways-video-lab-announcements`
   - Final decisions, locked templates, major wins, blocked states.
   - Low noise. Only benchmark updates and handoff summaries.

2. `#ways-video-lab-builds`
   - Active renders, Comfy/Wan/Higgsfield/CapCut runs, output links, contact sheets.
   - Working thread for daily build activity.

3. `#ways-video-lab-qa-gates`
   - 8/10 and 9/10 gate reviews, per-shot scoring, artifact failures, publish/internal decisions.
   - Keep harsh, evidence-backed, and concise.

4. `#ways-video-lab-automation`
   - Kanban updates, cron/watchers, dashboard status, model/lane tests, pipeline changes.
   - Use for “what can now run unattended?” and “what still needs human approval?”

5. `#ways-video-lab-templates`
   - Locked recipes, prompt templates, Comfy workflows, caption style, export specs.
   - Pin the Wan2.2 A14B template note here.

Optional if Discord supports forums:

- `WAYS Video Lab Candidates` forum with tags: `shark`, `wombat`, `mantis-shrimp`, `benchmark`, `internal`, `publish-gate`, `blocked`, `template`.

## First pinned posts

Use `seed-posts.md` in this folder.

## Current best local video benchmark

The approved local video model/template is the Wan2.2 A14B I2V shark v27 pass.

Template folder:

`C:\dev\curious-shorts\templates\wan22-a14b-i2v-short-template\`

Key settings:

- Comfy workflow: `C:\dev\vj-engine\comfyui\workflows\wan2_2_a14b_gguf_lightning_i2v_smoke.json`
- Original `WanImageToVideo` lane
- VAE override: `wan_2.1_vae.safetensors`
- Clip render: `432x768`, `25f`, `24fps`
- Assembly: stretch clips to VO beat durations, master `1080x1920`, Discord preview `720x1280`, generate contact sheet and ffprobe.

## Kanban board

Board: `ways-video-lab`

Local project root:

`C:\dev\curious-shorts\`

Use this board for pipeline automation, not one-off chat memory.

Canonical factory/QC spec:

`C:\dev\curious-shorts\ops\ways-video-lab-discord\WAYS_KANBAN_AND_QC_GATES.md`

Critical gates from that spec:

- Agent runs automated gates unattended, but halts for Josh at Plate QC, phone-size final review, and public publish authorization.
- Default upload state is private. Public publish requires explicit human authorization.
- Private draft bar is 8-9/10. Public bar is 9/10+ plus human approval.
- Premium plate lane is Higgsfield Unlimited only; never spend metered credits without approval.
- Ready-to-Publish cards must satisfy the full artifact contract, including `PUBLISH_GATE.md` and `youtube_draft_pack/` verification files.

## QC gate runner

Run the automated factory gate/WIP check from the project root:

```powershell
python3 tools/ways_qc_gate_runner.py --board dashboard/data.json --root C:\dev\curious-shorts --out ops\ways-video-lab-discord\ways_qc_report_latest.json --checklist-out ops\ways-video-lab-discord\WAYS_QC_GATE_RUNNER_CHECKLIST.md
```

The runner records per-card `blocking_gate` / `rework_reason`, blocks Gate 1/3/4 failures, enforces WIP limits, and keeps Gate 2 / Gate 5 / Gate 6 human-only as advisory blocked states unless explicit human approval fields are present.

Plate QC dashboard contract/reference server:

- Contract: `C:\dev\curious-shorts\ops\ways-video-lab-discord\PLATE_QC_DASHBOARD_CONTRACT.md`
- Reference server: `C:\dev\curious-shorts\scripts\plate_qc_dashboard_server.py`
- Queue input: `C:\dev\curious-shorts\dashboard\plate_qc_queue.json`
- Decision persistence: `C:\dev\curious-shorts\dashboard\plate_qc_decisions.json`

Discord-first QA interaction contract:

- Contract: `C:\dev\curious-shorts\ops\ways-video-lab-discord\DISCORD_QA_INTERACTION_CONTRACT.md`
- Helper/parser: `C:\dev\curious-shorts\tools\ways_discord_qa.py`
- Discord outbox: `C:\dev\curious-shorts\ops\ways-video-lab-discord\discord_qa_outbox.md`
- Final/publish decision ledger: `C:\dev\curious-shorts\dashboard\review_decisions.json`
