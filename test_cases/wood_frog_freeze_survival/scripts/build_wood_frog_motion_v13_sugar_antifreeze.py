from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import subprocess, shutil, json, math, random

CASE = Path('/mnt/c/dev/curious-shorts/test_cases/wood_frog_freeze_survival')
OUT = CASE / 'outputs/motion_v13_sugar_antifreeze'
FRAMES = OUT / 'frames'
SRC = CASE / 'assets/source_stills'
VOICE_SRC = CASE / 'outputs/static_motion_v06_artifact_clean/voiceover.mp3'
VOICE = OUT / 'voiceover.mp3'
W, H, FPS = 1080, 1920, 24
for p in [OUT]: p.mkdir(parents=True, exist_ok=True)
if VOICE_SRC.exists() and not VOICE.exists(): shutil.copy2(VOICE_SRC, VOICE)
if FRAMES.exists(): shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
if not Path(FONT_PATH).exists(): FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

# v09: each VO line gets a different visual proof language.
BEATS = [
    {'start':0.00,'end':2.35,'voiceover':'A frog can freeze solid.','caption':'A FROG CAN\nFREEZE SOLID','scene':'frozen_frog_hero','must_show':'real frog visibly freezing, no generated animal body'},
    {'start':2.35,'end':5.75,'voiceover':'In winter, ice can form through much of its body.','caption':'ICE FORMS\nTHROUGH ITS BODY','scene':'body_ice_cutaway','must_show':'ice/frost spreading through a frog-body silhouette'},
    {'start':5.75,'end':8.85,'voiceover':'Its heart can stop for a while.','caption':'ITS HEART\nCAN STOP','scene':'heart_stop_proof','must_show':'heart/pulse glow fading into stillness, no UI/readout'},
    {'start':8.85,'end':12.45,'voiceover':'Sugar-like fluids help protect the cells.','caption':'SUGAR HELPS\nPROTECT CELLS','scene':'cell_protection','must_show':'cells surrounded by golden protective fluid/droplets'},
    {'start':12.45,'end':16.90,'voiceover':'Then spring warms it up, and the frog starts moving again.','caption':'SPRING WARMS IT\nBACK TO LIFE','scene':'spring_thaw_movement','must_show':'warmth returns and frog/leaf scene shifts from cold to active spring'},
    {'start':16.90,'end':20.60,'voiceover':'It is not magic. It is survival chemistry.','caption':'NOT MAGIC\nSURVIVAL CHEMISTRY','scene':'chemistry_hero','must_show':'real frog hero plus clean chemistry-like protective particles, no labels'},
]

def load(name): return Image.open(SRC/name).convert('RGB')
ASSETS = {
    'frog1': load('source_01.jpg'),
    'frog2': load('source_02.jpg'),
    'frog3': load('source_03.jpg'),
    'frog4': load('source_04.jpg'),
}

