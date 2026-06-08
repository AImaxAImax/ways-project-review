from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import subprocess, shutil, json, math, random

CASE=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT=CASE/'outputs/say_dog_v20_readable_mechanism'
FRAMES=OUT/'frames'; SRC=OUT/'src_frames'
VOICE=CASE/'outputs/auto_static_v01/voiceover.mp3'
VIDEO_DIR=CASE/'assets/source_commons_video'
W,H,FPS=1080,1920,24
for p in [OUT]: p.mkdir(parents=True,exist_ok=True)
for p in [FRAMES,SRC]:
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True)

# Extract real Commons source frames used for animal/context beats.
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
MECH_DIR=CASE/'assets/premium_mechanism_v17c_abstract'
mech_assets={
    'cavitation':Image.open(MECH_DIR/'WAYS_mantis_v17c_collapse_0_00001_.png').convert('RGB'),
    'first_hit':Image.open(MECH_DIR/'WAYS_mantis_v17c_first_hit_0_00001_.png').convert('RGB'),
    'collapse':Image.open(MECH_DIR/'WAYS_mantis_v17c_first_hit_1_00001_.png').convert('RGB'),
}

def cover(im,focus_x=.5,focus_y=.5,zoom=1.0):
    iw,ih=im.size; target=9/16
    crop_w=int(ih*target/zoom); crop_h=int(ih/zoom)
    if crop_w>iw:
        crop_w=iw; crop_h=int(iw/target)
    cx=int(iw*focus_x); cy=int(ih*focus_y)
    x=max(0,min(iw-crop_w,cx-crop_w//2)); y=max(0,min(ih-crop_h,cy-crop_h//2))
    return im.crop((x,y,x+crop_w,y+crop_h)).resize((W,H),Image.LANCZOS)

def grade(im):
    im=ImageEnhance.Color(im).enhance(1.08)
    im=ImageEnhance.Contrast(im).enhance(1.12)
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

def vertical_water(t,stage='cavitation'):
    # Project-owned premium-ish underwater macro background. No text, no labels, no UI.
    im=Image.new('RGB',(W,H),(4,24,30)); px=im.load()
    # Downsampled procedural field then upscale to avoid per-pixel slow full-res math.
    sw,sh=180,320
    small=Image.new('RGB',(sw,sh))
    sp=small.load()
    for y in range(sh):
        yy=y/sh
        for x in range(sw):
            xx=x/sw
            wave=math.sin(8*xx+3.5*yy+4*t)+0.45*math.sin(19*xx-2*t)+0.25*math.sin(15*yy+7*t)
            glow=max(0,1-((xx-.58)**2/.18+(yy-.48)**2/.12))
            b=int(32+70*(1-yy)+18*wave+70*glow)
            g=int(44+92*(1-yy)+10*wave+48*glow)
            r=int(5+14*(1-yy)+8*glow)
            sp[x,y]=(max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b)))
    im=small.resize((W,H),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(1.6))
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    rnd=random.Random(500+int(t*1000))
    for i in range(90):
        x=rnd.randrange(20,W-20); y=(rnd.randrange(0,H)+int(t*210*(.4+i%5*.05)))%H
        a=rnd.randrange(18,62); rr=rnd.uniform(.8,3.3)
        d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(210,245,255,a))
    # Depth vignette
    vig=Image.new('RGBA',(W,H),(0,0,0,0)); vd=ImageDraw.Draw(vig,'RGBA')
    for y in range(H):
        a=int(72*(abs(y-H/2)/(H/2))**1.8)
        if a: vd.line((0,y,W,y),fill=(0,0,0,a))
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def draw_club(draw, cx, cy, angle, length, width, alpha=235, hot=False):
    # Stylized raptorial club/appendage, not a whole fake animal.
    ux,uy=math.cos(angle),math.sin(angle); px,py=-uy,ux
    butt=(cx-ux*length*.50, cy-uy*length*.50)
    tip=(cx+ux*length*.50, cy+uy*length*.50)
    pts=[(butt[0]+px*width*.28,butt[1]+py*width*.28),(cx-ux*length*.08+px*width*.55,cy-uy*length*.08+py*width*.55),(tip[0]+px*width*.36,tip[1]+py*width*.36),(tip[0]-px*width*.32,tip[1]-py*width*.32),(cx-ux*length*.08-px*width*.52,cy-uy*length*.08-py*width*.52),(butt[0]-px*width*.22,butt[1]-py*width*.22)]
    draw.polygon(pts,fill=(221,124,42,alpha),outline=(255,211,112,min(255,alpha)))
    # glossy chitin highlight stripe
    stripe=[(butt[0]+px*width*.05,butt[1]+py*width*.05),(tip[0]+px*width*.15,tip[1]+py*width*.15),(tip[0]+px*width*.27,tip[1]+py*width*.27),(butt[0]+px*width*.17,butt[1]+py*width*.17)]
    draw.polygon(stripe,fill=(255,201,83,110 if not hot else 175))
    # arm segment trailing behind
    tail=[(butt[0]-ux*230+px*24,butt[1]-uy*230+py*24),(butt[0]+px*17,butt[1]+py*17),(butt[0]-px*17,butt[1]-py*17),(butt[0]-ux*230-px*20,butt[1]-uy*230-py*20)]
    draw.polygon(tail,fill=(182,72,32,175),outline=(245,165,72,110))

