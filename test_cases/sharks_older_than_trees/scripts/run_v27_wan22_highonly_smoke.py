#!/usr/bin/env python3
import json, time, uuid
from pathlib import Path
import requests
COMFY='http://127.0.0.1:8188'
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
WORKFLOW=Path('/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json')
OUT=ROOT/'outputs/wan22_v27_animated_frames/highonly_smoke'; OUT.mkdir(parents=True,exist_ok=True)
img=ROOT/'assets/gpt_image_2_manual_v23/shot01_gpt_image2_hook_before_trees_v01.jpeg'
with img.open('rb') as f:
 r=requests.post(COMFY+'/upload/image',files={'image':(img.name,f,'image/jpeg')},data={'type':'input','overwrite':'true'},timeout=180); r.raise_for_status(); name=r.json().get('name')
requests.post(COMFY+'/free',json={'unload_models':True,'free_memory':True},timeout=30)
wf=json.loads(WORKFLOW.read_text())
wf['39']['inputs']['vae_name']='wan_2.1_vae.safetensors'
wf['62']['inputs']['image']=name
wf['63']['inputs'].update({'width':432,'height':768,'length':25})
wf['6']['inputs']['text']='premium natural-history documentary image-to-video. Ancient shark glides calmly through blue-green prehistoric ocean, subtle tail swish and fin motion, drifting particles, slow parallax water shimmer. Preserve exact shark anatomy, framing, colors, realistic style. No attack, no blood, no text, no logos, no scene cut, no morphing.'
wf['7']['inputs']['text']='text, logos, UI, morphing, distorted anatomy, duplicated fins, jitter, flicker, low quality'
wf['57']['inputs']['noise_seed']=777101
# Bypass low-noise sampler that currently stalls on node 58; decode high-noise latent directly for smoke.
wf['8']['inputs']['samples']=['57',0]
wf['61']['inputs']['filename_prefix']='ways_shark_v27_wan22_highonly_smoke/shot01_777101'
r=requests.post(COMFY+'/prompt',json={'prompt':wf,'client_id':str(uuid.uuid4())},timeout=60)
print(r.status_code, r.text[:1000], flush=True); r.raise_for_status(); pid=r.json()['prompt_id']
start=time.time()
while True:
 h=requests.get(COMFY+f'/history/{pid}',timeout=30).json()
 if pid in h:
  print(json.dumps(h[pid].get('status',{}),indent=2),flush=True)
  outs=[]
  for node_id,o in h[pid].get('outputs',{}).items():
   for key in ('videos','gifs','images'):
    for item in o.get(key,[]) or []:
     if isinstance(item,dict) and 'filename' in item: outs.append(item)
  print(json.dumps(outs,indent=2),flush=True)
  if not outs: raise SystemExit(2)
  item=outs[0]
  rr=requests.get(COMFY+'/view',params={'filename':item['filename'],'subfolder':item.get('subfolder',''),'type':item.get('type','output')},timeout=600); rr.raise_for_status()
  dest=OUT/'shot01_highonly_25f.mp4'; dest.write_bytes(rr.content)
  print(json.dumps({'saved':str(dest),'bytes':dest.stat().st_size,'elapsed':round(time.time()-start,1)}),flush=True)
  break
 print(json.dumps({'waiting_s':round(time.time()-start,1),'pid':pid}),flush=True); time.sleep(10)
