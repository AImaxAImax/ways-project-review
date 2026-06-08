#!/usr/bin/env python3
import json, time, urllib.request, urllib.parse, uuid, sys, shutil
from pathlib import Path

SERVER='127.0.0.1:8188'
CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/flying_snake_glide')
OUT=ROOT/'assets'/'comfy_sdxl_turbo_candidates_v01'
OUT.mkdir(parents=True, exist_ok=True)

def post(path, data):
    req=urllib.request.Request(f'http://{SERVER}{path}', data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def get_json(path):
    with urllib.request.urlopen(f'http://{SERVER}{path}', timeout=30) as r:
        return json.loads(r.read().decode())

def download_image(filename, subfolder='', folder_type='output', dest=None):
    params=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':folder_type})
    with urllib.request.urlopen(f'http://{SERVER}/view?{params}', timeout=60) as r:
        data=r.read()
    dest = dest or OUT/filename
    dest.write_bytes(data)
    return dest

def workflow(prompt, seed=1234, prefix='flying_snake'):
    neg='text, words, captions, watermark, logo, UI, labels, arrows, human, hands, wings, bird wings, feathers, insect wings, dragon, fantasy creature, deformed snake, two heads, extra heads, extra eyes, blurry, low quality, gore, scary horror'
    return {
      '1': {'class_type':'CheckpointLoaderSimple','inputs': {'ckpt_name':'sd_xl_turbo_1.0_fp16.safetensors'}},
      '2': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':prompt}},
      '3': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':neg}},
      '4': {'class_type':'EmptyLatentImage','inputs': {'width':768, 'height':1344, 'batch_size':1}},
      '5': {'class_type':'KSampler','inputs': {
        'model':['1',0], 'positive':['2',0], 'negative':['3',0], 'latent_image':['4',0],
        'seed':seed, 'steps':6, 'cfg':1.7, 'sampler_name':'euler', 'scheduler':'simple', 'denoise':1.0
      }},
      '6': {'class_type':'VAEDecode','inputs': {'samples':['5',0], 'vae':['1',2]}},
      '7': {'class_type':'SaveImage','inputs': {'images':['6',0], 'filename_prefix':prefix}}
    }

def run(prompt, seed=1234, prefix='flying_snake'):
    resp=post('/prompt', {'prompt': workflow(prompt, seed, prefix), 'client_id': CLIENT_ID})
    pid=resp['prompt_id']
    for _ in range(240):
        hist=get_json('/history/'+pid)
        if pid in hist:
            h=hist[pid]
            if h.get('status',{}).get('status_str') == 'error':
                raise RuntimeError(json.dumps(h.get('status'), indent=2))
            imgs=[]
            for node in h.get('outputs',{}).values():
                for im in node.get('images',[]):
                    dest=download_image(im['filename'], im.get('subfolder',''), im.get('type','output'))
                    imgs.append(str(dest))
            return imgs
        time.sleep(1)
    raise TimeoutError(pid)

STYLE='vertical 9:16 premium natural history documentary still, realistic flying snake gliding in rainforest canopy, full snake body visible, clear airborne action, educational YouTube Shorts visual, clean open space for editor-added captions, no text in image, no logos, no watermark, sharp cinematic wildlife photography'
SHOT_PROMPTS={
 '01_launch': STYLE + ', snake launching from a high tree branch into open air, branch visible on left, sky gap behind snake, instant read that snake is airborne',
 '02_no_wings': STYLE + ', airborne snake with no wings, full long body in S shape against blue sky and rainforest, no wings, no feathers, obvious real snake gliding',
 '03_flatten_body': STYLE + ', close side view of flying snake gliding, body looks wider and flattened like a ribbon, not a round coil, rainforest canopy below',
 '04_side_to_side': STYLE + ', flying snake gliding in an S shaped wave through the air between trees, body curves left and right, motion implied, full body visible',
 '05_tree_to_tree': STYLE + ', flying snake steering toward another tree branch, destination branch visible on right, snake airborne across open gap between trees'
}
if __name__=='__main__':
    count=int(sys.argv[1]) if len(sys.argv)>1 else 2
    manifest=[]
    base_seed=60741000
    for si,(shot,prompt) in enumerate(SHOT_PROMPTS.items(),1):
        for v in range(1,count+1):
            seed=base_seed+si*100+v
            prefix=f'{shot}_v{v:02d}'
            print('GENERATE', prefix, seed, flush=True)
            try:
                imgs=run(prompt, seed, prefix)
                for img in imgs:
                    manifest.append({'shot':shot,'variant':v,'seed':seed,'prompt':prompt,'file':img})
            except Exception as e:
                manifest.append({'shot':shot,'variant':v,'seed':seed,'prompt':prompt,'error':str(e)})
                print('ERROR', prefix, e, flush=True)
                raise
    mf=ROOT/'outputs'/'gate2_plate_qc'/'comfy_candidates_manifest_v01.json'
    mf.parent.mkdir(parents=True, exist_ok=True)
    mf.write_text(json.dumps(manifest,indent=2))
    print(json.dumps({'count':len(manifest),'manifest':str(mf),'out_dir':str(OUT)},indent=2))
