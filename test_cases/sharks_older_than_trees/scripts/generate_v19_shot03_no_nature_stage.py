#!/usr/bin/env python3
"""v19 Shot 3: avoid tree/forest trigger words; museum absence gag with apple/squirrel/acorn ghost props on barren stage."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw
SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v19_shot03_no_nature_stage'; GUIDE_DIR=ROOT/'assets'/'v19_guides'; COMFY_IN=COMFY/'input'/'v19_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot03_three_missing_props_no_nature_guide.png'
PROMPT=(
 'premium natural history museum stop-motion diorama, tactile paper and clay miniature, cinematic macro photography, warm museum spotlight with teal blue rim light, elegant family science frame, dry whimsical comedy, '
 'dark matte museum stage on barren volcanic stone, three separate empty spotlights, three pale transparent ghost-prop outlines showing things that are not here yet: left one apple outline, center one cute squirrel outline, right one acorn outline, '
 'the props are translucent absent silhouettes made of frosted paper, empty pedestals, no living objects, no outdoor scenery, smooth basalt backdrop, teal haze, dust motes, clean negative space, premium handcrafted look, visually consistent with previous teal museum shots, no readable text, no labels'
)
NEG=(
 'readable text, letters, numbers, labels, sign, caption, watermark, logo, plaque text, fake writing, chart text, '
 'tree, trees, forest, woods, woodland, trunk, branch, branches, bark, evergreen, pine, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, flowers, moss, jungle, orchard, mountains, sky, outdoor landscape, '
 'real apple, realistic living squirrel, real acorn, many apples, many squirrels, many nuts, crowded props, clutter, aquarium shelves, glass shelves, display case, coral, kelp, shark, fish, ocean, cracked earth foreground, white crack pattern, dry lake bed, tile pattern, low quality, malformed squirrel, extra limbs, scary, gore'
)
def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    # clean stage floor and backdrop, no nature-shaped lines
    d.line((0,1010,832,998),fill='black',width=4)
    d.arc((80,350,752,530),190,350,fill='black',width=3)
    # three pedestals + spotlight cones
    for cx in (190,420,650):
        d.ellipse((cx-105,1015,cx+105,1165),outline='black',width=4)
        d.line((cx-65,1165,cx+65,1165),fill='black',width=3)
        d.line((cx-60,1015,cx,750,cx+60,1015),fill='black',width=2)
    # apple ghost left
    d.ellipse((105,650,275,840),outline='black',width=8)
    d.arc((145,630,205,690),205,340,fill='black',width=5)
    d.line((195,645,225,585),fill='black',width=7)
    d.ellipse((223,565,285,600),outline='black',width=5)
    # squirrel ghost center, upright and simple
    d.ellipse((370,700,480,900),outline='black',width=8)
    d.ellipse((365,590,475,705),outline='black',width=8)
    d.line((385,600,402,545,430,610),fill='black',width=6)
    d.ellipse((438,635,452,649),fill='black')
    d.arc((470,635,625,890),85,315,fill='black',width=18)
    d.line((392,900,355,990),fill='black',width=6); d.line((458,900,505,990),fill='black',width=6)
    # acorn ghost right, oversized
    d.arc((555,650,750,790),180,360,fill='black',width=9)
    d.line((558,720,750,720),fill='black',width=8)
    d.ellipse((580,705,735,935),outline='black',width=8)
    for x in range(575,730,30): d.line((x,670,x+65,720),fill='black',width=3)
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
def workflow(seed,prefix,strength,cfg,steps,end_percent):
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v19_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':end_percent,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
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
    guide=make_guide(); manifest=[]; base=131907000
    for v,strength,cfg,steps,end_percent in [(1,0.22,4.8,26,0.54),(2,0.30,4.2,24,0.60),(3,0.38,3.7,24,0.66),(4,0.16,5.3,28,0.50),(5,0.26,5.0,26,0.58),(6,0.34,4.0,24,0.62),(7,0.44,3.5,24,0.70),(8,0.20,5.6,28,0.52)]:
        seed=base+v
        for f in run(seed,f'v19_shot03_no_nature_stage_v{v:02d}',strength,cfg,steps,end_percent):
            manifest.append({'shot':'03_before_apples_squirrels_nuts_no_nature_stage','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'end_percent':end_percent,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v19_shot03_no_nature_stage_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