def glass_target(layer,cx,cy,t,crack=0.0):
    # Curved shell/snail-like hard target, used as visual contact object without labels.
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(9,0,-1):
        rr=86+k*19
        a=int(6*k)
        d.ellipse((cx-rr*1.25,cy-rr*.68,cx+rr*1.25,cy+rr*.68),fill=(24,82,93,a))
    d.ellipse((cx-180,cy-84,cx+180,cy+84),fill=(36,88,88,135),outline=(195,242,235,110),width=3)
    d.arc((cx-142,cy-61,cx+142,cy+61),200,340,fill=(248,255,230,120),width=4)
    if crack>0:
        rnd=random.Random(44)
        for i in range(11):
            ang=-math.pi/2 + i*.22 + rnd.uniform(-.05,.05)
            r=40+crack*(80+rnd.random()*165)
            x2=cx+math.cos(ang)*r; y2=cy+math.sin(ang)*r*.42
            d.line((cx,cy,x2,y2),fill=(235,255,255,int(105*crack)),width=2)

def bubble_field(layer,cx,cy,t,mode):
    d=ImageDraw.Draw(layer,'RGBA')
    if mode=='form':
        # growing attached vapor bubble after pressure drop.
        p=min(1,max(0,(t-.10)/.62))
        r=48+240*p
        for k in range(8,0,-1):
            rr=r*(.58+k*.065); a=int(13*k*(1-p*.25))
            d.ellipse((cx-rr*1.15,cy-rr*.72,cx+rr*1.15,cy+rr*.72),outline=(215,252,255,a),width=4)
        d.ellipse((cx-r*.55,cy-r*.30,cx+r*.55,cy+r*.30),fill=(226,255,255,int(42+40*p)),outline=(255,255,255,150),width=3)
    elif mode=='impact':
        p=max(0,1-abs(t-.30)/.25)
        for k in range(7,0,-1):
            rr=44+k*26*(.7+p*.7)
            d.ellipse((cx-rr*1.4,cy-rr*.42,cx+rr*1.4,cy+rr*.42),fill=(255,247,195,int(11*k*p)))
        for i in range(34):
            a=-.38+i*.024; dist=60+260*(i/34)
            x=cx+math.cos(a)*dist; y=cy+math.sin(a)*dist*.6
            d.line((cx,cy,x,y),fill=(255,232,160,int(70*p*(1-i/38))),width=max(1,int(4*(1-i/40))))
    else:
        # collapse: bubble shrinks while an outward shock glow expands.
        p=min(1,max(0,(t-.08)/.64))
        r=245*(1-p)+34
        for k in range(8,0,-1):
            rr=r*(.55+k*.07)
            d.ellipse((cx-rr*1.1,cy-rr*.62,cx+rr*1.1,cy+rr*.62),outline=(220,255,255,int(14*k*(1-p*.45))),width=3)
        shock=70+430*p
        for k in range(4,0,-1):
            d.ellipse((cx-shock*1.22,cy-shock*.45,cx+shock*1.22,cy+shock*.45),outline=(245,255,235,int(55*(1-p)*k/4)),width=5)
        d.ellipse((cx-42,cy-30,cx+42,cy+30),fill=(255,255,245,int(90*(1-abs(p-.72)))))

