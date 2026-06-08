#!/usr/bin/env python3
"""Generate a small v3 proof set with distinct 'say dog, see dog' shot concepts."""
from importlib.machinery import SourceFileLoader
from pathlib import Path
import json

ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
gen=SourceFileLoader('comfy_gen', str(ROOT/'scripts/comfy_sdxl_turbo_generate.py')).load_module()

STYLE='vertical 9:16 premium soft 3D natural history museum animation still, family science YouTube Short, cinematic teal and warm amber palette, polished educational illustration, clean negative space for editor captions, no readable text, no logos, no watermark, kid safe, no gore, no horror, no scary teeth'

PROMPTS={
 '01_before_trees_split': STYLE + ', split scene showing an ancient shark underwater below and barren rocky land above with absolutely no trees, impossible comparison, calm awe, not a shark portrait only',
 '02_seriously_museum_proof': STYLE + ', museum fossil exhibit diorama, ancient shark fossil silhouette behind glass, scientific display mood, skeptical funny confirmation beat, no readable labels or letters',
 '03_before_apples_squirrels_gag': STYLE + ', playful prehistoric barren land scene with ghosted transparent icons of an apple, a squirrel, and an acorn floating as not-yet-existing ideas, no forest, visual joke, no readable text',
 '04_deep_time_timeline': STYLE + ', vertical geological timeline made of glowing rock strata and fossil layers, ancient ocean with small shark silhouette at bottom, deep time, clock-like circular fossil shapes, no numbers or text',
 '05_trees_arrive_late': STYLE + ', primitive early forest and tree-like plants emerging on shoreline above water, shark small in background below water, land and plants are the hero, tens of millions of years later feeling',
 '06_modern_viewer_reframe': STYLE + ', modern family-friendly aquarium or natural history museum scene, child silhouette looking at calm shark through glass, faint ancient fossil ocean reflection overlay, warm awe, no scary teeth',
 '07_final_world_before_forests': STYLE + ', final quiet awe, tiny ancient shark silhouette in vast glowing prehistoric ocean, faint barren shoreline above, a world before forests, peaceful majestic ending frame'
}

OUT=ROOT/'assets/comfy_say_dog_v3_proof'
OUT.mkdir(exist_ok=True, parents=True)
manifest=[]
base=26055000
for i,(shot,prompt) in enumerate(PROMPTS.items(),1):
    for v in range(1,4):
        seed=base+i*100+v
        imgs=gen.run(prompt, seed=seed, prefix=f'{shot}_v{v:02d}')
        for img in imgs:
            p=Path(img)
            manifest.append({'shot':shot,'variant':v,'seed':seed,'prompt':prompt,'file':str(p)})
(ROOT/'outputs/comfy_say_dog_v3_proof_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(ROOT/'outputs/comfy_say_dog_v3_proof_manifest.json')},indent=2))