def cover(im, fx=.5, fy=.5, zoom=1.0):
    iw, ih = im.size; target = 9/16
    crop_w = int(ih*target/zoom); crop_h = int(ih/zoom)
    if crop_w > iw:
        crop_w = iw; crop_h = int(iw/target)
    cx, cy = int(iw*fx), int(ih*fy)
    x = max(0, min(iw-crop_w, cx-crop_w//2)); y = max(0, min(ih-crop_h, cy-crop_h//2))
    return im.crop((x,y,x+crop_w,y+crop_h)).resize((W,H), Image.Resampling.LANCZOS)

def grade(im, cold=False, warm=False, contrast=1.10):
    im = im.convert('RGB')
    if cold:
        r,g,b = im.split(); im = Image.merge('RGB',(ImageEnhance.Brightness(r).enhance(.68), ImageEnhance.Brightness(g).enhance(.90), ImageEnhance.Brightness(b).enhance(1.28)))
        im = ImageEnhance.Color(im).enhance(.72)
    if warm:
        r,g,b = im.split(); im = Image.merge('RGB',(ImageEnhance.Brightness(r).enhance(1.15), ImageEnhance.Brightness(g).enhance(1.05), ImageEnhance.Brightness(b).enhance(.82)))
        im = ImageEnhance.Color(im).enhance(1.16)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Sharpness(im).enhance(1.06)
    mask = Image.new('L',(W,H),0); d=ImageDraw.Draw(mask); d.ellipse((-230,110,W+230,H+70),fill=255); mask=mask.filter(ImageFilter.GaussianBlur(185))
    return Image.composite(im, Image.new('RGB',(W,H),(4,10,14)), mask)

def move(im, u, fx=.5, fy=.5, z0=1.05, z1=1.16, px=.015, py=0, cold=False, warm=False):
    z=z0+(z1-z0)*u
    fx=max(.05,min(.95,fx+px*math.sin(u*math.pi)))
    fy=max(.05,min(.95,fy+py*math.sin(u*math.pi)))
    return grade(cover(im,fx,fy,z),cold=cold,warm=warm)

def add_caption_shade(im):
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    for y in range(610,1100,8):
        a=int(max(0,46*(1-abs(y-855)/255)))
        if a: d.rectangle((0,y,W,y+8),fill=(0,0,0,a))
    for y in range(H):
        a=int(25*(abs(y-H/2)/(H/2))**2)
        if a: d.line((0,y,W,y),fill=(0,0,0,a))
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def frost_lines(im, u, seed=1, amount=1.0, center=(.5,.5)):
    rng=random.Random(seed); layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    cx,cy=int(W*center[0]),int(H*center[1])
    # broad ice veins radiating/spreading. Keeps artifact-clean by avoiding tiny glitter.
    for i in range(int(18+52*u*amount)):
        ang=-2.5 + i*(5.0/(18+52*u*amount)) + rng.uniform(-.12,.12)
        start=30+rng.random()*130; length=(150+rng.random()*420)*(0.35+0.65*u)
        x1=cx+math.cos(ang)*start; y1=cy+math.sin(ang)*start*.70
        x2=cx+math.cos(ang)*(start+length); y2=cy+math.sin(ang)*(start+length)*.70
        a=int((40+60*u)*amount*(.55+rng.random()*.45))
        d.line((x1,y1,x2,y2),fill=(220,250,255,a),width=rng.choice([2,3,4]))
        if rng.random()<.40:
            mx=(x1+x2)/2; my=(y1+y2)/2
            d.line((mx,my,mx+math.cos(ang+.62)*length*.28,my+math.sin(ang+.62)*length*.20),fill=(220,250,255,int(a*.55)),width=2)
    return Image.alpha_composite(im.convert('RGBA'),layer.filter(ImageFilter.GaussianBlur(.45))).convert('RGB')

def frozen_frog_hero(u):
    im=move(ASSETS['frog1'],u,fx=.49,fy=.50,z0=1.04,z1=1.14,px=.014,cold=True)
    im=frost_lines(im,u,10,.75,center=(.50,.50))
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    # icy edge creeping in from frame edges, not an oval card.
    for k in range(5):
        a=int(16+18*u)
        d.rounded_rectangle((20+k*10,210+k*20,W-20-k*8,H-230-k*15),radius=70,outline=(200,238,255,a),width=5)
    return Image.alpha_composite(im.convert('RGBA'),layer.filter(ImageFilter.GaussianBlur(2))).convert('RGB')

def body_ice_cutaway(u):
    # v10: more say-dog-see-dog without the crude geometric silhouette from v09.
    # Uses a real frog body plate with a clean internal ice-field overlay: ice forms THROUGH the body.
    im = move(ASSETS['frog4'], u, fx=.50, fy=.50, z0=1.02, z1=1.12, px=.010, cold=True).convert('RGBA')
    layer = Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    cx,cy=int(W*.50),int(H*.50)
    # Soft body-area glow, organic not a card.
    p=min(1,u*1.12)
    for k in range(6,0,-1):
        rx=(120+k*48)*p; ry=(75+k*30)*p
        d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(190,235,255,int(6*k+8*p)),outline=(235,255,255,int(14*k*p)),width=3)
    # Ice veins spreading inside and across the torso.
    rng=random.Random(76)
    for i in range(int(24+78*u)):
        base_ang = -0.85 + (i/(24+78*u))*1.7
        x = cx-230 + rng.random()*460
        y = cy-130 + rng.random()*260
        length = (70+rng.random()*280)*(.35+.65*u)
        ang = base_ang + rng.uniform(-.45,.45)
        a=int(45+82*u)
        d.line((x,y,x+math.cos(ang)*length,y+math.sin(ang)*length*.55),fill=(228,252,255,a),width=rng.choice([2,3,4]))
        if rng.random()<.45:
            mx=x+math.cos(ang)*length*.55; my=y+math.sin(ang)*length*.30
            d.line((mx,my,mx+math.cos(ang-.65)*length*.30,my+math.sin(ang-.65)*length*.18),fill=(228,252,255,int(a*.55)),width=2)
    # Cold breath / frozen body volume pulse.
    for k in range(4):
        rr=140+k*92+20*math.sin(u*math.tau)
        d.ellipse((cx-rr,cy-rr*.55,cx+rr,cy+rr*.55),outline=(200,240,255,int(34/(k+1))),width=5)
    composed = Image.alpha_composite(im,layer.filter(ImageFilter.GaussianBlur(.7))).convert('RGB')
    if u < .35:
        return composed
    # hard visual reset inside the same caption beat: external frog body -> inside-body ice network
    v=(u-.35)/.65
    macro=internal_ice_macro(v)
    return Image.blend(composed, macro, min(1,v*1.4))


def internal_ice_macro(u):
    # Second half of "ice forms through its body": a fully different inside-body ice network shot.
    bg=Image.new('RGB',(W,H),(5,18,30)); pix=bg.load()
    for y in range(H):
        yy=y/H
        for x in range(0,W,3):
            xx=x/W
            val=int(28+88*(1-yy)+16*math.sin(9*xx+6*yy+u*2.6))
            col=(5,max(25,min(125,val)),max(60,min(180,val+54)))
            for dx in range(3):
                if x+dx<W: pix[x+dx,y]=col
    im=bg.convert('RGBA'); d=ImageDraw.Draw(im,'RGBA'); rng=random.Random(177)
    # Big clean crystalline channels, not speckles.
    for i in range(34):
        x=rng.randrange(-90,W+90); y=rng.randrange(250,H-250)
        length=rng.randrange(180,620); ang=rng.uniform(-.9,.9)
        a=rng.randrange(62,122)
        d.line((x,y,x+math.cos(ang)*length,y+math.sin(ang)*length*.58),fill=(225,252,255,a),width=rng.choice([3,4,5]))
        for j in range(2):
            b=x+math.cos(ang)*length*(.35+j*.25); c=y+math.sin(ang)*length*.58*(.35+j*.25)
            d.line((b,c,b+math.cos(ang+(.55 if j%2 else -.55))*length*.25,c+math.sin(ang+(.55 if j%2 else -.55))*length*.14),fill=(225,252,255,int(a*.55)),width=2)
    for k in range(5):
        rr=180+k*115+20*math.sin(u*math.tau)
        d.ellipse((W*.52-rr,H*.50-rr*.50,W*.52+rr,H*.50+rr*.50),outline=(220,250,255,int(28/(k+1))),width=6)
    return grade(im.filter(ImageFilter.GaussianBlur(.3)).convert('RGB'),cold=True,contrast=1.05)

def heart_stop_proof(u):
    im=move(ASSETS['frog2'],u,fx=.58,fy=.44,z0=1.16,z1=1.26,px=-.010,cold=True)
    im=frost_lines(im,u,34,.55,center=(.56,.47)).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    cx,cy=int(W*.54),int(H*.46)
    beat=max(0, math.sin((1-u)*math.pi*4))*(1-u)
    heart_alpha=int(150*(1-u)+25)
    # organic heart glow shrinks/fades, not an ECG/readout.
    points=[]
    for i in range(80):
        a=math.tau*i/80
        r=1-math.sin(a)
        x=16*math.sin(a)**3
        y=-(13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a))
        scale=8.6+8*beat-2.8*u
        points.append((cx+x*scale,cy+y*scale))
    d.polygon(points,fill=(255,78,78,heart_alpha),outline=(255,210,190,int(115*(1-u)+30)))
    for k in range(4):
        rr=90+k*72+beat*45
        d.ellipse((cx-rr,cy-rr*.72,cx+rr,cy+rr*.72),outline=(185,235,255,int((50*(1-u))/(k+1))),width=5)
    # final still ice lock
    if u>.62:
        p=(u-.62)/.38
        d.ellipse((cx-62*p,cy-44*p,cx+62*p,cy+44*p),fill=(218,248,255,int(80*p)),outline=(245,255,255,int(120*p)),width=4)
    return Image.alpha_composite(im,layer.filter(ImageFilter.GaussianBlur(.8))).convert('RGB')

