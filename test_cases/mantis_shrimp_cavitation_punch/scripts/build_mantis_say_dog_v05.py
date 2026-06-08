from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import math, json, subprocess, random, shutil, os

CASE = Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT = CASE / 'outputs/say_dog_v05_real_motion_hybrid'
FRAMES = OUT / 'frames'
SRC = OUT / 'source_frames'
CLIPS = CASE / 'outputs/wan_motion_v03_clean/clips'
VOICE = CASE / 'outputs/auto_static_v01/voiceover.mp3'
W, H, FPS = 1080, 1920, 24

beats = [
    ('01_hook_flash', 'THIS SHRIMP PUNCH\\nMAKES WATER FLASH', 3.92, 'hook_flash', 1),
    ('02_club_speed', 'ITS CLUB MOVES\\nINSANELY FAST', 3.91, 'speed_streak', 2),
    ('03_cavitation', 'THAT FLASH\\nIS CAVITATION', 3.92, 'bubble_form', 3),
    ('04_first_hit', 'THE PUNCH\\nHITS FIRST', 3.91, 'first_impact', 4),
    ('05_second_hit', 'THEN THE BUBBLE\\nCOLLAPSES', 3.91, 'bubble_collapse', 5),
    ('06_high_speed', 'SCIENTISTS FILMED IT\\nIN HIGH SPEED', 3.92, 'high_speed_strobe', 6),
    ('07_not_just_prey', 'IT DOES NOT JUST\\nPUNCH PREY', 3.92, 'prey_context', 7),
    ('08_water_punches', 'THE WATER\\nPUNCHES TOO', 3.91, 'water_second_hit', 8),
]

# Approximate impact/action loci in 1080x1920 frame for the v03 Wan plates.
LOCI = {
    1: (655, 1020), 2: (705, 1040), 3: (570, 900), 4: (550, 885),
    5: (610, 900), 6: (540, 980), 7: (680, 1030), 8: (625, 930),
}

for p in (OUT, FRAMES, SRC):
    p.mkdir(parents=True, exist_ok=True)
if FRAMES.exists(): shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)
if SRC.exists(): shutil.rmtree(SRC)
SRC.mkdir(parents=True)

# Extract the 25f clean Wan clips once, then do all compositing in PIL.
for i in range(1, 9):
    d = SRC / f'shot{i:02d}'
    d.mkdir(parents=True, exist_ok=True)
    clip = next(CLIPS.glob(f'shot{i:02d}_wan22_*.mp4'))
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', str(clip),
        '-vf', 'scale=1080:1920:flags=lanczos,fps=24', str(d / 'f_%03d.jpg')
    ], check=True)

cache: dict[int, list[Image.Image]] = {}
def get_clip(i: int) -> list[Image.Image]:
    if i not in cache:
        frames = []
        for p in sorted((SRC / f'shot{i:02d}').glob('f_*.jpg')):
            im = Image.open(p).convert('RGB')
            im = ImageEnhance.Color(im).enhance(1.04)
            im = ImageEnhance.Contrast(im).enhance(1.05)
            frames.append(im)
        cache[i] = frames
    return cache[i]

def pingpong_index(f: int, total: int, n_src: int) -> int:
    # Slow the 25-frame clip over a full beat without obvious hard loops.
    if n_src <= 1: return 0
    period = n_src * 2 - 2
    # 2.6 source-playthroughs per beat gives visible movement but not jitter.
    raw = (f / max(1, total - 1)) * period * 1.3
    k = int(raw) % period
    return k if k < n_src else period - k

