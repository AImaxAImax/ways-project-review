from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import math, random, json, shutil, subprocess

CASE=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT=CASE/'outputs/say_dog_v06_artifact_clean'
FRAMES=OUT/'frames'
VOICE=CASE/'outputs/auto_static_v01/voiceover.mp3'
W,H,FPS=1080,1920,24
for p in [OUT]: p.mkdir(parents=True,exist_ok=True)
if FRAMES.exists(): shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)

beats=[
 ('01_hook_flash','THIS SHRIMP PUNCH\\nMAKES WATER FLASH',3.92,'flash',4, (540,930)),
 ('02_club_speed','ITS CLUB MOVES\\nINSANELY FAST',3.91,'speed',5, (530,1010)),
 ('03_cavitation','THAT FLASH\\nIS CAVITATION',3.92,'cavitation',2, (600,1020)),
 ('04_first_hit','THE PUNCH\\nHITS FIRST',3.91,'impact',4, (585,995)),
 ('05_second_hit','THEN THE BUBBLE\\nCOLLAPSES',3.91,'collapse',3, (540,1040)),
 ('06_high_speed','SCIENTISTS FILMED IT\\nIN HIGH SPEED',3.92,'highspeed',1, (560,960)),
 ('07_not_just_prey','IT DOES NOT JUST\\nPUNCH PREY',3.92,'prey',5, (540,1020)),
 ('08_water_punches','THE WATER\\nPUNCHES TOO',3.91,'water',2, (610,1050)),
]

# Use only verified real Wikimedia source stills, not the AI/Wan plates that produced anatomy artifacts.
source={}
for i in range(1,6):
    im=Image.open(CASE/f'assets/source_stills/source_{i:02d}.jpg').convert('RGB')
    source[i]=im

def fit_cover(im:Image.Image, zoom:float, panx:float, pany:float)->Image.Image:
    iw,ih=im.size
    # cover 9:16 from square/landscape source, then crop with pan
    scale=max(W/iw,H/ih)*zoom
    nw,nh=int(iw*scale),int(ih*scale)
    big=im.resize((nw,nh),Image.LANCZOS)
    maxx=max(0,nw-W); maxy=max(0,nh-H)
    x=int(maxx*(0.5+panx*.5)); y=int(maxy*(0.5+pany*.5))
    x=max(0,min(maxx,x)); y=max(0,min(maxy,y))
    return big.crop((x,y,x+W,y+H))

def grade(im:Image.Image)->Image.Image:
    im=ImageEnhance.Color(im).enhance(1.08)
    im=ImageEnhance.Contrast(im).enhance(1.10)
    im=ImageEnhance.Brightness(im).enhance(.94)
    # soft vignette, no artificial UI or labels
    mask=Image.new('L',(W,H),0); d=ImageDraw.Draw(mask)
    d.ellipse((-260,120,W+260,H+80), fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(180))
    dark=Image.new('RGB',(W,H),(2,18,22))
    return Image.composite(im,dark,mask)

def bubbles(layer,cx,cy,t,seed=0,collapse=False,scale=1.0,density=34,alpha=130):
    d=ImageDraw.Draw(layer,'RGBA'); rnd=random.Random(seed)
    for _ in range(density):
        a=rnd.random()*math.tau
        if collapse:
            dist=(1-t)*(25+rnd.random()*170)*scale
            r=(2+rnd.random()*13)*(1-.62*t)*scale
            al=int(alpha*(.35+.65*t)*(0.5+rnd.random()*0.5))
        else:
            dist=t*(20+rnd.random()*185)*scale
            r=(1.5+rnd.random()*12)*(.35+.75*t)*scale
            al=int(alpha*(.45+.55*(1-abs(t-.55)))*(0.45+rnd.random()*0.55))
        x=cx+math.cos(a)*dist+rnd.uniform(-14,14)*scale
        y=cy+math.sin(a)*dist*.65+rnd.uniform(-10,10)*scale
        if x<0 or x>W or y<0 or y>H: continue
        d.ellipse((x-r,y-r,x+r,y+r), outline=(235,255,255,al), width=max(1,int(2.2*scale)))
        if r>7: d.ellipse((x-r*.25,y-r*.35,x-r*.05,y-r*.15), fill=(255,255,255,min(120,al)))