def cell_protection(u):
    # v13: make "sugar helps protect cells" read as antifreeze chemistry, not generic bubbles.
    # Visual grammar: blue ice crystals stay outside, gold glucose-rich fluid flows around intact cells.
    split = u >= .48
    v = (u-.48)/.52 if split else u/.48
    bg=Image.new('RGB',(W,H),(8,24,34)); pix=bg.load()
    for y in range(H):
        yy=y/H
        for x in range(0,W,3):
            xx=x/W
            # cold blue tissue-fluid base with subtle current
            wave=math.sin(8*xx+4*yy+u*2.4)+.55*math.sin(19*xx-3.1*u)
            val=int(22+54*(1-yy)+13*wave)
            col=(7,max(22,min(95,val+22)),max(45,min(150,val+58)))
            for dx in range(3):
                if x+dx<W: pix[x+dx,y]=col
    im=bg.convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
    # Cold ice crystals advance from top/sides, but stop at gold-protected cell halos.
    rng=random.Random(513)
    ice_front = 0.22 + .46*min(1,u*1.15)
    for i in range(36):
        side = rng.choice(['top','left','right'])
        if side == 'top':
            x=rng.randrange(-80,W+80); y=230+rng.randrange(0,int(520*ice_front))
            ang=math.pi/2+rng.uniform(-.45,.45)
        elif side == 'left':
            x=rng.randrange(-80,int(230+280*ice_front)); y=rng.randrange(320,H-280)
            ang=rng.uniform(-.25,.65)
        else:
            x=rng.randrange(int(W-230-280*ice_front),W+80); y=rng.randrange(320,H-280)
            ang=math.pi+rng.uniform(-.65,.25)
        length=rng.randrange(90,260)
        a=rng.randrange(44,92)
        d.line((x,y,x+math.cos(ang)*length,y+math.sin(ang)*length*.72),fill=(222,250,255,a),width=rng.choice([3,4,5]))
        d.line((x+math.cos(ang)*length*.55,y+math.sin(ang)*length*.40,x+math.cos(ang+.7)*length*.78,y+math.sin(ang+.7)*length*.35),fill=(222,250,255,int(a*.46)),width=2)
    # Cells: wide first, macro second, with clear gold protective rings.
    if not split:
        cells=[(W*.34,H*.43,128,78),(W*.63,H*.45,118,72),(W*.47,H*.64,138,82),(W*.68,H*.68,112,66)]
        flow=0.25+0.75*v
    else:
        # hard reset to macro: the claim is now unmistakably cells + protective fluid.
        cells=[(W*.37,H*.46,215,132),(W*.65,H*.58,195,118)]
        flow=1.0
    for j,(cx,cy,rx,ry) in enumerate(cells):
        wob=10*math.sin(u*math.tau+j*.9)
        # Gold glucose-like fluid halo/shield
        for k in range(5,0,-1):
            grow=(k*18 + 24*math.sin(u*math.tau+j)) * flow
            d.ellipse((cx-rx-grow,cy-ry-grow*.72+wob,cx+rx+grow,cy+ry+grow*.72+wob),outline=(255,214,78,int(34+13*k)),width=5)
        d.ellipse((cx-rx,cy-ry+wob,cx+rx,cy+ry+wob),fill=(38,126,130,155),outline=(205,250,238,145),width=6)
        d.ellipse((cx-rx*.34,cy-ry*.28+wob,cx+rx*.34,cy+ry*.28+wob),fill=(130,218,200,90))
        # A few gold droplets entering/around membrane
        for m in range(10 if split else 6):
            ang=m*math.tau/(10 if split else 6)+u*math.tau*.45+j
            rr=rx+35+18*math.sin(u*math.tau+m)
            x=cx+math.cos(ang)*rr; y=cy+math.sin(ang)*rr*.62+wob
            r=9+(m%3)*4 if split else 6+(m%3)*3
            d.ellipse((x-r,y-r,x+r,y+r),fill=(255,214,86,92),outline=(255,238,150,135),width=2)
    # Gold fluid stream crossing frame, unlike the prior random droplet field.
    for band in range(7):
        pts=[]
        y0=520+band*120+22*math.sin(u*math.tau+band)
        for x in range(-80,W+100,80):
            y=y0+34*math.sin(x*.007+u*2.6+band)
            pts.append((x,y))
        for a,b in zip(pts,pts[1:]):
            d.line((a[0],a[1],b[0],b[1]),fill=(255,204,68,int(34+20*flow)),width=9 if split else 6)
    # Darken edges so captions pop, no cards or labels.
    shade=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shade,'RGBA')
    for y in range(H):
        edge=(abs(y-H/2)/(H/2))**1.7
        a=int(34*edge)
        if a: sd.line((0,y,W,y),fill=(0,0,0,a))
    im=Image.alpha_composite(im,shade)
    return grade(im.filter(ImageFilter.GaussianBlur(.25)).convert('RGB'),contrast=1.09)

