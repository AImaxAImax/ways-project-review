#!/usr/bin/env python3
from importlib.machinery import SourceFileLoader
from pathlib import Path
import json
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/flying_snake_glide')
gen=SourceFileLoader('snake_gen', str(ROOT/'scripts/generate_flying_snake_comfy_candidates_v01.py')).load_module()
OUT=ROOT/'outputs/gate2_plate_qc'
STYLE='vertical 9:16 clean premium 3D educational natural history still, one green flying snake only, full body visible, airborne in open blue sky gap between rainforest trees, clear silhouette, family science YouTube Shorts, no text, no labels, no logos, no watermark, no extra snakes, no wings, no feathers'
PROMPTS={
 '01_launch': STYLE + ', snake launching off a single tree branch on the left into empty air, head forward, tail leaving branch, obvious jump from tree',
 '02_no_wings': STYLE + ', snake floating through open air with empty sky behind it, no branches touching body, no wings, full S-shaped snake visible',
 '03_flatten_body': STYLE + ', close side view of flying snake, body visibly wide and flat like a long ribbon airfoil, open sky behind, no branches touching body',
 '04_side_to_side': STYLE + ', snake gliding diagonally downward in a big S wave, open sky background, subtle motion trail made of light blur only, no arrows',
 '05_tree_to_tree': STYLE + ', snake gliding across a clear empty gap from a branch on the left toward a branch on the right, full body visible in midair'
}
manifest=[]
base=60752000
for si,(shot,prompt) in enumerate(PROMPTS.items(),1):
    for v in range(1,3):
        seed=base+si*100+v
        prefix=f'v02_{shot}_v{v:02d}'
        print('GENERATE',prefix,seed,flush=True)
        imgs=gen.run(prompt, seed, prefix)
        for img in imgs:
            manifest.append({'shot':shot,'variant':v,'seed':seed,'prompt':prompt,'file':img})
mf=OUT/'comfy_candidates_manifest_v02.json'
mf.write_text(json.dumps(manifest,indent=2))
print(json.dumps({'count':len(manifest),'manifest':str(mf)},indent=2))
