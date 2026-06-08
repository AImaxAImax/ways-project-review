#!/usr/bin/env python3
"""v14 Shot 1: img2img cleanup from v12_01 — preserve shark-in-water, simplify strange background."""
import json, time, urllib.request, urllib.parse, uuid, shutil
from pathlib import Path

SERVER='127.0.0.1:8188'; CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees'); COMFY=Path('/mnt/c/dev/ComfyUI')
OUT=ROOT/'assets'/'v14_shot01_img2img_bg_cleanup'; COMFY_IN=COMFY/'input'/'v14_refs'
OUT.mkdir(parents=True,exist_ok=True); COMFY_IN.mkdir(parents=True,exist_ok=True)
CKPT='DreamShaperXL_Turbo_V2-SFW.safetensors'
REF_SRC=ROOT/'assets/selected_frames_v12/shot01_before_trees_submerged_shark_v12_v01_selected.png'
REF_NAME='shot01_v12_01_submerged_ref.png'
shutil.copy2(REF_SRC, COMFY_IN/REF_NAME)
PROMPT=(
 'premium natural history museum diorama, cinematic macro photography, calm ancient shark swimming underwater in foreground, body clearly below water surface, soft ripples and refraction, '
 'simple clean background: one barren volcanic coastline above the waterline, low ochre sandbar and dark basalt cliffs, empty lifeless shore before plants existed, uncluttered teal water, elegant negative space, '
 'no strange patterns, no cracked floor, no aquarium shelves, no stacked horizontal bands, no foreground dry lake bed, peaceful educational science frame, high production value'
)
NEG=(
 'tree, trees, forest, plant, plants, vegetation, leaves, leaf, grass, fern, palm, bush, branches, flowers, moss, cactus, coral, kelp, jungle, woodland, '
 'cracked earth foreground, white crack pattern, tile pattern, dry lake bed, giraffe pattern, stacked water layers, aquarium shelf, glass shelf, multiple horizons, weird floating islands, clutter, '
 'shark sitting on water, shark on top of water, beached shark, toy shark, cutout shark, many sharks, scary teeth, open mouth, attack, blood, gore, text, letters, numbers, watermark, logo, low quality, malformed'
)
def post(path,data):
    import urllib.request, json
    req=urllib.request.Request(f'http://{SERVER}{path}',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode())
def get(path):
    import urllib.request, json
    with urllib.request.urlopen(f'http://{SERVER}{path}',timeout=30) as r: return json.loads(r.read().decode())
def dl(filename, subfolder='', folder_type='output'):
    q=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':folder_type})
    with urllib.request.urlopen(f'http://{SERVER}/view?{q}',timeout=60) as r: data=r.read()
    dest=OUT/filename; dest.write_bytes(data); return str(dest)
def workflow(seed,prefix,denoise,cfg,steps):
    return {
        '1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},
        '2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':PROMPT}},
        '3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},
        '4':{'class_type':'LoadImage','inputs':{'image':'v14_refs/'+REF_NAME}},
        '5':{'class_type':'VAEEncode','inputs':{'pixels':['4',0],'vae':['1',2]}},
        '6':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['2',0],'negative':['3',0],'latent_image':['5',0],'seed':seed,'steps':steps,'cfg':cfg,'sampler_name':'euler','scheduler':'normal','denoise':denoise}},
        '7':{'class_type':'VAEDecode','inputs':{'samples':['6',0],'vae':['1',2]}},
        '8':{'class_type':'SaveImage','inputs':{'images':['7',0],'filename_prefix':prefix}}
    }
def run(seed,prefix,denoise,cfg,steps):
    pid=post('/prompt',{'prompt':workflow(seed,prefix,denoise,cfg,steps),'client_id':CLIENT_ID})['prompt_id']
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
    manifest=[]; base=81402000
    variants=[(1,0.32,4.5,24),(2,0.40,4.8,26),(3,0.48,5.0,28),(4,0.55,4.2,26),(5,0.38,5.3,28),(6,0.45,4.0,24)]
    for v,denoise,cfg,steps in variants:
        seed=base+v
        for f in run(seed,f'v14_shot01_bg_cleanup_v{v:02d}',denoise,cfg,steps):
            manifest.append({'shot':'01_img2img_background_cleanup','variant':v,'seed':seed,'denoise':denoise,'cfg':cfg,'steps':steps,'reference':str(REF_SRC),'prompt':PROMPT,'negative':NEG,'file':f})
    out=ROOT/'outputs/v14_shot01_img2img_bg_cleanup_manifest.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(manifest),'manifest':str(out),'reference':str(REF_SRC)},indent=2))
