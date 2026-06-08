# WAYS project review bundle

This is a sanitized GitHub review bundle for the WAYS (**Wait, Are You Serious?**) short-form video factory.

It includes code, docs, templates, JSON manifests, QA notes, and selected Comfy workflow JSON. It intentionally excludes large generated media files, model weights, caches, and credential/token files.

Start here:

0. `docs/README.md` - canonical docs index; names the winning source on conflicts.
1. `docs/AGENT_REVIEW_BRIEF.md`
2. `docs/WAYS_PROJECT_HANDOFF_FULL_RUNDOWN.md`
3. `docs/CRONS_AND_AUTOMATION.md`
4. `docs/WORKFLOWS_AND_PHILOSOPHY.md`
5. `ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md`
6. `templates/wan22-a14b-i2v-short-template/README.md`

Important: do not assume this repo contains all generated videos/images. Media outputs are excluded for GitHub size/safety. The code and manifests reference local paths under `C:\dev\curious-shorts` / `/mnt/c/dev/curious-shorts`.

## Pre-push hygiene

Install the tracked hygiene hook in any clone before pushing:

```bash
git config core.hooksPath .githooks
```

The hook runs `python3 scripts/pre_push_hygiene_check.py` and blocks pushes that contain local username paths, token-like strings, or private-key headers in tracked files. The scanner self-tests known-bad samples before scanning so a broken regex fails closed.
