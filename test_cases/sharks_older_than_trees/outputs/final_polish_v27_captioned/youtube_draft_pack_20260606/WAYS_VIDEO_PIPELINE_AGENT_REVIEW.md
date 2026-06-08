# WAYS Short-Form Video Pipeline: Current State for Agent Review

**Channel:** Wait, Are You Serious? / WAYS  
**Current benchmark project:** `sharks_older_than_trees`  
**Current date/context:** 2026-06-06  
**Primary goal:** Build repeatable Idea → Script → Hero Photo → All Photos → I2V → Captioned Video → QA → YouTube Draft workflow.

## 1. Channel and audience rules

- The videos are **not aimed at kids**, but they should be **kid-friendly**, safe for a general/family audience, and interesting.
- Complex topics are allowed. The bar is: make the topic understandable without dumbing it down.
- WAYS tone: quick “Wait, are you serious?” curiosity, educational awe, no gore, no horror, no sensational fake claims.
- For animal/nature/science visuals: family-friendly does **not** mean fake, toy-like, or softened anatomy. Realism comes first.
- Draft/upload gate: do not upload to YouTube unless the candidate clears the active **8-9/10 private-draft bar**. Public publish still needs final human approval.

## 2. Current shark video status

### Current YouTube-ready candidate

- Video: `outputs/final_polish_v27_captioned/publish_candidate_captioned.mp4`
- Clean no-caption/less-final base copy: `outputs/final_polish_v27_captioned/clean_master_unmodified.mp4`
- Discord preview: `outputs/final_polish_v27_captioned/discord_preview_captioned.mp4`
- Captions: `outputs/final_polish_v27_captioned/captions.ass`, `outputs/final_polish_v27_captioned/captions.srt`
- Contact sheet: `outputs/final_polish_v27_captioned/contact_sheet_final_polish.jpg`
- Upload metadata pack: `outputs/final_polish_v27_captioned/youtube_draft_pack_20260606/`

### Verified specs

- `1080x1920`, vertical 9:16
- H.264 video at 24 fps
- AAC audio, 48 kHz mono
- Duration: `24.000s`
- File size: `16,306,185` bytes
- Audio volume check: mean about `-15.1 dB`, max about `-0.9 dB`
- MD5 video: `ed6157a72b32cbf6f2bd6b24ee5dde93`

### QA read

This is acceptable for a **private YouTube draft** under the current 8-9/10 threshold.

Strengths:
- Strong hook: “SHARKS WERE HERE BEFORE TREES” is readable immediately.
- Caption style is big, centered, high-contrast, and phone-readable.
- Real local Wan2.2 I2V motion is present instead of pure Ken Burns/fake deterministic motion.
- The final shot is calm/ancient, not horror or gore.
- Audio is present, normalized, and speech-forward.

Known risks before public publish:
- Some source plates still show AI/surreal texture, especially the apple/squirrel/nut comparison shot and first-forest/deep-time plates.
- The Wan clips are short 25-frame I2V clips stretched over VO beats, so motion is subtle.
- Source I2V resolution is `432x768` upscaled to `1080x1920`, so fine detail is softer than a true premium final render.
- Captions are key-word emphasized ASS captions, not true Whisper/CapCut word-by-word karaoke.
- This is a YouTube draft candidate, not an automatic public publish.

## 3. Pipeline architecture

### Stage A: Idea intake

Input can be:
- new curiosity fact,
- old backlog idea,
- user-supplied rough hook,
- research note,
- “can you believe this?” science/history/nature claim.

Output should be a small idea card:

```json
{
  "slug": "sharks_older_than_trees",
  "hook": "Sharks were here before trees.",
  "core_fact": "Sharks appeared over 400M years ago; first true trees appeared around 385M years ago.",
  "audience": "general/kid-friendly, not child-targeted",
  "visual_risk": "animal anatomy and deep-time imagery",
  "source_need": "realistic shark, fossil proof, pre-forest world, first forests, modern aquarium/payoff"
}
```

Acceptance criteria:
- One clear teachable moment.
- Hook payoff in first 1-2 seconds.
- Fact can be supported in the description if needed.
- Visuals can be shown literally or with an honest symbolic caveat.

### Stage B: Script

Current WAYS script target:
- Short, human, direct.
- One claim per beat.
- No generic AI-explainer cadence.
- Captions and VO should match exactly or near-exactly.
- Kid-friendly language, but not childish.

Current shark script/caption beats:

1. `SHARKS WERE HERE / BEFORE TREES`
2. `SERIOUSLY.`
3. `BEFORE APPLES. / BEFORE SQUIRRELS.`
4. `OVER 400 MILLION / YEARS AGO`
5. `THEN FORESTS / FINALLY ARRIVED`
6. `AND TODAY... / THEY ARE STILL HERE`
7. `SURVIVOR / FROM A WORLD / BEFORE FORESTS`

