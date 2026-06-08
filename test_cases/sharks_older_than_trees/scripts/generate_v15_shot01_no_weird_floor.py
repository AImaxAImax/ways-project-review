#!/usr/bin/env python3
"""v15 Shot 1: remove weird floor/background entirely — close underwater shark + simple distant barren coast."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw
SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v15_shot01_no_weird_floor'; GUIDE_DIR=ROOT/'assets'/'v15_guides'; COMFY_IN=COMFY/'input'/'v15_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot01_underwater_shark_simple_horizon_guide.png'
PROMPT=(
 'premium natural history museum stop-motion diorama, tactile paper and clay miniature, cinematic macro photography, elegant underwater scene, '
 'one calm ancient shark swimming underwater in foreground, body fully in blue teal water, dorsal fin near the surface, soft waterline ripples above the shark, peaceful and readable, '
 'far above the water surface only: a simple low barren volcanic coastline, ochre sandbar and dark basalt cliff, empty lifeless land before vegetation existed, clean horizon, '
 'smooth open water background with sun rays and tiny particles, no seafloor visible, no cracked ground, no foreground rocks, no layered shelves, no clutter, premium educational science frame, negative space'
)
NEG=(
 'tree, trees, forest, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, cactus, coral, kelp, jungle, woodland, '
 'seafloor, ocean floor, cracked earth, white crack pattern, dry lake bed, tile pattern, foreground rocks, rock under shark, bottom desert, stacked water layers, aquarium shelf, glass shelf, multiple horizons, weird floating islands, '
 'shark sitting on water, shark on top of water, beached shark, toy shark, cutout shark, many sharks, duplicate shark, scary teeth, open mouth, attack, blood, gore, text, letters, watermark, low quality, malformed shark'
)
def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    # simple distant above-water coast at very top
    d.line((0,405,832,395),fill='black',width=5)
    d.line((0,365,160,342,330,360,520,330,700,355,832,325),fill='black',width=4)
    # waterline ripple above shark
    d.arc((120,470,725,660),190,350,fill='black',width=4)
    d.arc((185,515,670,650),190,350,fill='black',width=2)
    # large single shark, entirely underwater and away from any floor
    cx,cy=430,850
    d.line((145,850,270,785,560,785,735,842),fill='black',width=9)
    d.line((155,865,295,930,565,925,730,852),fill='black',width=6)
    d.line((710,846,810,785,775,852,815,925,710,846),fill='black',width=6)
    d.line((455,790,520,640,575,795),fill='black',width=8)
    d.line((465,920,530,1050,585,915),fill='black',width=6)
    d.ellipse((235,835,250,850),fill='black')
    p=GUIDE_DIR/GUIDE_NAME; im.save(p); shutil.copy2(p,COMFY_IN/GUIDE_NAME); return p
def post(path,data):
    req=urllib.request.Request(f'http://{SERVER}{path}',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode())
def get(path):
    with urllib.request.urlopen(f'http://{SERVER}{path}',timeout=30) as r: return json.loads(r.read().decode())
def dl(filename, subfolder='', folder_type='output'):
    q=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':folder_type})
    with urllib.request.urlopen(f'http://{SERVER}/view?{q}',timeout=60) as r: data=r.read()
    dest=OUT/filename; dest.write_bytes(data); return str(dest)
def workflow(seed,prefix,strength,cfg,steps,end_percent):
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v15_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':end_percent,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
def run(seed,prefix,strength,cfg,steps,end_percent):
    pid=post('/prompt',{'prompt':workflow(seed,prefix,strength,cfg,steps,end_percent),'client_id':CLIENT_ID})['prompt_id']
    for _ in range(360):
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
if __name__ == '__main__':
    guide=make_guide(); manifest=[]; base=91503000
    for v,strength,cfg,steps,end_percent in [(1,0.18,4.8,24,0.48),(2,0.24,4.5,24,0.54),(3,0.30,4.0,24,0.60),(4,0.14,5.3,28,0.46),(5,0.22,5.0,26,0.56),(6,0.34,3.8,24,0.62),(7,0.28,4.8,26,0.58),(8,0.20,5.4,28,0.52)]:
        seed=base+v
        for f in run(seed,f'v15_shot01_no_weird_floor_v{v:02d}',strength,cfg,steps,end_percent):
            manifest.append({'shot':'01_no_weird_floor','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'end_percent':end_percent,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v15_shot01_no_weird_floor_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