def literal_mech(stage,t):
    # v20: same premium VFX base as v19, but the mechanism layer is larger,
    # separated by a cinematic shadow pocket, and readable on a 270px contact sheet.
    bg_key = 'cavitation' if stage=='cavitation' else ('first_hit' if stage=='first_hit' else 'collapse')
    base=cover(mech_assets[bg_key],.50+.010*math.sin(t*math.pi),.50,1.01+.030*t).convert('RGBA')
    base=ImageEnhance.Contrast(base.convert('RGB')).enhance(1.05).convert('RGBA')
    base=Image.alpha_composite(base,Image.new('RGBA',(W,H),(0,18,22,46)))

    # Dark, soft oval behind the science action. It is not a card or label, just separation.
    pocket=Image.new('RGBA',(W,H),(0,0,0,0)); pd=ImageDraw.Draw(pocket,'RGBA')
    pd.ellipse((120,610,1015,1190),fill=(0,10,12,112))
    pd.ellipse((250,710,935,1095),fill=(0,0,0,76))
    pocket=pocket.filter(ImageFilter.GaussianBlur(54))
    base=Image.alpha_composite(base,pocket)

    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    ang=-0.09
    if stage=='cavitation':
        p=min(1,t*1.10)
        x=112+570*p; y=950-82*math.sin(t*math.pi)
        # ghost trail makes the movement read without diagram arrows.
        for j,a in enumerate([54,36,22]):
            draw_club(d,x-72*(j+1),y+8*(j+1),ang,430,86,alpha=a,hot=False)
        draw_club(d,x,y,ang,470,104,alpha=232,hot=t>.20)
        bubble_field(layer,x+210,y-8,t,'form')
        glass_target(layer,825,905,t,crack=0)
    elif stage=='first_hit':
        p=min(1,max(0,(t-.10)/.34))
        x=228+500*p; y=955-28*math.sin(t*math.pi)
        draw_club(d,x-64,y+8,ang,455,92,alpha=62,hot=False)
        draw_club(d,x,y,ang,505,116,alpha=242,hot=True)
        glass_target(layer,828,908,t,crack=max(0,min(1,(t-.20)/.35)))
        bubble_field(layer,794,906,t,'impact')
        # contact spark, organic bloom not a geometric callout.
        pp=max(0,1-abs(t-.34)/.18)
        if pp:
            for k in range(5,0,-1):
                rr=34+k*34
                d.ellipse((790-rr,905-rr*.32,790+rr,905+rr*.32),fill=(255,246,190,int(12*k*pp)))
    else:
        p=min(1,max(0,t/.70))
        x=742+100*p; y=940
        draw_club(d,x,y,ang,450,94,alpha=198,hot=False)
        glass_target(layer,825,908,t,crack=.58+.22*math.sin(t*math.pi))
        bubble_field(layer,600,905,t,'collapse')
        # Extra crisp shrinking core so 'collapse' reads at phone size.
        core=max(0,1-abs(t-.56)/.28)
        if core:
            d.ellipse((600-58*core,905-38*core,600+58*core,905+38*core),fill=(255,255,238,int(150*core)))
        rnd=random.Random(12)
        for i in range(54):
            a=rnd.random()*math.tau; dist=(1-p)*(100+rnd.random()*250)+18
            x1=600+math.cos(a)*dist; y1=905+math.sin(a)*dist*.52
            x2=600+math.cos(a)*(dist-22); y2=905+math.sin(a)*(dist-22)*.52
            d.line((x1,y1,x2,y2),fill=(225,255,255,int(72*(1-p)*(rnd.random()*.7+.3))),width=2)
    layer=layer.filter(ImageFilter.GaussianBlur(.18))
    comp=Image.alpha_composite(base,layer).convert('RGB')
    comp=ImageEnhance.Contrast(comp).enhance(1.09)
    comp=ImageEnhance.Color(comp).enhance(1.04)
    return comp

def shade(im):
    out=im.convert('RGBA'); layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    for y in range(690,1190,10):
        a=int(max(0,42*(1-abs(y-940)/250)))
        d.rectangle((0,y,W,y+10),fill=(0,0,0,a))
    for y in range(H):
        a=int(34*(abs(y-H/2)/(H/2))**2)
        if a: d.line((0,y,W,y),fill=(0,0,0,a))
    return Image.alpha_composite(out,layer).convert('RGB')

def soft_water_flash(layer,cx,cy,t,peak=.45,strength=.16):
    p=max(0,1-abs(t-peak)/.18)
    if p<=0: return
    glow=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow,'RGBA')
    for k in range(6,0,-1):
        r=(32+k*36)*(.8+.25*p)
        gd.ellipse((cx-r,cy-r*.38,cx+r,cy+r*.38), fill=(210,245,255,int(5*k*p*strength)))
    glow=glow.filter(ImageFilter.GaussianBlur(18)); layer.alpha_composite(glow)

