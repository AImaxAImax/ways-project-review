#!/usr/bin/env python3
"""Generate v4 proof set: locked cut-paper/clay diorama style, strongly separated settings."""
from importlib.machinery import SourceFileLoader
from pathlib import Path
import json

ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
gen=SourceFileLoader('comfy_gen', str(ROOT/'scripts/comfy_sdxl_turbo_generate.py')).load_module()

LOCKED_STYLE=(
    'vertical 9:16 premium handmade stop motion diorama still, layered cut paper and soft clay miniature art style, '
    'matte paper texture, rounded friendly shapes, shallow depth of field, warm natural history museum lighting, '
    'cohesive teal blue and amber ochre palette, clean simple readable shapes, family science YouTube Short, '
    'no photorealism, no scary horror, no gore, no attack, no readable text, no letters, no numbers, no logo, no watermark'
)

SHOTS={
 '01_before_trees_no_forest': (
    'split-level scene: lower third is prehistoric teal ocean with one small calm ancient shark silhouette; upper two thirds is empty barren ochre rocky land under sky, absolutely no trees, no plants, no forest, vast empty land is the main subject, clear horizon line, visual joke of world before trees'
 ),
 '02_seriously_museum_fossil': (
    'warm museum tabletop exhibit setting, clay fossil shark skeleton silhouette embedded in flat amber stone slab under glass, tiny magnifying glass prop and display lights, proof beat, no ocean water, no living shark, museum setting dominates'
 ),
 '03_before_apples_squirrels_nuts': (
    'playful prehistoric barren land gag, three oversized simple clay props clearly visible: red apple, cute squirrel, and acorn nut, all floating like not-yet-existing ideas above empty rocky ground, crossed-out feeling without using symbols or text, no forest, comedic pause'
 ),
 '04_four_hundred_million_timeline': (
    'vertical geologic timeline diorama, stacked rock strata shelves from bottom to top, tiny shark fossil in lowest blue layer, primitive plant fossil much higher layer, circular fossil clock shapes, deep time museum display, no open ocean scene, timeline structure dominates'
 ),
 '05_trees_arrived_later': (
    'primitive early forest shoreline diorama, strange first tree-like plants and fern trunks rising from amber land, small calm shark barely visible in water at bottom edge, plants and early forest are the hero, arrival of trees, hopeful morning light'
 ),
 '06_modern_viewer_not_just_an_animal': (
    'modern natural history museum aquarium window, small child silhouette and adult silhouette looking through glass at calm shark, faint reflection of ancient fossils over the glass, viewer point of view, people and aquarium frame dominate, warm wonder'
 ),
 '07_survivor_before_forests_final': (
    'final quiet ancient world wide shot, vast glowing prehistoric teal ocean with one small calm shark silhouette, distant barren treeless shoreline above water, huge sense of age and survival, peaceful majestic ending, this is the only shark-centered ocean shot'
 )
}

manifest=[]
base=26104000
for i,(shot,desc) in enumerate(SHOTS.items(),1):
    prompt=f'{LOCKED_STYLE}, {desc}'
    for v in range(1,5):
        seed=base+i*100+v
        imgs=gen.run(prompt, seed=seed, prefix=f'v4_saydog_{shot}_v{v:02d}')
        for img in imgs:
            manifest.append({'shot':shot,'variant':v,'seed':seed,'prompt':prompt,'file':img})
out=ROOT/'outputs/comfy_say_dog_v4_manifest.json'
out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(out)},indent=2))
