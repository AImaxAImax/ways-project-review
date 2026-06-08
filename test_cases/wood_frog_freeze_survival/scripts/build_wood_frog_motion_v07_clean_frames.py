from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import subprocess, shutil, json, math, random, textwrap

CASE = Path('/mnt/c/dev/curious-shorts/test_cases/wood_frog_freeze_survival')
OUT = CASE / 'outputs/motion_v07_clean_frames'
FRAMES = OUT / 'frames'
SRC = CASE / 'assets/source_stills'
HOOK = CASE / 'outputs/gate2_plate_qc/feed_hook_variants_v05'
VOICE = OUT / 'voiceover.mp3'
W, H, FPS = 1080, 1920, 24
for p in [OUT]:
    p.mkdir(parents=True, exist_ok=True)
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)

FONT_CANDIDATES = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
]
FONT_PATH = next((p for p in FONT_CANDIDATES if Path(p).exists()), FONT_CANDIDATES[-1])

BEATS = [
    {'start':0.00,'end':2.40,'voiceover':'A frog can freeze solid.','caption':'A FROG CAN\nFREEZE SOLID','scene':'hook'},
    {'start':2.40,'end':5.65,'voiceover':'In winter, ice can form through much of its body.','caption':'ICE FORMS\nTHROUGH ITS BODY','scene':'freeze_body'},
    {'start':5.65,'end':8.85,'voiceover':'Its heart can stop for a while.','caption':'ITS HEART\nCAN STOP','scene':'heart_stop'},
    {'start':8.85,'end':12.40,'voiceover':'Sugar-like fluids help protect the cells.','caption':'SUGAR HELPS\nPROTECT CELLS','scene':'cells'},
    {'start':12.40,'end':17.20,'voiceover':'Then spring warms it up, and the frog starts moving again.','caption':'SPRING WARMS IT\nBACK TO LIFE','scene':'thaw'},
    {'start':17.20,'end':20.60,'voiceover':'It is not magic. It is survival chemistry.','caption':'NOT MAGIC\nSURVIVAL CHEMISTRY','scene':'final'},
]


def load(path: Path) -> Image.Image:
    return Image.open(path).convert('RGB')

ASSETS = {
    'hook': load(HOOK / 'wood_frog_hook_direct_fact_freeze_solid.jpg'),
    'split': load(HOOK / 'wood_frog_hook_contradiction_freeze_then_thaw_split.jpg'),
    'heart': load(HOOK / 'wood_frog_hook_visual_proof_heart_pause.jpg'),
    'frog1': load(SRC / 'source_01.jpg'),
    'frog2': load(SRC / 'source_02.jpg'),
    'frog3': load(SRC / 'source_03.jpg'),
    'frog4': load(SRC / 'source_04.jpg'),
    'cells': load(SRC / 'source_05_cell_protection_graphic.jpg'),
    'freeze': load(SRC / 'source_06_freeze_through_body_graphic.jpg'),
    'oldheart': load(SRC / 'source_07_heart_stop_graphic.jpg'),
}


