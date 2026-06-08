# Seed posts for WAYS Video Lab Discord channels

## Post in `#ways-video-lab-announcements`

**WAYS Video Lab is live.**

This is the dedicated place for building the Wait, Are You Serious? video pipeline from promising local experiments into a repeatable, semi-automated production system.

Current benchmark: the shark v27 local Wan2.2 A14B I2V pass is the best local video result so far and is now the saved template.

Template path:

`C:\dev\curious-shorts\templates\wan22-a14b-i2v-short-template\`

Kanban board:

`ways-video-lab`

Working rule: keep testing what is out there, but preserve the current best local template as the benchmark until something clearly beats it.

---

## Post in `#ways-video-lab-templates`

**Locked template: Wan2.2 A14B I2V local real-motion base**

Approved by Josh: “This is it! This is the model.”

Template folder:

`C:\dev\curious-shorts\templates\wan22-a14b-i2v-short-template\`

Critical recipe:

- Comfy workflow: `C:\dev\vj-engine\comfyui\workflows\wan2_2_a14b_gguf_lightning_i2v_smoke.json`
- Keep original `WanImageToVideo` lane.
- Override VAE to `wan_2.1_vae.safetensors`.
- Do not switch to `wan2.2_vae.safetensors` in the current install unless retested.
- Render short true-motion clips: `432x768`, `25f`, `24fps`.
- Stretch clips to VO beat durations.
- Master: `1080x1920`, H.264, AAC audio.
- Discord preview: `720x1280`, H.264, AAC audio.
- Always generate contact sheet + ffprobe + QA note.

This is a real-motion base lane. Final publish still needs captions, full-speed QA, and 9/10 gate.

---

## Post in `#ways-video-lab-qa-gates`

**QA gate rules**

A candidate must be judged on:

1. Actual motion vs still zoom.
2. Gross morphing/artifacts.
3. Animal anatomy and subject preservation.
4. Captions: readable, accurate, no double-captioning.
5. Audio: present, synced, normalized enough.
6. Phone-size read.
7. Per-shot 9/10 gate when active.
8. Publish-ready vs internal-only.

Do not call a Discord preview YouTube-ready until there is a full upload pack: 1080x1920 captioned master, clean master, captions file, contact sheet, ffprobe, audio sanity check, thumbnail/metadata starter, and README_QA.

---

## Post in `#ways-video-lab-automation`

**Automation roadmap**

Active board: `ways-video-lab`

Initial automation tracks:

- Lock and document the shark v27 benchmark template.
- Build a repeatable render harness from script/shot manifest → Wan clips → master/preview/contact sheet/ffprobe.
- Add automated preflight checks for Comfy server, workflow nodes, model files, VAE override, source stills, and voiceover.
- Add a cheap QA proxy: ffprobe, frame/contact-sheet generation, CLIP/DINO subject preservation where useful, and VLM survivor gate for anatomy/text/glass-plane issues.
- Build a dashboard for candidates, scores, artifacts, and human decisions.
- Keep testing new local/video lanes, but benchmark them against shark v27 before promoting.

---

## Post in `#ways-video-lab-builds`

**Build-log format**

Use this format for each build:

```md
## Build: <topic/version>

Goal:

Source assets:

Workflow/model:

Settings:

Outputs:
- Master:
- Preview:
- Contact sheet:
- Manifest:
- QA note:

Verification:
- ffprobe:
- Audio:
- Visual QA:

Decision:
- publish-ready / internal-only / blocked

Next action:
```
