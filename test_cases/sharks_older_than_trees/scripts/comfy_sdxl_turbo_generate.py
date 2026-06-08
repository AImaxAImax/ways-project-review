#!/usr/bin/env python3
import json, time, urllib.request, urllib.parse, uuid, sys
from pathlib import Path

SERVER='127.0.0.1:8188'
CLIENT_ID=str(uuid.uuid4())
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
OUT=ROOT/'assets'/'comfy_sdxl_turbo_v1'
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

def workflow(prompt, seed=1234, prefix='sharks_smoke'):
    neg='text, words, captions, watermark, logo, gore, blood, scary teeth, horror, distorted animal, deformed, blurry, low quality, extra fins, extra eyes'
    return {
      '1': {'class_type':'CheckpointLoaderSimple','inputs': {'ckpt_name':'sd_xl_turbo_1.0_fp16.safetensors'}},
      '2': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':prompt}},
      '3': {'class_type':'CLIPTextEncode','inputs': {'clip':['1',1], 'text':neg}},
      '4': {'class_type':'EmptyLatentImage','inputs': {'width':768, 'height':1344, 'batch_size':1}},
      '5': {'class_type':'KSampler','inputs': {
        'model':['1',0], 'positive':['2',0], 'negative':['3',0], 'latent_image':['4',0],
        'seed':seed, 'steps':5, 'cfg':1.5, 'sampler_name':'euler', 'scheduler':'simple', 'denoise':1.0
      }},
      '6': {'class_type':'VAEDecode','inputs': {'samples':['5',0], 'vae':['1',2]}},
      '7': {'class_type':'SaveImage','inputs': {'images':['6',0], 'filename_prefix':prefix}}
    }

def run(prompt, seed=1234, prefix='sharks_smoke'):
    resp=post('/prompt', {'prompt': workflow(prompt, seed, prefix), 'client_id': CLIENT_ID})
    pid=resp['prompt_id']
    for _ in range(180):
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

if __name__=='__main__':
    prompt=sys.argv[1] if len(sys.argv)>1 else 'vertical 9:16 cinematic soft 3D educational animation still, ancient shark silhouette gliding calmly through prehistoric blue green ocean, sunbeams, floating particles, premium family science YouTube Shorts visual, natural history museum quality, no text'
    imgs=run(prompt, seed=int(time.time())%100000000, prefix='sharks_smoke')
    print(json.dumps(imgs, indent=2))
