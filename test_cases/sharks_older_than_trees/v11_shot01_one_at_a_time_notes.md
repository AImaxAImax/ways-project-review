# v11 Shot 1 — One-at-a-time Production Notes

## User direction
Build the visuals one shot at a time because batch contact sheets were drifting or regressing.

## Shot
**01 — “Sharks were here before trees.”**

## Workflow change
After the v10 regression, the new method avoids using crude POC frames as full ControlNet references.

Instead:
- create a sparse composition guide only
- use ControlNet lightly
- generate from empty latent, not img2img from low-quality art
- avoid positive prompt words that accidentally trigger trees
- describe the land as lifeless volcanic/geologic coastline before vegetation

## v11 result
The first v11 attempt still produced trees/plants, because the prompt contained tree-related language and the model defaulted to scenic forests.

The v11b/v11c attempts corrected that by using:
- “lifeless volcanic coastline”
- “before land vegetation existed”
- “barren ochre badlands / basalt cliffs”
- strong negative prompt for trees/plants/grass/leaves

## Selected current frame
Selected: **v11c v04**

Path:
`assets/selected_frames_v11/shot01_before_trees_v11c_v04_selected.png`

Why:
- no trees/plants
- barren land reads clearly
- calm shark is visible
- higher quality than the POC cut-out frames
- good enough directionally to hold as the current Shot 1 candidate

## Backup candidates
- v11b v05 — clean barren lagoon with shark, very readable
- v11c v02 — shark more prominent, but less elegant than v11c v04

## Next step
Move to Shot 2 only after user approves this direction, or do one micro-pass on Shot 1 to make the shark 10–15% larger while preserving the barren landscape quality.
