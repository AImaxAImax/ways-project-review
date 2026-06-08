#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import math, subprocess, json, os

ROOT=Path('/mnt/c/dev/curious-shorts')
CASE=ROOT/'test_cases/mantis_shrimp_cavitation_punch'
OUT=CASE/'outputs/motion_graphic_rework_v01'
FR=24
DUR=31.32
W,H=1080,1920
OUT.mkdir(parents=True, exist_ok=True)
FRAMES=OUT/'frames'
FRAMES.mkdir(exist_ok=True)

def ease(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)

def seg(t,a,b):
    return ease((t-a)/(b-a))

def gradient_bg(t):
    im=Image.new('RGB',(W,H),(5,18,28))
    d=ImageDraw.Draw(im,'RGBA')
    # water gradient and soft light columns
    for y in range(0,H,8):
        v=y/H
        col=(int(4+8*(1-v)), int(28+42*(1-v)), int(42+70*(1-v)))
        d.rectangle([0,y,W,y+8], fill=col+(255,))
    for i,x in enumerate([180,520,860]):
        alpha=int(24+10*math.sin(t*0.7+i))
        d.polygon([(x-120,0),(x+80,0),(x+210,H),(x-230,H)], fill=(80,190,210,alpha))
    # substrate
    d.ellipse((-250,1510,1320,2160), fill=(66,55,46,230))
    d.ellipse((420,1440,1350,2040), fill=(42,73,63,155))
    return im.filter(ImageFilter.GaussianBlur(0.2))

def shrimp(draw, t, x=250, y=1080, scale=1.0, attack=0):
    # stylized but non-text mantis shrimp: body, eyes, raptorial club
    s=scale
    body=(x-120*s,y-150*s,x+120*s,y+210*s)
    draw.ellipse(body, fill=(42,145,124,230), outline=(140,240,210,190), width=int(5*s))
    draw.ellipse((x-100*s,y-230*s,x-10*s,y-130*s), fill=(155,80,190,235), outline=(230,200,255,170), width=int(4*s))
    draw.ellipse((x+10*s,y-230*s,x+100*s,y-130*s), fill=(155,80,190,235), outline=(230,200,255,170), width=int(4*s))
    draw.ellipse((x-64*s,y-198*s,x-44*s,y-178*s), fill=(18,18,28,255))
    draw.ellipse((x+44*s,y-198*s,x+64*s,y-178*s), fill=(18,18,28,255))
    # antennae
    for side in [-1,1]:
        draw.line((x+side*45*s,y-210*s,x+side*(110+20*math.sin(t))*s,y-360*s), fill=(240,85,70,190), width=int(5*s))
    # legs
    for i in range(4):
        yy=y-50*s+i*65*s
        draw.line((x-90*s,yy,x-190*s,yy+45*s), fill=(255,205,80,180), width=int(9*s))
        draw.line((x+90*s,yy,x+165*s,yy+40*s), fill=(255,205,80,180), width=int(8*s))
    # striking arm/club, sweeping toward target
    start=(x+95*s,y-35*s)
    endx= x+(190+360*attack)*s
    endy= y-(20+60*attack)*s
    mid=(x+(170+150*attack)*s,y-(120+40*attack)*s)
    draw.line([start, mid, (endx,endy)], fill=(245,207,70,255), width=int(19*s), joint='curve')
    draw.ellipse((endx-42*s,endy-35*s,endx+48*s,endy+38*s), fill=(250,185,55,255), outline=(255,240,150,230), width=int(4*s))
    # motion ghosts during attack
    if attack>0.15:
        for g in [0.25,0.5,0.75]:
            gx=x+(190+360*(attack-g*0.18))*s; gy=y-(20+60*(attack-g*0.18))*s
            draw.ellipse((gx-36*s,gy-28*s,gx+40*s,gy+31*s), outline=(255,240,140,int(70*g)), width=int(5*s))

