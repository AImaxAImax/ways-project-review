from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import subprocess, shutil, json, math, random

CASE=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT=CASE/'outputs/say_dog_v27_higgsfield_crop_clean'
FRAMES=OUT/'frames'; SRC=OUT/'src_frames'
VOICE=CASE/'outputs/auto_static_v01/voiceover.mp3'
VIDEO_DIR=CASE/'assets/source_commons_video'
W,H,FPS=1080,1920,24
for p in [OUT]: p.mkdir(parents=True,exist_ok=True)
for p in [FRAMES,SRC]:
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True)

# Extract real Commons source frames used for animal/context beats.
for name,path in {'peacock':VIDEO_DIR/'peacock_mantis.webm','wide':VIDEO_DIR/'mantis_philippines.webm','higgs':CASE/'outputs/higgsfield_video_route/higgsfield_mantis_mechanism_test01_480p_silent.mp4'}.items():
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

def higgs_plate(t, start=0.0, end=1.0, fx=.50, fy=.50, zoom=1.04):
    # v27: Higgsfield paid-test result used only as a cinematic source plate.
    # Crop to vertical, preserve generated motion, then let captions carry the science.
    arr=vframes('higgs')
    u=max(0,min(1,start+(end-start)*t))
    idx=max(0,min(len(arr)-1, int(u*(len(arr)-1))))
    im=grade(cover(arr[idx],fx,fy,zoom))
    # Slight sharpening/contrast so the bubble reads at phone size after upscaling from 480p.
    im=ImageEnhance.Sharpness(im).enhance(1.16)
    im=ImageEnhance.Contrast(im).enhance(1.07)
    return im

def vertical_water(t,stage='cavitation'):
    # v27: controlled clean underwater macro plate for all mechanism beats.
    # No generated flare stills, no text, no labels, no accidental artifacts.
    sw,sh=216,384
    small=Image.new('RGB',(sw,sh))
    sp=small.load()
    for y in range(sh):
        yy=y/sh
        for x in range(sw):
            xx=x/sw
            wave=math.sin(7.0*xx+3.2*yy+2.8*t)+0.42*math.sin(18*xx-3.1*t)+0.22*math.sin(13*yy+5.0*t)
            caustic=max(0, math.sin(34*(xx+.15*math.sin(t*1.2))+18*yy+4*t))**7
            glow=max(0,1-((xx-.58)**2/.20+(yy-.48)**2/.14))
            b=int(38+78*(1-yy)+13*wave+55*glow+35*caustic)
            g=int(48+96*(1-yy)+9*wave+38*glow+22*caustic)
            r=int(4+16*(1-yy)+6*glow+7*caustic)
            sp[x,y]=(max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b)))
    im=small.resize((W,H),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(1.2)).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    # large slow soft bokeh only, avoids tiny speckle artifacts under captions
    rnd=random.Random(830+int(t*24))
    for i in range(18):
        x=(rnd.randrange(-100,W+100)+int(t*30*(i%3-1)))% (W+180)-90
        y=(rnd.randrange(250,H-220)+int(t*52*(1+i%4*.25)))%H
        rr=rnd.uniform(8,28); a=rnd.randrange(7,22)
        d.ellipse((x-rr,y-rr*.72,x+rr,y+rr*.72),outline=(196,240,255,a),width=2)
    layer=layer.filter(ImageFilter.GaussianBlur(2.2))
    # cinematic top/bottom depth rolloff
    vig=Image.new('RGBA',(W,H),(0,0,0,0)); vd=ImageDraw.Draw(vig,'RGBA')
    for y in range(H):
        edge=(abs(y-H/2)/(H/2))**1.7
        a=int(64*edge)
        if a: vd.line((0,y,W,y),fill=(0,0,0,a))
    return Image.alpha_composite(Image.alpha_composite(im,layer),vig).convert('RGB')

