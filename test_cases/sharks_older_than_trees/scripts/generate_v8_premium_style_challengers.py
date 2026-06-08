#!/usr/bin/env python3
"""Generate premium SDXL-base style-frame challengers for production reset."""
import json, time, urllib.request, urllib.parse, uuid
from pathlib import Path

SERVER='127.0.0.1:8188'
CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
OUT=ROOT/'assets'/'v8_premium_style_challengers'
OUT.mkdir(parents=True, exist_ok=True)

NEG='readable text, letters, numbers, watermark, logo, caption, scary teeth, shark attack, blood, gore, horror, photorealistic stock photo, low quality, blurry, malformed animal, extra fins, extra limbs, cluttered composition'

def post(path, data):
    req=urllib.request.Request(f'http://{SERVER}{path}', data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read().decode())

def get_json(path):
    with urllib.request.urlopen(f'http://{SERVER}{path}', timeout=30) as r: return json.loads(r.read().decode())

def download(filename, subfolder='', folder_type='output', dest=None):
    params=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':folder_type})
    with urllib.request.urlopen(f'http://{SERVER}/view?{params}', timeout=60) as r: data=r.read()
    dest=dest or OUT/filename
    dest.write_bytes(data)
    return str(dest)

def workflow(prompt, seed, prefix):
    return {
      '1': {'class_type':'CheckpointLoaderSimple','inputs': {'ckpt_name':'sd_xl_base_1.0.safetensors'}},
      '2': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':prompt}},
      '3': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':NEG}},
      '4': {'class_type':'EmptyLatentImage','inputs': {'width':832, 'height':1472, 'batch_size':1}},
      '5': {'class_type':'KSampler','inputs': {'model':['1',0], 'positive':['2',0], 'negative':['3',0], 'latent_image':['4',0], 'seed':seed, 'steps':32, 'cfg':6.5, 'sampler_name':'euler', 'scheduler':'normal', 'denoise':1.0}},
      '6': {'class_type':'VAEDecode','inputs': {'samples':['5',0], 'vae':['1',2]}},
      '7': {'class_type':'SaveImage','inputs': {'images':['6',0], 'filename_prefix':prefix}}
    }

def run(prompt, seed, prefix):
    pid=post('/prompt', {'prompt':workflow(prompt, seed, prefix), 'client_id':CLIENT_ID})['prompt_id']
    for _ in range(360):
        h=get_json('/history/'+pid)
        if pid in h:
            status=h[pid].get('status',{})
            if status.get('status_str') == 'error': raise RuntimeError(json.dumps(status,indent=2))
            files=[]
            for node in h[pid].get('outputs',{}).values():
                for im in node.get('images',[]): files.append(download(im['filename'], im.get('subfolder',''), im.get('type','output')))
            return files
        time.sleep(1)
    raise TimeoutError(pid)

PROMPTS={
 'A_tactile_paper_before_trees': 'award-winning premium tactile paper diorama, high-end layered paper sculpture photographed in a miniature studio, family science YouTube Short style frame, subject sharks existed before trees: lower third teal prehistoric ocean with one small calm ancient shark silhouette, upper two thirds empty barren ochre rocky land with absolutely no trees and no plants, real handmade paper fibers, precise cut edges, layered cast shadows, macro lens, warm museum spotlight, cinematic depth of field, boutique stop-motion title sequence, clean negative space for captions, mobile-readable composition',
 'B_storybook_clay_gag': 'premium natural-history storybook 3D clay and paper hybrid, charming family science YouTube Short style frame, subject before apples and squirrels had anywhere to hide nuts: whimsical prehistoric barren-land diorama with three clear hero props, one red apple, one cute squirrel, one acorn nut, arranged as playful not-yet-existing ideas, tactile clay characters, paper rocks, warm amber gallery lighting, rich teal and ochre palette, cinematic shallow depth of field, polished mobile-readable silhouettes',
 'C_museum_timeline': 'premium editorial museum infographic diorama, natural history exhibit quality, family science YouTube Short style frame, subject first sharks appeared more than four hundred million years ago: vertical geologic timeline made from stacked tactile display layers, ancient ocean fossil layer with small shark at bottom, rock strata, circular fossil clock shapes, primitive plant layer much higher up, elegant warm gallery lighting, paper sculpture and clay model materials, polished National Geographic Kids composition, cinematic depth'
}
manifest=[]
base=26130000
for i,(name,prompt) in enumerate(PROMPTS.items(),1):
    for v in range(1,4):
        seed=base+i*100+v
        files=run(prompt, seed, f'v8_style_{name}_v{v:02d}')
        for f in files: manifest.append({'name':name,'variant':v,'seed':seed,'prompt':prompt,'file':f})
out=ROOT/'outputs/v8_premium_style_challengers_manifest.json'
out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(out)},indent=2))