def spring_thaw_movement(u):
    # Visibly different: cold frog closeup thawing into warm leaf-litter frog, with moving light and droplets.
    cold=move(ASSETS['frog2'],min(1,u*1.2),fx=.53,fy=.48,z0=1.11,z1=1.17,px=.008,cold=True)
    warm=move(ASSETS['frog4'],max(0,(u-.12)/.88),fx=.50,fy=.49,z0=1.07,z1=1.22,px=-.020,warm=True)
    alpha=min(1,max(0,(u-.16)/.46))
    im=Image.blend(cold,warm,alpha).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    # warm sweep + water droplets = thaw/action, no arrows or text.
    for k in range(10):
        x0=-340+u*(W+680)+k*40
        d.polygon([(x0,0),(x0+180,0),(x0+18,H),(x0-210,H)],fill=(255,196,83,int(12+22*u)))
    rng=random.Random(99)
    for i in range(30):
        x=(rng.randrange(-80,W+80)+int(u*(120+i*7)))%(W+160)-80
        y=rng.randrange(260,H-260)
        r=rng.randrange(7,21)
        d.ellipse((x-r,y-r,x+r,y+r),outline=(195,245,230,int(20+35*u)),width=2)
    # tiny foreground leaf parallax silhouettes to sell movement
    for i in range(7):
        x=(i*190-int(u*85))%(W+120)-60; y=1320+(i*73%250)
        d.ellipse((x-70,y-18,x+70,y+18),fill=(38,72,38,int(28+36*u)))
    return Image.alpha_composite(im,layer.filter(ImageFilter.GaussianBlur(4))).convert('RGB')

