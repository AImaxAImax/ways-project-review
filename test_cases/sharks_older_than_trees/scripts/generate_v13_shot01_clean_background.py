#!/usr/bin/env python3
"""v13 Shot 1: keep v12's shark-in-water success, simplify weird layered/cracked background."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw

SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v13_shot01_clean_background'; GUIDE_DIR=ROOT/'assets'/'v13_guides'; COMFY_IN=COMFY/'input'/'v13_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot01_clean_single_coast_submerged_shark_guide.png'

PROMPT=(
 'premium natural history museum diorama, handcrafted stop-motion miniature, tactile paper and clay geology, macro studio photography, cinematic depth of field, warm museum light, '
 'simple clean ancient shallow sea scene, one calm ancient shark swimming underwater in foreground, shark body below the water surface, dorsal fin near surface, soft ripples and refraction around the back, peaceful not scary, '
 'above the waterline a single simple barren volcanic coastline: low ochre sandbar, dark basalt cliff, empty lifeless rocky shore, no plants, no trees, no grass, no forest, '
 'clean uncluttered background, no cracked dry lake floor, no stacked aquarium shelves, no strange layered bands, no extra islands in foreground, elegant negative space, high production value'
)
NEG=(
 'tree, trees, forest, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, cactus, coral, kelp, jungle, woodland, '
 'cracked earth foreground, white crack pattern, dry lake bed, tile pattern, giraffe pattern, stacked water layers, aquarium glass shelves, multiple horizons, weird floating islands, cluttered foreground, foreground rocks blocking shark, '
 'shark lying on surface, shark sitting on water, toy shark, cutout shark, beached shark, shark on land, floating on top, dry outline, dead shark, full body above water, many sharks, duplicate sharks, '
 'readable text, letters, numbers, logo, watermark, caption, sign, label, scary teeth, shark attack, open mouth, blood, gore, horror, blurry, low quality, malformed shark, malformed fins'
)

def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    # One simple surface/waterline and one clean barren coast above it.
    d.line((0,535,832,520),fill='black',width=5)
    d.line((0,475,170,440,340,462,520,425,700,455,832,415),fill='black',width=4)
    d.line((250,515,610,505),fill='black',width=3)  # simple cliff top/edge
    # open underwater volume, no bottom cracks/layers.
    d.arc((80,720,770,1090),188,350,fill='black',width=3)  # subtle ripple band
    d.arc((155,765,700,1015),188,350,fill='black',width=2)
    # shark underwater, slightly below surface, clear but not huge.
    cx,cy=430,815
    d.line((210,815,300,770,510,765,665,808),fill='black',width=8)  # back
    d.line((220,825,315,875,510,875,660,820),fill='black',width=5)  # belly
    d.line((646,812,730,760,700,820,735,875,646,812),fill='black',width=5)  # tail
    d.line((415,770,462,660,505,775),fill='black',width=7)  # dorsal
    d.line((460,875,505,955,545,872),fill='black',width=5)  # pectoral
    d.ellipse((278,798,290,810),fill='black')
    # water surface highlight crossing above shark, not through whole image as weird band.
    d.line((170,735,705,720),fill='black',width=2)
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
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v13_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':end_percent,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
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
    guide=make_guide(); manifest=[]; base=71301000
    for v,strength,cfg,steps,end_percent in [(1,0.18,4.9,26,0.50),(2,0.24,4.5,24,0.55),(3,0.30,4.0,24,0.60),(4,0.14,5.3,28,0.48),(5,0.22,5.0,26,0.58),(6,0.34,3.8,24,0.62)]:
        seed=base+v
        for f in run(seed,f'v13_shot01_clean_background_v{v:02d}',strength,cfg,steps,end_percent):
            manifest.append({'shot':'01_clean_background_submerged_shark','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'end_percent':end_percent,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v13_shot01_clean_background_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
