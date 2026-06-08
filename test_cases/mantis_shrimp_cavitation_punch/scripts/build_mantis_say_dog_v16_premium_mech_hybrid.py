from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
import subprocess, shutil, json, math, random

CASE=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT=CASE/'outputs/say_dog_v16_premium_mech_hybrid'
FRAMES=OUT/'frames'; SRC=OUT/'src_frames'
VOICE=CASE/'outputs/auto_static_v01/voiceover.mp3'
VIDEO_DIR=CASE/'assets/source_commons_video'
W,H,FPS=1080,1920,24
for p in [OUT]: p.mkdir(parents=True,exist_ok=True)
for p in [FRAMES,SRC]:
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True)

for name,path in {'peacock':VIDEO_DIR/'peacock_mantis.webm','wide':VIDEO_DIR/'mantis_philippines.webm'}.items():
    d=SRC/name; d.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(path),'-vf','fps=24',str(d/'f_%05d.jpg')],check=True)

video_cache={}
def vframes(name):
    if name not in video_cache:
        video_cache[name]=[Image.open(p).convert('RGB') for p in sorted((SRC/name).glob('f_*.jpg'))]
    return video_cache[name]

def load_photo(i):
    full=CASE/f'assets/source_stills_fullres/source_{i:02d}_full.jpg'
    fallback=CASE/f'assets/source_stills/source_{i:02d}.jpg'
    return Image.open(full if full.exists() else fallback).convert('RGB')
photos={i:load_photo(i) for i in range(1,6)}

