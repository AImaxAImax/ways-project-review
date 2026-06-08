#!/usr/bin/env python3
from __future__ import annotations
import json, time, uuid, subprocess
from pathlib import Path
import requests

COMFY='http://127.0.0.1:8188'
CASE=Path('/mnt/c/dev/curious-shorts/test_cases/owl_head_turn')
WORKFLOW=Path('/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json')
OUT=CASE/'outputs/wan22_owl_head_turn_v01'
OUT.mkdir(parents=True, exist_ok=True)
PLATE=CASE/'assets/pending_human_plate_review/higgsfield_v02_top_picks/01_ref_nano04_turn_01.png'

PROMPT=(
 'premium natural-history documentary image-to-video from the exact owl source still. '
 'Preserve the single owl, branch, forest background, feathers, eyes, and realistic anatomy. '
 'The owl body stays locked and perched while only the head makes a slow believable owl swivel: '
 'head turns from looking over its shoulder slightly back toward camera, then pauses with intense eye contact. '
 'Very subtle camera creep, tiny feather movement, soft forest particles, cinematic dusk light. '
 'No scene cut, no second owl, no duplicate head, no stretched neck, no horror, no gore, no text, no labels, no watermark, no logo.'
)
NEG=(
 'text, subtitles, readable letters, watermark, logo, UI, labels, arrows, anatomy diagram, x-ray, skeleton, '
 'extra owl, duplicate head, duplicate face, melted eyes, warped beak, broken neck, gore, horror, scene transition, '
 'hard cut, morphing animal anatomy, body turning, camera whip, flicker, low quality, blurry, compression artifacts'
)
SHOTS=[
 # Match the known-working Wan2.2 A14B smoke settings from the shark pilot: 25 frames.
 {'id':'01','seed':812701,'width':432,'height':768,'length':25,'prompt':PROMPT},
 {'id':'02','seed':812702,'width':432,'height':768,'length':25,'prompt':PROMPT.replace('slightly back toward camera','a tiny amount farther over the shoulder, then subtly back toward camera')},
]

def upload(path:Path)->str:
    with path.open('rb') as f:
        r=requests.post(COMFY+'/upload/image',files={'image':(path.name,f,'image/png')},data={'type':'input','overwrite':'true'},timeout=180)
    r.raise_for_status(); return r.json().get('name') or path.name

def queue(wf):
    r=requests.post(COMFY+'/prompt',json={'prompt':wf,'client_id':str(uuid.uuid4())},timeout=60)
    if r.status_code>=400: raise RuntimeError(r.text[:4000])
    data=r.json()
    if data.get('node_errors'): raise RuntimeError(json.dumps(data['node_errors'],indent=2)[:10000])
    return data['prompt_id']

def wait(pid, timeout=7200):
    start=time.time()
    while time.time()-start<timeout:
        hist=requests.get(COMFY+f'/history/{pid}',timeout=30).json()
        if pid in hist:
            status=hist[pid].get('status',{})
            if status.get('status_str')=='error':
                raise RuntimeError(json.dumps(status.get('messages',[]),indent=2)[:12000])
            return hist[pid]
        print(json.dumps({'waiting_s':round(time.time()-start,1),'prompt_id':pid}),flush=True)
        time.sleep(10)
    raise TimeoutError(pid)

def outs(entry):
    out=[]
    for node_id,node_out in entry.get('outputs',{}).items():
        for key in ('videos','gifs','images'):
            for item in node_out.get(key,[]) or []:
                if isinstance(item,dict) and 'filename' in item:
                    out.append({**item,'_node_id':node_id,'_kind':key})
    return out

try: requests.post(COMFY+'/free',json={'unload_models':True,'free_memory':True},timeout=30)
except Exception as e: print(json.dumps({'free_warning':repr(e)}),flush=True)
print(json.dumps({'system':requests.get(COMFY+'/system_stats',timeout=10).json()['devices'][0], 'plate':str(PLATE)}),flush=True)
uploaded=upload(PLATE)
results=[]
for shot in SHOTS:
    wf=json.loads(WORKFLOW.read_text())
    wf['39']['inputs']['vae_name']='wan_2.1_vae.safetensors'
    # Current ComfyUI/Wan nodes expect the original WanImageToVideo node shape from the workflow:
    # node 63 emits positive, negative, and latent outputs. Do not swap in Wan22ImageToVideoLatent here,
    # because this Comfy build produced a 48-vs-16 latent channel mismatch.
    wf['63']['class_type']='WanImageToVideo'
    wf['63']['inputs']={'positive':['6',0], 'negative':['7',0], 'vae':['39',0], 'width':shot['width'], 'height':shot['height'], 'length':shot['length'], 'batch_size':1, 'start_image':['62',0]}
    wf['62']['inputs']['image']=uploaded
    wf['6']['inputs']['text']=shot['prompt']
    wf['7']['inputs']['text']=NEG
    wf['57']['inputs']['positive']=['63',0]
    wf['57']['inputs']['negative']=['63',1]
    wf['57']['inputs']['latent_image']=['63',2]
    wf['57']['inputs']['noise_seed']=shot['seed']
    wf['58']['inputs']['positive']=['63',0]
    wf['58']['inputs']['negative']=['63',1]
    wf['58']['inputs']['latent_image']=['57',0]
    wf['58']['inputs']['noise_seed']=shot['seed']+1000
    wf['61']['inputs']['filename_prefix']=f"ways_owl_head_turn_v01/shot{shot['id']}_{shot['seed']}"
    pid=queue(wf)
    print(json.dumps({'queued':pid,'shot':shot}),flush=True)
    entry=wait(pid)
    items=outs(entry)
    if not items: raise RuntimeError('no outputs')
    item=items[0]
    r=requests.get(COMFY+'/view',params={'filename':item['filename'],'subfolder':item.get('subfolder',''),'type':item.get('type','output')},timeout=600)
    r.raise_for_status()
    dest=OUT/f"shot{shot['id']}_owl_head_turn_wan22_{shot['width']}x{shot['height']}_{shot['length']}f_seed{shot['seed']}.mp4"
    dest.write_bytes(r.content)
    meta={**shot,'prompt_id':pid,'uploaded_image':uploaded,'comfy_output':item,'clip':str(dest),'bytes':dest.stat().st_size}
    dest.with_suffix('.json').write_text(json.dumps(meta,indent=2,default=str))
    results.append(meta)
    print(json.dumps({'saved':str(dest),'bytes':dest.stat().st_size}),flush=True)

# contact sheet for motion candidates
clips=[r['clip'] for r in results]
if clips:
    sheet=OUT/'contact_sheet_owl_i2v_v01.jpg'
    cmd=['ffmpeg','-y']
    # make a 2x2 contact from first clip at several timestamps
    cmd=['ffmpeg','-y','-i',clips[0],'-vf','fps=2,scale=270:480,tile=2x2','-frames:v','1',str(sheet)]
    subprocess.run(cmd,check=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
manifest={'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'plate':str(PLATE),'results':results,'outputs':{'contact_sheet':str(OUT/'contact_sheet_owl_i2v_v01.jpg')}}
(OUT/'wan22_owl_i2v_manifest_v01.json').write_text(json.dumps(manifest,indent=2,default=str))
print(json.dumps({'ok':True,'manifest':str(OUT/'wan22_owl_i2v_manifest_v01.json'),'results':[r['clip'] for r in results]},indent=2))