def chemistry_hero(u):
    if u < .55:
        im=move(ASSETS['frog3'],u/.55,fx=.47,fy=.48,z0=1.04,z1=1.14,px=.016,warm=True).convert('RGBA')
        v=u/.55
    else:
        # second final reset: different warm frog crop/source so the ending is not two near-identical holds.
        v=(u-.55)/.45
        im=move(ASSETS['frog1'],v,fx=.56,fy=.47,z0=1.18,z1=1.31,px=-.012,warm=True).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA')
    for i in range(42):
        ang=i*.62+u*1.7; rad=160+(i%7)*42
        x=W*.54+math.cos(ang)*rad; y=H*.50+math.sin(ang)*rad*.56
        r=6+(i%4)*3; a=38+(i%3)*18
        d.ellipse((x-r,y-r,x+r,y+r),fill=(255,218,94,a),outline=(255,240,165,a+20),width=2)
    for k in range(4):
        rr=180+k*92+20*math.sin(u*math.tau)
        d.ellipse((W*.54-rr,H*.50-rr*.52,W*.54+rr,H*.50+rr*.52),outline=(255,224,112,int(32/(k+1))),width=5)
    return Image.alpha_composite(im,layer.filter(ImageFilter.GaussianBlur(1.1))).convert('RGB')

def frame_for(scene,u):
    return {
        'frozen_frog_hero': frozen_frog_hero,
        'body_ice_cutaway': body_ice_cutaway,
        'heart_stop_proof': heart_stop_proof,
        'cell_protection': cell_protection,
        'spring_thaw_movement': spring_thaw_movement,
        'chemistry_hero': chemistry_hero,
    }[scene](u)

