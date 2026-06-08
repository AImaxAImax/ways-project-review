from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import subprocess, shutil, json, math, random

CASE=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT=CASE/'outputs/say_dog_v08_clean_variety'
FRAMES=OUT/'frames'; SRC=OUT/'src_frames'
VOICE=CASE/'outputs/auto_static_v01/voiceover.mp3'
VIDEO_DIR=CASE/'assets/source_commons_video'
W,H,FPS=1080,1920,24
for p in [OUT]: p.mkdir(parents=True,exist_ok=True)
for p in [FRAMES,SRC]:
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True)

# Extract only real Commons videos. Still plates are real Wikimedia photos.
for name,path in {'peacock':VIDEO_DIR/'peacock_mantis.webm','wide':VIDEO_DIR/'mantis_philippines.webm'}.items():
    d=SRC/name; d.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(path),'-vf','fps=24',str(d/'f_%05d.jpg')],check=True)
video_cache={}
def vframes(name):
    if name not in video_cache:
        video_cache[name]=[Image.open(p).convert('RGB') for p in sorted((SRC/name).glob('f_*.jpg'))]
    return video_cache[name]
photos={i:Image.open(CASE/f'assets/source_stills/source_{i:02d}.jpg').convert('RGB') for i in range(1,6)}

def cover(im,focus_x=.5,focus_y=.5,zoom=1.0):
    iw,ih=im.size; target=9/16
    crop_w=int(ih*target/zoom); crop_h=int(ih/zoom)
    if crop_w>iw:
        crop_w=iw; crop_h=int(iw/target)
    cx=int(iw*focus_x); cy=int(ih*focus_y)
    x=max(0,min(iw-crop_w,cx-crop_w//2)); y=max(0,min(ih-crop_h,cy-crop_h//2))
    return im.crop((x,y,x+crop_w,y+crop_h)).resize((W,H),Image.LANCZOS)

def grade(im):
    im=ImageEnhance.Color(im).enhance(1.06)
    im=ImageEnhance.Contrast(im).enhance(1.08)
    im=ImageEnhance.Brightness(im).enhance(.96)
    mask=Image.new('L',(W,H),0); d=ImageDraw.Draw(mask)
    d.ellipse((-250,100,W+250,H+90), fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(170))
    return Image.composite(im,Image.new('RGB',(W,H),(3,17,21)),mask)

def still(src,t,fx=.5,fy=.5,zoom0=1.1,zoom1=1.18,panx=0,pany=0):
    im=photos[src]
    z=zoom0+(zoom1-zoom0)*t
    fx=max(.05,min(.95,fx+panx*math.sin(t*math.pi)*.03))
    fy=max(.05,min(.95,fy+pany*math.sin(t*math.pi)*.03))
    return grade(cover(im,fx,fy,z))

def video(name,t,fx=.35,zoom=1.05,offset=0):
    arr=vframes(name); idx=int((offset*FPS+t*(len(arr)-1)*.72))%len(arr)
    return grade(cover(arr[idx],fx,.5,zoom))

def shade(im):
    out=im.convert('RGBA'); layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    for y in range(690,1180,10):
        a=int(max(0,34*(1-abs(y-930)/245)))
        d.rectangle((0,y,W,y+10),fill=(0,0,0,a))
    return Image.alpha_composite(out,layer).convert('RGB')

def bubbles(layer,cx,cy,t,seed=1,collapse=False,density=18,scale=.50,alpha=62):
    d=ImageDraw.Draw(layer,'RGBA'); rnd=random.Random(seed)
    for _ in range(density):
        ang=rnd.random()*math.tau
        dist=((1-t) if collapse else t)*(18+rnd.random()*130)*scale
        rr=(1.2+rnd.random()*8)*(1-.55*t if collapse else .38+.55*t)*scale
        al=int(alpha*(.45+.55*t if collapse else .55+.45*(1-abs(t-.55)))*(0.45+rnd.random()*.55))
        x=cx+math.cos(ang)*dist+rnd.uniform(-8,8); y=cy+math.sin(ang)*dist*.62+rnd.uniform(-6,6)
        if 0<x<W and 0<y<H: d.ellipse((x-rr,y-rr,x+rr,y+rr), outline=(235,255,255,al), width=1)

def flash(layer,cx,cy,t,peak=.3,strength=.35):
    p=max(0,1-abs(t-peak)/.12)
    if p<=0: return
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(3,0,-1):
        r=(32+k*27)*(.85+.3*p)
        d.ellipse((cx-r,cy-r*.46,cx+r,cy+r*.46), fill=(250,255,235,int(14*k*p*strength)))
    d.ellipse((cx-48*p,cy-24*p,cx+62*p,cy+30*p), fill=(255,255,232,int(50*p*strength)))

def ripple(layer,cx,cy,t,maxr=250,alpha=52,count=2):
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(count):
        r=maxr*(t*.86+k*.20)
        if 12<r<maxr:
            d.ellipse((cx-r,cy-r*.52,cx+r,cy+r*.52), outline=(220,250,255,int(alpha*(1-r/maxr))), width=3)

beats=[
 ('01_hook_flash','THIS SHRIMP PUNCH\\nMAKES WATER FLASH',3.92,'video','peacock',{'fx':.31,'zoom':1.03,'offset':0},'flash',(610,945)),
 ('02_club_speed','ITS CLUB MOVES\\nINSANELY FAST',3.91,'still',5,{'fx':.58,'fy':.48,'zoom0':1.08,'zoom1':1.22,'panx':1},'speed',(590,980)),
 ('03_cavitation','THAT FLASH\\nIS CAVITATION',3.92,'still',2,{'fx':.48,'fy':.52,'zoom0':1.10,'zoom1':1.18,'panx':-1},'cavitation',(615,965)),
 ('04_first_hit','THE PUNCH\\nHITS FIRST',3.91,'still',4,{'fx':.52,'fy':.49,'zoom0':1.12,'zoom1':1.21,'pany':-1},'impact',(585,975)),
 ('05_second_hit','THEN THE BUBBLE\\nCOLLAPSES',3.91,'still',3,{'fx':.50,'fy':.50,'zoom0':1.10,'zoom1':1.20,'panx':1},'collapse',(575,990)),
 ('06_high_speed','SCIENTISTS FILMED IT\\nIN HIGH SPEED',3.92,'montage',[1,4,5,2],{},'montage',(600,960)),
 ('07_not_just_prey','IT DOES NOT JUST\\nPUNCH PREY',3.92,'video','wide',{'fx':.32,'zoom':1.0,'offset':1},'clean',(560,1000)),
 ('08_water_punches','THE WATER\\nPUNCHES TOO',3.91,'video','peacock',{'fx':.38,'zoom':1.08,'offset':8},'water',(620,950)),
]

def base_frame(mode,src,params,t):
    if mode=='video': return video(src,t,**params)
    if mode=='still': return still(src,t,**params)
    # montage: hard cuts between real stills, no fake frame dividers
    seq=src; seg=min(len(seq)-1,int(t*len(seq))); local=(t*len(seq))%1
    return still(seq[seg],local,fx=.5,fy=.5,zoom0=1.08,zoom1=1.15,panx=(-1)**seg)

def make_frame(mode,src,params,kind,loc,t):
    im=base_frame(mode,src,params,t).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); cx,cy=loc
    if kind=='flash': flash(layer,cx,cy,t,.26,.50); bubbles(layer,cx,cy,min(1,t*1.1),seed=11,density=12,scale=.48,alpha=48); ripple(layer,cx,cy,max(0,(t-.25)/.75),230,38,2)
    elif kind=='speed': flash(layer,cx-80,cy+25,t,.42,.16)
    elif kind=='cavitation': bubbles(layer,cx,cy,min(1,t*1.05),seed=33,density=22,scale=.56,alpha=60); flash(layer,cx,cy,t,.50,.18)
    elif kind=='impact': flash(layer,cx,cy,t,.30,.38); ripple(layer,cx,cy,max(0,(t-.28)/.52),220,56,2)
    elif kind=='collapse': bubbles(layer,cx,cy,t,seed=55,collapse=True,density=22,scale=.60,alpha=68); ripple(layer,cx+10,cy+8,max(0,(t-.42)/.58),300,62,3)
    elif kind=='montage':
        if t>.45: ripple(layer,cx,cy,(t-.45)/.55,260,35,2)
    elif kind=='water': bubbles(layer,cx,cy,min(1,t*1.0),seed=88,density=12,scale=.52,alpha=50); bubbles(layer,cx+25,cy+10,max(0,(t-.35)/.65),seed=89,collapse=True,density=18,scale=.58,alpha=70); ripple(layer,cx+25,cy+10,max(0,(t-.35)/.65),330,76,3)
    return shade(Image.alpha_composite(im,layer))

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
for bi,(bid,cap,dur,mode,src,params,kind,loc) in enumerate(beats,1):
    n=round(dur*FPS); bm.append({'beat':bi,'id':bid,'caption':cap.replace('\\n',' / '),'mode':mode,'source':src,'visual_kind':kind,'frames':n,'strategy':'real video/photos only, varied sources/crops, low-opacity no-text effects'})
    for f in range(n):
        make_frame(mode,src,params,kind,loc,f/max(1,n-1)).save(FRAMES/f'frame_{idx:05d}.jpg',quality=94); idx+=1
(OUT/'beat_map_v08.json').write_text(json.dumps(bm,indent=2))
ass=OUT/'captions_say_dog_v08.ass'; write_ass(ass)
silent=OUT/'mantis_say_dog_v08_silent_1080.mp4'; master=OUT/'mantis_say_dog_v08_captioned_1080.mp4'; preview=OUT/'mantis_say_dog_v08_captioned_720.mp4'; contact=OUT/'contact_sheet_mantis_say_dog_v08.jpg'
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','17','-preset','medium',str(silent)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(VOICE),'-vf',f'ass={ass}','-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview),'-vf','fps=1,scale=270:480,tile=6x6','-frames:v','1','-update','1',str(contact)],check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size,bit_rate','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate,bit_rate','-of','json',str(preview)],text=True)
(OUT/'ffprobe_preview.json').write_text(probe)
(OUT/'README_QA.md').write_text(f'''# Mantis shrimp cavitation punch — v08 clean variety candidate

Status: internal review candidate.

Built after v07 proved cleaner but too repetitive. v08 mixes real Commons video with real Wikimedia source photos, varied crops, and very low-opacity no-text mechanism cues. No generated animal frames are used.

Outputs:
- Preview: `{preview}`
- Master: `{master}`
- Contact sheet: `{contact}`
- Beat map: `{OUT/'beat_map_v08.json'}`
''')
print(json.dumps({'preview':str(preview),'master':str(master),'contact_sheet':str(contact),'frames':idx,'ffprobe':json.loads(probe)},indent=2))
