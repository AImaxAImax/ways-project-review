#!/usr/bin/env python3
"""v12c Shot 3: simplify to one clear red apple + one squirrel + one oversized acorn on black museum stage."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw
SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v12c_shot03_simple_trio'; GUIDE_DIR=ROOT/'assets'/'v12_guides'; COMFY_IN=COMFY/'input'/'v12_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot03_simple_apple_squirrel_acorn_stage_guide.png'
PROMPT=(
 'premium handcrafted stop-motion miniature, tactile cut paper and soft clay, macro studio photography, warm museum spotlight, dark matte black stage, bare slate floor, '
 'exactly three large readable objects centered on stage: left one glossy red apple, middle one cute gray squirrel standing upright with fluffy tail, right one oversized brown acorn with textured cap, '
 'simple uncluttered composition, charming dry comedy science frame, clear silhouettes, crisp object shadows, high production value, clean negative space, no border'
)
NEG=(
 'tree, trees, forest, woods, woodland, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, jungle, orchard, mountains, outdoor landscape, sky, horizon, snow, stump, many apples, many squirrels, many acorns, '
 'ocean, underwater, shark, fish, coral, kelp, beach, picture frame, wooden frame, poster border, readable text, letters, numbers, logo, watermark, caption, sign, label, scary, blood, gore, horror, blurry, low quality, malformed squirrel, extra limbs, crowded, duplicate characters, hidden apple, hidden acorn, tiny acorn'
)
def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    d.line((0,1000,832,1000),fill='black',width=4)
    # apple left
    d.ellipse((105,665,285,855),outline='black',width=10)
    d.arc((145,642,210,700),205,340,fill='black',width=6)
    d.line((195,655,225,590),fill='black',width=8)
    d.ellipse((223,570,292,607),outline='black',width=6)
    # squirrel center larger
    d.ellipse((360,705,492,925),outline='black',width=10)
    d.ellipse((365,590,482,710),outline='black',width=10)
    d.line((385,600,402,535,430,610),fill='black',width=8)
    d.ellipse((448,633,464,649),fill='black')
    d.arc((472,630,650,905),82,315,fill='black',width=22)
    d.arc((515,690,610,860),90,310,fill='black',width=8)
    d.line((392,920,355,1000),fill='black',width=8); d.line((462,920,510,1000),fill='black',width=8)
    # acorn right: huge and separated
    d.arc((565,650,770,795),180,360,fill='black',width=11)
    d.line((566,724,770,724),fill='black',width=10)
    d.ellipse((588,705,750,955),outline='black',width=10)
    for x in range(578,736,30): d.line((x,670,x+65,724),fill='black',width=4)
    d.line((665,657,700,595),fill='black',width=8)
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
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v12_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':0.70,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
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
    guide=make_guide(); manifest=[]; base=51273000
    for v,strength,cfg,steps in [(1,0.52,4.2,24),(2,0.64,3.4,24),(3,0.46,4.8,26),(4,0.58,4.0,26),(5,0.68,3.2,24),(6,0.40,5.2,28)]:
        seed=base+v
        for f in run(seed,f'v12c_shot03_simple_trio_v{v:02d}',strength,cfg,steps):
            manifest.append({'shot':'03_simple_apple_squirrel_acorn','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v12c_shot03_simple_trio_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
