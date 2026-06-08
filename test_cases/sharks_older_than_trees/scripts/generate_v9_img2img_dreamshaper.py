#!/usr/bin/env python3
"""v9: use v7 controlled layouts as img2img references with DreamShaper XL Turbo for polish.
Goal: preserve say-dog-see-dog layout while upgrading material quality beyond procedural POC.
"""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path

SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
COMFY=Path('/mnt/c/dev/ComfyUI')
REF_SRC=ROOT/'assets'/'v7_premium_papercut'
REF_IN=COMFY/'input'/'v9_shark_refs'
OUT=ROOT/'assets'/'v9_img2img_dreamshaper'; OUT.mkdir(parents=True,exist_ok=True); REF_IN.mkdir(parents=True,exist_ok=True)
NEG='readable text, letters, numbers, logo, watermark, scary teeth, shark attack, blood, gore, horror, photorealistic stock photo, deformed, malformed, clutter, inconsistent style, dense forest where barren land should be'
STYLE='premium tactile stop-motion paper diorama, high-end handcrafted layered paper sculpture and clay miniature, real paper fibers, precise cut edges, cast shadows, macro lens, warm natural-history museum lighting, cinematic depth of field, polished boutique educational short, teal ocean and ochre amber palette, mobile-readable silhouettes, clean negative space for captions'
SHOTS=[
 ('01_before_trees_barren_land_premium.png','ancient world before trees existed: barren rocky ochre land with absolutely no trees or plants above a teal prehistoric ocean with one small calm shark, emptiness of land is the hero'),
 ('02_seriously_fossil_museum_premium.png','museum fossil proof shot: tactile stone slab and shark fossil skeleton exhibit under warm display lighting, no living aquarium scene'),
 ('03_apples_squirrel_nuts_gag_premium.png','comedic prehistoric gag: one red apple, one cute squirrel, one acorn nut as clear oversized hero props on empty rocky ground, no dense forest'),
 ('04_geologic_deep_time_timeline_premium.png','vertical geologic timeline diorama: stacked rock strata shelves, shark fossil in lowest layer, fossil clock shapes, primitive plants much higher up'),
 ('05_primitive_forest_arrives_premium.png','primitive early forest arrives later: strange first tree-like plants and ferns rising on shoreline, shark small in water'),
 ('06_modern_viewer_aquarium_premium.png','modern museum aquarium viewer POV: child and adult silhouettes looking through glass at calm shark, warm wonder'),
 ('07_survivor_world_before_forests_premium.png','final quiet awe: calm ancient shark in vast teal prehistoric ocean, distant barren treeless shoreline, peaceful survivor')
]

def post(path,data):
    req=urllib.request.Request(f'http://{SERVER}{path}',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode())
def get(path):
    with urllib.request.urlopen(f'http://{SERVER}{path}',timeout=30) as r: return json.loads(r.read().decode())
def dl(filename, subfolder='', folder_type='output'):
    q=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':folder_type})
    with urllib.request.urlopen(f'http://{SERVER}/view?{q}',timeout=60) as r: data=r.read()
    dest=OUT/filename; dest.write_bytes(data); return str(dest)
def workflow(prompt, image_name, seed, prefix, denoise=0.48):
    return {
      '1': {'class_type':'CheckpointLoaderSimple','inputs': {'ckpt_name':'DreamShaperXL_Turbo_V2-SFW.safetensors'}},
      '2': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':prompt}},
      '3': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':NEG}},
      '4': {'class_type':'LoadImage','inputs': {'image':image_name}},
      '5': {'class_type':'VAEEncode','inputs': {'pixels':['4',0], 'vae':['1',2]}},
      '6': {'class_type':'KSampler','inputs': {'model':['1',0], 'positive':['2',0], 'negative':['3',0], 'latent_image':['5',0], 'seed':seed, 'steps':12, 'cfg':2.6, 'sampler_name':'euler', 'scheduler':'normal', 'denoise':denoise}},
      '7': {'class_type':'VAEDecode','inputs': {'samples':['6',0], 'vae':['1',2]}},
      '8': {'class_type':'SaveImage','inputs': {'images':['7',0], 'filename_prefix':prefix}}
    }
def run(prompt,img,seed,prefix,denoise):
    pid=post('/prompt',{'prompt':workflow(prompt,img,seed,prefix,denoise),'client_id':CLIENT_ID})['prompt_id']
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
manifest=[]; base=26152000
for idx,(fname,desc) in enumerate(SHOTS,1):
    src=REF_SRC/fname; dst=REF_IN/fname; shutil.copy2(src,dst)
    image_name=f'v9_shark_refs/{fname}'
    prompt=STYLE+', '+desc
    for v,denoise in [(1,0.38),(2,0.50)]:
        seed=base+idx*100+v
        for f in run(prompt,image_name,seed,f'v9_img2img_{idx:02d}_v{v}',denoise):
            manifest.append({'shot':idx,'variant':v,'denoise':denoise,'seed':seed,'ref':str(src),'prompt':prompt,'file':f})
out=ROOT/'outputs/v9_img2img_dreamshaper_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(out)},indent=2))
