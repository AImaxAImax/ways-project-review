#!/usr/bin/env python3
"""Targeted v5 regen for failing rows from v4 using custom negatives."""
import json, time, urllib.request, urllib.parse, uuid
from pathlib import Path

SERVER='127.0.0.1:8188'
CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
OUT=ROOT/'assets'/'comfy_sdxl_turbo_v1'
OUT.mkdir(parents=True, exist_ok=True)

LOCKED_STYLE=(
    'vertical 9:16 premium handmade stop motion diorama still, layered cut paper and soft clay miniature art style, '
    'matte paper texture, rounded friendly simple shapes, shallow depth of field, warm natural history museum lighting, '
    'cohesive teal blue and amber ochre palette, family science YouTube Short, no readable text, no letters, no numbers, no logo, no watermark'
)

def post(path, data):
    req=urllib.request.Request(f'http://{SERVER}{path}', data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def get_json(path):
    with urllib.request.urlopen(f'http://{SERVER}{path}', timeout=30) as r:
        return json.loads(r.read().decode())

def download(filename, subfolder='', folder_type='output'):
    params=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':folder_type})
    with urllib.request.urlopen(f'http://{SERVER}/view?{params}', timeout=60) as r:
        data=r.read()
    dest=OUT/filename
    dest.write_bytes(data)
    return str(dest)

def workflow(prompt, negative, seed, prefix):
    return {
      '1': {'class_type':'CheckpointLoaderSimple','inputs': {'ckpt_name':'sd_xl_turbo_1.0_fp16.safetensors'}},
      '2': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':prompt}},
      '3': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':negative}},
      '4': {'class_type':'EmptyLatentImage','inputs': {'width':768, 'height':1344, 'batch_size':1}},
      '5': {'class_type':'KSampler','inputs': {'model':['1',0], 'positive':['2',0], 'negative':['3',0], 'latent_image':['4',0], 'seed':seed, 'steps':7, 'cfg':2.0, 'sampler_name':'euler', 'scheduler':'simple', 'denoise':1.0}},
      '6': {'class_type':'VAEDecode','inputs': {'samples':['5',0], 'vae':['1',2]}},
      '7': {'class_type':'SaveImage','inputs': {'images':['6',0], 'filename_prefix':prefix}}
    }

def run(prompt, negative, seed, prefix):
    pid=post('/prompt', {'prompt':workflow(prompt,negative,seed,prefix), 'client_id':CLIENT_ID})['prompt_id']
    for _ in range(180):
        h=get_json('/history/'+pid)
        if pid in h:
            status=h[pid].get('status',{})
            if status.get('status_str') == 'error':
                raise RuntimeError(json.dumps(status,indent=2))
            imgs=[]
            for node in h[pid].get('outputs',{}).values():
                for im in node.get('images',[]):
                    imgs.append(download(im['filename'], im.get('subfolder',''), im.get('type','output')))
            return imgs
        time.sleep(1)
    raise TimeoutError(pid)

SHOTS={
 '01_before_trees_no_forest': {
   'prompt': LOCKED_STYLE + ', ancient world before any land plants existed, flat empty ochre desert islands and bare black volcanic rocks above a teal ocean, smooth naked shoreline, one small calm shark silhouette in lower water only, the emptiness of land is the main subject, no vegetation anywhere, no trees, no trunks, no leaves, no grass, no coral above water',
   'negative': 'tree, trees, forest, plant, plants, leaves, grass, fern, palm, bushes, branches, jungle, coral forest, underwater portrait, close up shark, scary teeth, photoreal, text, letters, numbers, logo, watermark, gore, horror'
 },
 '02_seriously_museum_fossil': {
   'prompt': LOCKED_STYLE + ', natural history museum fossil proof shot, a flat stone slab on a wooden exhibit table, fossilized shark skeleton imprint carved into amber rock, magnifying glass, small display lamp, archival specimen tray, no water, no aquarium, no living fish, proof beat',
   'negative': 'living shark, swimming shark, aquarium, water tank, ocean, fish school, coral, plants, trees, text, letters, numbers, logo, watermark, photoreal, scary, gore'
 },
 '03_before_apples_squirrels_nuts': {
   'prompt': LOCKED_STYLE + ', comedic barren prehistoric tabletop diorama with three clear toy-like props on empty rocky ground: one red apple, one cute squirrel, one acorn nut, all oversized and easy to read, mostly empty background, no forest, just a few bare rocks, visual gag of things that do not exist yet',
   'negative': 'forest, many trees, dense plants, orchard, jungle, too many apples, text, letters, numbers, logo, watermark, photoreal, scary, gore'
 },
 '07_survivor_before_forests_final': {
   'prompt': LOCKED_STYLE + ', final quiet awe shot: one calm ancient shark in a vast teal prehistoric ocean, distant empty barren ochre shoreline with no trees and no plants, huge open water, minimal composition, peaceful survivor from a world before forests',
   'negative': 'trees, forest, plants, leaves, branches, grass, fern, palm, coral forest, many sharks, shark attack, close mouth, scary teeth, text, letters, numbers, logo, watermark, photoreal, gore'
 }
}

manifest=[]
base=26116000
for i,(shot,meta) in enumerate(SHOTS.items(),1):
    for v in range(1,7):
        seed=base+i*100+v
        imgs=run(meta['prompt'], meta['negative'], seed, f'v5_targeted_{shot}_v{v:02d}')
        for img in imgs:
            manifest.append({'shot':shot,'variant':v,'seed':seed,'prompt':meta['prompt'],'negative':meta['negative'],'file':img})
out=ROOT/'outputs/comfy_say_dog_v5_targeted_manifest.json'
out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(out)},indent=2))
