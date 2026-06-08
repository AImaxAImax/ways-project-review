# Flying Snake Higgsfield Frames v01 QA

Generated via authenticated Higgsfield CLI using free/low-cost Higgsfield image lanes after user preference update.

## Artifacts
- Contact sheet: `outputs/higgsfield_frames_v01/higgsfield_snake_candidates_contact_sheet_v01.jpg`
- Prompt pack: `outputs/higgsfield_frames_v01/higgsfield_prompt_pack_v01.json`
- Generation manifest: `outputs/higgsfield_frames_v01/higgsfield_generation_manifest_v01.json`
- Raw frames: `outputs/higgsfield_frames_v01/raw/*.png`

## Candidate verdicts

| ID | Model | Verdict | Notes |
|---|---|---|---|
| `nano_01` | Nano Banana 2 Flash | Reject / weak | Snake readable, but too buried in foliage and branch/canopy clutter. Airborne action is not instant. |
| `nano_02` | Nano Banana 2 Flash | Maybe | Clear single snake between trees, good body wave. Still looks more like a normal snake floating than a flattened glider. Usable as a style/source backup, not hero. |
| `nano_03` | Nano Banana 2 Flash | Best still candidate | Strong open-air read, single snake, clean negative space, no text/logos. Body looks pale/smooth and not obviously flattened, but action reads as gliding. |
| `nano_04` | Nano Banana 2 Flash | Reject | Dynamic, but anatomy breaks: reads like two heads / doubled body, branch contact ambiguity. Not usable. |
| `seedream_02` | Seedream V5 Lite | Good candidate | Cleanest simple silhouette, airborne over canopy, no clutter/text. Slightly stylized/soft but source-plate usable for the "side-to-side glide" beat. |
| `seedream_03` | Seedream V5 Lite | Best candidate | Most premium/clear: snake suspended high over canopy, one animal, strong open-air context, no text/logos. Good hero/source plate. |
| `seedream_04` | Seedream V5 Lite | Maybe / weak | Very clear open gap and tree-to-tree direction, but snake is too tiny/thin for phone-size hero. Could work as wide transition only. |

## Overall Gate 2 note
This Higgsfield pass is a meaningful upgrade over local Comfy v02. Best picks are `seedream_03`, `seedream_02`, and `nano_03`. They clearly show a snake in open air with no visible text/logos/watermarks. None perfectly show the flattened airfoil body, so next generation should target belly-wide/flattened-body closeups and a launch-from-branch frame.

## Recommended next step
Queue a second Higgsfield sweep with the three best frames as visual references if possible, focused on:
1. launch frame: branch clearly behind, snake already separated from it;
2. flattened body close/medium: underside visible, body wide like a ribbon;
3. tree-to-tree steering: snake larger in frame than `seedream_04`.
