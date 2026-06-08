#!/usr/bin/env python3
"""Generate SDXL Turbo candidates for the sharks short.

Builds out the selected #4 style across the full six-shot storyboard.
"""
from importlib.machinery import SourceFileLoader
from pathlib import Path
import json, time

ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
gen=SourceFileLoader('comfy_gen', str(ROOT/'scripts/comfy_sdxl_turbo_generate.py')).load_module()

STYLE=(
    'vertical 9:16 premium cinematic soft 3D educational animation still, '
    'calm family science YouTube Short, natural history museum quality, '
    'dreamy prehistoric blue green ocean palette, soft sun rays, floating particles, '
    'gentle awe, painterly but polished, clean negative space for editor-added captions, '
    'no text in image, no logos, no watermark, no gore, no horror, no open mouth, no attack pose, '
    'not toddlerish, not cartoon mascot'
)

SHOT_PROMPTS={
  '01_before_trees_hook': (
    STYLE + ', ancient shark swimming in a vast Paleozoic ocean before forests existed, single elegant shark silhouette in the mid-distance, sunbeams from above, mysterious and beautiful, minimalist composition'
  ),
  '02_empty_land_before_forests': (
    STYLE + ', cinematic split-feeling composition: underwater ancient shark world in foreground and distant barren rocky shoreline above water hinting a world before forests, no modern plants, no tall trees, atmospheric haze'
  ),
  '03_shark_older_than_trees': (
    STYLE + ', calm prehistoric shark hero shot in side profile, anatomically believable ancient shark, smooth graceful body, no teeth focus, gentle eye, deep teal ocean, small primitive sea life silhouettes for scale'
  ),
  '04_trees_arrive_later': (
    STYLE + ', poetic visual contrast: faint ghostly silhouettes of early primitive tree-like plants above the waterline while an ancient shark glides below, implying sharks came first, elegant composition, no literal text'
  ),
  '05_survival_through_ages': (
    STYLE + ', timeless ancient shark gliding through layered ocean light, subtle silhouettes of changing eras as abstract shapes in the background, survivor feeling, calm powerful animal, cinematic depth'
  ),
  '06_world_before_forests': (
    STYLE + ', final quiet awe image, ancient shark in a vast glowing prehistoric ocean, small solitary silhouette, shafts of light, a world before forests, peaceful majestic ending frame, clean dark upper space for final caption'
  ),
}

OUT=ROOT/'assets/comfy_shot_set_v1'
OUT.mkdir(parents=True, exist_ok=True)
manifest=[]
base_seed=26052600
variants=10

for shot_idx,(shot,prompt) in enumerate(SHOT_PROMPTS.items(),1):
    for variant in range(1, variants+1):
        seed=base_seed + shot_idx*100 + variant
        prefix=f'{shot}_v{variant:02d}'
        print(f'GENERATE {shot} variant {variant} seed={seed}', flush=True)
        imgs=gen.run(prompt, seed=seed, prefix=prefix)
        for img in imgs:
            p=Path(img)
            target=OUT/p.name
            if p.resolve()!=target.resolve():
                target.write_bytes(p.read_bytes())
            manifest.append({'shot':shot,'variant':variant,'seed':seed,'prompt':prompt,'file':str(target)})

mf=ROOT/'outputs/comfy_shot_set_v1_manifest.json'
mf.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(mf),'out_dir':str(OUT)},indent=2))