def cinematic_grade(im: Image.Image, beat: int, t: float) -> Image.Image:
    im = im.convert('RGB')
    # Slight push-in/handheld drift for visible reset, preserving real-motion source.
    zoom = 1.015 + 0.055 * t
    zw, zh = int(W / zoom), int(H / zoom)
    # tiny beat-specific drift, no subject-losing pan
    dx = int((beat % 3 - 1) * 12 * math.sin(t * math.pi))
    dy = int((beat % 2) * 10 * math.sin(t * math.pi * .7))
    left = max(0, min(W - zw, (W - zw)//2 + dx))
    top = max(0, min(H - zh, (H - zh)//2 + dy))
    im = im.crop((left, top, left+zw, top+zh)).resize((W, H), Image.LANCZOS)
    # Subtle vignette and contrast; no labels/boxes.
    vign = Image.new('L', (W, H), 0)
    vd = ImageDraw.Draw(vign)
    vd.ellipse((-210, 120, W+210, H+120), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(190))
    dark = Image.new('RGB', (W, H), (0, 18, 25))
    im = Image.composite(im, dark, vign)
    return im

def add_bubbles(layer: Image.Image, cx: float, cy: float, t: float, *, scale=1.0, collapse=False, seed=0, density=42, alpha_boost=0) -> None:
    d = ImageDraw.Draw(layer, 'RGBA')
    rnd = random.Random(seed)
    for j in range(density):
        ang = rnd.random() * math.tau
        if collapse:
            dist = (1 - t) * (20 + rnd.random()*230) * scale
            rr = (2 + rnd.random()*22) * (1 - .72*t) * scale
            a = int((80 + 135*t + alpha_boost) * (0.55 + rnd.random()*0.45))
        else:
            dist = t * (25 + rnd.random()*255) * scale
            rr = (2 + rnd.random()*20) * (.25 + t) * scale
            a = int((58 + 145*(1-abs(t-.55)) + alpha_boost) * (0.55 + rnd.random()*0.45))
        x = cx + math.cos(ang)*dist + rnd.uniform(-24, 24)*scale
        y = cy + math.sin(ang)*dist*.66 + rnd.uniform(-18, 18)*scale
        if x < -50 or x > W+50 or y < -50 or y > H+50: continue
        col = (218, 252, 255, max(0, min(245, a)))
        d.ellipse((x-rr, y-rr, x+rr, y+rr), outline=col, width=max(2, int(3*scale)))
        if rr > 8:
            d.ellipse((x-rr*.35, y-rr*.5, x-rr*.05, y-rr*.18), fill=(255,255,255,min(160,a)))

def add_ripples(layer: Image.Image, cx: float, cy: float, t: float, *, maxr=360, count=4, alpha=160, squash=.58) -> None:
    d = ImageDraw.Draw(layer, 'RGBA')
    for k in range(count):
        r = maxr * (t * .86 + k * .14)
        if r < 10 or r > maxr: continue
        a = int(alpha * (1 - r/maxr))
        d.ellipse((cx-r, cy-r*squash, cx+r, cy+r*squash), outline=(210, 250, 255, a), width=7)

def add_flash(layer: Image.Image, cx: float, cy: float, t: float, *, peak=.34, strength=1.0) -> None:
    d = ImageDraw.Draw(layer, 'RGBA')
    p = max(0.0, 1 - abs(t-peak)/.22)
    if p <= 0: return
    for q in range(6, 0, -1):
        rr = (42 + q*31) * (0.72 + .55*p)
        a = int(34 * p * strength * q/6)
        d.ellipse((cx-rr, cy-rr*.58, cx+rr, cy+rr*.58), fill=(240,255,245,a))
    d.ellipse((cx-78*p, cy-42*p, cx+125*p, cy+62*p), fill=(255,255,235,int(130*p*strength)))

def add_motion_streak(layer: Image.Image, cx: float, cy: float, t: float, *, seed=0) -> None:
    d = ImageDraw.Draw(layer, 'RGBA')
    # A translucent club-path slash, integrated into footage rather than a cartoon diagram.
    p = min(1, max(0, (t-.05)/.75))
    x0, y0 = cx - 360 + 80*p, cy + 65 - 30*p
    x1, y1 = cx - 50 + 250*p, cy - 10 + 18*p
    for k in range(7):
        kk = k / 6
        a = int(80 * (1-kk) * (0.4 + .6*p))
        off = 13*k
        d.line((x0-off, y0+off*.08, x1-off*.18, y1+off*.04), fill=(255,218,120,a), width=max(6, 30-k*3))
    # tiny bright particles at the lead edge
    rnd = random.Random(seed)
    for _ in range(35):
        x = x1 + rnd.uniform(-35, 55); y = y1 + rnd.uniform(-28, 28)
        r = rnd.uniform(1.5, 4.0); a = rnd.randrange(40, 140)
        d.ellipse((x-r,y-r,x+r,y+r), fill=(240,255,255,a))

def add_crack_impact(layer: Image.Image, cx: float, cy: float, t: float) -> None:
    d = ImageDraw.Draw(layer, 'RGBA')
    p = min(1, max(0, (t-.18)/.34))
    if p <= 0: return
    add_flash(layer, cx, cy, .34, peak=.34, strength=1.25)
    for a in [-1.05,-.58,-.18,.24,.67,1.06]:
        length = 55 + 85*p
        d.line((cx, cy, cx+math.cos(a)*length, cy+math.sin(a)*length*.62), fill=(255,238,180,int(160*(1-p*.25))), width=5)
    add_ripples(layer, cx, cy, p, maxr=250, count=3, alpha=190)

def strobe_frame(clip_idx: int, t: float, total_frames: int) -> Image.Image:
    src = get_clip(clip_idx)
    # Four full-height slices from progressive instants of the strike, blended over a blurred source base.
    base = cinematic_grade(src[pingpong_index(int(t*total_frames), total_frames, len(src))], 6, t)
    bg = base.filter(ImageFilter.GaussianBlur(8))
    bg = ImageEnhance.Brightness(bg).enhance(.72)
    out = bg.convert('RGBA')
    strip_w = W // 4
    for j in range(4):
        frac = min(1, max(0, t*1.12 + (j-1.5)*.11))
        idx = min(len(src)-1, max(0, int(frac * (len(src)-1))))
        im = cinematic_grade(src[idx], 6+j, frac).convert('RGBA')
        crop = im.crop((j*strip_w, 0, (j+1)*strip_w if j<3 else W, H))
        x = j*strip_w
        out.alpha_composite(crop, (x,0))
        dd = ImageDraw.Draw(out, 'RGBA')
        if j:
            dd.rectangle((x-2,0,x+2,H), fill=(255,255,255,30))
    layer = Image.new('RGBA', (W,H), (0,0,0,0))
    cx, cy = LOCI[6]
    add_ripples(layer, cx, cy, t, maxr=430, count=5, alpha=105)
    add_bubbles(layer, cx+60, cy-40, min(1,t*1.2), scale=.75, seed=66, density=24)
    out = Image.alpha_composite(out, layer)
    return out.convert('RGB')

def make_frame(kind: str, beat: int, clip_idx: int, f: int, n: int) -> Image.Image:
    t = f / max(1, n-1)
    if kind == 'high_speed_strobe':
        return strobe_frame(clip_idx, t, n)
    src = get_clip(clip_idx)
    im = cinematic_grade(src[pingpong_index(f, n, len(src))], beat, t).convert('RGBA')
    layer = Image.new('RGBA', (W, H), (0,0,0,0))
    cx, cy = LOCI[clip_idx]
    if kind == 'hook_flash':
        add_flash(layer, cx, cy, t, peak=.28, strength=1.25)
        add_bubbles(layer, cx, cy, min(1,t*1.45), scale=1.0, seed=101, density=42, alpha_boost=10)
        if t > .28: add_ripples(layer, cx, cy, min(1,(t-.28)/.72), maxr=350, count=4, alpha=165)
    elif kind == 'speed_streak':
        add_motion_streak(layer, cx, cy, t, seed=202)
        if t > .55: add_bubbles(layer, cx+15, cy-5, (t-.55)/.45, scale=.62, seed=203, density=20)
    elif kind == 'bubble_form':
        add_bubbles(layer, cx, cy, min(1,t*1.18), scale=1.08, seed=303, density=54, alpha_boost=15)
        add_flash(layer, cx, cy, t, peak=.42, strength=.72)
    elif kind == 'first_impact':
        add_motion_streak(layer, cx+20, cy+15, min(1,t*1.15), seed=404)
        add_crack_impact(layer, cx, cy, t)
    elif kind == 'bubble_collapse':
        add_bubbles(layer, cx, cy, t, scale=1.08, collapse=True, seed=505, density=52, alpha_boost=8)
        if t > .40:
            p = (t-.40)/.60
            add_flash(layer, cx+35, cy+20, .34, peak=.34, strength=.72*(1-p))
            add_ripples(layer, cx+20, cy+15, p, maxr=405, count=5, alpha=220)
    elif kind == 'prey_context':
        add_bubbles(layer, cx-35, cy+40, .72 + .18*math.sin(t*math.pi), scale=.42, seed=707, density=16)
        # Only environmental motion, no diagram marks.
        if t > .62: add_ripples(layer, cx-120, cy+40, (t-.62)/.38, maxr=180, count=2, alpha=65)
    elif kind == 'water_second_hit':
        add_bubbles(layer, cx-45, cy+10, min(1,t*1.28), scale=.85, seed=808, density=38)
        if t > .34:
            p = (t-.34)/.66
            add_bubbles(layer, cx+45, cy+15, p, scale=.92, collapse=True, seed=809, density=42, alpha_boost=22)
            add_ripples(layer, cx+45, cy+15, p, maxr=470, count=6, alpha=230)
            add_flash(layer, cx+45, cy+15, .34, peak=.34, strength=.68*(1-p*.2))
    # Composite and add very subtle lower contrast behind central captions only via gradient, not a box.
    im = Image.alpha_composite(im, layer)
    grad = Image.new('RGBA', (W,H), (0,0,0,0))
    gd = ImageDraw.Draw(grad, 'RGBA')
    for y in range(650, 1220, 8):
        dist = abs(y-930)/285
        a = int(max(0, 38*(1-dist)))
        gd.rectangle((0,y,W,y+8), fill=(0,0,0,a))
    im = Image.alpha_composite(im, grad)
    return im.convert('RGB')

def write_ass(path: Path):
    def ts(t: float) -> str:
        h = int(t//3600); m = int((t%3600)//60); s = t%60
        return f'{h}:{m:02d}:{s:05.2f}'
    head = """[Script Info]
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
"""
    lines = []
    cur = 0.0
    for _, cap, dur, _, _ in beats:
        a, b = cap.split('\\n')
        # Static keyword-highlight style matching prior WAYS captions.
        text = r'{\c&H0000D7FF&}' + a + r'{\c&H00FFFFFF&}\N' + b
        lines.append(f'Dialogue: 0,{ts(cur)},{ts(cur+dur)},Caption,,0,0,0,,{text}')
        cur += dur
    path.write_text(head + '\n'.join(lines) + '\n')

idx = 0
beat_map = []
for bi, (bid, cap, dur, kind, clip_idx) in enumerate(beats, 1):
    n = round(dur * FPS)
    beat_map.append({
        'beat': bi,
        'id': bid,
        'caption': cap.replace('\\n',' / '),
        'visual_kind': kind,
        'source_clip': clip_idx,
        'frames': n,
        'qa_intent': 'real v03 Wan motion base plus no-text cavitation/impact overlay'
    })
    for f in range(n):
        im = make_frame(kind, bi, clip_idx, f, n)
        im.save(FRAMES / f'frame_{idx:05d}.jpg', quality=93)
        idx += 1

(OUT / 'beat_map_v05.json').write_text(json.dumps(beat_map, indent=2))
ass = OUT / 'captions_say_dog_v05.ass'
write_ass(ass)
silent = OUT / 'mantis_say_dog_v05_silent_1080.mp4'
master = OUT / 'mantis_say_dog_v05_captioned_1080.mp4'
preview = OUT / 'mantis_say_dog_v05_captioned_720.mp4'
contact = OUT / 'contact_sheet_mantis_say_dog_v05.jpg'

subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','17','-preset','medium',str(silent)], check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(VOICE),'-vf',f'ass={ass}', '-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1', '-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)], check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)], check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview),'-vf','fps=1,scale=270:480,tile=6x6','-frames:v','1','-update','1',str(contact)], check=True)
probe = subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size,bit_rate','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate,bit_rate','-of','json',str(preview)], text=True)
(OUT / 'ffprobe_preview.json').write_text(probe)
(OUT / 'README_QA.md').write_text(f"""# Mantis shrimp cavitation punch — v05 real-motion hybrid

Status: internal finalist candidate, pending harsh visual QA.

Intent: combine v03's real-looking Wan motion base with v04's say-dog-see-dog mechanism clarity. This version removes the cartoon/schematic teal proof shots from v04 and uses no non-caption text. Cavitation/impact/bubble-collapse are shown as project-owned no-text overlays on top of the real-motion mantis footage, so it is still a fallback visualization rather than actual licensed high-speed footage.

Outputs:
- Preview: `{preview}`
- Master: `{master}`
- Silent clean: `{silent}`
- Contact sheet: `{contact}`
- Beat map: `{OUT/'beat_map_v05.json'}`
""")
print(json.dumps({'preview': str(preview), 'master': str(master), 'contact_sheet': str(contact), 'frames': idx, 'ffprobe': json.loads(probe)}, indent=2))