def draw_club(draw, cx, cy, angle, length, width, alpha=235, hot=False):
    # Smooth stylized raptorial club/appendage, not a whole fake animal.
    ux,uy=math.cos(angle),math.sin(angle); px,py=-uy,ux
    butt=(cx-ux*length*.50, cy-uy*length*.50)
    tip=(cx+ux*length*.50, cy+uy*length*.50)
    pts=[(butt[0]+px*width*.22,butt[1]+py*width*.22),(cx-ux*length*.05+px*width*.50,cy-uy*length*.05+py*width*.50),(tip[0]+px*width*.34,tip[1]+py*width*.34),(tip[0]-px*width*.30,tip[1]-py*width*.30),(cx-ux*length*.05-px*width*.47,cy-uy*length*.05-py*width*.47),(butt[0]-px*width*.20,butt[1]-py*width*.20)]
    # layered fill gives a less flat 2D look without diagram arrows/cards
    draw.polygon(pts,fill=(218,88,36,alpha),outline=(250,176,86,min(180,alpha)))
    inner=[(butt[0]+px*width*.05,butt[1]+py*width*.05),(cx+px*width*.26,cy+py*width*.26),(tip[0]+px*width*.20,tip[1]+py*width*.20),(tip[0]-px*width*.04,tip[1]-py*width*.04),(cx-px*width*.18,cy-py*width*.18),(butt[0]-px*width*.03,butt[1]-py*width*.03)]
    draw.polygon(inner,fill=(255,126,45,int(alpha*.82)))
    stripe=[(butt[0]+px*width*.10,butt[1]+py*width*.10),(tip[0]+px*width*.17,tip[1]+py*width*.17),(tip[0]+px*width*.25,tip[1]+py*width*.25),(butt[0]+px*width*.18,butt[1]+py*width*.18)]
    draw.polygon(stripe,fill=(255,221,105,124 if not hot else 172))
    # trailing arm, subdued so it does not look like a second object
    tail=[(butt[0]-ux*210+px*20,butt[1]-uy*210+py*20),(butt[0]+px*15,butt[1]+py*15),(butt[0]-px*15,butt[1]-py*15),(butt[0]-ux*210-px*18,butt[1]-uy*210-py*18)]
    draw.polygon(tail,fill=(139,56,35,int(alpha*.54)),outline=(233,132,65,70))

def glass_target(layer,cx,cy,t,crack=0.0):
    # Curved shell/hard target with organic shading. No labels or callout geometry.
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(10,0,-1):
        rr=70+k*20
        d.ellipse((cx-rr*1.18,cy-rr*.62,cx+rr*1.18,cy+rr*.62),fill=(17,73,84,int(4.8*k)))
    d.ellipse((cx-178,cy-86,cx+178,cy+86),fill=(52,112,110,180),outline=(210,250,242,135),width=3)
    for k in range(5):
        yy=cy-54+k*24
        d.arc((cx-148,yy-38,cx+148,yy+38),205,335,fill=(244,255,235,42+k*7),width=2)
    d.ellipse((cx-58,cy-28,cx+56,cy+28),fill=(238,252,230,62),outline=(235,255,252,72),width=1)
    if crack>0:
        rnd=random.Random(44)
        for i in range(9):
            ang=-math.pi/2 + i*.25 + rnd.uniform(-.04,.04)
            r=30+crack*(70+rnd.random()*145)
            x2=cx+math.cos(ang)*r; y2=cy+math.sin(ang)*r*.42
            d.line((cx,cy,x2,y2),fill=(232,255,255,int(82*crack)),width=2)

