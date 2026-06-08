#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import math, subprocess, json, shutil
ROOT=Path('/mnt/c/dev/curious-shorts')
CASE=ROOT/'test_cases/mantis_shrimp_cavitation_punch'
PLATES=CASE/'assets/wan_motion_v03_clean_plates'
OUT=CASE/'outputs/clean_source_motion_v03_proxy'
FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); shutil.rmtree(FRAMES,ignore_errors=True); FRAMES.mkdir()
W,H,FR,DUR=1080,1920,24,31.32
shots=[('01',0,3.92),('02',1,3.91),('03',2,3.92),('04',3,3.91),('05',4,3.91),('06',5,3.92),('07',6,3.92),('08',7,3.91)]
plates=[Image.open(PLATES/f'shot{i:02d}_clean_mantis_photo_plate.png').convert('RGB') for i in range(1,9)]

def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)

def cover_motion(im,t,shot_idx,local):
    # Full-frame motion proxy: no overlay graphics, no generated artifacts, no text.
    # Uses only crop drift + underwater refractive mesh warping + quick localized strike/recoil deformation.
    zoom=1.035 + 0.018*math.sin(local*math.pi)
    rw,rh=int(W*zoom),int(H*zoom)
    big=im.resize((rw,rh),Image.Resampling.LANCZOS)
    # small camera travel but not the only motion
    px=int((rw-W)*(0.5+0.35*math.sin(0.8*local+shot_idx)))
    py=int((rh-H)*(0.5+0.28*math.cos(0.9*local+shot_idx*.6)))
    frame=big.crop((px,py,px+W,py+H))
    # water refraction mesh, subtle and organic
    grid=18
    mesh=[]
    amp=3.5 + 3.0*math.sin(local*math.pi)**2
    # strike pulse for action beats, still as warping not overlay drawing
    strike=math.exp(-((local-0.42)/0.12)**2) if shot_idx in [0,1,3] else 0
    collapse=math.exp(-((local-0.56)/0.16)**2) if shot_idx in [2,4,7] else 0
    amp += 9*strike + 7*collapse
    for y in range(0,H,grid):
        for x in range(0,W,grid):
            x2=min(x+grid,W); y2=min(y+grid,H)
            cx=(x+x2)/2; cy=(y+y2)/2
            # general watery motion
            dx=amp*math.sin(cy*0.013 + local*5.4 + shot_idx*.9) + 2.2*math.sin(cx*0.006+local*2)
            dy=amp*.55*math.cos(cx*0.011 + local*4.7 + shot_idx*.5)
            # localized impact area on right/lower-middle: makes the image itself pulse/recoil
            dist=((cx-735)**2/180000 + (cy-1030)**2/240000)
            local_amp=math.exp(-dist)*(strike*22 + collapse*18)
            dx += local_amp*math.sin(local*18 + cy*.02)
            dy += local_amp*math.cos(local*17 + cx*.02)
            src=(x+dx,y+dy,x2+dx,y+dy,x2+dx,y2+dy,x+dx,y2+dy)
            mesh.append(((x,y,x2,y2),src))
    frame=frame.transform((W,H),Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
    # speed ramp blur around action moments, no added objects
    if strike+collapse>0.35:
        blur=frame.filter(ImageFilter.GaussianBlur(1.1*(strike+collapse)))
        frame=Image.blend(frame,blur,0.18)
    # subtle breathing contrast/light, no particles drawn
    frame=ImageEnhance.Contrast(frame).enhance(1.02+0.04*math.sin(local*math.pi))
    frame=ImageEnhance.Brightness(frame).enhance(0.97+0.04*math.sin(local*2*math.pi+shot_idx))
    return frame

idx=0; timeline=[]; t0=0
for shot_id,si,dur in shots:
    n=round(dur*FR)
    for j in range(n):
        local=j/max(1,n-1)
        im=cover_motion(plates[si],t0+j/FR,si,local)
        im.save(FRAMES/f'frame_{idx:05d}.jpg',quality=93)
        idx+=1
    timeline.append((shot_id,t0,t0+dur)); t0+=dur
# trim exact enough
clean=OUT/'clean_master.mp4'; cap=OUT/'publish_candidate_captioned.mp4'; prev=OUT/'discord_preview_captioned.mp4'; sheet=OUT/'contact_sheet.jpg'; ffp=OUT/'ffprobe_publish.json'
audio=CASE/'outputs/auto_static_v01/voiceover.mp3'; ass=CASE/'outputs/auto_static_v01/captions.ass'
subprocess.run(['ffmpeg','-y','-framerate',str(FR),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(clean)],check=True)
subprocess.run(['ffmpeg','-y','-i',str(clean),'-i',str(audio),'-vf',f"ass='{ass}'",'-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(cap)],check=True)
subprocess.run(['ffmpeg','-y','-i',str(cap),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','slow','-crf','23','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(prev)],check=True)
subprocess.run(['ffmpeg','-y','-i',str(cap),'-vf','fps=1/3,scale=270:480,tile=4x3:padding=8:margin=8:color=black','-frames:v','1','-update','1',str(sheet)],check=True)
with ffp.open('w') as f: subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(cap)],stdout=f,check=True)
manifest={'lane':'clean_source_motion_proxy','v02_rejection_fixed':['removed overlay/proof artifacts','removed graphic rings/labels/arrows/HUD','motion uses in-frame image/water deformation not objects on top'], 'limitation':'This is a fast proxy while Wan shark-style I2V v03 is rendering; it is cleaner but not final post-ready if motion still feels too synthetic.', 'outputs':{'master':str(cap.relative_to(CASE)),'preview':str(prev.relative_to(CASE)),'contact_sheet':str(sheet.relative_to(CASE))}}
(OUT/'render_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
