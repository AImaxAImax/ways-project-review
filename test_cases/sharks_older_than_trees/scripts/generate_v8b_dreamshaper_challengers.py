#!/usr/bin/env python3
"""DreamShaper XL Turbo challengers: faster/high-quality local model for premium art direction."""
from importlib.machinery import SourceFileLoader
from pathlib import Path
import json, time, urllib.request, urllib.parse, uuid

SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
OUT=ROOT/'assets'/'v8b_dreamshaper_challengers'; OUT.mkdir(parents=True,exist_ok=True)
NEG='readable text, letters, numbers, watermark, logo, caption, UI, label, scary teeth, shark attack, blood, gore, horror, low quality, blurry, deformed animal, malformed, cluttered, generic stock photo'

def post(path,data):
    req=urllib.request.Request(f'http://{SERVER}{path}',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode())
def get(path):
    with urllib.request.urlopen(f'http://{SERVER}{path}',timeout=30) as r: return json.loads(r.read().decode())
def dl(filename, subfolder='', folder_type='output'):
    q=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':folder_type})
    with urllib.request.urlopen(f'http://{SERVER}/view?{q}',timeout=60) as r: data=r.read()
    dest=OUT/filename; dest.write_bytes(data); return str(dest)
def workflow(prompt,seed,prefix):
    return {
      '1': {'class_type':'CheckpointLoaderSimple','inputs': {'ckpt_name':'DreamShaperXL_Turbo_V2-SFW.safetensors'}},
      '2': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':prompt}},
      '3': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':NEG}},
      '4': {'class_type':'EmptyLatentImage','inputs': {'width':832, 'height':1472, 'batch_size':1}},
      '5': {'class_type':'KSampler','inputs': {'model':['1',0], 'positive':['2',0], 'negative':['3',0], 'latent_image':['4',0], 'seed':seed, 'steps':10, 'cfg':2.4, 'sampler_name':'euler', 'scheduler':'normal', 'denoise':1.0}},
      '6': {'class_type':'VAEDecode','inputs': {'samples':['5',0], 'vae':['1',2]}},
      '7': {'class_type':'SaveImage','inputs': {'images':['6',0], 'filename_prefix':prefix}}
    }
def run(prompt,seed,prefix):
    pid=post('/prompt',{'prompt':workflow(prompt,seed,prefix),'client_id':CLIENT_ID})['prompt_id']
    for _ in range(240):
        h=get('/history/'+pid)
        if pid in h:
            st=h[pid].get('status',{})
            if st.get('status_str')=='error': raise RuntimeError(json.dumps(st,indent=2))
            files=[]
            for node in h[pid].get('outputs',{}).values():
                for im in node.get('images',[]): files.append(dl(im['filename'],im.get('subfolder',''),im.get('type','output')))
            return files
        time.sleep(1)
    raise TimeoutError(pid)

STYLE='premium tactile stop-motion paper diorama, high-end handcrafted layered paper sculpture and clay miniature, real material texture, precise cut edges, cast shadows, macro lens, warm natural-history museum lighting, cinematic depth of field, polished boutique educational short, teal ocean and ochre amber palette, mobile-readable silhouettes, clean negative space for captions'
PROMPTS={
 '01_before_trees_no_plants': STYLE+', ancient world before trees existed: lower third teal prehistoric ocean with one small calm ancient shark silhouette, upper two thirds empty barren rocky ochre land, absolutely no trees, no plants, no leaves, no grass, vast empty land is the hero, kid-safe awe',
 '03_apple_squirrel_acorn_gag': STYLE+', comedic prehistoric barren tabletop gag: one red apple, one cute squirrel, one acorn nut are clear oversized hero props on empty rocky ground, visual joke before apples and squirrels had anywhere to hide nuts, no forest, no dense plants',
 '04_deep_time_timeline': STYLE+', vertical geologic timeline museum diorama: stacked rock strata shelves, small shark fossil in lowest ancient ocean layer, circular fossil clock shapes, primitive plant layer much higher up, deep time is obvious, no readable text'
}
manifest=[]; base=26142000
for i,(name,prompt) in enumerate(PROMPTS.items(),1):
    for v in range(1,5):
        seed=base+i*100+v
        for f in run(prompt,seed,f'v8b_dreamshaper_{name}_v{v:02d}'):
            manifest.append({'name':name,'variant':v,'seed':seed,'prompt':prompt,'file':f})
out=ROOT/'outputs/v8b_dreamshaper_challengers_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(out)},indent=2))
