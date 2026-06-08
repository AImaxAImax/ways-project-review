#!/usr/bin/env python3
"""v11 Shot 1 only: premium 'before trees' hero frame.
Key fix after v10: use a sparse composition guide with ControlNet + empty latent,
not img2img from low-quality POC art.
"""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw

SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v11_shot01_before_trees'
GUIDE_DIR=ROOT/'assets'/'v11_guides'
COMFY_IN=COMFY/'input'/'v11_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)

CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'
CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'
GUIDE_NAME='shot01_before_trees_sparse_guide.png'

PROMPT=(
    'award-winning premium tactile paper diorama style frame for a family science YouTube Short, '
    'high-end handcrafted layered paper sculpture photographed in a miniature studio, real paper fibers, precise cut edges, boutique stop-motion title sequence quality, '
    'macro lens, warm natural-history museum spotlighting, cinematic depth of field, rich teal ocean and ochre amber barren land palette, '
    'subject: sharks existed before trees, ancient world before land plants, lower third glowing teal prehistoric ocean with one small calm ancient shark silhouette, '
    'upper two thirds empty barren ochre rocky land and sky, absolutely no trees, no plants, no leaves, no grass, no forest, no coral forest, '
    'the empty treeless land is the hero, clean negative space for captions, mobile-readable dramatic composition, kid-safe awe, premium editorial finish'
)
NEG=(
    'trees, tree, forest, plants, plant, leaves, leaf, grass, fern, palm, jungle, bushes, branches, flowers, green vegetation, coral forest, kelp forest, '
    'readable text, letters, numbers, logo, watermark, caption, UI, sign, label, scary teeth, shark attack, blood, gore, horror, low quality, blurry, malformed shark, extra fins, crowded composition'
)

def make_guide():
    W,H=832,1472
    im=Image.new('RGB',(W,H),'white')
    d=ImageDraw.Draw(im)
    # horizon and water boundary; intentionally sparse so it controls composition only
    d.line((0,600,832,565),fill='black',width=5)
    # barren land masses above horizon
    d.line((40,500,170,430,310,470,420,405,590,450,760,385,832,420),fill='black',width=5)
    d.line((80,690,220,620,360,665,480,600,640,650,780,610),fill='black',width=4)
    # small shark silhouette in lower third
    cx,cy=430,1060
    body=[(cx-130,cy),(cx-70,cy-32),(cx+80,cy-30),(cx+145,cy),(cx+80,cy+30),(cx-70,cy+32)]
    d.line(body+[body[0]],fill='black',width=5)
    d.line((cx+135,cy,cx+205,cy-45,cx+185,cy,cx+205,cy+45,cx+135,cy),fill='black',width=5)
    d.line((cx-15,cy-25,cx+25,cy-95,cx+50,cy-15),fill='black',width=5)
    # light wave arcs
    for y in [850,950,1160,1280]:
        d.arc((120,y,690,y+80),0,180,fill='black',width=2)
    path=GUIDE_DIR/GUIDE_NAME
    im.save(path)
    shutil.copy2(path, COMFY_IN/GUIDE_NAME)
    return path

def post(path,data):
    req=urllib.request.Request(f'http://{SERVER}{path}',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode())
def get(path):
    with urllib.request.urlopen(f'http://{SERVER}{path}',timeout=30) as r: return json.loads(r.read().decode())
def dl(filename, subfolder='', folder_type='output'):
    q=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':folder_type})
    with urllib.request.urlopen(f'http://{SERVER}/view?{q}',timeout=60) as r: data=r.read()
    dest=OUT/filename; dest.write_bytes(data); return str(dest)
def workflow(seed,prefix,strength,cfg,steps):
    return {
      '1': {'class_type':'CheckpointLoaderSimple','inputs': {'ckpt_name':CKPT}},
      '2': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':PROMPT}},
      '3': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':NEG}},
      '4': {'class_type':'LoadImage','inputs': {'image':'v11_guides/'+GUIDE_NAME}},
      '5': {'class_type':'Canny','inputs': {'image':['4',0], 'low_threshold':0.10, 'high_threshold':0.55}},
      '6': {'class_type':'ControlNetLoader','inputs': {'control_net_name':CNET}},
      '7': {'class_type':'ControlNetApplyAdvanced','inputs': {'positive':['2',0], 'negative':['3',0], 'control_net':['6',0], 'image':['5',0], 'strength':strength, 'start_percent':0.0, 'end_percent':0.62, 'vae':['1',2]}},
      '8': {'class_type':'EmptyLatentImage','inputs': {'width':832, 'height':1472, 'batch_size':1}},
      '9': {'class_type':'KSampler','inputs': {'model':['1',0], 'positive':['7',0], 'negative':['7',1], 'latent_image':['8',0], 'seed':seed, 'steps':steps, 'cfg':cfg, 'sampler_name':'euler', 'scheduler':'normal', 'denoise':1.0}},
      '10': {'class_type':'VAEDecode','inputs': {'samples':['9',0], 'vae':['1',2]}},
      '11': {'class_type':'SaveImage','inputs': {'images':['10',0], 'filename_prefix':prefix}}
    }
def run(seed,prefix,strength,cfg,steps):
    pid=post('/prompt',{'prompt':workflow(seed,prefix,strength,cfg,steps),'client_id':CLIENT_ID})['prompt_id']
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

guide=make_guide()
settings=[
    (1,0.28,3.2,16),(2,0.34,3.0,16),(3,0.22,3.6,18),(4,0.40,2.8,16),(5,0.18,4.0,20),(6,0.30,3.4,18)
]
manifest=[]; base=26180000
for v,strength,cfg,steps in settings:
    seed=base+v
    for f in run(seed,f'v11_shot01_before_trees_v{v:02d}',strength,cfg,steps):
        manifest.append({'shot':'01_before_trees','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
out=ROOT/'outputs/v11_shot01_before_trees_manifest.json'
out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
