#!/usr/bin/env python3
"""v12b Shot 3: remove outdoor/scenic cues; make a museum stage prop trio only."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw
SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v12b_shot03_prop_trio_stage'; GUIDE_DIR=ROOT/'assets'/'v12_guides'; COMFY_IN=COMFY/'input'/'v12_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot03_prop_trio_black_stage_guide.png'
PROMPT=(
 'premium tactile stop-motion paper and clay diorama, handcrafted miniature, macro studio photography, warm museum spotlights, polished family science editorial frame, whimsical dry comedy, '
 'single black cyclorama studio stage, bare slate floor, three unmistakable separate prop characters displayed like evidence: left bright red apple, center cute gray squirrel standing upright with fluffy tail, right large brown acorn, '
 'clear silhouettes, separated spacing, dramatic object shadows, high production value, clean negative space for editor captions, visually unique tabletop gag frame, no picture frame border'
)
NEG=(
 'tree, trees, forest, woods, woodland, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, jungle, orchard, mountains, outdoor landscape, sky, horizon, snow, many apples, many squirrels, many nuts, '
 'ocean, underwater, shark, fish, coral, kelp, beach, picture frame, wooden frame, poster border, readable text, letters, numbers, logo, watermark, caption, sign, label, scary, blood, gore, horror, blurry, low quality, malformed squirrel, extra limbs, crowded, duplicate characters, hidden apple, hidden acorn'
)
def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    # black stage boundary and three plinth/spot circles
    d.line((0,1000,832,1000),fill='black',width=4)
    for cx in (190,420,650):
        d.ellipse((cx-125,1030,cx+125,1220),outline='black',width=4)
        d.line((cx-60,1220,cx+60,1220),fill='black',width=3)
    # apple left
    d.ellipse((105,660,275,845),outline='black',width=8)
    d.arc((145,638,205,690),205,340,fill='black',width=5)
    d.line((190,650,220,590),fill='black',width=7)
    d.ellipse((218,572,285,608),outline='black',width=5)
    # squirrel center, bigger and clean
    d.ellipse((365,720,475,900),outline='black',width=8)
    d.ellipse((360,610,465,715),outline='black',width=8)
    d.line((380,615,395,555,420,620),fill='black',width=6)
    d.ellipse((432,645,445,658),fill='black')
    d.arc((455,650,610,880),85,315,fill='black',width=18)
    d.arc((493,690,575,840),90,315,fill='black',width=7)
    d.line((388,900,355,985),fill='black',width=6); d.line((450,900,492,985),fill='black',width=6)
    d.line((385,785,335,825),fill='black',width=5)
    # acorn right
    d.arc((555,650,750,785),180,360,fill='black',width=9)
    d.line((558,715,750,715),fill='black',width=8)
    d.ellipse((578,700,735,925),outline='black',width=8)
    for x in range(575,730,28): d.line((x,665,x+60,715),fill='black',width=3)
    d.line((650,655,680,600),fill='black',width=7)
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
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v12_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':0.65,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
def run(seed,prefix,strength,cfg,steps):
    pid=post('/prompt',{'prompt':workflow(seed,prefix,strength,cfg,steps),'client_id':CLIENT_ID})['prompt_id']
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
    guide=make_guide(); manifest=[]; base=41271000
    for v,strength,cfg,steps in [(1,0.42,4.3,24),(2,0.50,3.8,24),(3,0.34,4.8,26),(4,0.58,3.4,22),(5,0.45,5.0,26),(6,0.62,3.2,24)]:
        seed=base+v
        for f in run(seed,f'v12b_shot03_prop_trio_stage_v{v:02d}',strength,cfg,steps):
            manifest.append({'shot':'03_apple_squirrel_acorn_stage','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v12b_shot03_prop_trio_stage_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
