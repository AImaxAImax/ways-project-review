# Iteration Notes — v4/v5/v6

## User feedback
The visuals need both:
1. **Consistent art style** across the video.
2. **Different settings that literally match the words** — “say dog, see dog.”

## What happened
### v4 Comfy pass
- Better style consistency: cut-paper/clay diorama look started to hold.
- Better setting separation: museum, timeline, forest, aquarium became distinct.
- Still failed several literal beats:
  - “before trees” kept generating trees/plants.
  - “seriously/fossil” often became living sharks in an aquarium.
  - final “before forests” kept adding branch/coral shapes that read like forests.

### v5 targeted Comfy pass
- Custom negative prompts improved the museum fossil row.
- The model still ignored “no trees/no plants” in several shots.
- Apple/squirrel/nut became clearer but still too busy/foresty.

### v6 controlled paper-cut refs
- Controlled reference plates solve the core direction problem:
  - consistent single art language
  - clearly different settings
  - literal objects/ideas per narration line
- These are not final polish, but they are the clearest art-direction target so far.

## Current recommendation
Use v6 controlled paper-cut frames as the **reference target / layout lock**, then either:
1. Polish this controlled vector/paper-cut style directly into final frames, or
2. Use these as img2img/control references for a more premium Comfy pass.

Do not continue pure text-to-image prompting without visual references; SDXL Turbo keeps drifting back toward similar underwater shark scenes and unwanted trees.

## Latest artifacts
- v4 Comfy sheet: `outputs/comfy_say_dog_v4_contact_sheet.jpg`
- v5 targeted Comfy sheet: `outputs/comfy_say_dog_v5_targeted_contact_sheet.jpg`
- v6 controlled sheet: `outputs/v6_controlled_papercut_contact_sheet.jpg`
- v6 frame folder: `assets/v6_controlled_papercut_refs/`
