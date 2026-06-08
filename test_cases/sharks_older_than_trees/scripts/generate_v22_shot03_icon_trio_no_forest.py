#!/usr/bin/env python3
"""v22 Shot 3: controlled icon-trio on seamless teal set to avoid forest/museum drift."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw

SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v22_shot03_icon_trio_no_forest'; GUIDE_DIR=ROOT/'assets'/'v22_guides'; COMFY_IN=COMFY/'input'/'v22_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot03_icon_trio_apple_squirrel_walnut_guide.png'
PROMPT=(
 'vertical 9:16 premium tactile educational miniature, seamless teal-blue studio cyclorama background, dark matte basalt plinth, warm amber rim light, macro photography, family science short, playful dry comedy, '
 'exactly three separate large handmade clay icon objects arranged left to right and nothing else: left one glossy red apple icon with tiny brown stem, center one single cute gray squirrel icon standing upright with fluffy tail, right one oversized brown walnut nut icon with wrinkled shell texture, '
 'three objects far apart, clean silhouettes, sparse negative space, premium natural-history quality but not a museum hallway and not an outdoor landscape, no trees, no grass, no leaves, no forest, no labels, no readable text'
)
NEG=(
 'readable text, letters, numbers, labels, sign, caption, watermark, logo, plaque text, fake writing, chart text, '
 'tree, trees, forest, woods, woodland, trunk, branch, branches, bark, evergreen, pine, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, flowers, moss, jungle, orchard, vine, roots, outdoor landscape, mountains, sky, clouds, water, shoreline, '
 'many fruit, extra apples, many squirrels, extra squirrels, many nuts, scattered nuts, acorn cap leaf, crowded props, clutter, museum hallway, display case, aquarium shelves, glass shelves, indoor gallery, modern objects, '
 'coral, kelp, shark, fish, cracked earth foreground, white crack pattern, dry lake bed, tile pattern, low quality, malformed squirrel, extra limbs, scary, gore'
)
def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    d.rectangle((60,940,772,1110),outline='black',width=5)
    for cx in (180,416,652): d.ellipse((cx-96,965,cx+96,1110),outline='black',width=4)
    # apple
    d.ellipse((96,570,264,760),outline='black',width=11); d.ellipse((128,550,228,700),outline='black',width=11); d.line((183,572,205,520),fill='black',width=8)
    # squirrel
    d.ellipse((366,650,475,830),outline='black',width=9); d.ellipse((360,538,480,660),outline='black',width=9); d.line((385,548,405,500,432,555),fill='black',width=7); d.ellipse((440,585,456,601),fill='black'); d.arc((468,590,635,850),88,315,fill='black',width=22); d.line((390,830,360,918),fill='black',width=8); d.line((450,830,502,918),fill='black',width=8)
    # walnut/nut (not acorn, no leaf/cap/stem)
    d.ellipse((560,600,744,875),outline='black',width=11)
    d.line((652,610,662,668,640,720,665,780,648,865),fill='black',width=5)
    for y in (650,705,760,815): d.arc((585,y-35,720,y+35),15,165,fill='black',width=4)
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
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v22_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':end_percent,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
def run(seed,prefix,strength,cfg,steps,end_percent):
    pid=post('/prompt',{'prompt':workflow(seed,prefix,strength,cfg,steps,end_percent),'client_id':CLIENT_ID})['prompt_id']
    for _ in range(420):
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
    guide=make_guide(); manifest=[]; base=143022000
    configs=[(1,0.32,4.8,26,0.62),(2,0.42,4.0,24,0.70),(3,0.52,3.5,24,0.78),(4,0.24,5.4,28,0.58),(5,0.36,5.0,26,0.66),(6,0.46,4.2,24,0.74),(7,0.28,5.8,28,0.60),(8,0.40,4.6,26,0.68)]
    for v,strength,cfg,steps,end_percent in configs:
        seed=base+v
        for f in run(seed,f'v22_shot03_icon_trio_no_forest_v{v:02d}',strength,cfg,steps,end_percent):
            manifest.append({'shot':'03_icon_trio_no_forest','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'end_percent':end_percent,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v22_shot03_icon_trio_no_forest_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