def bubble_field(layer,cx,cy,t,mode):
    d=ImageDraw.Draw(layer,'RGBA')
    if mode=='form':
        # growing attached vapor bubble after pressure drop.
        p=min(1,max(0,(t-.10)/.62))
        r=48+240*p
        for k in range(5,0,-1):
            rr=r*(.62+k*.075); a=int(9*k*(1-p*.18))
            d.ellipse((cx-rr*1.10,cy-rr*.66,cx+rr*1.10,cy+rr*.66),outline=(205,248,255,a),width=4)
        d.ellipse((cx-r*.52,cy-r*.29,cx+r*.52,cy+r*.29),fill=(218,252,255,int(34+30*p)),outline=(245,255,255,112),width=3)
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
    # v27: same premium VFX base as v19, but the mechanism layer is larger,
    # separated by a cinematic shadow pocket, and readable on a 270px contact sheet.
    bg_key = 'cavitation' if stage=='cavitation' else ('first_hit' if stage=='first_hit' else 'collapse')
    # v27 correction: use one controlled clean mechanism world for all three proof
    # beats. This avoids the artifacted generated flash background and improves
    # continuity across club -> bubble -> collapse.
    base = vertical_water(t, stage).convert('RGBA')
    base = ImageEnhance.Contrast(base.convert('RGB')).enhance(0.98).convert('RGBA')
    base = Image.alpha_composite(base, Image.new('RGBA',(W,H),(0,12,18,68)))

    # Dark, soft oval behind the science action. It is not a card or label, just separation.
    pocket=Image.new('RGBA',(W,H),(0,0,0,0)); pd=ImageDraw.Draw(pocket,'RGBA')
    pd.ellipse((56,520,1060,1285),fill=(0,10,12,142))
    pd.ellipse((180,645,1000,1150),fill=(0,0,0,82))
    pocket=pocket.filter(ImageFilter.GaussianBlur(54))
    base=Image.alpha_composite(base,pocket)

    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    ang=-0.09
    if stage=='cavitation':
        p=min(1,t*1.08)
        # close-up: keep the whole mechanism readable in every sampled frame.
        x=210+390*p; y=910-48*math.sin(t*math.pi)
        for j,a in enumerate([38,20]):
            draw_club(d,x-74*(j+1),y+7*(j+1),ang,660,148,alpha=a,hot=False)
        draw_club(d,x,y,ang,735,174,alpha=238,hot=t>.20)
        bubble_field(layer,680,y-4,t,'form')
        glass_target(layer,820,920,t,crack=0)
        pp=min(1,max(0,(t-.14)/.55))
        if pp:
            for k in range(5,0,-1):
                rr=105+k*64*pp
                d.ellipse((680-rr*1.18,y-rr*.54,680+rr*1.18,y+rr*.54),fill=(210,250,255,int(9*k*pp)))
    elif stage=='first_hit':
        p=min(1,max(0,(t-.08)/.34))
        x=280+340*p; y=928-18*math.sin(t*math.pi)
        draw_club(d,x-70,y+7,ang,690,150,alpha=62,hot=False)
        draw_club(d,x,y,ang,760,182,alpha=246,hot=True)
        glass_target(layer,810,922,t,crack=max(0,min(1,(t-.18)/.35)))
        bubble_field(layer,780,922,t,'impact')
        pp=max(0,1-abs(t-.32)/.18)
        if pp:
            for k in range(6,0,-1):
                rr=46+k*50
                d.ellipse((780-rr,922-rr*.36,780+rr,922+rr*.36),fill=(255,246,190,int(16*k*pp)))
    else:
        p=min(1,max(0,t/.70))
        x=650+70*p; y=934
        draw_club(d,x,y,ang,720,156,alpha=212,hot=False)
        glass_target(layer,810,924,t,crack=.64+.24*math.sin(t*math.pi))
        bubble_field(layer,560,922,t,'collapse')
        core=max(0,1-abs(t-.56)/.28)
        if core:
            d.ellipse((560-92*core,922-58*core,560+92*core,922+58*core),fill=(255,255,238,int(170*core)))
        rnd=random.Random(12)
        for i in range(70):
            a=rnd.random()*math.tau; dist=(1-p)*(135+rnd.random()*340)+22
            x1=560+math.cos(a)*dist; y1=922+math.sin(a)*dist*.52
            x2=560+math.cos(a)*(dist-28); y2=922+math.sin(a)*(dist-28)*.52
            d.line((x1,y1,x2,y2),fill=(225,255,255,int(84*(1-p)*(rnd.random()*.7+.3))),width=2)
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
 ('03_cavitation','THAT FLASH\\nIS CAVITATION',3.92,'higgs','higgs',{'start':.05,'end':.45,'fx':.62,'fy':.44,'zoom':1.34},'higgs_bubble',(650,865)),
 ('04_first_hit','THE PUNCH\\nHITS FIRST',3.91,'higgs','higgs',{'start':.30,'end':.68,'fx':.63,'fy':.44,'zoom':1.40},'higgs_impact',(675,880)),
 ('05_second_hit','THEN THE BUBBLE\\nCOLLAPSES',3.91,'higgs','higgs',{'start':.58,'end':.98,'fx':.64,'fy':.44,'zoom':1.42},'higgs_collapse',(660,870)),
 ('06_high_speed','SCIENTISTS FILMED IT\\nIN HIGH SPEED',3.92,'montage',[1,4,5,2],{},'montage_clean',(600,960)),
 ('07_not_just_prey','IT DOES NOT JUST\\nPUNCH PREY',3.92,'video','wide',{'fx':.32,'zoom':1.0,'offset':1},'clean',(560,1000)),
 ('08_water_punches','THE WATER\\nPUNCHES TOO',3.91,'video','peacock',{'fx':.38,'zoom':1.08,'offset':8},'water',(620,950)),
]

def base_frame(mode,src,params,t):
    if mode=='video': return video(src,t,**params)
    if mode=='still': return still(src,t,**params)
    if mode=='mech': return literal_mech(src,t)
    if mode=='higgs': return higgs_plate(t, **params)
    seq=src; seg=min(len(seq)-1,int(t*len(seq))); local=(t*len(seq))%1
    return still(seq[seg],local,fx=.5,fy=.5,zoom0=1.02,zoom1=1.07,panx=(-1)**seg)

