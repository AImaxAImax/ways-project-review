from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import subprocess, shutil, json, math, random

CASE = Path('/mnt/c/dev/curious-shorts/test_cases/wood_frog_freeze_survival')
OUT = CASE / 'outputs/motion_v09_say_dog_distinct'
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
    # Distinct proof visual: a simplified frog-body silhouette over cold water with ice forming inside.
    bg=Image.new('RGB',(W,H),(6,26,36)); pix=bg.load()
    for y in range(H):
        yy=y/H
        for x in range(0,W,3):
            xx=x/W
            wave=math.sin(7*xx+4*yy+2*u)+.5*math.sin(18*xx-3*u)
            val=int(32+75*(1-yy)+12*wave)
            col=(5,max(25,min(120,val)),max(45,min(160,val+38)))
            for dx in range(3):
                if x+dx<W: pix[x+dx,y]=col
    im=bg.convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
    cx,cy=int(W*.50),int(H*.50)
    # body silhouette, no labels/medical UI
    body=(cx-305,cy-210,cx+305,cy+210)
    d.ellipse(body,fill=(42,112,120,180),outline=(210,255,250,115),width=5)
    d.ellipse((cx-400,cy-250,cx-145,cy+10),fill=(38,104,112,160),outline=(210,255,250,85),width=4)
    d.ellipse((cx+145,cy-250,cx+400,cy+10),fill=(38,104,112,160),outline=(210,255,250,85),width=4)
    d.polygon([(cx-260,cy+150),(cx-480,cy+330),(cx-390,cy+380),(cx-145,cy+210)],fill=(38,104,112,140),outline=(210,255,250,75))
    d.polygon([(cx+260,cy+150),(cx+480,cy+330),(cx+390,cy+380),(cx+145,cy+210)],fill=(38,104,112,140),outline=(210,255,250,75))
    # ice propagates through the silhouette
    rng=random.Random(76)
    for i in range(int(22+68*u)):
        x=cx-250 + rng.random()*500; y=cy-150+rng.random()*290
        length=(80+rng.random()*260)*(.35+.65*u); ang=rng.uniform(-.95,.95)
        a=int(48+72*u)
        d.line((x,y,x+math.cos(ang)*length,y+math.sin(ang)*length*.7),fill=(228,252,255,a),width=rng.choice([2,3,4]))
    # large translucent ice volume grows, literal "through its body"
    p=min(1,u*1.15)
    d.ellipse((cx-280*p,cy-140*p,cx+280*p,cy+140*p),fill=(190,235,255,int(28+36*p)),outline=(235,255,255,105),width=4)
    return grade(im.convert('RGB'),cold=True,contrast=1.06)

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
    bg=Image.new('RGB',(W,H),(9,28,35)); pix=bg.load()
    for y in range(H):
        yy=y/H
        for x in range(0,W,3):
            xx=x/W
            val=int(18+42*(1-yy)+11*math.sin(8*xx+5*yy+u*2.1))
            col=(8,max(24,min(92,val+24)),max(42,min(140,val+56)))
            for dx in range(3):
                if x+dx<W: pix[x+dx,y]=col
    im=bg.convert('RGBA'); d=ImageDraw.Draw(im,'RGBA'); rng=random.Random(4)
    for i in range(10):
        cx=int((145+i*123+38*math.sin(u*math.tau+i))%(W+180)-90)
        cy=330+(i*217%990)+int(22*math.sin(u*math.tau*.65+i))
        rx=82+(i%3)*21; ry=56+(i%4)*10
        d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(38,126,132,130),outline=(198,246,238,130),width=4)
        d.ellipse((cx-rx*.32,cy-ry*.24,cx+rx*.32,cy+ry*.24),fill=(136,220,205,82))
    # golden sugar-like protection flows around cells
    for i in range(56):
        cx=int((rng.randrange(-120,W+120)+u*(90+i%9*10))%(W+240)-120)
        cy=rng.randrange(300,H-280)
        r=rng.randrange(7,24)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(255,222,122,38),outline=(255,238,168,88),width=2)
    for k in range(6,0,-1):
        rr=130+k*83+20*math.sin(u*math.tau)
        d.ellipse((W/2-rr,H*.52-rr*.55,W/2+rr,H*.52+rr*.55),outline=(255,226,130,int(45/k)),width=7)
    return grade(im.filter(ImageFilter.GaussianBlur(.35)).convert('RGB'),contrast=1.07)

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
    im=move(ASSETS['frog3'],u,fx=.47,fy=.48,z0=1.04,z1=1.15,px=.016,warm=True).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,'RGBA'); rng=random.Random(123)
    # clean chemistry feel without molecule diagrams/labels: protective particles orbiting the frog.
    for i in range(38):
        ang=i*.62+u*1.4; rad=180+(i%7)*42
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
        caption_text = r'\\N'.join(parts)
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
clean=OUT/'wood_frog_motion_v09_clean_1080.mp4'
master=OUT/'wood_frog_motion_v09_captioned_1080.mp4'
preview=OUT/'wood_frog_motion_v09_captioned_720.mp4'
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
sheet_path=OUT/'contact_sheet_wood_frog_motion_v09.jpg'; sheet.save(sheet_path,quality=94); shutil.rmtree(thumbdir)
ffprobe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=index,codec_type,codec_name,width,height,sample_rate,channels','-of','json',str(master)])
(OUT/'ffprobe_captioned_master.json').write_bytes(ffprobe)
manifest={'slug':'wood_frog_freeze_survival','version':'v09_say_dog_distinct','motion_policy':'deterministic source-preserving motion plus distinct proof graphics; no AI frog bodies; no paid video credits','beats':BEATS,'outputs':{'clean_master':str(clean.relative_to(CASE)),'captioned_master':str(master.relative_to(CASE)),'captioned_preview':str(preview.relative_to(CASE)),'contact_sheet':str(sheet_path.relative_to(CASE)),'captions_ass':str(ass.relative_to(CASE)),'captions_srt':str(srt.relative_to(CASE)),'ffprobe':str((OUT/'ffprobe_captioned_master.json').relative_to(CASE))}}
(OUT/'render_manifest_v09.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest['outputs'],indent=2))
