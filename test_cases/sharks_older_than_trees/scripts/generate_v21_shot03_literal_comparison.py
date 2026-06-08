#!/usr/bin/env python3
"""v21 Shot 3: literal apple + squirrel + acorn comparison gag, less museum-room sameness."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw

SERVER='127.0.0.1:8188'
CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v21_shot03_literal_comparison'
GUIDE_DIR=ROOT/'assets'/'v21_guides'
COMFY_IN=COMFY/'input'/'v21_guides'
OUT.mkdir(parents=True,exist_ok=True)
GUIDE_DIR.mkdir(parents=True,exist_ok=True)
COMFY_IN.mkdir(parents=True,exist_ok=True)

CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'
CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'
GUIDE_NAME='shot03_literal_apple_squirrel_acorn_barren_coast_guide.png'

PROMPT=(
 'vertical 9:16 premium tactile natural-history miniature, cinematic macro photography, teal prehistoric water and warm amber rim light, family science short, playful dry comedy, '
 'barren volcanic rock ledge beside shallow ancient teal water, absolutely no vegetation, no trees, no grass, no leaves, no forest, '
 'exactly three clear future-things displayed as simple ghosted props over the empty lifeless land: left one bright red apple with a tiny brown stem, center one cute single squirrel miniature standing upright with fluffy tail, right one oversized brown acorn nut with cap texture, '
 'the apple, squirrel, and acorn are separated far apart and unmistakable, clean silhouettes, sparse composition, natural-history premium look, not a museum hallway, not display shelves, clean negative space for captions, no readable text, no labels'
)
NEG=(
 'readable text, letters, numbers, labels, sign, caption, watermark, logo, plaque text, fake writing, chart text, '
 'tree, trees, forest, woods, woodland, trunk, branch, branches, bark, evergreen, pine, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, flowers, moss, jungle, orchard, vine, roots, '
 'many fruit, many squirrels, many nuts, crowded props, clutter, museum hallway, display case, aquarium shelves, glass shelves, indoor gallery, outdoor forest, mountains, modern objects, '
 'coral, kelp, shark, fish, cracked earth foreground, white crack pattern, dry lake bed, tile pattern, low quality, malformed squirrel, extra limbs, scary, gore'
)

def make_guide():
    W,H=832,1472
    im=Image.new('RGB',(W,H),'white')
    d=ImageDraw.Draw(im)
    # waterline / barren coast blocks
    d.rectangle((0,910,W,H),outline='black',width=5)
    d.line((0,945,180,925,340,955,530,930,832,950),fill='black',width=6)
    d.arc((60,330,772,520),190,350,fill='black',width=3)
    # three separated ghost prop zones
    for cx in (180,416,652):
        d.ellipse((cx-100,965,cx+100,1125),outline='black',width=4)
    # apple
    d.ellipse((95,575,265,765),outline='black',width=10)
    d.ellipse((130,555,230,705),outline='black',width=10)
    d.line((185,575,202,520),fill='black',width=7)
    # squirrel
    d.ellipse((370,640,472,830),outline='black',width=8)
    d.ellipse((360,535,478,655),outline='black',width=8)
    d.line((383,545,405,493,430,552),fill='black',width=6)
    d.ellipse((438,582,454,598),fill='black')
    d.arc((465,585,635,845),88,315,fill='black',width=20)
    d.line((390,830,355,920),fill='black',width=7)
    d.line((450,830,505,920),fill='black',width=7)
    # acorn
    d.arc((550,585,755,725),180,360,fill='black',width=10)
    d.line((552,665,755,665),fill='black',width=9)
    d.ellipse((585,650,728,900),outline='black',width=9)
    for x in range(565,725,28):
        d.line((x,615,x+70,665),fill='black',width=3)
    d.line((652,590,680,535),fill='black',width=7)
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
      '4':{'class_type':'LoadImage','inputs':{'image':'v21_guides/'+GUIDE_NAME}},
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
    for _ in range(420):
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
    base=143021000
    configs=[(1,0.24,4.8,26,0.55),(2,0.32,4.2,24,0.62),(3,0.42,3.6,24,0.70),(4,0.18,5.4,28,0.52),(5,0.28,5.0,26,0.60),(6,0.36,4.0,24,0.66),(7,0.48,3.4,24,0.74),(8,0.22,5.7,28,0.54)]
    for v,strength,cfg,steps,end_percent in configs:
        seed=base+v
        for f in run(seed,f'v21_shot03_literal_comparison_v{v:02d}',strength,cfg,steps,end_percent):
            manifest.append({'shot':'03_literal_comparison','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'end_percent':end_percent,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v21_shot03_literal_comparison_manifest.json'
    out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
