#!/usr/bin/env python3
from __future__ import annotations
import json, time, uuid
from pathlib import Path
import requests
COMFY='http://127.0.0.1:8188'
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
WORKFLOW=Path('/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_ti2v_5b_i2v_smoke.json')
OUT=ROOT/'outputs/wan22_v27_animated_frames'/'pilot_5b'
OUT.mkdir(parents=True, exist_ok=True)
SHOT={
 'id':'07',
 'path':ROOT/'assets/gpt_image_2_manual_v23/04_final_predator_got_here_first.png',
 'seed':627207,
 'prompt':'premium natural-history documentary image-to-video from the exact still. The realistic shark slowly glides toward camera with subtle tail and fin motion, deep ocean particles drift, shafts of light shimmer, distant volcanic glow barely moves. Preserve exact anatomy and calm confident tone. No lunge, no open bloody mouth, no monster look, no text, no logos, no morphing, no scene cut.'
}

def upload(path):
 with path.open('rb') as f:
  r=requests.post(COMFY+'/upload/image',files={'image':(path.name,f,'image/png')},data={'type':'input','overwrite':'true'},timeout=180)
 r.raise_for_status(); return r.json().get('name') or path.name

def queue(wf):
 r=requests.post(COMFY+'/prompt',json={'prompt':wf,'client_id':str(uuid.uuid4())},timeout=60)
 if r.status_code>=400: raise RuntimeError(r.text[:4000])
 data=r.json()
 if data.get('node_errors'): raise RuntimeError(json.dumps(data['node_errors'],indent=2)[:8000])
 return data['prompt_id']

def wait(pid, timeout=7200):
 start=time.time()
 while time.time()-start<timeout:
  hist=requests.get(COMFY+f'/history/{pid}',timeout=30).json()
  if pid in hist:
   status=hist[pid].get('status',{})
   if status.get('status_str')=='error': raise RuntimeError(json.dumps(status.get('messages',[]),indent=2)[:12000])
   return hist[pid]
  print(json.dumps({'waiting_s':round(time.time()-start,1),'prompt_id':pid}),flush=True)
  time.sleep(10)
 raise TimeoutError(pid)

def outs(entry):
 out=[]
 for node_id,node_out in entry.get('outputs',{}).items():
  for key in ('videos','gifs','images'):
   for item in node_out.get(key,[]) or []:
    if isinstance(item,dict) and 'filename' in item: out.append({**item,'_node_id':node_id,'_kind':key})
 return out

try:
 requests.post(COMFY+'/free',json={'unload_models':True,'free_memory':True},timeout=30)
except Exception as e: print({'free_warning':repr(e)},flush=True)
print(json.dumps({'system':requests.get(COMFY+'/system_stats',timeout=10).json()['devices'][0]}),flush=True)
wf=json.loads(WORKFLOW.read_text())
name=upload(SHOT['path'])
wf['59']['inputs']['image']=name
wf['55']['inputs']['width']=432
wf['55']['inputs']['height']=768
wf['55']['inputs']['length']=25
wf['6']['inputs']['text']=SHOT['prompt']
wf['7']['inputs']['text']='text, subtitles, readable letters, watermark, logo, UI, hard cut, scene transition, horror, blood, attack, morphing animal anatomy, duplicated fins, distorted face, melted geometry, jitter, flicker, low quality, blurry, compression artifacts'
wf['3']['inputs']['seed']=SHOT['seed']
wf['3']['inputs']['steps']=12
wf['3']['inputs']['cfg']=4.0
wf['58']['inputs']['filename_prefix']=f"ways_shark_v27_wan22_5b_pilot/shot{SHOT['id']}_{SHOT['seed']}"
pid=queue(wf)
print(json.dumps({'queued':pid,'shot':SHOT['id'],'seed':SHOT['seed'],'workflow':str(WORKFLOW),'image':name}),flush=True)
entry=wait(pid)
items=outs(entry)
print(json.dumps({'outputs':items},indent=2),flush=True)
if not items: raise RuntimeError('no outputs')
r=requests.get(COMFY+'/view',params={'filename':items[0]['filename'],'subfolder':items[0].get('subfolder',''),'type':items[0].get('type','output')},timeout=600)
r.raise_for_status()
dest=OUT/f"shot{SHOT['id']}_wan22_5b_432x768_25f_seed{SHOT['seed']}.mp4"
dest.write_bytes(r.content)
meta={**SHOT,'prompt_id':pid,'uploaded_image':name,'comfy_output':items[0],'clip':str(dest)}
dest.with_suffix('.json').write_text(json.dumps(meta,indent=2,default=str))
print(json.dumps({'saved':str(dest),'bytes':dest.stat().st_size}),flush=True)