def cover(im,focus_x=.5,focus_y=.5,zoom=1.0):
    iw,ih=im.size; target=9/16
    crop_w=int(ih*target/zoom); crop_h=int(ih/zoom)
    if crop_w>iw:
        crop_w=iw; crop_h=int(iw/target)
    cx=int(iw*focus_x); cy=int(ih*focus_y)
    x=max(0,min(iw-crop_w,cx-crop_w//2)); y=max(0,min(ih-crop_h,cy-crop_h//2))
    return im.crop((x,y,x+crop_w,y+crop_h)).resize((W,H),Image.LANCZOS)

def grade(im):
    im=ImageEnhance.Color(im).enhance(1.07)
    im=ImageEnhance.Contrast(im).enhance(1.10)
    im=ImageEnhance.Brightness(im).enhance(.95)
    mask=Image.new('L',(W,H),0); d=ImageDraw.Draw(mask)
    d.ellipse((-250,80,W+250,H+100), fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(170))
    return Image.composite(im,Image.new('RGB',(W,H),(2,14,18)),mask)

def still(src,t,fx=.5,fy=.5,zoom0=1.10,zoom1=1.18,panx=0,pany=0):
    im=photos[src]
    z=zoom0+(zoom1-zoom0)*t
    fx=max(.05,min(.95,fx+panx*math.sin(t*math.pi)*.025))
    fy=max(.05,min(.95,fy+pany*math.sin(t*math.pi)*.025))
    return grade(cover(im,fx,fy,z))

def video(name,t,fx=.35,zoom=1.05,offset=0,speed=.72):
    arr=vframes(name); idx=int((offset*FPS+t*(len(arr)-1)*speed))%len(arr)
    return grade(cover(arr[idx],fx,.5,zoom))

def mechanism_frame(stage,t):
    # Premium-looking no-text mechanism plate: close-up, full-frame, no labels/cards/rings/thin lines.
    bg=Image.new('RGB',(W,H),(4,15,22))
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    for y in range(H):
        a=y/H
        col=(int(4+8*a), int(18+45*(1-a)), int(26+64*(1-a)))
        d.line((0,y,W,y), fill=(*col,255))
    # soft depth texture
    rnd=random.Random(1701)
    for _ in range(140):
        x=rnd.randrange(W); y=rnd.randrange(H); r=rnd.uniform(1.0,5.0); al=rnd.randrange(7,22)
        d.ellipse((x-r,y-r,x+r,y+r), fill=(155,215,225,al))
    cx,cy=560,980
    # organic shell/target, large and close, intentionally not diagram-text
    d.ellipse((cx+150,cy-145,cx+520,cy+210), fill=(170,126,82,175))
    d.ellipse((cx+205,cy-100,cx+480,cy+180), fill=(75,55,44,150))
    d.arc((cx+195,cy-115,cx+495,cy+185), 200, 350, fill=(236,190,110,80), width=10)
    # broad smasher club sweeps in; fills frame enough to read on phone
    ease=1-(1-min(1,t))**3
    head_x=cx-300 + 430*ease
    head_y=cy+120 - 75*math.sin(t*math.pi)
    d.line((head_x-460,head_y+250,head_x+65,head_y-4), fill=(255,115,25,220), width=58)
    d.line((head_x-430,head_y+218,head_x+45,head_y-18), fill=(255,225,72,185), width=24)
    d.ellipse((head_x+25,head_y-38,head_x+125,head_y+45), fill=(255,191,62,205))
    d.ellipse((head_x+45,head_y-22,head_x+112,head_y+30), fill=(250,124,35,200))
    if stage=='cavitation':
        b=max(0,min(1,(t-.12)/.80)); rr=65+240*b
        # growing vapor cavity, big and soft, no outline
        d.ellipse((cx+120-rr,cy-rr*.55,cx+120+rr,cy+rr*.55), fill=(185,236,255,int(42+58*(1-abs(b-.55)))))
        d.ellipse((cx+120-rr*.62,cy-rr*.32,cx+120+rr*.62,cy+rr*.32), fill=(5,28,40,118))
        d.ellipse((cx+40,cy-120,cx+250,cy+75), fill=(255,255,220,int(42*b)))
    elif stage=='first_hit':
        hit=max(0,1-abs(t-.48)/.24)
        # impact bloom and pressure plume, soft filled shapes only
        d.ellipse((cx+150-280*hit,cy-135*hit,cx+150+330*hit,cy+135*hit), fill=(255,246,210,int(84*hit)))
        d.ellipse((cx+230-190*hit,cy-90*hit,cx+230+460*hit,cy+95*hit), fill=(170,232,255,int(54*hit)))
        d.ellipse((cx+260-100*hit,cy-48*hit,cx+260+245*hit,cy+50*hit), fill=(6,25,38,int(38*hit)))
    elif stage=='collapse':
        b=max(0,min(1,t)); rr=280*(1-b)+46
        d.ellipse((cx+145-rr,cy-rr*.55,cx+145+rr,cy+rr*.55), fill=(150,230,255,int(58*(1-b)+20)))
        d.ellipse((cx+145-rr*.45,cy-rr*.25,cx+145+rr*.45,cy+rr*.25), fill=(4,22,34,int(118*(1-b)+30)))
        snap=max(0,1-abs(t-.68)/.20)
        d.ellipse((cx+150-410*snap,cy-180*snap,cx+150+520*snap,cy+185*snap), fill=(255,238,192,int(68*snap)))
    layer=layer.filter(ImageFilter.GaussianBlur(2))
    out=Image.alpha_composite(bg.convert('RGBA'),layer).convert('RGB')
    out=ImageEnhance.Color(out).enhance(1.12)
    out=ImageEnhance.Contrast(out).enhance(1.14)
    return shade(out)

def shade(im):
    out=im.convert('RGBA'); layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    for y in range(680,1190,10):
        a=int(max(0,40*(1-abs(y-935)/250)))
        d.rectangle((0,y,W,y+10),fill=(0,0,0,a))
    # subtle top/bottom vignette
    for y in range(H):
        a=int(34*(abs(y-H/2)/(H/2))**2)
        if a: d.line((0,y,W,y),fill=(0,0,0,a))
    return Image.alpha_composite(out,layer).convert('RGB')

def bubble_cluster(layer,cx,cy,t,seed=1,collapse=False,density=24,scale=.58,alpha=72):
    d=ImageDraw.Draw(layer,'RGBA'); rnd=random.Random(seed)
    for _ in range(density):
        ang=rnd.random()*math.tau
        travel=((1-t) if collapse else t)
        dist=travel*(16+rnd.random()*150)*scale
        rr=(1.0+rnd.random()*9)*(1-.58*t if collapse else .30+.70*t)*scale
        al=int(alpha*(.50+.50*t if collapse else .50+.50*(1-abs(t-.52)))*(0.42+rnd.random()*.58))
        x=cx+math.cos(ang)*dist+rnd.uniform(-7,7); y=cy+math.sin(ang)*dist*.56+rnd.uniform(-5,5)
        if 0<x<W and 0<y<H:
            d.ellipse((x-rr,y-rr,x+rr,y+rr),outline=(235,255,255,al),width=1)
            if rr>3: d.point((x-rr*.25,y-rr*.25),fill=(255,255,255,min(255,al+40)))

def flash(layer,cx,cy,t,peak=.28,strength=.45):
    p=max(0,1-abs(t-peak)/.105)
    if p<=0: return
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(4,0,-1):
        r=(22+k*30)*(.75+.35*p)
        d.ellipse((cx-r,cy-r*.45,cx+r,cy+r*.45), fill=(245,255,235,int(11*k*p*strength)))
    d.ellipse((cx-45*p,cy-20*p,cx+60*p,cy+24*p), fill=(255,255,235,int(52*p*strength)))

def soft_water_flash(layer,cx,cy,t,peak=.45,strength=.16):
    # camera-like soft bloom, no outlines/no circles/no diagram cards
    p=max(0,1-abs(t-peak)/.18)
    if p<=0: return
    glow=Image.new('RGBA',(W,H),(0,0,0,0))
    gd=ImageDraw.Draw(glow,'RGBA')
    for k in range(6,0,-1):
        r=(32+k*36)*(.8+.25*p)
        gd.ellipse((cx-r,cy-r*.38,cx+r,cy+r*.38), fill=(210,245,255,int(5*k*p*strength)))
    glow=glow.filter(ImageFilter.GaussianBlur(18))
    layer.alpha_composite(glow)

def ripple(layer,cx,cy,t,maxr=270,alpha=62,count=2):
    # v16: no geometric rings, they read as artifacts.
    return

def speed_streaks(layer,cx,cy,t):
    # v16: no sharp speed lines, they look synthetic.
    return

def mech_inset(t,large=False):
    return Image.new('RGBA',(1,1),(0,0,0,0))

beats=[
 ('01_hook_flash','THIS SHRIMP PUNCH\\nMAKES WATER FLASH',3.92,'video','peacock',{'fx':.31,'zoom':1.03,'offset':0},'flash',(610,945)),
 ('02_club_speed','ITS CLUB MOVES\\nINSANELY FAST',3.91,'still',5,{'fx':.58,'fy':.48,'zoom0':1.02,'zoom1':1.10,'panx':1},'speed_clean',(585,982)),
 ('03_cavitation','THAT FLASH\\nIS CAVITATION',3.92,'anim','cavitation',{},'clean',(615,965)),
 ('04_first_hit','THE PUNCH\\nHITS FIRST',3.91,'anim','first_hit',{},'clean',(585,975)),
 ('05_second_hit','THEN THE BUBBLE\\nCOLLAPSES',3.91,'anim','collapse',{},'clean',(575,990)),
 ('06_high_speed','SCIENTISTS FILMED IT\\nIN HIGH SPEED',3.92,'montage',[1,4,5,2],{},'montage_clean',(600,960)),
 ('07_not_just_prey','IT DOES NOT JUST\\nPUNCH PREY',3.92,'video','wide',{'fx':.32,'zoom':1.0,'offset':1},'clean',(560,1000)),
 ('08_water_punches','THE WATER\\nPUNCHES TOO',3.91,'video','peacock',{'fx':.38,'zoom':1.08,'offset':8},'water',(620,950)),
]

def base_frame(mode,src,params,t):
    if mode=='video': return video(src,t,**params)
    if mode=='still': return still(src,t,**params)
    if mode=='anim': return mechanism_frame(src,t)
    seq=src; seg=min(len(seq)-1,int(t*len(seq))); local=(t*len(seq))%1
    return still(seq[seg],local,fx=.5,fy=.5,zoom0=1.02,zoom1=1.07,panx=(-1)**seg)

def make_frame(mode,src,params,kind,loc,t):
    im=base_frame(mode,src,params,t).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); cx,cy=loc
    if kind=='flash':
        soft_water_flash(layer,cx,cy,t,.26,.26) 
    elif kind=='speed_clean':
        soft_water_flash(layer,cx-82,cy+25,t,.42,.16)
    elif kind=='cavitation':
        soft_water_flash(layer,cx,cy,t,.50,.18)
    elif kind=='impact_clean':
        soft_water_flash(layer,cx,cy,t,.30,.22)
    elif kind=='collapse':
        soft_water_flash(layer,cx+10,cy+8,t,.55,.14)
    elif kind=='montage_clean':
        soft_water_flash(layer,cx,cy,t,.54,.10)
    elif kind=='water':
        soft_water_flash(layer,cx+25,cy+10,t,.45,.18)
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
    n=round(dur*FPS)
    bm.append({'beat':bi,'id':bid,'caption':cap.replace('\\n',' / '),'mode':mode,'source':str(src),'visual_kind':kind,'frames':n,'strategy':'real video/photos + procedural bubbles/flash/ripples; no cards, no diagram overlays, minimal soft particle/flash cues; no AI animal frames'})
    for f in range(n):
        make_frame(mode,src,params,kind,loc,f/max(1,n-1)).save(FRAMES/f'frame_{idx:05d}.jpg',quality=94); idx+=1
(OUT/'beat_map_v16.json').write_text(json.dumps(bm,indent=2))
ass=OUT/'captions_say_dog_v16.ass'; write_ass(ass)
silent=OUT/'mantis_say_dog_v16_silent_1080.mp4'; master=OUT/'mantis_say_dog_v16_captioned_1080.mp4'; preview=OUT/'mantis_say_dog_v16_captioned_720.mp4'; contact=OUT/'contact_sheet_mantis_say_dog_v16.jpg'
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','17','-preset','medium',str(silent)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(VOICE),'-vf',f'ass={ass}','-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview),'-vf','fps=1,scale=270:480,tile=6x6','-frames:v','1','-update','1',str(contact)],check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size,bit_rate','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate,bit_rate','-of','json',str(preview)],text=True)
(OUT/'ffprobe_preview.json').write_text(probe)
(OUT/'README_QA.md').write_text(f'''# Mantis shrimp cavitation punch — v16 premium mechanism hybrid

Status: show candidate if contact-sheet QA passes.

Built after v09 proved generated animal frames were risky. v16 keeps real mantis footage/photos for animal beats and uses larger no-text, full-frame mechanism animation for cavitation/impact/collapse. No AI animal frames are used.

Outputs:
- Preview: `{preview}`
- Master: `{master}`
- Contact sheet: `{contact}`
- Beat map: `{OUT/'beat_map_v16.json'}`
''')
print(json.dumps({'preview':str(preview),'master':str(master),'contact_sheet':str(contact),'frames':idx,'ffprobe':json.loads(probe)},indent=2))
