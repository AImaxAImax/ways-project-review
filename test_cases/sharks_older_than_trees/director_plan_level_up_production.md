# Director Plan — Level Up Production Beyond 5/10 POC

## Current conclusion
The user is right: v7 is a 5/10 POC. It proves the concept, but it is not production-grade.

## Tests run after feedback
### v8 SDXL-base challengers
- Installed SDXL base locally for ComfyUI: `sd_xl_base_1.0.safetensors`.
- Generated premium style-frame challengers.
- Result: prettier than v7 in places, but failed control:
  - “before trees” generated trees.
  - timeline generated text-like artifacts.
  - style/settings drifted.

### v8b DreamShaper XL Turbo challengers
- Installed DreamShaper XL Turbo locally: `DreamShaperXL_Turbo_V2-SFW.safetensors`.
- Result: much prettier local model, but pure text-to-image still failed “say dog, see dog.”
  - Before-trees row repeatedly generated trees/forests.
  - Apple/squirrel/acorn row looked polished but became a forest scene.
  - Timeline row became a canyon/ocean scene, not a clear timeline.

### v9 img2img from v7 layouts
- Used v7 as layout references with DreamShaper img2img.
- Result: layout stayed controlled, but quality did not lift enough. It remained too simple/pictogram-like.

## Production diagnosis
We have two separate problems:
1. **Control problem:** pure text-to-image makes prettier images but violates literal shot content.
2. **Quality problem:** controlled procedural layouts obey the story but look too simple.

The final pipeline needs **both control and quality**. Pure prompting is not enough. Pure procedural drawing is not enough.

## Recommended production path
### Phase 1 — Style-frame target, not full video
Create 3–5 premium style frames using a stronger image generation backend or a stronger Comfy control stack. Do not make all 7 shots until one style frame hits at least 8/10.

Target frames:
1. Before trees — hardest control test: barren land + ocean + shark, no trees.
2. Apple/squirrel/acorn gag — hardest charm/prop test.
3. Deep-time timeline — hardest infographic/test artifact control.

### Phase 2 — Add control tools to Comfy
Local Comfy needs a proper control stack before final production:
- SDXL ControlNet Canny/Lineart/Scribble or equivalent
- optional IP-Adapter/style reference
- use v7 layouts as control images, not merely img2img
- generate 8–16 candidates per shot and curate

### Phase 3 — Upgrade output composition
Once stills are selected:
- add camera moves/2.5D parallax
- add foreground paper dust/fiber particles
- add shadow/spotlight animation
- add captions with brand styling
- add sound design: soft museum ambience, water shimmer, timeline ticks, paper swishes

## Quality gate before rendering a new cut
Do not render a full short until the following are true:
- One style frame is clearly 8/10+.
- The same style works on three very different shots.
- The before-trees shot contains no trees/plants.
- The apple/squirrel/acorn shot contains all three items clearly.
- The timeline shot reads as timeline before captions.
- No generated text artifacts.

## Current artifact paths
- v8 SDXL challengers: `outputs/v8_premium_style_challengers_contact_sheet.jpg`
- v8b DreamShaper challengers: `outputs/v8b_dreamshaper_challengers_contact_sheet.jpg`
- v9 img2img DreamShaper: `outputs/v9_img2img_dreamshaper_contact_sheet.jpg`

## Next concrete action
Set up the Comfy control stack or enable a stronger external image-generation provider. Then produce only the three target style frames above and judge those before producing all 7 shots.