def ripple(layer,cx,cy,t,maxr=300,alpha=95,count=3):
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(count):
        r=maxr*(t*.85+k*.17)
        if r<12 or r>maxr: continue
        al=int(alpha*(1-r/maxr))
        d.ellipse((cx-r,cy-r*.56,cx+r,cy+r*.56), outline=(220,250,255,al), width=5)

def flash(layer,cx,cy,t,peak=.32,strength=.65):
    d=ImageDraw.Draw(layer,'RGBA')
    p=max(0,1-abs(t-peak)/.18)
    if p<=0: return
    # Natural short exposure bloom, not a drawn blob.
    for k in range(4,0,-1):
        r=(40+k*35)*(.8+.35*p)
        d.ellipse((cx-r,cy-r*.48,cx+r,cy+r*.48), fill=(245,255,238,int(18*k*p*strength)))
    d.ellipse((cx-70*p,cy-34*p,cx+95*p,cy+44*p), fill=(255,255,230,int(95*p*strength)))

def streak(layer,cx,cy,t):
    d=ImageDraw.Draw(layer,'RGBA')
    p=min(1,max(0,(t-.05)/.72))
    # Thin, low-opacity motion smear. Avoid cartoon arrows/rings.
    x0,y0=cx-360,cy+70; x1,y1=cx-70+170*p,cy+20-15*p
    for k in range(5):
        al=int(48*(1-k/5)*p)
        d.line((x0-18*k,y0+6*k,x1-5*k,y1+2*k), fill=(255,226,145,al), width=max(3,18-3*k))

def make_highspeed(t):
    # Clean rapid proof feeling by cutting between real stills inside the beat. No white frame dividers.
    seq=[4,5,3,2]
    which=seq[min(3,int(t*4))]
    tt=(t*4)%1
    return compose_base(which, .12+0.05*tt, math.sin(tt*math.pi)*.08, (which-3)*.08)

def compose_base(src_idx, t, panx=0, pany=0):
    zoom=1.38+0.08*t
    return grade(fit_cover(source[src_idx],zoom,panx,pany))

def frame(kind,src_idx,focus,t):
    if kind=='highspeed':
        im=make_highspeed(t).convert('RGBA')
    else:
        # Beat-specific pan directions create resets without fake morphing.
        panx={1:0,2:.18,3:-.12,4:.08,5:-.05,6:.0,7:.13,8:-.14}.get(src_idx,0)
        pany={1:.08,2:-.04,3:.12,4:-.08,5:.03,6:0,7:.0,8:-.03}.get(src_idx,0)
        im=compose_base(src_idx,t, panx*math.sin(t*math.pi), pany*math.sin(t*math.pi)).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0))
    cx,cy=focus
    if kind=='flash':
        flash(layer,cx,cy,t,.28,.8); bubbles(layer,cx,cy,min(1,t*1.3),seed=11,scale=.75,density=24,alpha=92); ripple(layer,cx,cy,max(0,(t-.25)/.75),310,85,3)
    elif kind=='speed':
        streak(layer,cx,cy,t)
        if t>.58: bubbles(layer,cx-20,cy+5,(t-.58)/.42,seed=22,scale=.45,density=14,alpha=80)
    elif kind=='cavitation':
        bubbles(layer,cx,cy,min(1,t*1.15),seed=33,scale=.82,density=30,alpha=105); flash(layer,cx,cy,t,.45,.35)
    elif kind=='impact':
        streak(layer,cx,cy,min(1,t*1.2)); flash(layer,cx,cy,t,.30,.65); ripple(layer,cx,cy,max(0,(t-.22)/.5),250,110,3)
    elif kind=='collapse':
        bubbles(layer,cx,cy,t,seed=55,collapse=True,scale=.80,density=30,alpha=120)
        if t>.42: ripple(layer,cx+20,cy+5,(t-.42)/.58,360,130,4)
    elif kind=='prey':
        # Keep nearly clean: just water motes.
        bubbles(layer,cx-120,cy+20,.65+0.12*math.sin(t*math.tau),seed=77,scale=.32,density=8,alpha=42)
    elif kind=='water':
        bubbles(layer,cx-20,cy,min(1,t*1.1),seed=88,scale=.62,density=18,alpha=84)
        if t>.35: bubbles(layer,cx+35,cy+15,(t-.35)/.65,seed=89,collapse=True,scale=.70,density=26,alpha=120); ripple(layer,cx+35,cy+15,(t-.35)/.65,410,145,5)
    elif kind=='highspeed':
        ripple(layer,cx,cy,t,330,62,3)
    im=Image.alpha_composite(im,layer)
    # caption readability shadow only, soft and invisible as a design object
    shade=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shade,'RGBA')
    for y in range(680,1180,10):
        a=int(max(0,34*(1-abs(y-930)/250)))
        sd.rectangle((0,y,W,y+10), fill=(0,0,0,a))
    return Image.alpha_composite(im,shade).convert('RGB')

