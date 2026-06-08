# Next Steps — Test Short 001

## Current rough cut
- Output: `outputs/sharks_older_than_trees_roger_comfy_v2.mp4`
- Duration: ~23.9s
- Resolution: 1080×1920
- Voice: Roger / ElevenLabs selected for current prototype
- Visual lane: ComfyUI SDXL Turbo stills, curated from 60 initial candidates plus 24 softer regen variants.
- Status: useful proof that local image-gen works, but visually too repetitive. Most frames say “calm shark underwater” instead of literal line-by-line ideas.
- Next visual rule: **say dog, see dog**. See `visual_direction_v3_say_dog_see_dog.md`.
## Script decision
- Current last line: “You’re looking at a survivor from a world before forests.”
- Replaces the too-abstract “old idea that still works” line.
- Keep evaluating against narration; if it still feels too polished, alternate closer: “You’re looking at something that survived a world before forests.”

## Immediate review questions
1. Is the ~24s Roger pacing too fast, too slow, or right?
2. Does the hook deserve a harder first line? Options:
   - “Sharks are older than trees.”
   - “This animal is older than every forest on Earth.”
   - “Sharks were here before trees existed.”
3. Should the narrator be male, female, or mascot/character?
4. Should the brand feel more:
   - museum science
   - cozy bedtime learning
   - bright YouTube facts
   - storybook adventure

## Voice gate
Current proxy voices are rejected. Use `voice_audition_packet.md` to generate higher-quality auditions before final concept validation. Edge/local voices remain timing scratch only.

ElevenLabs permissions fixed and four audition files generated in `outputs/voice_auditions/`:
- `01_warm_older_brother_uncle.mp3` — Roger, ~24.0s — **selected for current prototype**
- `02_warm_older_sister_aunt.mp3` — Sarah, ~23.8s
- `03_soft_science_storyteller.mp3` — George, ~23.6s
- `04_younger_curious_narrator.mp3` — Jessica, ~25.9s

Voice decision: Roger is a good fit for now. Keep as prototype voice while moving into visual generation. See `selected_voice.md` and `outputs/selected_voice_manifest.json`.

## Visual generation status
Local ComfyUI image generation is now unblocked.

Working lane:
- Server: `http://127.0.0.1:8188`
- Launch method: Windows ComfyUI venv from WSL via `/mnt/c/Windows/System32/cmd.exe`
- GPU verified: NVIDIA GeForce RTX 5090
- Checkpoint installed: `C:\dev\ComfyUI\models\checkpoints\sd_xl_turbo_1.0_fp16.safetensors`
- Agent script: `scripts/comfy_sdxl_turbo_generate.py`
- Setup notes: `image_gen_setup.md`

First outputs:
- All-candidates contact sheet: `outputs/comfy_shot_set_v1_all_contact_sheets.jpg`
- Soft regen contact sheet: `outputs/comfy_soft_regen_contact_sheet.jpg`
- Selected-stills contact sheet: `outputs/comfy_selected_v1_contact_sheet.jpg`
- Selected manifest: `outputs/comfy_selected_v2_manifest.json`
- First Comfy/Roger cut: `outputs/sharks_older_than_trees_roger_comfy_v2.mp4`

## Local generation pass
Generated six 9:16 stills from `prompts_and_metadata.json` direction using the ComfyUI SDXL Turbo lane. First pass used 60 candidates, then a 24-candidate softer regen for less teeth/scary energy.

Suggested first local lane:
1. Flux/SDXL stills in ComfyUI.
2. Pick best still per shot.
3. Assemble with pan/zoom first.
4. Then animate only shots 2, 3, 5, and 6 via local I2V.

## Quality bar
Reject outputs with:
- scary shark attack energy
- mangled animals
- unreadable/generated text artifacts
- inconsistent style between shots
- weak “image wobble” that adds no real motion
- toddler-content look

## Paid challenger only after local pass
If local motion is weak, buy/try only one hero shot first:
- ancient shark gliding through prehistoric ocean
- final peaceful shark + tree memory line

Do not pay for every shot until we know the local lane cannot clear the trust/retention bar.