def cover(im: Image.Image, focus_x=.5, focus_y=.5, zoom=1.0):
    iw, ih = im.size
    target = 9/16
    crop_w = int(ih * target / zoom)
    crop_h = int(ih / zoom)
    if crop_w > iw:
        crop_w = iw
        crop_h = int(iw / target)
    cx, cy = int(iw*focus_x), int(ih*focus_y)
    x = max(0, min(iw-crop_w, cx-crop_w//2))
    y = max(0, min(ih-crop_h, cy-crop_h//2))
    return im.crop((x,y,x+crop_w,y+crop_h)).resize((W,H), Image.Resampling.LANCZOS)


def grade(im: Image.Image, cold=False, warm=False):
    im = im.convert('RGB')
    if cold:
        r,g,b = im.split()
        im = Image.merge('RGB', (ImageEnhance.Brightness(r).enhance(.72), g, ImageEnhance.Brightness(b).enhance(1.22)))
        im = ImageEnhance.Color(im).enhance(.74)
    if warm:
        r,g,b = im.split()
        im = Image.merge('RGB', (ImageEnhance.Brightness(r).enhance(1.12), g, ImageEnhance.Brightness(b).enhance(.84)))
        im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.10)
    im = ImageEnhance.Sharpness(im).enhance(1.04)
    mask = Image.new('L', (W,H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-220,120,W+220,H+80), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(190))
    return Image.composite(im, Image.new('RGB',(W,H),(6,12,16)), mask)


def base_motion(im: Image.Image, t: float, fx=.50, fy=.50, zoom0=1.05, zoom1=1.13, panx=.02, pany=.0, cold=False, warm=False):
    z = zoom0 + (zoom1-zoom0)*t
    fx = max(.05, min(.95, fx + panx*math.sin(t*math.pi)))
    fy = max(.05, min(.95, fy + pany*math.sin(t*math.pi)))
    return grade(cover(im, fx, fy, z), cold=cold, warm=warm)


def frost_creep(frame: Image.Image, t: float, seed=0, strength=1.0):
    rng = random.Random(seed)
    layer = Image.new('RGBA', (W,H), (0,0,0,0))
    d = ImageDraw.Draw(layer, 'RGBA')
    # Large slow frost veins. Avoid tiny noisy speckle that reads as artifacts.
    n = int(20 + 46*t)
    for i in range(n):
        x = rng.randint(-80, W+40)
        y = rng.randint(220, H-260)
        length = rng.randint(90, 310)
        a = int((28 + 68*t) * strength * (0.55 + rng.random()*0.45))
        d.line((x,y,x+length,y-length*rng.uniform(.55,1.25)), fill=(220,250,255,a), width=rng.choice([2,3,4]))
        if rng.random() < .35:
            d.line((x+length*.55,y-length*.5,x+length*.85,y-length*.2), fill=(220,250,255,int(a*.65)), width=2)
    # cold breath/haze pulse
    for k in range(4):
        rr = 180 + k*120 + t*80
        d.ellipse((W*.48-rr,H*.48-rr*.55,W*.48+rr,H*.48+rr*.55), outline=(185,235,255,int(22*(1-t)+10)), width=5)
    layer = layer.filter(ImageFilter.GaussianBlur(.6))
    return Image.alpha_composite(frame.convert('RGBA'), layer).convert('RGB')


def thaw_warmth(frame: Image.Image, t: float):
    layer = Image.new('RGBA',(W,H),(0,0,0,0))
    d = ImageDraw.Draw(layer,'RGBA')
    # no text/icons, just warm light sweeping in
    for k in range(9):
        x0 = -260 + t*(W+520) + k*32
        d.polygon([(x0,0),(x0+180,0),(x0+20,H),(x0-190,H)], fill=(255,198,92,int(12+14*t)))
    for i in range(22):
        x = (i*163 + int(t*230)) % (W+120)-60
        y = 330 + (i*211 % 1100)
        r = 12 + (i%5)*5
        d.ellipse((x-r,y-r,x+r,y+r), outline=(210,245,225,int(18+20*t)), width=2)
    layer = layer.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(frame.convert('RGBA'), layer).convert('RGB')


def subtle_pulse_freeze(frame: Image.Image, t: float):
    layer = Image.new('RGBA',(W,H),(0,0,0,0))
    d = ImageDraw.Draw(layer,'RGBA')
    cx, cy = int(W*.55), int(H*.48)
    # Slow pulse fades down rather than medical monitor/readout.
    amp = max(0, 1-t*.95)
    for k in range(4):
        rr = 65 + k*76 + 12*math.sin(t*math.tau)
        d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr), outline=(170,230,255,int(38*amp/(k+1))), width=6)
    # freeze locks the center
    d.ellipse((cx-36,cy-36,cx+36,cy+36), fill=(195,238,255,int(50+70*t)), outline=(240,255,255,120), width=4)
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    return Image.alpha_composite(frame.convert('RGBA'), layer).convert('RGB')


def cell_motion(t: float):
    # Re-render a clean abstract cell-protection plate from scratch, avoiding labels/icons/text.
    bg = Image.new('RGB',(W,H),(10,28,36))
    pix = bg.load()
    for y in range(H):
        yy = y/H
        for x in range(0,W,3):
            xx = x/W
            val = int(18 + 44*(1-yy) + 12*math.sin(8*xx+4*yy+t*1.6))
            col = (8, max(22,min(95,val+24)), max(40,min(140,val+54)))
            for dx in range(3):
                if x+dx<W: pix[x+dx,y] = col
    im = bg.convert('RGBA')
    d = ImageDraw.Draw(im,'RGBA')
    rng = random.Random(4)
    # cells
    for i in range(9):
        cx = int((120 + i*137 + 32*math.sin(t*math.tau+i)) % (W+180)-90)
        cy = 360 + (i*223 % 940) + int(18*math.sin(t*math.tau*.7+i))
        rx = 82 + (i%3)*22; ry = 55 + (i%4)*11
        d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry), fill=(40,126,132,125), outline=(198,246,238,120), width=4)
        d.ellipse((cx-rx*.32,cy-ry*.24,cx+rx*.32,cy+ry*.24), fill=(136,220,205,75))
    # protective sugar-like fluid glow, clean organic droplets no molecular symbols
    for i in range(40):
        cx = int((rng.randrange(-80,W+80) + t*(40+i%7*5)) % (W+160)-80)
        cy = rng.randrange(300,H-270)
        r = rng.randrange(6,22)
        d.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(255,222,122,34), outline=(255,235,160,80), width=2)
    # soft focused central protection halo
    for k in range(5,0,-1):
        rr = 135 + k*78 + 16*math.sin(t*math.tau)
        d.ellipse((W/2-rr,H*.52-rr*.55,W/2+rr,H*.52+rr*.55), outline=(255,226,130,int(30/k)), width=7)
    im = im.filter(ImageFilter.GaussianBlur(.35))
    return grade(im.convert('RGB'), cold=False, warm=False)


