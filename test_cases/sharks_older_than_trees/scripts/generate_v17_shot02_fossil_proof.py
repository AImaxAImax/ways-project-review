#!/usr/bin/env python3
"""v17 Shot 2: stronger 'Seriously' proof beat — fossil slab/tooth, no aquarium box/coral."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw
SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v17_shot02_seriously_fossil_proof'; GUIDE_DIR=ROOT/'assets'/'v17_guides'; COMFY_IN=COMFY/'input'/'v17_guides'
OUT.mkdir(parents=True,exist_ok=True); GUIDE_DIR.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'; CNET='xinsir_controlnet_canny_sdxl_v2.safetensors'; GUIDE_NAME='shot02_fossil_slab_tooth_proof_guide.png'
PROMPT=(
 'premium natural history museum stop-motion diorama, tactile paper and clay miniature, cinematic macro photography, warm museum spotlight with teal blue rim light, elegant educational science frame, '
 'a quiet proof moment for the word Seriously: one large ancient shark fossil impression carved into a smooth dark stone slab, shark silhouette fossil clearly embedded in rock, one oversized fossil shark tooth beside the slab, dramatic evidence table, '
 'dark matte stone surface, soft dust particles, clean negative space, handcrafted premium miniature, visually consistent with teal underwater Shot 1 but a new fossil proof composition, no glass display case, no aquarium, no coral, no plants, no readable text'
)
NEG=(
 'readable text, letters, numbers, labels, sign, caption, watermark, logo, plaque text, fake writing, chart text, '
 'glass box, aquarium, display case, terrarium, shelf, window frame, picture frame, wooden frame, coral, kelp, seaweed, bush, branches, tree, trees, forest, plant, plants, vegetation, leaves, leaf, grass, fern, palm, flowers, moss, jungle, woodland, '
 'many sharks, living swimming shark, open ocean scene, cracked earth foreground, white crack pattern, dry lake bed, tile pattern, stacked layers, multiple horizons, clutter, scary teeth mouth, attack, blood, gore, horror, low quality, malformed fossil, malformed shark, human hands, people'
)
def make_guide():
    W,H=832,1472; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    # stone evidence table / slab
    d.ellipse((110,1130,735,1290),outline='black',width=3)
    d.polygon([(115,510),(705,455),(765,970),(75,1050)],outline='black')
    for seg in [((115,510),(705,455)),((705,455),(765,970)),((765,970),(75,1050)),((75,1050),(115,510))]:
        d.line(seg, fill='black', width=5)
    # embedded fossil shark outline on slab
    d.line((155,725,270,660,520,655,685,710),fill='black',width=8)
    d.line((160,742,290,800,525,795,680,720),fill='black',width=5)
    d.line((655,716,748,665,715,724,758,790,655,716),fill='black',width=5)
    d.line((418,660,468,550,520,666),fill='black',width=7)
    d.line((442,792,500,900,552,790),fill='black',width=5)
    d.ellipse((228,710,242,724),fill='black')
    # oversized fossil tooth at lower right, separate proof object
    d.polygon([(575,990),(680,1035),(618,1245)],outline='black')
    d.line((575,990,680,1035,618,1245,575,990),fill='black',width=7)
    d.arc((560,955,695,1085),195,345,fill='black',width=5)
    # subtle spotlight rings only
    d.arc((190,310,665,520),190,350,fill='black',width=2)
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
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},'3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},'4':{'class_type':'LoadImage','inputs':{'image':'v17_guides/'+GUIDE_NAME}},'5':{'class_type':'Canny','inputs':{'image':['4',0],'low_threshold':0.08,'high_threshold':0.45}},'6':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CNET}},'7':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['6',0],'image':['5',0],'strength':strength,'start_percent':0.0,'end_percent':end_percent,'vae':['1',2]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['7',0],'negative':['7',1],'latent_image':['8',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['1',2]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}}}
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
    guide=make_guide(); manifest=[]; base=111705000
    for v,strength,cfg,steps,end_percent in [(1,0.18,4.9,26,0.50),(2,0.24,4.5,24,0.55),(3,0.30,4.0,24,0.60),(4,0.14,5.3,28,0.48),(5,0.22,5.0,26,0.58),(6,0.34,3.8,24,0.62),(7,0.28,4.8,26,0.56),(8,0.20,5.4,28,0.52)]:
        seed=base+v
        for f in run(seed,f'v17_shot02_fossil_proof_v{v:02d}',strength,cfg,steps,end_percent):
            manifest.append({'shot':'02_seriously_fossil_proof','variant':v,'seed':seed,'strength':strength,'cfg':cfg,'steps':steps,'end_percent':end_percent,'guide':str(guide),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v17_shot02_fossil_proof_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'guide':str(guide)},indent=2))
