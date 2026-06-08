from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import subprocess, shutil, json, math, random

CASE=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT=CASE/'outputs/say_dog_v09_generated_hybrid'
FRAMES=OUT/'frames'; SRC=OUT/'src_frames'
VOICE=CASE/'outputs/auto_static_v01/voiceover.mp3'
GEN=CASE/'assets/generated_frames_v09_img2img/outputs'
VIDEO_DIR=CASE/'assets/source_commons_video'
W,H,FPS=1080,1920,24
for p in [OUT]: p.mkdir(parents=True,exist_ok=True)
for p in [FRAMES,SRC]:
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True)

# Real source video for context/high-speed beat. Generated frames are img2img from real Wikimedia stills.
for name,path in {'peacock':VIDEO_DIR/'peacock_mantis.webm','wide':VIDEO_DIR/'mantis_philippines.webm'}.items():
    d=SRC/name; d.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(path),'-vf','fps=24',str(d/'f_%05d.jpg')],check=True)
video_cache={}
def vframes(name):
    if name not in video_cache:
        video_cache[name]=[Image.open(p).convert('RGB') for p in sorted((SRC/name).glob('f_*.jpg'))]
    return video_cache[name]

generated={
 'hook': GEN/'hook_flash_v1_den0.22_seed2006107646.png',
 'speed': GEN/'club_speed_v1_den0.22_seed391863842.png',
 'cavitation': GEN/'cavitation_bubbles_v1_den0.22_seed3993534475.png',
 'impact': GEN/'hook_flash_v2_den0.32_seed3424188944.png',
 'collapse': GEN/'bubble_collapse_v1_den0.22_seed2314200666.png',
 'water': GEN/'final_water_punch_v1_den0.22_seed3272143140.png',
}
photos={k:Image.open(v).convert('RGB') for k,v in generated.items()}

beats=[
 ('01_hook_flash','THIS SHRIMP PUNCH\\nMAKES WATER FLASH',3.92,'gen','hook','flash',(610,970)),
 ('02_club_speed','ITS CLUB MOVES\\nINSANELY FAST',3.91,'gen','speed','speed',(575,990)),
 ('03_cavitation','THAT FLASH\\nIS CAVITATION',3.92,'gen','cavitation','cavitation',(600,1010)),
 ('04_first_hit','THE PUNCH\\nHITS FIRST',3.91,'gen','impact','impact',(600,980)),
 ('05_second_hit','THEN THE BUBBLE\\nCOLLAPSES',3.91,'gen','collapse','collapse',(570,1040)),
 ('06_high_speed','SCIENTISTS FILMED IT\\nIN HIGH SPEED',3.92,'video','peacock','replay',(600,960)),
 ('07_not_just_prey','IT DOES NOT JUST\\nPUNCH PREY',3.92,'video','wide','clean',(560,1000)),
 ('08_water_punches','THE WATER\\nPUNCHES TOO',3.91,'gen','water','water',(615,1000)),
]

def cover(im,fx=.5,fy=.5,zoom=1.0):
    iw,ih=im.size; target=9/16
    cw=int(ih*target/zoom); ch=int(ih/zoom)
    if cw>iw: cw=iw; ch=int(iw/target)
    cx=int(iw*fx); cy=int(ih*fy); x=max(0,min(iw-cw,cx-cw//2)); y=max(0,min(ih-ch,cy-ch//2))
    return im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.LANCZOS)

def grade(im):
    im=ImageEnhance.Color(im).enhance(1.04)
    im=ImageEnhance.Contrast(im).enhance(1.08)
    im=ImageEnhance.Brightness(im).enhance(.96)
    mask=Image.new('L',(W,H),0); d=ImageDraw.Draw(mask)
    d.ellipse((-245,90,W+245,H+90),fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(170))
    return Image.composite(im,Image.new('RGB',(W,H),(3,16,20)),mask)

def gen_base(key,t):
    im=photos[key]
    # Generated frames are already 9:16. Keep zoom conservative to avoid exposing artifacts.
    zoom=1.00+0.055*t
    iw,ih=im.size; cw=int(iw/zoom); ch=int(ih/zoom)
    pan=(math.sin(t*math.pi)-.5)*.018
    x=max(0,min(iw-cw,int((iw-cw)*(0.5+pan)))); y=max(0,min(ih-ch,int((ih-ch)*.5)))
    return grade(im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.LANCZOS))

def video_base(name,t):
    arr=vframes(name); idx=int(t*(len(arr)-1)*.72)%len(arr)
    fx=.34 if name=='peacock' else .32
    return grade(cover(arr[idx],fx,.5,1.05 if name=='peacock' else 1.0))

def bubbles(layer,cx,cy,t,seed=1,collapse=False,density=10,scale=.42,alpha=42):
    d=ImageDraw.Draw(layer,'RGBA'); rnd=random.Random(seed)
    for _ in range(density):
        ang=rnd.random()*math.tau; dist=((1-t) if collapse else t)*(18+rnd.random()*110)*scale
        rr=(1+rnd.random()*6)*(1-.55*t if collapse else .4+.55*t)*scale
        al=int(alpha*(.45+.55*t if collapse else .55+.45*(1-abs(t-.55)))*(0.5+rnd.random()*.5))
        x=cx+math.cos(ang)*dist+rnd.uniform(-6,6); y=cy+math.sin(ang)*dist*.62+rnd.uniform(-5,5)
        if 0<x<W and 0<y<H: d.ellipse((x-rr,y-rr,x+rr,y+rr),outline=(235,255,255,al),width=1)

