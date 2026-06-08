#!/usr/bin/env python3
"""v16 Shot 2: 'Seriously.' Evidence/proof beat in the v15 premium natural-history style."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw

SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v16_shot02_seriously_evidence'; GUIDE_DIR=ROOT/'assets'/'v16_guides'; COMFY_IN=COMFY/'input'/'v16_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot02_seriously_fossil_evidence_guide.png'

PROMPT=(
 'premium natural history museum stop-motion diorama, tactile paper and clay miniature, cinematic macro photography, warm museum spotlight, elegant educational science frame, '
 'a dramatic evidence beat for the word Seriously: one ancient shark fossil silhouette embedded in a smooth stone slab, shark-shaped fossil clearly visible, beside it one small calm modern shark model in clean teal water, '
 'museum exhibit table made of matte dark stone, soft blue teal glow, tiny dust particles, tasteful negative space for editor caption, handcrafted premium look, visually related to the previous underwater shark style but a new museum proof composition, '
 'no readable text, no labels, no trees, no plants, no forest, no clutter'
)
NEG=(
 'readable text, letters, numbers, labels, sign, caption, watermark, logo, plaque text, fake writing, chart text, '
 'tree, trees, forest, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, jungle, woodland, coral, kelp, '
 'cracked earth foreground, white crack pattern, dry lake bed, tile pattern, aquarium shelves, glass shelves, stacked layers, multiple horizons, weird floating islands, clutter, many sharks, scary teeth, open mouth, attack, blood, gore, horror, low quality, malformed shark, malformed fossil, human hands, people'
)

def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    # museum tabletop/slab perspective
    d.polygon([(95,520),(740,455),(790,1040),(55,1115)],outline='black')
    d.line((95,520,55,1115),fill='black',width=5); d.line((740,455,790,1040),fill='black',width=5)
    # large fossil shark silhouette embedded in slab
    d.line((165,730,290,665,545,660,685,715),fill='black',width=9)
    d.line((168,745,310,805,545,795,682,725),fill='black',width=6)
    d.line((660,720,760,665,720,725,765,800,660,720),fill='black',width=6)
    d.line((430,662,485,550,535,670),fill='black',width=7)
    d.line((448,794,500,900,552,790),fill='black',width=5)
    d.ellipse((235,715,250,730),fill='black')
    # small modern shark/water cameo in top right bowl/window, to tie style
    d.ellipse((510,250,750,390),outline='black',width=4)
    d.arc((535,280,725,375),190,350,fill='black',width=3)
    d.line((565,325,620,300,700,325),fill='black',width=4)
    d.line((690,325,735,300,720,330,738,360,690,325),fill='black',width=3)
    d.line((640,305,665,250,690,310),fill='black',width=4)
    # spotlight ring, no text
    d.ellipse((140,1160,690,1280),outline='black',width=3)
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
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v16_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':end_percent,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
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
    guide=make_guide(); manifest=[]; base=101604000
    for v,strength,cfg,steps,end_percent in [(1,0.18,4.9,26,0.50),(2,0.24,4.5,24,0.55),(3,0.30,4.0,24,0.60),(4,0.14,5.3,28,0.48),(5,0.22,5.0,26,0.58),(6,0.34,3.8,24,0.62)]:
        seed=base+v
        for f in run(seed,f'v16_shot02_seriously_evidence_v{v:02d}',strength,cfg,steps,end_percent):
            manifest.append({'shot':'02_seriously_evidence','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'end_percent':end_percent,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v16_shot02_seriously_evidence_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
