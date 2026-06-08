#!/usr/bin/env python3
"""v12 Shot 3: 'Before forests. Before apples. Before squirrels had anywhere to hide nuts.'
Generate a visually distinct, say-dog-see-dog comedy/proof frame with clear apple, squirrel, and acorn.
"""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw

SERVER='127.0.0.1:8188'
CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v12_shot03_apple_squirrel_acorn'
GUIDE_DIR=ROOT/'assets'/'v12_guides'
COMFY_IN=COMFY/'input'/'v12_guides'
OUT.mkdir(parents=True,exist_ok=True)
GUIDE_DIR.mkdir(parents=True,exist_ok=True)
COMFY_IN.mkdir(parents=True,exist_ok=True)

CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'
CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'
GUIDE_NAME='shot03_apple_squirrel_acorn_clear_props_guide.png'

PROMPT=(
 'premium tactile stop-motion paper diorama, handcrafted layered cut paper and soft clay miniature, macro studio photography, warm museum spotlight, cinematic depth of field, polished editorial family science frame, whimsical dry humor, '
 'visually different from ocean scenes: a clean tabletop natural history exhibit on barren prehistoric rock, dark warm background, three unmistakable separate prop characters in spotlights: '
 'left a bright red apple, center a cute gray squirrel standing upright with big fluffy tail, right a large brown acorn nut, all three separated with clear silhouettes, charming comedy beat, no trees anywhere, no forest, no leaves, '
 'empty ancient barren ground behind them to imply these things did not exist yet, premium stop motion, clean negative space for editor captions, high production value, no picture frame border'
)
NEG=(
 'tree, trees, forest, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, jungle, woodland, orchard, fruit tree, many apples, many squirrels, many nuts, '
 'ocean, underwater, shark, fish, coral, kelp, beach, picture frame, wooden frame, poster border, readable text, letters, numbers, logo, watermark, caption, sign, label, scary, blood, gore, horror, blurry, low quality, malformed squirrel, extra limbs, crowded, duplicate characters, hidden apple, hidden acorn'
)

def make_guide():
    W,H=832,1472
    im=Image.new('RGB',(W,H),'white')
    d=ImageDraw.Draw(im)
    # tabletop / barren rock horizon
    d.line((0,930,832,900),fill='black',width=4)
    d.line((70,1035,250,1010,420,1040,605,990,780,1030),fill='black',width=3)
    # three soft spotlight ovals / plinths
    for cx in (190,420,650):
        d.ellipse((cx-115,1050,cx+115,1220),outline='black',width=3)
    # apple left: very recognizable apple + stem
    d.ellipse((95,620,285,820),outline='black',width=7)
    d.arc((135,595,205,660),200,350,fill='black',width=5)
    d.line((190,610,215,550),fill='black',width=6)
    d.ellipse((213,535,270,570),outline='black',width=5)
    # squirrel center: upright body, head, ear, tail
    d.ellipse((365,650,475,850),outline='black',width=7) # body
    d.ellipse((360,560,465,665),outline='black',width=7) # head
    d.polygon([(382,565),(395,510),(420,570)],outline='black')
    d.line((382,565,395,510,420,570),fill='black',width=5)
    d.ellipse((432,595,444,607),fill='black')
    d.arc((455,605,590,820),90,310,fill='black',width=16) # fluffy tail outer
    d.arc((482,640,560,790),90,310,fill='black',width=7) # inner tail
    d.line((392,840,360,930),fill='black',width=5)
    d.line((448,842,485,930),fill='black',width=5)
    d.line((380,735,330,780),fill='black',width=5)
    # acorn right: cap + nut body
    d.arc((555,570,750,710),180,360,fill='black',width=8)
    d.line((560,640,745,640),fill='black',width=7)
    d.ellipse((575,630,735,850),outline='black',width=7)
    for x in range(580,730,25):
        d.line((x,585,x+55,640),fill='black',width=3)
    d.line((650,575,675,530),fill='black',width=6)
    # negative visual reminder: barren cracked backdrop, no plant shapes
    d.line((55,910,110,880,160,905),fill='black',width=3)
    d.line((520,900,575,860,620,890),fill='black',width=3)
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

def workflow(seed,prefix,strength,cfg,steps):
    return {
        '1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},
        '2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},
        '3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},
        '4':{'class_type':'LoadImage','inputs':{'image':'v12_guides/'+GUIDE_NAME}},
        '5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},
        '6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},
        '7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':0.58,'vae':['1',2]}},
        '8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},
        '9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},
        '10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},
        '11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}
    }

def run(seed,prefix,strength,cfg,steps):
    pid=post('/prompt',{'prompt':workflow(seed,prefix,strength,cfg,steps),'client_id':CLIENT_ID})['prompt_id']
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
    base=31270000
    variants=[
        (1,0.22,4.7,24),
        (2,0.30,4.2,22),
        (3,0.38,3.8,22),
        (4,0.16,5.0,26),
        (5,0.28,4.8,24),
        (6,0.34,4.5,24),
    ]
    for v,strength,cfg,steps in variants:
        seed=base+v
        for f in run(seed,f'v12_shot03_apple_squirrel_acorn_v{v:02d}',strength,cfg,steps):
            manifest.append({'shot':'03_apple_squirrel_acorn','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v12_shot03_apple_squirrel_acorn_manifest.json'
    out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
