#!/usr/bin/env python3
"""v10 hero-frame ControlNet test: DreamShaper XL Turbo + SDXL Canny ControlNet + v7 layouts.
Only three production test frames. Goal: 8/10 style-frame direction before rendering all 7 shots.
"""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path

SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
COMFY=Path('/mnt/c/dev/ComfyUI')
REF_SRC=ROOT/'assets'/'v7_premium_papercut'
REF_IN=COMFY/'input'/'v10_hero_refs'
OUT=ROOT/'assets'/'v10_controlnet_hero_frames'
OUT.mkdir(parents=True,exist_ok=True); REF_IN.mkdir(parents=True,exist_ok=True)

CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'
CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'
NEG='readable text, letters, numbers, labels, watermark, logo, UI, caption, shark attack, scary open mouth, scary teeth, blood, gore, horror, photorealistic stock photo, blurry, low quality, deformed animal, malformed squirrel, extra limbs, dense forest in barren land shot, trees in barren land shot'
STYLE='masterpiece premium tactile stop-motion paper diorama, high-end handcrafted layered paper sculpture and clay miniature, boutique museum miniature photographed with macro lens, real paper fibers and precise cut edges, rich material texture, layered cast shadows, warm natural-history exhibit spotlighting, cinematic depth of field, polished editorial family science short, National Geographic Kids meets Aardman title sequence, teal ocean and ochre amber palette, mobile-readable silhouettes, clean negative space for captions'
SHOTS=[
 ('01_before_trees','01_before_trees_barren_land_premium.png','ancient world before trees existed: empty barren ochre rocky land above teal prehistoric ocean, absolutely no trees, no plants, no leaves, no grass, one small calm ancient shark in the lower water, the empty land is the main subject, awe and scale'),
 ('03_apple_squirrel_acorn','03_apples_squirrel_nuts_gag_premium.png','charming prehistoric gag: one red apple, one cute squirrel, one acorn nut as clear oversized hero props on empty rocky ground, playful not-yet-existing idea, no forest, no dense plants, charming character design'),
 ('04_deep_time_timeline','04_geologic_deep_time_timeline_premium.png','vertical geologic deep-time timeline museum diorama, stacked rock strata shelves, small shark fossil in lowest ancient ocean layer, circular fossil clock forms, primitive plant layer much higher up, reads as timeline before captions, no text')
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
def workflow(prompt,image_name,seed,prefix,denoise,strength):
    return {
      '1': {'class_type':'CheckpointLoaderSimple','inputs': {'ckpt_name':CKPT}},
      '2': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':prompt}},
      '3': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':NEG}},
      '4': {'class_type':'LoadImage','inputs': {'image':image_name}},
      '5': {'class_type':'Canny','inputs': {'image':['4',0], 'low_threshold':0.22, 'high_threshold':0.72}},
      '6': {'class_type':'ControlNetLoader','inputs': {'control_net_name':CNET}},
      '7': {'class_type':'ControlNetApplyAdvanced','inputs': {'positive':['2',0], 'negative':['3',0], 'control_net':['6',0], 'image':['5',0], 'strength':strength, 'start_percent':0.0, 'end_percent':0.82, 'vae':['1',2]}},
      '8': {'class_type':'VAEEncode','inputs': {'pixels':['4',0], 'vae':['1',2]}},
      '9': {'class_type':'KSampler','inputs': {'model':['1',0], 'positive':['7',0], 'negative':['7',1], 'latent_image':['8',0], 'seed':seed, 'steps':14, 'cfg':2.8, 'sampler_name':'euler', 'scheduler':'normal', 'denoise':denoise}},
      '10': {'class_type':'VAEDecode','inputs': {'samples':['9',0], 'vae':['1',2]}},
      '11': {'class_type':'SaveImage','inputs': {'images':['10',0], 'filename_prefix':prefix}}
    }
def run(prompt,img,seed,prefix,denoise,strength):
    pid=post('/prompt',{'prompt':workflow(prompt,img,seed,prefix,denoise,strength),'client_id':CLIENT_ID})['prompt_id']
    for _ in range(300):
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
manifest=[]; base=26168000
settings=[(1,0.48,0.90),(2,0.58,0.85),(3,0.68,0.72),(4,0.76,0.62)]
for idx,(shot,ref,desc) in enumerate(SHOTS,1):
    shutil.copy2(REF_SRC/ref, REF_IN/ref)
    image_name=f'v10_hero_refs/{ref}'
    prompt=STYLE+', '+desc
    for v,denoise,strength in settings:
        seed=base+idx*100+v
        for f in run(prompt,image_name,seed,f'v10_control_hero_{shot}_v{v:02d}',denoise,strength):
            manifest.append({'shot':shot,'variant':v,'denoise':denoise,'strength':strength,'seed':seed,'ref':str(REF_SRC/ref),'prompt':prompt,'file':f})
out=ROOT/'outputs/v10_controlnet_hero_frames_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(out)},indent=2))
