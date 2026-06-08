#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import math, subprocess, json
ROOT=Path('/mnt/c/dev/curious-shorts')
CASE=ROOT/'test_cases/mantis_shrimp_cavitation_punch'
SRC=CASE/'assets/source_stills'
OUT=CASE/'outputs/motion_graphic_rework_v02'
FRAMES=OUT/'frames'
OUT.mkdir(parents=True, exist_ok=True); FRAMES.mkdir(exist_ok=True)
W,H,FR,DUR=1080,1920,24,31.32
sources=[SRC/'source_04.jpg',SRC/'source_05.jpg',SRC/'source_02.jpg',SRC/'source_03.jpg']
imgs=[Image.open(p).convert('RGB') for p in sources]

def cover(im, zoom=1.0, cx=.5, cy=.5):
    scale=max(W/im.width,H/im.height)*zoom
    im=im.resize((int(im.width*scale),int(im.height*scale)),Image.Resampling.LANCZOS)
    x=int(cx*im.width-W/2); y=int(cy*im.height-H/2)
    x=max(0,min(x,im.width-W)); y=max(0,min(y,im.height-H))
    return im.crop((x,y,x+W,y+H))

def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def seg(t,a,b): return ease((t-a)/(b-a))

def base(t, idx=0, zoom=1.15):
    im=cover(imgs[idx%len(imgs)], zoom=zoom, cx=.52+.08*math.sin(t*.17), cy=.52+.05*math.cos(t*.13))
    im=ImageEnhance.Contrast(im).enhance(1.28)
    im=ImageEnhance.Color(im).enhance(1.12)
    im=ImageEnhance.Brightness(im).enhance(.62)
    # underwater blue grade + vignette
    blue=Image.new('RGB',(W,H),(0,42,58)); im=Image.blend(im,blue,.28)
    mask=Image.new('L',(W,H),0); d=ImageDraw.Draw(mask); d.ellipse((-120,130,W+120,H-130),fill=255); mask=mask.filter(ImageFilter.GaussianBlur(180))
    return Image.composite(im, Image.new('RGB',(W,H),(0,8,16)), mask)

def draw_target(d,x=760,y=1010,s=1,crack=0):
    d.ellipse((x-95*s,y-80*s,x+95*s,y+80*s),fill=(140,110,75,235),outline=(255,218,150,220),width=int(6*s))
    d.arc((x-65*s,y-52*s,x+72*s,y+62*s),205,45,fill=(255,235,170,190),width=int(9*s))
    if crack>0:
        a=int(240*crack)
        d.line((x-18*s,y-54*s,x+18*s,y-6*s,x-10*s,y+50*s),fill=(20,12,8,a),width=int(7*s))
        d.line((x+17*s,y-7*s,x+63*s,y+24*s),fill=(20,12,8,a),width=int(5*s))

def draw_club_path(d,p,flash=0):
    # Real-photo background + explicit gold striking club/vector, no labels/text.
    sx,sy=265,1170
    ex=420+360*p; ey=1110-170*p
    mid=(sx+150+130*p, sy-165-40*p)
    # motion ghosts
    for g,a in [(0.0,225),(.18,110),(.34,60)]:
        q=max(0,p-g); gx=420+360*q; gy=1110-170*q
        d.line((sx,sy,mid[0]-70*g,mid[1]+30*g,gx,gy),fill=(255,212,70,a),width=18)
        d.ellipse((gx-44,gy-34,gx+54,gy+42),fill=(255,190,58,a),outline=(255,245,170,min(255,a+20)),width=4)
    if flash>0:
        d.ellipse((780-90*flash,990-90*flash,780+90*flash,990+90*flash),fill=(255,245,190,int(120*flash)))

def bubbles(d,cx,cy,amt=1,collapse=0,flash=0,shock=0):
    for i in range(42):
        ang=i*math.tau/42 + .2*math.sin(i)
        dist=(75+210*((i*37)%100)/100)*(1-.55*collapse)
        x=cx+math.cos(ang)*dist; y=cy+math.sin(ang)*dist*.65
        r=(8+((i*11)%28))*(1+.5*collapse)
        a=int(205*amt*(.35+.65*((i*17)%100)/100))
        d.ellipse((x-r,y-r,x+r,y+r),outline=(205,250,255,a),width=3)
    if flash>0:
        for k in range(5):
            r=45+k*55+65*flash; a=int(175*flash/(k+1))
            d.ellipse((cx-r,cy-r*.7,cx+r,cy+r*.7),outline=(255,248,185,a),width=7)
    if shock>0:
        for k in range(6):
            r=80+shock*470+k*45; a=int(170*(1-shock)/(k+1))
            if a>0: d.ellipse((cx-r,cy-r*.55,cx+r,cy+r*.55),outline=(195,245,255,a),width=6)

