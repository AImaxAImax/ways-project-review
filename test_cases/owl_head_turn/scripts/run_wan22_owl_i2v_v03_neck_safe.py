#!/usr/bin/env python3
from __future__ import annotations
import json, time, uuid, subprocess
from pathlib import Path
import requests

COMFY='http://127.0.0.1:8188'
CASE=Path('/mnt/c/dev/curious-shorts/test_cases/owl_head_turn')
WORKFLOW=Path('/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json')
OUT=CASE/'outputs/wan22_owl_head_turn_v03_neck_safe'
OUT.mkdir(parents=True, exist_ok=True)

NEG=(
 'text, subtitles, readable letters, watermark, logo, UI, labels, arrows, anatomy diagram, x-ray, skeleton, '
 'extra owl, duplicate head, duplicate face, melted eyes, warped beak, broken neck, stretched neck, rubber neck, twisted neck skin, '
 'neck deformation, melting feathers, body turning, morphing animal anatomy, horror, gore, scene transition, hard cut, camera whip, flicker, low quality, blurry, compression artifacts'
)

SHOTS=[
 {
  'id':'01','seed':913301,'width':432,'height':768,'length':25,
  'plate':CASE/'assets/pending_human_plate_review/higgsfield_v02_top_picks/03_seedream_body_front_face_back_01.png',
  'prompt':('premium natural-history documentary image-to-video from the exact owl source still. Preserve the single owl, stump, feathers, eyes, facial disk, body, and realistic anatomy exactly. The owl is already showing the head-rotation fact: chest/body facing away while face looks back toward camera. Do not twist or stretch the neck. Keep the neck hidden inside thick feathers. Only tiny lifelike motion: subtle blink, micro feather breathing, very slow camera creep, soft background movement. No head morph, no body turn, no duplicate head, no text, no watermark.')
 },
 {
  'id':'02','seed':913302,'width':432,'height':768,'length':25,
  'plate':CASE/'assets/pending_human_plate_review/higgsfield_v02_top_picks/02_ref_seedream01_turn_01.png',
  'prompt':('premium natural-history documentary image-to-video from the exact owl source still. Preserve the single owl, branch, forest background, feathers, eyes, facial disk, and realistic anatomy exactly. Body stays locked and perched, head is already turned over the shoulder. Avoid any visible neck twisting: no stretched neck, no rubber neck, no melting collar feathers. Only tiny lifelike motion: blink, slight eye intensity change, subtle feather breathing, slow camera creep, soft forest particles. No second owl, no duplicate head, no body turn, no text, no watermark.')
 },
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

try:
    requests.post(COMFY+'/free',json={'unload_models':True,'free_memory':True},timeout=30)
except Exception as e:
    print(json.dumps({'free_warning':repr(e)}),flush=True)
print(json.dumps({'system':requests.get(COMFY+'/system_stats',timeout=10).json()['devices'][0]['name']}),flush=True)
results=[]
for shot in SHOTS:
    uploaded=upload(shot['plate'])
    wf=json.loads(WORKFLOW.read_text())
    wf['39']['inputs']['vae_name']='wan_2.1_vae.safetensors'
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
    wf['61']['inputs']['filename_prefix']=f"ways_owl_head_turn_v03_neck_safe/shot{shot['id']}_{shot['seed']}"
    pid=queue(wf)
    print(json.dumps({'queued':pid,'shot_id':shot['id'],'plate':str(shot['plate'])}),flush=True)
    entry=wait(pid)
    items=outs(entry)
    if not items: raise RuntimeError('no outputs')
    item=items[0]
    r=requests.get(COMFY+'/view',params={'filename':item['filename'],'subfolder':item.get('subfolder',''),'type':item.get('type','output')},timeout=600)
    r.raise_for_status()
    dest=OUT/f"shot{shot['id']}_owl_neck_safe_wan22_{shot['width']}x{shot['height']}_{shot['length']}f_seed{shot['seed']}.mp4"
    dest.write_bytes(r.content)
    meta={k:(str(v) if isinstance(v,Path) else v) for k,v in shot.items()}
    meta.update({'prompt_id':pid,'uploaded_image':uploaded,'comfy_output':item,'clip':str(dest),'bytes':dest.stat().st_size})
    dest.with_suffix('.json').write_text(json.dumps(meta,indent=2,default=str))
    results.append(meta)
    print(json.dumps({'saved':str(dest),'bytes':dest.stat().st_size}),flush=True)

# combined candidate sheet
sheet=OUT/'contact_sheet_owl_i2v_v03_neck_safe.jpg'
if results:
    cmd=['ffmpeg','-y']
    for r in results: cmd += ['-i', r['clip']]
    cmd += ['-filter_complex','[0:v]fps=3,scale=270:480,tile=3x2[s0];[1:v]fps=3,scale=270:480,tile=3x2[s1];[s0][s1]vstack=inputs=2[out]','-map','[out]','-frames:v','1',str(sheet)]
    subprocess.run(cmd,check=False)
manifest={'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'results':results,'outputs':{'contact_sheet':str(sheet)}}
(OUT/'wan22_owl_i2v_manifest_v03_neck_safe.json').write_text(json.dumps(manifest,indent=2,default=str))
print(json.dumps({'ok':True,'manifest':str(OUT/'wan22_owl_i2v_manifest_v03_neck_safe.json'),'clips':[r['clip'] for r in results]},indent=2))
