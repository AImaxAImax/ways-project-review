#!/usr/bin/env python3
"""v11c Shot 1: build on v11b success; make shark more readable, keep barren-land quality."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw
SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v11c_shot01_before_trees'; GUIDE_DIR=ROOT/'assets'/'v11_guides'; COMFY_IN=COMFY/'input'/'v11_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot01_barren_coast_readable_shark_guide.png'
PROMPT=(
 'premium tactile stop-motion paper geology diorama, handcrafted layered paper and clay miniature, real cut paper strata, macro studio photography, warm museum spotlight, cinematic depth of field, polished editorial family science frame, '
 'ancient lifeless volcanic coast before land vegetation existed, wide empty ochre badlands, basalt cliffs, desert islands and teal prehistoric ocean, no living things on land, '
 'one clearly readable calm ancient shark silhouette gliding in the foreground water, shark visible but peaceful, empty barren land remains the main idea, stark primordial world, clean negative space for captions, high production value, no picture frame border'
)
NEG=(
 'tree, trees, forest, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, cactus, coral, kelp, jungle, woodland, picture frame, wooden frame, poster border, '
 'readable text, letters, numbers, logo, watermark, caption, sign, label, scary teeth, shark attack, blood, gore, horror, blurry, low quality, malformed shark, crowded, many sharks'
)

def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    d.line((0,560,832,545),fill='black',width=4)
    d.line((0,520,170,455,330,500,480,450,650,495,832,438),fill='black',width=4)
    d.line((0,735,140,680,310,720,500,660,690,710,832,650),fill='black',width=3)
    # foreground water basin/ocean curve
    d.arc((130,835,720,1320),185,355,fill='black',width=5)
    d.arc((210,925,650,1225),185,355,fill='black',width=3)
    # larger readable shark in foreground water
    cx,cy=435,1110
    body=[(cx-150,cy),(cx-80,cy-38),(cx+105,cy-34),(cx+175,cy),(cx+105,cy+34),(cx-80,cy+38)]
    d.line(body+[body[0]],fill='black',width=6)
    d.line((cx+160,cy,cx+230,cy-55,cx+205,cy,cx+230,cy+55,cx+160,cy),fill='black',width=5)
    d.line((cx-5,cy-30,cx+38,cy-110,cx+70,cy-18),fill='black',width=5)
    d.ellipse((cx-110,cy-6,cx-100,cy+4),fill='black')
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
def workflow(seed,prefix,strength,cfg,steps):
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v11_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':0.50,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
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

guide=make_guide(); manifest=[]; base=26184000
for v,strength,cfg,steps in [(1,0.18,4.3,22),(2,0.24,4.0,20),(3,0.30,3.6,20),(4,0.12,4.8,24)]:
    seed=base+v
    for f in run(seed,f'v11c_shot01_readable_shark_v{v:02d}',strength,cfg,steps):
        manifest.append({'shot':'01_before_trees','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
out=ROOT/'outputs/v11c_shot01_before_trees_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
