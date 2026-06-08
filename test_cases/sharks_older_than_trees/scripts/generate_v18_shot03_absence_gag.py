#!/usr/bin/env python3
"""v18 Shot 3: 'Before forests. Before apples. Before squirrels had anywhere to hide nuts.'
Premium museum-style absence gag: three missing/ghost prop zones, not an outdoor forest scene.
"""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw

SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v18_shot03_absence_gag'; GUIDE_DIR=ROOT/'assets'/'v18_guides'; COMFY_IN=COMFY/'input'/'v18_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot03_absence_gag_three_spotlights_guide.png'

PROMPT=(
 'premium natural history museum stop-motion diorama, tactile paper and clay miniature, cinematic macro photography, warm museum spotlight with teal blue rim light, elegant family science frame, whimsical dry comedy, '
 'a dark matte museum stage showing the idea that forests, apples, squirrels, and nuts did not exist yet: three separate empty spotlight pedestals with translucent ghost-like simple silhouettes above them, '
 'left faint ghost silhouette of a tree/forest icon, center faint ghost silhouette of one apple, right faint ghost silhouette of a cute squirrel holding an acorn, all as pale transparent cut-paper outlines, intentionally absent and not real objects, '
 'behind them a smooth barren volcanic stone backdrop with teal haze, clean negative space, premium handcrafted look, visually consistent with previous teal museum shots, no readable text, no labels, no real forest, no real plants, no grass'
)
NEG=(
 'readable text, letters, numbers, labels, sign, caption, watermark, logo, plaque text, fake writing, chart text, '
 'real tree, real trees, real forest, dense forest, outdoor forest scene, green plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, jungle, woodland, orchard, mountains, sky, sunny landscape, '
 'many apples, many squirrels, many nuts, crowded props, realistic living squirrel, real apple pile, clutter, aquarium shelves, glass shelves, display case, coral, kelp, shark, fish, ocean, cracked earth foreground, white crack pattern, dry lake bed, tile pattern, low quality, malformed squirrel, extra limbs, scary, gore'
)

def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    # stage floor and three spotlight pedestals
    d.line((0,1005,832,995),fill='black',width=4)
    for cx in (185,415,645):
        d.ellipse((cx-105,1015,cx+105,1165),outline='black',width=4)
        d.line((cx-65,1165,cx+65,1165),fill='black',width=3)
        d.line((cx-55,1015,cx,830,cx+55,1015),fill='black',width=2)  # spotlight cone
    # left ghost tree/forest icon outline (simple absent icon, not scenic)
    d.line((185,820,185,965),fill='black',width=5)
    d.polygon([(185,640),(105,825),(265,825)],outline='black')
    d.line((185,640,105,825,265,825,185,640),fill='black',width=5)
    d.polygon([(185,565),(125,700),(245,700)],outline='black')
    d.line((185,565,125,700,245,700,185,565),fill='black',width=4)
    # center ghost apple outline
    d.ellipse((330,640,500,825),outline='black',width=6)
    d.arc((365,620,425,680),205,340,fill='black',width=5)
    d.line((420,645,448,585),fill='black',width=6)
    d.ellipse((446,565,505,598),outline='black',width=5)
    # right ghost squirrel + acorn outline
    d.ellipse((595,700,690,875),outline='black',width=6)
    d.ellipse((590,610,685,705),outline='black',width=6)
    d.line((607,615,622,560,650,620),fill='black',width=5)
    d.arc((680,650,785,850),90,315,fill='black',width=12)
    d.line((620,875,590,975),fill='black',width=5); d.line((665,875,705,975),fill='black',width=5)
    # acorn in paws
    d.arc((548,760,620,820),180,360,fill='black',width=5)
    d.ellipse((558,795,612,885),outline='black',width=5)
    # simple barren backdrop line, not landscape
    d.arc((70,330,762,530),190,350,fill='black',width=3)
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
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v18_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':end_percent,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
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
    guide=make_guide(); manifest=[]; base=121806000
    for v,strength,cfg,steps,end_percent in [(1,0.18,4.9,26,0.50),(2,0.24,4.5,24,0.55),(3,0.30,4.0,24,0.60),(4,0.14,5.3,28,0.48),(5,0.22,5.0,26,0.58),(6,0.34,3.8,24,0.62),(7,0.40,3.5,24,0.66),(8,0.28,5.0,26,0.56)]:
        seed=base+v
        for f in run(seed,f'v18_shot03_absence_gag_v{v:02d}',strength,cfg,steps,end_percent):
            manifest.append({'shot':'03_before_forests_apples_squirrels_absence_gag','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'end_percent':end_percent,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v18_shot03_absence_gag_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
