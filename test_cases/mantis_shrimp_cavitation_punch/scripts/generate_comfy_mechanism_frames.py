from __future__ import annotations
import json, time, urllib.request, urllib.parse, uuid
from pathlib import Path

BASE='http://127.0.0.1:8188'
OUT=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch/assets/premium_mechanism_v17')
OUT.mkdir(parents=True, exist_ok=True)
CLIENT=str(uuid.uuid4())

negative='text, words, letters, captions, labels, watermark, logo, diagram arrows, UI, frame border, cheap cartoon, toy, malformed shrimp, extra limbs, inaccurate anatomy, low quality, blurry, noisy, jpeg artifacts'
base_prompt='vertical 9:16 premium cinematic science documentary illustration, no text, no labels, no watermark, underwater macro high speed photography style, realistic water particles, dramatic volumetric light, clean center area for captions, high detail, polished, photoreal, no arrows, no typography'
items=[
 ('cavitation', base_prompt+', mantis shrimp smasher club near a shell target, bright white blue vapor cavitation bubble forming at the club tip, orange club partially visible, shell target, real underwater macro look'),
 ('first_hit', base_prompt+', mantis shrimp smasher club impacting a hard shell target, soft bright white blue impact bloom and pressure distortion in water, orange club partly visible, nature documentary high speed moment'),
 ('collapse', base_prompt+', cavitation bubble collapsing after mantis shrimp strike near a shell, second shock burst of light and water distortion, orange mantis shrimp club partly visible, premium scientific visual'),
]

def post(path, data):
    req=urllib.request.Request(BASE+path, data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=30))

def get(path):
    return json.load(urllib.request.urlopen(BASE+path, timeout=30))

def workflow(prompt, prefix, seed):
    return {
      '1': {'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':'DreamShaperXL_Turbo_V2-SFW.safetensors'}},
      '2': {'class_type':'CLIPTextEncode','inputs':{'text':prompt,'clip':['1',1]}},
      '3': {'class_type':'CLIPTextEncode','inputs':{'text':negative,'clip':['1',1]}},
      '4': {'class_type':'EmptyLatentImage','inputs':{'width':768,'height':1344,'batch_size':1}},
      '5': {'class_type':'KSampler','inputs':{'model':['1',0],'positive':['2',0],'negative':['3',0],'latent_image':['4',0],'seed':seed,'steps':10,'cfg':2.0,'sampler_name':'dpmpp_2m','scheduler':'karras','denoise':1.0}},
      '6': {'class_type':'VAEDecode','inputs':{'samples':['5',0],'vae':['1',2]}},
      '7': {'class_type':'SaveImage','inputs':{'images':['6',0],'filename_prefix':prefix}},
    }

manifest=[]
for idx,(name,prompt) in enumerate(items):
    seed=804200+idx*101
    prefix=f'WAYS_mantis_v17_{name}'
    res=post('/prompt', {'prompt':workflow(prompt,prefix,seed),'client_id':CLIENT})
    pid=res['prompt_id']; print('queued',name,pid)
    for _ in range(240):
        hist=get('/history/'+pid)
        if pid in hist:
            outputs=hist[pid].get('outputs',{})
            imgs=[]
            for node,out in outputs.items():
                for im in out.get('images',[]):
                    imgs.append(im)
            for im in imgs:
                q=urllib.parse.urlencode({'filename':im['filename'],'subfolder':im.get('subfolder',''),'type':im.get('type','output')})
                data=urllib.request.urlopen(BASE+'/view?'+q,timeout=60).read()
                local=OUT/im['filename']
                local.write_bytes(data)
                manifest.append({'stage':name,'prompt_id':pid,'seed':seed,'filename':im['filename'],'local_path':str(local),'prompt':prompt})
                print('saved',local)
            break
        time.sleep(2)
    else:
        raise RuntimeError('timeout '+pid)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'out':str(OUT),'count':len(manifest)},indent=2))