def flash(layer,cx,cy,t,peak=.3,strength=.24):
    p=max(0,1-abs(t-peak)/.11)
    if p<=0: return
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(2,0,-1):
        r=(35+k*28)*(.85+.3*p)
        d.ellipse((cx-r,cy-r*.46,cx+r,cy+r*.46),fill=(250,255,235,int(12*k*p*strength)))

def ripple(layer,cx,cy,t,maxr=250,alpha=40,count=2):
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(count):
        r=maxr*(t*.86+k*.22)
        if 12<r<maxr: d.ellipse((cx-r,cy-r*.52,cx+r,cy+r*.52),outline=(220,250,255,int(alpha*(1-r/maxr))),width=3)

def shade(im):
    out=im.convert('RGBA'); layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    for y in range(690,1180,10):
        a=int(max(0,34*(1-abs(y-930)/245)))
        d.rectangle((0,y,W,y+10),fill=(0,0,0,a))
    return Image.alpha_composite(out,layer).convert('RGB')

def make_frame(mode,key,kind,loc,t):
    im=(gen_base(key,t) if mode=='gen' else video_base(key,t)).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); cx,cy=loc
    # Very low opacity accents only, because selected frames already carry most of the visual.
    if kind=='flash': ripple(layer,cx,cy,max(0,(t-.24)/.76),230,28,2)
    elif kind=='speed': flash(layer,cx-70,cy,t,.45,.10)
    elif kind=='cavitation': bubbles(layer,cx,cy,min(1,t*1.05),seed=3,density=9,alpha=30)
    elif kind=='impact': flash(layer,cx,cy,t,.30,.18); ripple(layer,cx,cy,max(0,(t-.28)/.52),220,36,2)
    elif kind=='collapse': bubbles(layer,cx,cy,t,seed=5,collapse=True,density=12,alpha=38); ripple(layer,cx+8,cy+8,max(0,(t-.42)/.58),280,42,2)
    elif kind=='replay': ripple(layer,cx,cy,t,260,28,2)
    elif kind=='water': ripple(layer,cx+18,cy+10,max(0,(t-.30)/.70),330,55,3)
    im=Image.alpha_composite(im,layer)
    return shade(im)

def write_ass(path):
    def ts(t): return f"{int(t//3600)}:{int((t%3600)//60):02d}:{t%60:05.2f}"
    head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,102,&H00FFFFFF,&H0000D7FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,3,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    cur=0; lines=[]
    for _,cap,dur,*_ in beats:
        a,b=cap.split('\\n')
        lines.append(f"Dialogue: 0,{ts(cur)},{ts(cur+dur)},Caption,,0,0,0,,{{\\c&H0000D7FF&}}{a}{{\\c&H00FFFFFF&}}\\N{b}")
        cur+=dur
    path.write_text(head+'\n'.join(lines)+'\n')

idx=0; bm=[]
for bi,(bid,cap,dur,mode,key,kind,loc) in enumerate(beats,1):
    n=round(dur*FPS); bm.append({'beat':bi,'id':bid,'caption':cap.replace('\\n',' / '),'mode':mode,'source':str(generated.get(key,key)),'kind':kind,'frames':n,'strategy':'selected img2img generated mechanism frame + real Commons video context, no text'})
    for f in range(n): make_frame(mode,key,kind,loc,f/max(1,n-1)).save(FRAMES/f'frame_{idx:05d}.jpg',quality=94); idx+=1
(OUT/'beat_map_v09.json').write_text(json.dumps(bm,indent=2))
ass=OUT/'captions_say_dog_v09.ass'; write_ass(ass)
silent=OUT/'mantis_say_dog_v09_silent_1080.mp4'; master=OUT/'mantis_say_dog_v09_captioned_1080.mp4'; preview=OUT/'mantis_say_dog_v09_captioned_720.mp4'; contact=OUT/'contact_sheet_mantis_say_dog_v09.jpg'
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','17','-preset','medium',str(silent)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(VOICE),'-vf',f'ass={ass}','-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview),'-vf','fps=1,scale=270:480,tile=6x6','-frames:v','1','-update','1',str(contact)],check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size,bit_rate','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate,bit_rate','-of','json',str(preview)],text=True)
(OUT/'ffprobe_preview.json').write_text(probe)
(OUT/'README_QA.md').write_text(f'''# Mantis shrimp cavitation punch — v09 generated hybrid

Status: internal generated-frame experiment candidate.

This uses locally generated img2img frames for mechanism beats, anchored to real Wikimedia source stills to reduce the fake-anatomy problem from txt2img. It keeps real Commons video for context beats. No non-caption text.

Outputs:
- Preview: `{preview}`
- Master: `{master}`
- Contact sheet: `{contact}`
- Beat map: `{OUT/'beat_map_v09.json'}`
''')
print(json.dumps({'preview':str(preview),'master':str(master),'contact_sheet':str(contact),'frames':idx,'ffprobe':json.loads(probe)},indent=2))