def target(draw, x=790,y=1015,scale=1.0, crack=0):
    s=scale
    draw.ellipse((x-92*s,y-82*s,x+100*s,y+92*s), fill=(122,105,85,245), outline=(218,190,140,220), width=int(6*s))
    draw.arc((x-58*s,y-48*s,x+62*s,y+60*s), start=210, end=60, fill=(232,220,170,200), width=int(9*s))
    if crack>0:
        a=int(220*crack)
        draw.line((x-10*s,y-58*s,x+18*s,y-10*s,x-20*s,y+48*s), fill=(30,20,16,a), width=int(7*s))
        draw.line((x+18*s,y-10*s,x+58*s,y+25*s), fill=(30,20,16,a), width=int(5*s))

def bubbles(draw, center, amount, radius, alpha=180, collapse=0, flash=0):
    cx,cy=center
    n=32
    for i in range(n):
        ang=i*2*math.pi/n + 0.3*math.sin(i)
        rr=radius*(0.25+0.75*((i*37)%100)/100)
        if collapse>0: rr*=1-0.62*collapse
        x=cx+math.cos(ang)*rr
        y=cy+math.sin(ang)*rr*0.72
        r=9+((i*13)%25)
        if collapse>0: r*=1+0.55*collapse
        a=int(alpha*amount*(0.4+0.6*((i*19)%100)/100))
        draw.ellipse((x-r,y-r,x+r,y+r), outline=(205,245,255,a), width=3)
    if flash>0:
        for k in range(5):
            r=55+k*45+flash*55
            a=int(150*flash/(k+1))
            draw.ellipse((cx-r,cy-r,cx+r,cy+r), outline=(255,245,170,a), width=8)
        draw.ellipse((cx-70*flash,cy-70*flash,cx+70*flash,cy+70*flash), fill=(255,250,210,int(155*flash)))

def shock(draw, center, amount, color=(210,248,255)):
    cx,cy=center
    for k in range(5):
        r=60+amount*420+k*45
        a=int(170*(1-amount)/(k+1))
        if a>0:
            draw.ellipse((cx-r,cy-r*0.65,cx+r,cy+r*0.65), outline=color+(a,), width=7)
            draw.line((cx-r,cy,cx+r,cy), fill=color+(max(0,a-40),), width=3)

def highspeed_strip(im, t):
    d=ImageDraw.Draw(im,'RGBA')
    # three ghost frames without labels/text
    xs=[150,420,690]
    alphas=[90,145,210]
    for idx,x in enumerate(xs):
        box=(x,690,x+250,1180)
        d.rounded_rectangle(box, radius=28, fill=(8,20,30,120), outline=(170,235,255,80), width=4)
        local=seg((t%4), idx*0.6, idx*0.6+1.2)
        shrimp(d,t,x=x+82,y=1010,scale=0.42,attack=local)
        target(d,x=x+188,y=955,scale=0.42,crack=local)
        bubbles(d,(x+180,956),local,60,alpha=150,flash=max(0,local-0.45))