def scene_frame(scene: str, u: float):
    if scene == 'hook':
        # v07: use a real frog base with frost motion, not the earlier translucent oval proof plate.
        # The first caption carries the impossible fact; this keeps the frame artifact-clean.
        fr = base_motion(ASSETS['frog1'], u, fx=.48, fy=.50, zoom0=1.05, zoom1=1.14, panx=.018, cold=True)
        return frost_creep(fr, u, 10, .92)
    if scene == 'freeze_body':
        fr = base_motion(ASSETS['freeze'], u, zoom0=1.04, zoom1=1.12, panx=.015, cold=True)
        return frost_creep(fr, u, 22, .9)
    if scene == 'heart_stop':
        # v07: avoid the prebuilt heart/pulse plate because the circular overlay can read as UI/artifact.
        fr = base_motion(ASSETS['frog2'], u, fx=.52, fy=.48, zoom0=1.08, zoom1=1.17, panx=-.012, cold=True)
        fr = frost_creep(fr, u, 33, .70)
        return subtle_pulse_freeze(fr, u)
    if scene == 'cells':
        return cell_motion(u)
    if scene == 'thaw':
        # start cold split then warm into real frog source; gives visible motion without AI body morphing.
        if u < .42:
            fr = base_motion(ASSETS['split'], u/.42, zoom0=1.0, zoom1=1.07, cold=False)
            return thaw_warmth(fr, u*.8)
        v=(u-.42)/.58
        fr = base_motion(ASSETS['frog4'], v, fx=.52, fy=.48, zoom0=1.08, zoom1=1.18, panx=-.018, warm=True)
        return thaw_warmth(fr, .55+.45*v)
    if scene == 'final':
        fr = base_motion(ASSETS['frog3'], u, fx=.46, fy=.48, zoom0=1.03, zoom1=1.12, panx=.015, warm=True)
        # very light residual frost melts away
        fr = frost_creep(fr, max(0,1-u)*.35, 44, .28)
        return thaw_warmth(fr, u*.55)
    return Image.new('RGB',(W,H),(0,0,0))


def caption_ass():
    def ts(sec):
        h=int(sec//3600); m=int(sec%3600//60); s=sec%60
        return f'{h}:{m:02d}:{s:05.2f}'
    lines = [
        '[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1080', 'PlayResY: 1920', '',
        '[V4+ Styles]',
        'Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding',
        'Style: Caption,DejaVu Sans Condensed,102,&H00FFFFFF,&H0000D7FF,&H00000000,&H80000000,-1,0,0,0,100,100,-1,0,1,9,4,5,70,70,690,1',
        '', '[Events]',
        'Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text'
    ]
    for b in BEATS:
        txt = b['caption'].replace('\n', r'\N')
        # yellow first key word/phrase only; no separate non-caption labels.
        parts = txt.split(r'\N')
        if parts:
            first = parts[0]
            words = first.split(' ')
            if words:
                words[0] = r'{\c&H0000D7FF&}' + words[0] + r'{\c&H00FFFFFF&}'
                parts[0] = ' '.join(words)
        txt = r'\N'.join(parts)
        lines.append(f"Dialogue: 0,{ts(b['start'])},{ts(b['end'])},Caption,,0,0,0,,{txt}")
    path = OUT / 'captions.ass'
    path.write_text('\n'.join(lines), encoding='utf-8')
    return path


def srt():
    def ts(sec):
        ms=int(round((sec-int(sec))*1000)); sec=int(sec); h=sec//3600; m=(sec%3600)//60; s=sec%60
        return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
    chunks=[]
    for i,b in enumerate(BEATS,1):
        chunks.append(f"{i}\n{ts(b['start'])} --> {ts(b['end'])}\n{b['caption']}\n")
    path=OUT/'captions.srt'; path.write_text('\n'.join(chunks), encoding='utf-8'); return path

# Render frames.
total = int(math.ceil(BEATS[-1]['end']*FPS))
for fi in range(total):
    t = fi/FPS
    b = next((bb for bb in BEATS if bb['start'] <= t < bb['end']), BEATS[-1])
    u = (t-b['start']) / max(.001, b['end']-b['start'])
    fr = scene_frame(b['scene'], u)
    # caption-safe shade band only, not a card.
    shade = Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shade,'RGBA')
    for y in range(610,1100,8):
        a=int(max(0, 46*(1-abs(y-855)/250)))
        if a: sd.rectangle((0,y,W,y+8), fill=(0,0,0,a))
    fr = Image.alpha_composite(fr.convert('RGBA'), shade).convert('RGB')
    fr.save(FRAMES/f'f_{fi:05d}.jpg', quality=93)

