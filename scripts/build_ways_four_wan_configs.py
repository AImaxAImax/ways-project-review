#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT=Path('/mnt/c/dev/curious-shorts')
WORKFLOW='/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json'
NEG='text, subtitles, readable letters, watermark, logo, UI, hard cut, scene transition, horror, blood, attack, morphing animal anatomy, duplicated limbs, detached tentacles, distorted face, melted geometry, jitter, flicker, low quality, blurry, compression artifacts'
DATA={
 'saturn_hexagon_storm': {'plates':'assets/wan_template_v01_plates','captions':['SATURN HAS A\nHEXAGON STORM','IT IS A REAL\nJET STREAM','EACH SIDE IS WIDER\nTHAN EARTH','STORMS KEEP\nSPINNING INSIDE','A STRANGE SHAPE\nMADE OF WEATHER'], 'prompt':'premium NASA Cassini science documentary image-to-video. Preserve exact Saturn polar storm imagery and hexagon geometry, slow orbital camera creep, gentle cloud drift, atmospheric shimmer, no text, no labels, no logos, no scene cut.'},
 'wombat_cube_poop': {'plates':'assets/sdxl_wan_template_v01_plates','captions':['WOMBATS POOP\nCUBES','NOT PERFECT\nTOY BLOCKS','THE SHAPE FORMS\nINSIDE','CORNERS BEFORE\nLANDING','BATHROOM FACT\nPLUS PHYSICS'], 'prompt':'premium natural-history documentary image-to-video from the exact wombat still. Preserve wombat anatomy and composition. Add subtle true motion: slow camera creep, grass movement, fur movement, dust motes. Preserve cube-scat props if present. No text, no logos, no morphing, no scene cut.'},
 'octopus_three_hearts': {'plates':'assets/sdxl_wan_template_v01_plates','captions':['AN OCTOPUS HAS\nTHREE HEARTS','TWO PUSH THROUGH\nTHE GILLS','ONE POWERS\nTHE BODY','SWIMMING SLOWS\nONE DOWN','CRAWLING CAN\nBE EASIER'], 'prompt':'premium underwater documentary image-to-video from the exact octopus still. Preserve octopus anatomy, all arms connected to body, realistic underwater style. Add subtle true motion: water particles, gentle arm sway, slow camera creep, soft light shimmer. No detached tentacles, no text, no logos, no scene cut.'},
 'tardigrade_survival_mode': {'plates':'assets/sdxl_wan_template_v01_plates','captions':['TARDIGRADES CAN\nPAUSE THEIR BODIES','TOO DRY?\nTINY TUN','METABOLISM DROPS\nLIKE PAUSE','WATER RETURNS\nTHEY WAKE UP','NATURE’S STRANGEST\nSURVIVAL TRICK'], 'prompt':'premium microscope science documentary image-to-video from the exact tardigrade still. Preserve water bear body shape and microscope texture. Add subtle true motion: microscope focus breathing, tiny particles, water shimmer, slow parallax. No text, no labels, no logos, no morphing, no scene cut.'}
}
weights=[.9,1.05,1.15,1.1,1.0]
def duration(path):
 return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],text=True).strip())
def main():
 made=[]
 for idx,(slug,d) in enumerate(DATA.items()):
  proj=ROOT/'test_cases'/slug; vo=proj/'outputs/wan22_template_v01/voiceover.mp3'
  dur=duration(vo); total=sum(weights); shots=[]
  for i,cap in enumerate(d['captions'],1):
   ext='jpg' if slug=='saturn_hexagon_storm' else 'png'
   filename = f"shot{i:02d}_{slug}_" + ('plate.jpg' if slug=='saturn_hexagon_storm' else 'sdxl_plate.png')
   plate=proj/d['plates']/filename
   if not plate.exists():
    # fallback for prepared real tardigrade naming
    matches=sorted((proj/d['plates']).glob(f'shot{i:02d}_*'))
    if not matches: raise FileNotFoundError(plate)
    plate=matches[0]
   shots.append({'id':f'{i:02d}','image':str(plate.relative_to(proj)),'duration':round(dur*weights[i-1]/total,3),'caption':cap,'seed':960000+idx*100+i,'prompt':d['prompt']})
  cfg={'project_root':str(proj),'slug':slug,'output_dir':'outputs/wan22_template_v01','voiceover':'outputs/wan22_template_v01/voiceover.mp3','workflow':WORKFLOW,'comfy_url':'http://127.0.0.1:8188','negative_prompt':NEG,'render_settings':{'fps':24,'wan_width':432,'wan_height':768,'wan_length_frames':25,'master_width':1080,'master_height':1920,'master_crf':18,'audio_bitrate':'160k','audio_sample_rate':48000,'preview_width':720,'preview_height':1280,'preview_crf':24,'preview_audio_bitrate':'96k'},'workflow_overrides':{'39.inputs.vae_name':'wan_2.1_vae.safetensors'},'required_vae':'wan_2.1_vae.safetensors','qa_gate':['actual I2V motion','no generated text/logos','captioned final polish generated','every shot >=8/10 visual QA','audio stream present'],'shots':shots}
  out=proj/'render_wan22_harness_config.json'; out.write_text(json.dumps(cfg,indent=2)+'\n'); made.append(str(out))
 print(json.dumps({'configs':made},indent=2))
if __name__=='__main__': main()