for idx in range(int(DUR*FR)):
    t=idx/FR
    im=gradient_bg(t)
    d=ImageDraw.Draw(im,'RGBA')
    # default scene variables
    attack=0; crack=0; bubble_amt=0; collapse=0; flash=0; sh=0
    if t<3.92:
        attack=seg(t,0.4,1.4); crack=seg(t,1.15,1.7); bubble_amt=seg(t,0.9,1.8); flash=max(0,1-abs(t-1.25)/0.7); sh=seg(t,1.25,2.4)
    elif t<7.83:
        p=seg(t,3.92,7.83); attack=0.25+0.55*p; bubble_amt=p; flash=0.25*p
    elif t<11.75:
        p=seg(t,7.83,11.75); attack=0.86; bubble_amt=0.65+0.35*math.sin(p*math.pi); flash=0.15+0.25*math.sin(p*math.pi)
        # close-up bubble cloud
    elif t<15.66:
        p=seg(t,11.75,15.66); attack=p; crack=p; bubble_amt=0.25*p; flash=max(0,1-abs(p-0.86)/0.25); sh=0.25*max(0,p-0.75)
    elif t<19.57:
        p=seg(t,15.66,19.57); attack=1; crack=1; bubble_amt=1; collapse=p; flash=max(0,1-abs(p-0.58)/0.22); sh=p
    elif t<23.49:
        highspeed_strip(im,t-19.57)
        d=ImageDraw.Draw(im,'RGBA')
        # add subtle waves, skip main draw and save after vignette
        im=ImageEnhance.Contrast(im).enhance(1.06)
        im.save(FRAMES/f'frame_{idx:05d}.jpg',quality=92)
        continue
    elif t<27.41:
        p=seg(t,23.49,27.41); attack=1; crack=1; bubble_amt=0.7; collapse=0.2+0.6*p; sh=p
    else:
        p=seg(t,27.41,31.32); attack=1; crack=1; bubble_amt=1; collapse=0.4+0.6*p; flash=max(0,1-abs(p-0.55)/0.32); sh=p
    # camera changes/closeups
    if 7.83 <= t < 11.75:
        shrimp(d,t,x=185,y=1055,scale=0.95,attack=attack)
        target(d,x=765,y=980,scale=1.15,crack=crack)
        bubbles(d,(725,970),bubble_amt,205,alpha=210,collapse=collapse,flash=flash)
        shock(d,(735,970),sh)
    else:
        shrimp(d,t,x=250,y=1080,scale=1.0,attack=attack)
        target(d,x=790,y=1015,scale=1.0,crack=crack)
        bubbles(d,(755,1000),bubble_amt,190,alpha=205,collapse=collapse,flash=flash)
        shock(d,(755,1000),sh)
    # water particles
    for j in range(55):
        x=(j*211 + int(t*34))%W
        y=(j*137 + int(t*19))%H
        a=35+((j*17)%50)
        d.ellipse((x-2,y-2,x+2,y+2), fill=(170,235,245,a))
    im=ImageEnhance.Contrast(im).enhance(1.08)
    im.save(FRAMES/f'frame_{idx:05d}.jpg',quality=92)

# encode clean, captioned, preview, sheets
clean=OUT/'clean_master.mp4'
captioned=OUT/'publish_candidate_captioned.mp4'
preview=OUT/'discord_preview_captioned.mp4'
audio=CASE/'outputs/auto_static_v01/voiceover.mp3'
ass=CASE/'outputs/auto_static_v01/captions.ass'
subprocess.run(['ffmpeg','-y','-framerate',str(FR),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(clean)],check=True)
subprocess.run(['ffmpeg','-y','-i',str(clean),'-i',str(audio),'-vf',f"ass='{ass}'",'-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(captioned)],check=True)
subprocess.run(['ffmpeg','-y','-i',str(captioned),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','slow','-crf','23','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
# contact sheet
sheet=OUT/'contact_sheet.jpg'
subprocess.run(['ffmpeg','-y','-i',str(captioned),'-vf','fps=1/3,scale=270:480,tile=4x3:padding=8:margin=8:color=black','-frames:v','1',str(sheet)],check=True)
ffp=OUT/'ffprobe_publish.json'
with ffp.open('w') as f:
    subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(captioned)],stdout=f,check=True)
manifest={
 'lane':'deterministic_motion_graphic_proof_sequence',
 'no_paid_or_credit_tools':True,
 'source_note':'Uses deterministic project-owned motion graphics plus existing approved mantis script/VO/caption scaffold. It is a proof motion-graphic fallback, not claimed as real high-speed footage.',
 'beats':[
  'impact flash/bubble cloud', 'club motion tears water into bubbles', 'cavitation bubble cloud close-up', 'first impact', 'bubble collapse + second shock', 'high-speed sequence visualization', 'not just punch prey', 'water punches too replay'
 ],
 'outputs': {k:str(v.relative_to(CASE)) for k,v in {'clean_master':clean,'publish_candidate_captioned':captioned,'discord_preview_captioned':preview,'contact_sheet':sheet,'ffprobe':ffp}.items()}
}
(OUT/'render_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