def highspeed(im,t):
    d=ImageDraw.Draw(im,'RGBA')
    for i,x in enumerate([100,390,680]):
        p=seg(t, i*.55, i*.55+1.0)
        d.rounded_rectangle((x,700,x+300,1160),radius=28,fill=(0,10,18,130),outline=(150,235,255,70),width=3)
        draw_target(d,x+215,930,.55,p)
        # mini club sequence
        sx,sy=x+75,1035; ex=x+115+140*p; ey=1010-65*p
        d.line((sx,sy,ex,ey),fill=(255,210,70,190),width=11)
        d.ellipse((ex-24,ey-18,ex+29,ey+22),fill=(255,184,58,210))
        bubbles(d,x+213,928,p,collapse=max(0,p-.45),flash=max(0,p-.5),shock=max(0,p-.55))

for idx in range(int(DUR*FR)):
    t=idx/FR
    scene=0 if t<7.83 else 1 if t<15.66 else 2 if t<23.49 else 3
    im=base(t,scene,zoom=1.24 if scene!=1 else 1.38)
    d=ImageDraw.Draw(im,'RGBA')
    # source/photo underlay is always real; overlay is proof graphic.
    if t<3.92:
        p=seg(t,.3,1.35); flash=max(0,1-abs(t-1.15)/.65); sh=seg(t,1.25,2.7)
        draw_target(d,782,992,1,p); draw_club_path(d,p,flash); bubbles(d,785,990,p,0,flash,sh)
    elif t<7.83:
        p=seg(t,3.92,7.83)
        draw_target(d,782,992,1,.2*p); draw_club_path(d,.25+.55*p,.25*p); bubbles(d,785,990,p,0,.15*p,0)
    elif t<11.75:
        p=seg(t,7.83,11.75)
        # bubble proof close-up; background real photo, front bubble field
        draw_target(d,770,1000,1.05,.15)
        draw_club_path(d,.88,.15)
        bubbles(d,760,985,.9,0,.35+0.25*math.sin(p*math.pi),0)
    elif t<15.66:
        p=seg(t,11.75,15.66)
        draw_target(d,780,995,1,p); draw_club_path(d,p,max(0,1-abs(p-.85)/.22)); bubbles(d,785,990,.45*p,0,max(0,1-abs(p-.85)/.2),.1*p)
    elif t<19.57:
        p=seg(t,15.66,19.57)
        draw_target(d,780,995,1,1); draw_club_path(d,1,.1); bubbles(d,785,990,1,p,max(0,1-abs(p-.55)/.22),p)
    elif t<23.49:
        highspeed(im,t-19.57)
    elif t<27.41:
        p=seg(t,23.49,27.41)
        draw_target(d,780,995,1,1); draw_club_path(d,1,.05); bubbles(d,785,990,.8,.2+.4*p,0,p)
    else:
        p=seg(t,27.41,31.32)
        draw_target(d,780,995,1,1); draw_club_path(d,1,max(0,1-abs(p-.58)/.25)); bubbles(d,785,990,1,.4+.55*p,max(0,1-abs(p-.55)/.28),p)
    # subtle particles
    for j in range(34):
        x=(j*217+int(t*22))%W; y=(j*151+int(t*18))%H; a=35+((j*19)%45)
        d.ellipse((x-2,y-2,x+2,y+2),fill=(180,240,250,a))
    im.save(FRAMES/f'frame_{idx:05d}.jpg',quality=93)

clean=OUT/'clean_master.mp4'; cap=OUT/'publish_candidate_captioned.mp4'; prev=OUT/'discord_preview_captioned.mp4'; sheet=OUT/'contact_sheet.jpg'; ffp=OUT/'ffprobe_publish.json'
audio=CASE/'outputs/auto_static_v01/voiceover.mp3'; ass=CASE/'outputs/auto_static_v01/captions.ass'
subprocess.run(['ffmpeg','-y','-framerate',str(FR),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(clean)],check=True)
subprocess.run(['ffmpeg','-y','-i',str(clean),'-i',str(audio),'-vf',f"ass='{ass}'",'-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(cap)],check=True)
subprocess.run(['ffmpeg','-y','-i',str(cap),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','slow','-crf','23','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(prev)],check=True)
subprocess.run(['ffmpeg','-y','-i',str(cap),'-vf','fps=1/3,scale=270:480,tile=4x3:padding=8:margin=8:color=black','-frames:v','1','-update','1',str(sheet)],check=True)
with ffp.open('w') as f: subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(cap)],stdout=f,check=True)
manifest={'lane':'real_mantis_source_photo_plus_deterministic_cavitation_motion_graphic','right_safe_photo_sources':'Wikimedia CC BY-SA Diego Delso source stills; proof overlay project-owned deterministic graphics','not_claimed_real_high_speed_footage':True,'no_paid_or_credit_tools':True,'outputs':{'clean_master':str(clean.relative_to(CASE)),'publish_candidate_captioned':str(cap.relative_to(CASE)),'discord_preview_captioned':str(prev.relative_to(CASE)),'contact_sheet':str(sheet.relative_to(CASE)),'ffprobe':str(ffp.relative_to(CASE))}}
(OUT/'render_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
