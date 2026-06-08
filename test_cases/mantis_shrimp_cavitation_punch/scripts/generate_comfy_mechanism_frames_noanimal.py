from __future__ import annotations
import json, time, urllib.request, urllib.parse, uuid
from pathlib import Path
BASE='http://127.0.0.1:8188'
OUT=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch/assets/premium_mechanism_v17b_noanimal')
OUT.mkdir(parents=True, exist_ok=True)
CLIENT=str(uuid.uuid4())
negative='text, words, letters, labels, watermark, logo, diagram arrows, UI, border, full shrimp, shrimp face, eyes, legs, antennae, animal body, creature, malformed anatomy, toy, cartoon, cheap, low quality, blurry, noisy'
base='vertical 9:16 premium cinematic 3D scientific visualization, no text, no labels, no watermark, no arrows, no animal face, no full shrimp body, underwater macro high-speed physics scene, photorealistic water, volumetric blue light, black teal background, caption safe center, polished documentary visual'
items=[
('cavitation', base+', only an orange mantis-shrimp-like smasher club appendage entering from lower left toward a shell target, large translucent white blue vapor bubble forming at the club tip, premium 3D render, no creature body'),
('first_hit', base+', only orange smasher club appendage striking a hard shell target, intense soft white blue impact bloom and natural water distortion, premium 3D render, no creature body'),
('collapse', base+', only a translucent cavitation bubble imploding beside a shell target after impact, second shock burst of soft light and turbulent water, orange club edge barely visible, premium 3D render, no creature body'),
]
def post(path,data):
 req=urllib.request.Request(BASE+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'}); return json.load(urllib.request.urlopen(req,timeout=30))
def get(path): return json.load(urllib.request.urlopen(BASE+path,timeout=30))
def wf(prompt,prefix,seed):
 return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':'DreamShaperXL_Turbo_V2-SFW.safetensors'}},'2':{'class_type':'CLIPTextEncode','inputs':{'text':prompt,'clip':['1',1]}},'3':{'class_type':'CLIPTextEncode','inputs':{'text':negative,'clip':['1',1]}},'4':{'class_type':'EmptyLatentImage','inputs':{'width':768,'height':1344,'batch_size':1}},'5':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['2',0],'negative':['3',0],'latent_image':['4',0],'seed':seed,'steps':12,'cfg':2.4,'sampler_name':'dpmpp_2m','scheduler':'karras','denoise':1.0}},'6':{'class_type':'VAEDecode','inputs':{'samples':['5',0],'vae':['1',2]}},'7':{'class_type':'SaveImage','inputs':{'images':['6',0],'filename_prefix':prefix}}}
manifest=[]
for idx,(name,prompt) in enumerate(items):
 for variant in range(2):
  seed=915000+idx*211+variant*17; prefix=f'WAYS_mantis_v17b_{name}_{variant}'
  pid=post('/prompt',{'prompt':wf(prompt,prefix,seed),'client_id':CLIENT})['prompt_id']; print('queued',name,variant,pid)
  for _ in range(240):
   hist=get('/history/'+pid)
   if pid in hist:
    for out in hist[pid].get('outputs',{}).values():
     for im in out.get('images',[]):
      q=urllib.parse.urlencode({'filename':im['filename'],'subfolder':im.get('subfolder',''),'type':im.get('type','output')})
      data=urllib.request.urlopen(BASE+'/view?'+q,timeout=60).read(); local=OUT/im['filename']; local.write_bytes(data)
      manifest.append({'stage':name,'variant':variant,'seed':seed,'local_path':str(local),'prompt':prompt}); print('saved',local)
    break
   time.sleep(2)
  else: raise RuntimeError('timeout')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'out':str(OUT),'count':len(manifest)},indent=2))