Acceptance criteria:
- Every line has a visual beat.
- No line requires repeated filler footage.
- If a line says the thing, the shot should show the thing or a clean symbolic proxy.

### Stage C: Hero photo / source plate generation

Current best still lane:
- Manual/high-touch GPT Image 2 or equivalent premium stills for the key plates.
- Local/Comfy can be candidate lanes, but not assumed final for animal anatomy.
- Higgsfield image lane only if verified non-credit/Unlimited. Never spend credits without approval.

For WAYS animal/science plates, asset gate is strict:
- no text, labels, numbers, logos, UI, watermarks,
- caption-safe negative space,
- phone-size concept read,
- realistic animal anatomy,
- kid-friendly awe, not horror,
- source plate must be animation-ready with foreground/midground/background separation.

Shark v27 selected stills in `render_wan22_harness_config.json`:
- `assets/gpt_image_2_manual_v23/shot01_gpt_image2_hook_before_trees_v01.jpeg`
- `assets/gpt_image_2_manual_v24/shot02_seriously_fossil_proof_v01.jpeg`
- `assets/gpt_image_2_manual_v24/shot03_apple_squirrel_nut_v01.jpeg`
- `assets/gpt_image_2_manual_v24/shot04_deep_time_rock_layers_sharks_v01.jpeg`
- `assets/gpt_image_2_manual_v24/shot05_first_trees_coastline_v01.jpeg`
- `assets/gpt_image_2_manual_v24/shot06_kid_aquarium_deep_time_v01.jpeg`
- `assets/gpt_image_2_manual_v23/04_final_predator_got_here_first.png`

### Stage D: All photos / storyboard manifest

Current manifest format includes:
- shot id,
- image path,
- duration,
- caption,
- seed,
- I2V prompt,
- output clip path.

Primary file:
- `render_wan22_harness_config.json`

Rules:
- Do not reuse one still for too many adjacent beats unless intentionally accepted as a static-first internal draft.
- Every beat needs a unique matching visual when the goal is final/publish.
- Long beats should be split or given enough motion/visual change to avoid repeated-still fatigue.

### Stage E: I2V render