def write_ass(path):
    def ts(t):
        h=int(t//3600); m=int((t%3600)//60); s=t%60; return f'{h}:{m:02d}:{s:05.2f}'
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
    lines=[]; cur=0.0
    for _,cap,dur,_,_,_ in beats:
        a,b=cap.split('\\n')
        text=r'{\c&H0000D7FF&}'+a+r'{\c&H00FFFFFF&}\N'+b
        lines.append(f'Dialogue: 0,{ts(cur)},{ts(cur+dur)},Caption,,0,0,0,,{text}')
        cur+=dur
    path.write_text(head+'\n'.join(lines)+'\n')

idx=0; beat_map=[]
for bi,(bid,cap,dur,kind,src_idx,focus) in enumerate(beats,1):
    n=round(dur*FPS); beat_map.append({'beat':bi,'id':bid,'caption':cap.replace('\\n',' / '),'kind':kind,'source_still':f'source_{src_idx:02d}','frames':n,'artifact_strategy':'real-source-still base, low-opacity no-text overlays only'})
    for f in range(n):
        t=f/max(1,n-1)
        frame(kind,src_idx,focus,t).save(FRAMES/f'frame_{idx:05d}.jpg',quality=93)
        idx+=1
(OUT/'beat_map_v06.json').write_text(json.dumps(beat_map,indent=2))
ass=OUT/'captions_say_dog_v06.ass'; write_ass(ass)
silent=OUT/'mantis_say_dog_v06_silent_1080.mp4'; master=OUT/'mantis_say_dog_v06_captioned_1080.mp4'; preview=OUT/'mantis_say_dog_v06_captioned_720.mp4'; contact=OUT/'contact_sheet_mantis_say_dog_v06.jpg'
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','17','-preset','medium',str(silent)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(VOICE),'-vf',f'ass={ass}','-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview),'-vf','fps=1,scale=270:480,tile=6x6','-frames:v','1','-update','1',str(contact)],check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size,bit_rate','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate,bit_rate','-of','json',str(preview)],text=True)
(OUT/'ffprobe_preview.json').write_text(probe)
(OUT/'README_QA.md').write_text(f'''# Mantis shrimp cavitation punch — v06 artifact-clean

Status: artifact-clean internal review candidate. This pass intentionally backs away from AI/Wan full-motion plates because v05 showed visible generated anatomy/overlay artifacts.

Strategy:
- Use verified real Wikimedia mantis stills only as visual bases.
- Add only low-opacity no-text cavitation/impact cues.
- No labels, diagram UI, frame dividers, or non-caption text.
- Accepts less true subject motion in exchange for fewer visible AI artifacts.

Outputs:
- Preview: `{preview}`
- Master: `{master}`
- Contact sheet: `{contact}`
- Beat map: `{OUT/'beat_map_v06.json'}`
''')
print(json.dumps({'preview':str(preview),'master':str(master),'contact_sheet':str(contact),'frames':idx,'ffprobe':json.loads(probe)},indent=2))