beats=[
 ('01_hook_flash','THIS SHRIMP PUNCH\\nMAKES WATER FLASH',3.92,'video','peacock',{'fx':.31,'zoom':1.03,'offset':0},'flash',(610,945)),
 ('02_club_speed','ITS CLUB MOVES\\nINSANELY FAST',3.91,'still',5,{'fx':.58,'fy':.48,'zoom0':1.02,'zoom1':1.10,'panx':1},'speed_clean',(585,982)),
 ('03_cavitation','THAT FLASH\\nIS CAVITATION',3.92,'mech','cavitation',{},'literal',(615,965)),
 ('04_first_hit','THE PUNCH\\nHITS FIRST',3.91,'mech','first_hit',{},'literal',(585,975)),
 ('05_second_hit','THEN THE BUBBLE\\nCOLLAPSES',3.91,'mech','collapse',{},'literal',(575,990)),
 ('06_high_speed','SCIENTISTS FILMED IT\\nIN HIGH SPEED',3.92,'montage',[1,4,5,2],{},'montage_clean',(600,960)),
 ('07_not_just_prey','IT DOES NOT JUST\\nPUNCH PREY',3.92,'video','wide',{'fx':.32,'zoom':1.0,'offset':1},'clean',(560,1000)),
 ('08_water_punches','THE WATER\\nPUNCHES TOO',3.91,'video','peacock',{'fx':.38,'zoom':1.08,'offset':8},'water',(620,950)),
]

def base_frame(mode,src,params,t):
    if mode=='video': return video(src,t,**params)
    if mode=='still': return still(src,t,**params)
    if mode=='mech': return literal_mech(src,t)
    seq=src; seg=min(len(seq)-1,int(t*len(seq))); local=(t*len(seq))%1
    return still(seq[seg],local,fx=.5,fy=.5,zoom0=1.02,zoom1=1.07,panx=(-1)**seg)

def make_frame(mode,src,params,kind,loc,t):
    im=base_frame(mode,src,params,t).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); cx,cy=loc
    if kind=='flash': soft_water_flash(layer,cx,cy,t,.26,.26)
    elif kind=='speed_clean': soft_water_flash(layer,cx-82,cy+25,t,.42,.16)
    elif kind=='montage_clean': soft_water_flash(layer,cx,cy,t,.54,.10)
    elif kind=='water': soft_water_flash(layer,cx+25,cy+10,t,.45,.18)
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
    bm.append({'beat':bi,'id':bid,'caption':cap.replace('\\n',' / '),'mode':mode,'source':str(src),'visual_kind':kind,'frames':n,'strategy':'real video/photos plus project-owned no-text literal 3D-style mechanism frames: club geometry, target, vapor bubble growth/collapse; no labels, cards, arrows, or generated animal bodies'})
    for f in range(n):
        make_frame(mode,src,params,kind,loc,f/max(1,n-1)).save(FRAMES/f'frame_{idx:05d}.jpg',quality=94); idx+=1
(OUT/'beat_map_v20.json').write_text(json.dumps(bm,indent=2))
ass=OUT/'captions_say_dog_v20.ass'; write_ass(ass)
silent=OUT/'mantis_say_dog_v20_silent_1080.mp4'; master=OUT/'mantis_say_dog_v20_captioned_1080.mp4'; preview=OUT/'mantis_say_dog_v20_captioned_720.mp4'; contact=OUT/'contact_sheet_mantis_say_dog_v20.jpg'
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','17','-preset','medium',str(silent)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(VOICE),'-vf',f'ass={ass}','-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview),'-vf','fps=1,scale=270:480,tile=6x6','-frames:v','1','-update','1',str(contact)],check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size,bit_rate','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate,bit_rate','-of','json',str(preview)],text=True)
(OUT/'ffprobe_preview.json').write_text(probe)
(OUT/'README_QA.md').write_text(f'''# Mantis shrimp cavitation punch — v20 literal mechanism candidate

Status: internal candidate until contact-sheet/video QA.

Built after v17 abstract VFX improved polish but failed literal proof. v20 keeps real mantis sources for animal/context beats and replaces abstract mechanism shots with project-owned no-text literal mechanism animation: stylized raptorial club, hard target, cavitation bubble growth, first impact flash, and bubble collapse/shock glow.

No AI-generated animal bodies, no labels, no arrows, no diagram cards, no non-caption text.

Outputs:
- Preview: `{preview}`
- Master: `{master}`
- Contact sheet: `{contact}`
- Beat map: `{OUT/'beat_map_v20.json'}`
''')
print(json.dumps({'preview':str(preview),'master':str(master),'contact_sheet':str(contact),'frames':idx,'ffprobe':json.loads(probe)},indent=2))
