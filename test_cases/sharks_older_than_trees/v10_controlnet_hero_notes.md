# v10 ControlNet Hero-Frame Test Notes

## What changed
Installed and used SDXL Canny ControlNet with DreamShaper XL Turbo:
- ControlNet model: `C:\dev\ComfyUI\models\controlnet\xinsir_controlnet_canny_sdxl_v2.safetensors`
- Base model: `DreamShaperXL_Turbo_V2-SFW.safetensors`
- Workflow: v7 layout reference → Canny control → DreamShaper polish.

## Result
This is the closest pipeline so far to the target because it combines:
- layout control from the cut-out POC
- higher-quality image model polish
- literal “say dog, see dog” structure

Preview sheet:
`outputs/v10_controlnet_hero_frames_contact_sheet.jpg`

## Best current variants
- **01 before trees:** v2 or v3. Both preserve barren land + ocean + shark and avoid trees. v2 is cleaner; v3 has a more readable shark.
- **03 apple/squirrel/acorn:** v3/v4 are the strongest visually, but the squirrel/acorn still read too abstract. Needs clearer charming character silhouette and separate acorn/nut.
- **04 deep-time timeline:** v4 is most production-like and dimensional, but it still uses too many repeated clock/icon marks and needs a cleaner geologic timeline without fake text-like clutter.

## Quality diagnosis
v10 is a real step in the right direction, but not final. It proves the correct technical path: **ControlNet + premium model + hard curation**.

## Next pass: v10.1
Generate only targeted fixes:
1. Before trees: refine around v2/v3, keep no plants/trees.
2. Apple/squirrel/acorn: stronger character design; apple, squirrel, acorn must be unmistakable and separated.
3. Timeline: make it read as stacked rock strata + fossils, fewer repeated clock icons, no fake text artifacts.

Do not reset the style. Improve within this controlled premium cut-out direction.