Current winning template:
- `C:\dev\curious-shorts	emplates\wan22-a14b-i2v-short-template\`
- WSL path: `/mnt/c/dev/curious-shorts/templates/wan22-a14b-i2v-short-template/`

Current proven workflow:
- ComfyUI workflow: `C:\devj-engine\comfyui\workflows\wan2_2_a14b_gguf_lightning_i2v_smoke.json`
- Important repair: set `39.inputs.vae_name` to `wan_2.1_vae.safetensors`
- Do not swap to `wan2.2_vae.safetensors` in this setup. It caused latent/channel mismatch failures.
- Do not use untested `Wan22ImageToVideoLatent` patches.

Proven settings:
- Wan clip size: `432x768`
- Clip length: `25` frames
- Timeline: `24 fps`
- Seeds: `627101` through `627107`
- Strategy: generate short true-motion clips, then stretch to match VO/caption beat durations.

Output directory for successful shark batch:
- `outputs/wan22_v27_animated_frames/`

Acceptance criteria:
- all expected clips present,
- no catastrophic morphing/anatomy failures,
- no generated text/logos,
- ffprobe confirms final master and preview have audio,
- contact sheet exists.

### Stage F: Assembly

Current assembly pattern:
1. Download/collect each Wan clip.
2. Stretch `25 / 24 = 1.0417s` clips to target beat durations using `setpts`.
3. Scale/crop to `1080x1920`.
4. Concatenate in order.
5. Mux voiceover/audio.
6. Export clean master and Discord preview.
7. Generate ffprobe JSON and contact sheet.

Current base outputs:
- `outputs/wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_audio.mp4`
- `outputs/wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_discord.mp4`
- `outputs/wan22_v27_animated_frames/contact_sheet_v27_wan22.jpg`

### Stage G: Final polish / captions

Current final-polish output:
- `outputs/final_polish_v27_captioned/`

The final-polish lane:
- preserves clean master,
- creates ASS and SRT captions,
- burns large centered WAYS captions,
- highlights useful key words in yellow,
- normalizes audio,
- writes ffprobe JSON,
- creates contact sheet,
- creates `PUBLISH_GATE.md`.

Known improvement needed:
- Upgrade to true word-level karaoke when reliable Whisper/CapCut word timings are available.
- Keep current key-word captions acceptable for drafts where readability matters more than word-level highlighting.

### Stage H: QA gate

Minimum checks before showing/uploading:
- video is playable,
- 1080x1920 master exists,
- audio stream exists and is not clipped,
- captions are readable at phone size,
- no double captions or extra on-screen labels,
- visual reset every 2-3 seconds,
- each shot maps to the spoken claim,
- animal anatomy does not fail,
- contact sheet reviewed,
- private YouTube draft only if 8-9/10 or better.

Separate scores:
- **Private draft score:** can be 8-9/10 with known polish risks.
- **Public publish score:** should be 9/10+ and preferably human-approved.
- **Template score:** whether the pipeline is reusable even if a specific video has weak assets.

### Stage I: YouTube draft upload

Draft metadata is stored in:
- `outputs/final_polish_v27_captioned/youtube_draft_pack_20260606/youtube_metadata.json`
- `outputs/final_polish_v27_captioned/youtube_draft_pack_20260606/description_upload.txt`

Upload rules:
- Always upload as `private` draft unless explicitly told to publish.
- `selfDeclaredMadeForKids` should be `false` for WAYS: kid-friendly/general audience, not made for children.
- Category: `28` Science & Technology.
- Verify via YouTube Data API after upload.
- Save upload result and verification JSON beside the pack.
- If custom thumbnail 403s, do not block upload. Report auto-thumbnail fallback.

## 4. Current bottlenecks and next build priorities

### Bottleneck 1: still/photo generation consistency

The main quality determinant is the still plate. The I2V template can animate, but it cannot fix weak/fake source plates.

Next agent work:
- Build a plate queue from ideas/scripts.
- Generate hero photo first, then all required shot plates.
- Gate plates before I2V.
- Keep accepted/rejected manifests.

### Bottleneck 2: true motion vs stretched short clips

Wan2.2 A14B clip quality is now proven, but clips are short.

Next agent work:
- Test longer clip settings if GPU budget allows.
- Test frame interpolation between stretched frames.
- Create a mid-run QA watchdog that stops bad render surfaces early.

### Bottleneck 3: captions

Current captions are readable and draft-ready, but not yet best-in-class karaoke.

Next agent work:
- Add Whisper/CapCut word-timing lane.
- Verify word count against script.
- Keep inactive words white and active/key words yellow.

### Bottleneck 4: automated QA proxy

Contact-sheet review works, but automatic scoring is still advisory.

Next agent work:
- Add hard ffprobe checks.
- Add contact-sheet VLM gate for: text artifacts, caption clipping, animal anatomy, repeated-still fatigue, phone-size read.
- Keep VLM gate advisory until calibrated against Josh’s labels.

### Bottleneck 5: production ops

Discord WAYS Video Lab channel creation is waiting on admin permissions/user check.

Already prepared local ops files:
- `C:\dev\curious-shorts\ops\ways-video-lab-discord\README.md`
- `C:\dev\curious-shorts\ops\ways-video-lab-discord\seed-posts.md`
- `C:\dev\curious-shorts\ops\ways-video-lab-discord\kanban-bootstrap.md`

Kanban board:
- `ways-video-lab`

## 5. Recommended next-agent execution plan

1. Treat the shark v27 draft as the current benchmark.
2. Do not rebuild it from scratch unless human review rejects a specific shot or caption style.
3. Start the next video from the same pipeline:
   - idea card,
   - human script,
   - hero frame,
   - all shot frames,
   - asset contact sheet,
   - Wan2.2 I2V batch,
   - final-polish caption pack,
   - contact-sheet QA,
   - YouTube private draft only if 8-9/10.
4. Build a reusable `idea_to_video` runner that accepts a manifest and emits the same artifact contract.
5. Add a dashboard or review queue for still plates so Josh can quickly approve/reject hero/all-photo candidates.

## 6. Artifact contract for future videos

Each video should ship a folder containing:

```text
project_slug/
  idea_card.json
  script.md
  storyboard_manifest.json
  assets/
    accepted_stills/
    rejected_stills/
  outputs/
    i2v_clips/
    clean_master.mp4
    publish_candidate_captioned.mp4
    discord_preview_captioned.mp4
    captions.ass
    captions.srt
    contact_sheet.jpg
    ffprobe_publish.json
    audio_report.txt
    PUBLISH_GATE.md
    youtube_draft_pack/
      youtube_metadata.json
      description_upload.txt
      thumbnail_candidate.jpg
      youtube_upload_result.json
      youtube_verification.json
```

## 7. Current decision

The shark video is **YT-private-draft ready**, not public-publish-final. It clears the practical draft bar because the specs, audio, captions, and overall visual read are good enough to review in Studio. Public posting should wait for human review of the private draft.