def make_frame(mode,src,params,kind,loc,t):
    im=base_frame(mode,src,params,t).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); cx,cy=loc
    if kind=='flash': soft_water_flash(layer,cx,cy,t,.26,.26)
    elif kind=='speed_clean': soft_water_flash(layer,cx-82,cy+25,t,.42,.16)
    elif kind=='montage_clean': soft_water_flash(layer,cx,cy,t,.54,.10)
    elif kind=='water': soft_water_flash(layer,cx+25,cy+10,t,.45,.18)
    elif kind=='higgs_bubble':
        soft_water_flash(layer,cx,cy,t,.50,.12)
        d=ImageDraw.Draw(layer,'RGBA'); p=min(1,max(0,(t-.10)/.70)); rr=55+165*p
        d.ellipse((cx-rr,cy-rr*.66,cx+rr,cy+rr*.66),outline=(225,252,255,int(54*(1-p*.25))),width=3)
    elif kind=='higgs_impact':
        soft_water_flash(layer,cx,cy,t,.38,.34)
        d=ImageDraw.Draw(layer,'RGBA'); p=max(0,1-abs(t-.40)/.18)
        if p:
            for k in range(5,0,-1):
                rr=38+k*45; d.ellipse((cx-rr*1.25,cy-rr*.42,cx+rr*1.25,cy+rr*.42),fill=(255,238,168,int(10*k*p)))
    elif kind=='higgs_collapse':
        soft_water_flash(layer,cx,cy,t,.55,.22)
        d=ImageDraw.Draw(layer,'RGBA'); p=min(1,max(0,(t-.10)/.72)); shock=70+360*p
        d.ellipse((cx-shock*1.18,cy-shock*.48,cx+shock*1.18,cy+shock*.48),outline=(236,255,245,int(58*(1-p))),width=5)
        core=max(0,1-abs(t-.58)/.24)
        if core: d.ellipse((cx-75*core,cy-45*core,cx+75*core,cy+45*core),fill=(255,255,238,int(80*core)))
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
    for bid,cap,dur,mode,*_ in beats:
        a,b=cap.split('\\n')
        # Keep creator-style captions, but move the 3 mechanism captions up so
        # club/bubble/impact proof is not hidden behind the words at phone size.
        pos='{\\pos(540,560)}' if mode=='mech' else ''
        lines.append(f"Dialogue: 0,{ts(cur)},{ts(cur+dur)},Caption,,0,0,0,,{pos}{{\\c&H0000D7FF&}}{a}{{\\c&H00FFFFFF&}}\\N{b}")
        cur+=dur
    path.write_text(head+'\n'.join(lines)+'\n')

idx=0; bm=[]
for bi,(bid,cap,dur,mode,src,params,kind,loc) in enumerate(beats,1):
    n=round(dur*FPS)
    bm.append({'beat':bi,'id':bid,'caption':cap.replace('\\n',' / '),'mode':mode,'source':str(src),'visual_kind':kind,'frames':n,'strategy':'real video/photos plus project-owned no-text literal 3D-style mechanism frames: club geometry, target, vapor bubble growth/collapse; no labels, cards, arrows, or generated animal bodies'})
    for f in range(n):
        make_frame(mode,src,params,kind,loc,f/max(1,n-1)).save(FRAMES/f'frame_{idx:05d}.jpg',quality=94); idx+=1
(OUT/'beat_map_v27.json').write_text(json.dumps(bm,indent=2))
ass=OUT/'captions_say_dog_v27.ass'; write_ass(ass)
silent=OUT/'mantis_say_dog_v27_higgsfield_crop_clean_silent_1080.mp4'; master=OUT/'mantis_say_dog_v27_higgsfield_crop_clean_captioned_1080.mp4'; preview=OUT/'mantis_say_dog_v27_higgsfield_crop_clean_captioned_720.mp4'; contact=OUT/'contact_sheet_mantis_say_dog_v27_higgsfield_crop_clean.jpg'
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','17','-preset','medium',str(silent)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(VOICE),'-vf',f'ass={ass}','-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview),'-vf','fps=1,scale=270:480,tile=6x6','-frames:v','1','-update','1',str(contact)],check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size,bit_rate','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate,bit_rate','-of','json',str(preview)],text=True)
(OUT/'ffprobe_preview.json').write_text(probe)
(OUT/'README_QA.md').write_text(f'''# Mantis shrimp cavitation punch — v27 Higgsfield crop-clean candidate

Status: internal candidate until contact-sheet/video QA. v27 tests the safest forward route: use a tighter crop from the verified one-credit-controlled Higgsfield plate as real-motion mechanism base, reducing the crab-claw read, with only subtle no-text emphasis and creator captions.

Built after the Higgsfield paid-test preflight and QA. v27 keeps real mantis sources for animal/context beats, uses the downloaded silent Higgsfield 480p plate for the cavitation/impact/collapse beats, and adds only subtle no-text bubble/flash/shock emphasis so captions carry the exact biology.

No new AI-generated animal bodies beyond the already-QA'd Higgsfield plate, no labels, no arrows, no diagram cards, no non-caption text. Original Higgsfield file had audio; this build uses the verified silent copy.

Outputs:
- Preview: `{preview}`
- Master: `{master}`
- Contact sheet: `{contact}`
- Beat map: `{OUT/'beat_map_v27.json'}`
''')
print(json.dumps({'preview':str(preview),'master':str(master),'contact_sheet':str(contact),'frames':idx,'ffprobe':json.loads(probe)},indent=2))