def write_captions():
    def ts(sec):
        h=int(sec//3600); m=int(sec%3600//60); s=sec%60
        return f'{h}:{m:02d}:{s:05.2f}'
    lines=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','','[V4+ Styles]',
        'Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding',
        'Style: Caption,DejaVu Sans Condensed,102,&H00FFFFFF,&H0000D7FF,&H00000000,&H80000000,-1,0,0,0,100,100,-1,0,1,9,4,5,70,70,690,1',
        '','[Events]','Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text']
    for b in BEATS:
        parts=b['caption'].replace('\n',r'\N').split(r'\N')
        w=parts[0].split(' '); w[0]=r'{\c&H0000D7FF&}'+w[0]+r'{\c&H00FFFFFF&}'; parts[0]=' '.join(w)
        caption_text = r'\N'.join(parts)
        lines.append(f"Dialogue: 0,{ts(b['start'])},{ts(b['end'])},Caption,,0,0,0,,{caption_text}")
    ass=OUT/'captions.ass'; ass.write_text('\n'.join(lines),encoding='utf-8')
    def srt_ts(sec):
        ms=int(round((sec-int(sec))*1000)); sec=int(sec); h=sec//3600; m=(sec%3600)//60; s=sec%60
        return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
    chunks=[]
    for i,b in enumerate(BEATS,1): chunks.append(f"{i}\n{srt_ts(b['start'])} --> {srt_ts(b['end'])}\n{b['caption']}\n")
    srt=OUT/'captions.srt'; srt.write_text('\n'.join(chunks),encoding='utf-8')
    return ass,srt

# render frames
total=int(math.ceil(BEATS[-1]['end']*FPS))
for fi in range(total):
    t=fi/FPS
    b=next((bb for bb in BEATS if bb['start'] <= t < bb['end']), BEATS[-1])
    u=(t-b['start'])/max(.001,b['end']-b['start'])
    fr=add_caption_shade(frame_for(b['scene'],u))
    fr.save(FRAMES/f'f_{fi:05d}.jpg',quality=93)
ass,srt=write_captions()
clean=OUT/'wood_frog_motion_v13_clean_1080.mp4'
master=OUT/'wood_frog_motion_v13_captioned_1080.mp4'
preview=OUT/'wood_frog_motion_v13_captioned_720.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate',str(FPS),'-i',str(FRAMES/'f_%05d.jpg'),'-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(clean)],check=True)
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(clean)]
if VOICE.exists():
    cmd += ['-i',str(VOICE),'-vf',f'ass={ass}','-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.4:attack=5:release=90,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest']
else:
    cmd += ['-vf',f'ass={ass}']
cmd += ['-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)]
subprocess.run(cmd,check=True)
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','slow','-crf','23','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
# contact sheet
thumbdir=OUT/'contact_tmp';
if thumbdir.exists(): shutil.rmtree(thumbdir)
thumbdir.mkdir()
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(master),'-vf','fps=1/2,scale=270:480:flags=lanczos',str(thumbdir/'thumb_%03d.jpg')],check=True)
thumbs=[Image.open(p).convert('RGB') for p in sorted(thumbdir.glob('thumb_*.jpg'))]
cols=4; rows=math.ceil(len(thumbs)/cols)
sheet=Image.new('RGB',(cols*270,rows*520),(16,18,20)); d=ImageDraw.Draw(sheet); font=ImageFont.truetype(FONT_PATH,26)
for i,th in enumerate(thumbs):
    x=(i%cols)*270; y=(i//cols)*520; sheet.paste(th,(x,y)); d.text((x+10,y+486),f'{i*2:02d}s',fill=(235,235,235),font=font)
sheet_path=OUT/'contact_sheet_wood_frog_motion_v13.jpg'; sheet.save(sheet_path,quality=94); shutil.rmtree(thumbdir)
ffprobe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=index,codec_type,codec_name,width,height,sample_rate,channels','-of','json',str(master)])
(OUT/'ffprobe_captioned_master.json').write_bytes(ffprobe)
manifest={'slug':'wood_frog_freeze_survival','version':'v13_sugar_antifreeze','motion_policy':'deterministic source-preserving motion plus distinct proof graphics; no AI frog bodies; no paid video credits','beats':BEATS,'outputs':{'clean_master':str(clean.relative_to(CASE)),'captioned_master':str(master.relative_to(CASE)),'captioned_preview':str(preview.relative_to(CASE)),'contact_sheet':str(sheet_path.relative_to(CASE)),'captions_ass':str(ass.relative_to(CASE)),'captions_srt':str(srt.relative_to(CASE)),'ffprobe':str((OUT/'ffprobe_captioned_master.json').relative_to(CASE))}}
(OUT/'render_manifest_v09.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest['outputs'],indent=2))
