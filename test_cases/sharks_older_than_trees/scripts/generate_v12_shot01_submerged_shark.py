#!/usr/bin/env python3
"""v12 Shot 1: fix shark-water relationship — shark must read as in water, not sitting on top."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw

SERVER='127.0.0.1:8188'
CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v12_shot01_submerged_shark'
GUIDE_DIR=ROOT/'assets'/'v12_guides'
COMFY_IN=COMFY/'input'/'v12_guides'
OUT.mkdir(parents=True,exist_ok=True)
GUIDE_DIR.mkdir(parents=True,exist_ok=True)
COMFY_IN.mkdir(parents=True,exist_ok=True)

CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'
CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'
GUIDE_NAME='shot01_submerged_shark_waterline_guide.png'

PROMPT=(
 'premium tactile stop-motion paper geology diorama, handcrafted layered paper and clay miniature, macro studio photography, warm natural history museum spotlight, cinematic depth of field, polished editorial family science frame, '
 'ancient lifeless volcanic coastline before land vegetation existed, empty ochre badlands, black basalt cliffs, barren desert islands, teal shallow prehistoric sea, no living things on land, '
 'one calm ancient shark swimming partly underwater in the foreground shallow sea, shark body partially submerged below a visible waterline, dorsal fin and back breaking the surface, lower body softened by translucent water, gentle ripples and small wake around fins, underwater shadow and refraction, peaceful not scary, '
 'barren lifeless land remains obvious behind the water, stark primordial world, clean negative space for captions, high production value, no picture frame border'
)
NEG=(
 'tree, trees, forest, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, cactus, coral, kelp, jungle, woodland, picture frame, wooden frame, poster border, '
 'shark lying on surface, shark sitting on water, toy shark, cutout shark, beached shark, shark on land, floating on top, dry outline, dead shark, full body above water, '
 'readable text, letters, numbers, logo, watermark, caption, sign, label, scary teeth, shark attack, open mouth, blood, gore, horror, blurry, low quality, malformed shark, crowded, many sharks'
)

def make_guide():
    W,H=832,1472
    im=Image.new('RGB',(W,H),'white')
    d=ImageDraw.Draw(im)
    # Barren volcanic coast / cliffs in upper half.
    d.line((0,525,832,505),fill='black',width=4)
    d.line((0,485,150,430,300,468,470,420,640,462,832,405),fill='black',width=4)
    d.line((0,690,130,640,305,685,500,625,690,675,832,610),fill='black',width=3)
    # Foreground sea basin and water surface lines.
    d.line((40,900,790,875),fill='black',width=5)   # waterline crossing shark
    d.arc((70,790,775,1325),182,358,fill='black',width=5)
    d.arc((145,910,710,1230),186,354,fill='black',width=3)
    # Ripple bands around the shark.
    for off,w in [(0,3),(52,2),(104,2)]:
        d.arc((160-off//2,845+off,690+off//2,1045+off),190,350,fill='black',width=w)
    # Shark: only dorsal/back strongly above waterline; lower body dotted/softer below water.
    cx,cy=425,920
    # above-water back silhouette
    d.arc((205,790,625,1010),200,340,fill='black',width=9)
    # head and tail just at/under waterline
    d.line((230,910,315,870,480,870,610,900),fill='black',width=6)
    d.line((598,900,680,855,650,908,690,960,598,900),fill='black',width=5)
    # dorsal fin breaking surface
    d.line((395,872,445,750,490,875),fill='black',width=7)
    # faint underwater belly/body below surface (broken lines so it doesn't look dry/on-top)
    d.arc((230,835,610,1055),20,160,fill='black',width=3)
    d.line((315,970,435,1008,560,965),fill='black',width=2)
    d.ellipse((280,888,290,898),fill='black')
    p=GUIDE_DIR/GUIDE_NAME
    im.save(p)
    shutil.copy2(p,COMFY_IN/GUIDE_NAME)
    return p

def post(path,data):
    req=urllib.request.Request(f'http://{SERVER}{path}',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.loads(r.read().decode())

def get(path):
    with urllib.request.urlopen(f'http://{SERVER}{path}',timeout=30) as r:
        return json.loads(r.read().decode())

def dl(filename, subfolder='', folder_type='output'):
    q=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':folder_type})
    with urllib.request.urlopen(f'http://{SERVER}/view?{q}',timeout=60) as r:
        data=r.read()
    dest=OUT/filename
    dest.write_bytes(data)
    return str(dest)

def workflow(seed,prefix,strength,cfg,steps,end_percent):
    return {
        '1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},
        '2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},
        '3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},
        '4':{'class_type':'LoadImage','inputs':{'image':'v12_guides/'+GUIDE_NAME}},
        '5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},
        '6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},
        '7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':end_percent,'vae':['1',2]}},
        '8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},
        '9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},
        '10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},
        '11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}
    }

def run(seed,prefix,strength,cfg,steps,end_percent):
    pid=post('/prompt',{'prompt':workflow(seed,prefix,strength,cfg,steps,end_percent),'client_id':CLIENT_ID})['prompt_id']
    for _ in range(360):
        h=get('/history/'+pid)
        if pid in h:
            st=h[pid].get('status',{})
            if st.get('status_str')=='error':
                raise RuntimeError(json.dumps(st,indent=2))
            files=[]
            for node in h[pid].get('outputs',{}).values():
                for im in node.get('images',[]):
                    files.append(dl(im['filename'],im.get('subfolder',''),im.get('type','output')))
            return files
        time.sleep(1)
    raise TimeoutError(pid)

if __name__ == '__main__':
    guide=make_guide()
    manifest=[]
    base=61274000
    variants=[
        (1,0.18,4.8,24,0.52),
        (2,0.24,4.3,22,0.56),
        (3,0.30,3.9,22,0.60),
        (4,0.36,3.6,22,0.64),
        (5,0.14,5.2,26,0.50),
        (6,0.28,4.8,24,0.58),
        (7,0.22,5.0,26,0.62),
        (8,0.34,4.1,24,0.66),
    ]
    for v,strength,cfg,steps,end_percent in variants:
        seed=base+v
        for f in run(seed,f'v12_shot01_submerged_shark_v{v:02d}',strength,cfg,steps,end_percent):
            manifest.append({'shot':'01_before_trees_submerged_shark','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'end_percent':end_percent,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v12_shot01_submerged_shark_manifest.json'
    out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
