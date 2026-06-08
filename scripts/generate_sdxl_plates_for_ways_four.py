#!/usr/bin/env python3
from __future__ import annotations
import json, time, uuid, urllib.request, urllib.parse, shutil
from pathlib import Path
from PIL import Image
import requests
ROOT=Path('/mnt/c/dev/curious-shorts')
COMFY='http://127.0.0.1:8188'
NEG='text, letters, words, numbers, watermark, logo, UI, captions, subtitles, signature, low quality, blurry, distorted anatomy, extra limbs, horror, gore, blood, deformed, duplicate animal, malformed face, ugly, cartoon'
TOPICS={
'wombat_cube_poop':[
'realistic common wombat in Australian grassland, golden hour, premium natural history documentary photo, friendly educational tone, full body, caption safe dark negative space, vertical composition, cinematic, no text',
'realistic wombat near small brown cube shaped scat pellets on soil, tasteful educational nature documentary, premium photo realism, caption safe negative space, vertical 9:16, no text',
'cinematic science macro concept of soft organic intestinal tissue gently shaping cube-like pellets, educational documentary, realistic material, no labels, no text, caption safe',
'close documentary view of several small brown cube shaped wombat scat pellets on natural dirt with wombat blurred in background, premium macro, no text',
'realistic common wombat looking at camera in natural habitat, satisfying final hero shot, premium wildlife documentary, caption safe, no text'],
'octopus_three_hearts':[
'realistic octopus underwater on reef, premium natural history documentary photo, all arms anatomically attached, cinematic water particles, caption safe negative space, no text',
'realistic octopus side view underwater with subtle translucent scientific glow points on body suggesting two gill hearts, no labels, premium documentary, no text',
'realistic octopus crawling on seabed, body-centered subtle red glow point suggesting main heart, anatomy correct, premium underwater photo, no text',
'realistic octopus swimming gently through water, arms coherent and attached, cinematic blue water, premium documentary, caption safe, no text',
'realistic octopus crawling over reef floor, strong final wonder shot, premium natural history, no text, no labels'],
'tardigrade_survival_mode':[
'realistic tardigrade water bear microscope image, premium science documentary, translucent tiny animal, dark clean microscope background, caption safe, no text',
'realistic tardigrade curled into tiny tun survival state, microscope macro, dry texture, premium science documentary, no labels, no text',
'realistic microscope scene of tiny tardigrade in suspended dry pause state with particles, cinematic science image, no text',
'realistic tardigrade rehydrating in water droplet under microscope, premium science documentary, bubbles and shimmer, no text',
'realistic tardigrade water bear hero microscope shot, cute but scientifically believable, premium macro, no text'],
}

def post_json(path,payload,timeout=30):
 r=requests.post(COMFY+path,json=payload,timeout=timeout); r.raise_for_status(); return r.json()
def wait(pid,timeout=900):
 start=time.time()
 while time.time()-start<timeout:
  h=requests.get(f'{COMFY}/history/{pid}',timeout=30).json()
  if pid in h:
   st=h[pid].get('status',{})
   if st.get('status_str')=='error': raise RuntimeError(json.dumps(st.get('messages',[]),indent=2)[:4000])
   return h[pid]
  print(json.dumps({'waiting':round(time.time()-start,1),'prompt_id':pid}),flush=True); time.sleep(5)
 raise TimeoutError(pid)
def items(entry):
 out=[]
 for node,outd in entry.get('outputs',{}).items():
  for im in outd.get('images',[]) or []: out.append(im)
 return out
def dl(item,dest):
 r=requests.get(COMFY+'/view',params={'filename':item['filename'],'subfolder':item.get('subfolder',''),'type':item.get('type','output')},timeout=120); r.raise_for_status(); dest.write_bytes(r.content)
def workflow(prompt, seed, prefix):
 return {
  '1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':'DreamShaperXL_Turbo_V2-SFW.safetensors'}},
  '2':{'class_type':'CLIPTextEncode','inputs':{'text':prompt+', ultra realistic, sharp subject, cinematic lighting, phone-size readable focal object, no text','clip':['1',1]}},
  '3':{'class_type':'CLIPTextEncode','inputs':{'text':NEG,'clip':['1',1]}},
  '4':{'class_type':'EmptyLatentImage','inputs':{'width':832,'height':1472,'batch_size':1}},
  '5':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['2',0],'negative':['3',0],'latent_image':['4',0],'seed':seed,'steps':8,'cfg':2.0,'sampler_name':'dpmpp_sde','scheduler':'karras','denoise':1.0}},
  '6':{'class_type':'VAEDecode','inputs':{'samples':['5',0],'vae':['1',2]}},
  '7':{'class_type':'SaveImage','inputs':{'images':['6',0],'filename_prefix':prefix}}
 }
def main():
 try: post_json('/free',{'unload_models':True,'free_memory':True},timeout=30)
 except Exception as e: print({'free_warn':repr(e)})
 made=[]
 for ti,(slug,prompts) in enumerate(TOPICS.items()):
  outdir=ROOT/'test_cases'/slug/'assets'/'sdxl_wan_template_v01_plates'; outdir.mkdir(parents=True,exist_ok=True)
  for i,prompt in enumerate(prompts,1):
   dest=outdir/f'shot{i:02d}_{slug}_sdxl_plate.png'
   if dest.exists() and dest.stat().st_size>1000:
    made.append(str(dest)); continue
   wf=workflow(prompt, 910000+ti*100+i, f'ways_four/{slug}_shot{i:02d}')
   data=post_json('/prompt',{'prompt':wf,'client_id':str(uuid.uuid4())},timeout=60)
   if data.get('node_errors'): raise RuntimeError(json.dumps(data['node_errors'],indent=2)[:4000])
   pid=data['prompt_id']; print(json.dumps({'queued':slug,'shot':i,'pid':pid}),flush=True)
   entry=wait(pid); its=items(entry)
   if not its: raise RuntimeError('no image')
   dl(its[0],dest)
   Image.open(dest).verify()
   made.append(str(dest)); print(json.dumps({'saved':str(dest),'bytes':dest.stat().st_size}),flush=True)
 print(json.dumps({'made':made},indent=2))
if __name__=='__main__': main()