ass = caption_ass(); srt_path=srt()
# silent clean base
silent = OUT/'wood_frog_motion_v07_clean_1080.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate',str(FPS),'-i',str(FRAMES/'f_%05d.jpg'),'-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)], check=True)
# captioned with audio
master = OUT/'wood_frog_motion_v07_captioned_1080.mp4'
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(silent)]
if VOICE.exists():
    cmd += ['-i',str(VOICE),'-vf',f"ass={ass}",'-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.4:attack=5:release=90,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest']
else:
    cmd += ['-vf',f"ass={ass}"]
cmd += ['-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)]
subprocess.run(cmd, check=True)
preview = OUT/'wood_frog_motion_v07_captioned_720.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','slow','-crf','23','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)], check=True)
# contact sheet from master every ~2s
sheet = OUT/'contact_sheet_wood_frog_motion_v07.jpg'
thumbdir=OUT/'contact_tmp'
if thumbdir.exists(): shutil.rmtree(thumbdir)
thumbdir.mkdir()
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(master),'-vf','fps=1/2,scale=270:480:flags=lanczos',str(thumbdir/'thumb_%03d.jpg')], check=True)
thumbs=[Image.open(p).convert('RGB') for p in sorted(thumbdir.glob('thumb_*.jpg'))]
cols=4; rows=math.ceil(len(thumbs)/cols)
sheet_im=Image.new('RGB',(cols*270, rows*520),(16,18,20)); d=ImageDraw.Draw(sheet_im)
font=ImageFont.truetype(FONT_PATH, 26)
for i,th in enumerate(thumbs):
    x=(i%cols)*270; y=(i//cols)*520
    sheet_im.paste(th,(x,y)); d.text((x+10,y+486),f'{i*2:02d}s',fill=(235,235,235),font=font)
sheet_im.save(sheet, quality=94)
shutil.rmtree(thumbdir)
# specs
ffprobe = subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=index,codec_type,codec_name,width,height,sample_rate,channels','-of','json',str(master)])
(OUT/'ffprobe_captioned_master.json').write_bytes(ffprobe)
manifest = {
    'slug':'wood_frog_freeze_survival',
    'version':'v07_clean_frames_static_motion',
    'motion_policy':'deterministic source-preserving motion: zoom/pan, clean frost/thaw overlays, cell motion graphics; no AI-generated frog bodies; no paid video credits',
    'voiceover':str(VOICE.relative_to(CASE)) if VOICE.exists() else None,
    'voice_note':'Temporary/internal TTS if provider is not approved elevenlabs_george; do not publish without approved voice.',
    'beats':BEATS,
    'outputs':{
        'clean_master':str(silent.relative_to(CASE)),
        'captioned_master':str(master.relative_to(CASE)),
        'captioned_preview':str(preview.relative_to(CASE)),
        'captions_ass':str(ass.relative_to(CASE)),
        'captions_srt':str(srt_path.relative_to(CASE)),
        'contact_sheet':str(sheet.relative_to(CASE)),
        'ffprobe':str((OUT/'ffprobe_captioned_master.json').relative_to(CASE)),
    }
}
(OUT/'render_manifest_v06.json').write_text(json.dumps(manifest,indent=2), encoding='utf-8')
print(json.dumps(manifest['outputs'], indent=2))
