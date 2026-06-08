from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, subprocess, json, datetime, shutil

ROOT = Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
OUTDIR = ROOT / 'outputs' / 'motion_probe_v26_final_predator_audio'
FRAMEDIR = OUTDIR / 'frames'
OUTDIR.mkdir(parents=True, exist_ok=True)
if FRAMEDIR.exists():
    shutil.rmtree(FRAMEDIR)
FRAMEDIR.mkdir(parents=True)

W, H = 1080, 1920
FPS = 24
BG = (5, 9, 12)

# Current curated still set. Shot 1 and final predator are from GPT Image 2 manual v23; shots 2-6 from v24. Durations slightly stretched to selected VO length.
SHOTS = [
    {
        'id':'01',
        'path': ROOT/'assets/gpt_image_2_manual_v23/shot01_gpt_image2_hook_before_trees_v01.jpeg',
        'duration':3.570,
        'caption':'SHARKS WERE HERE\nBEFORE TREES',
        'move':'slow_push_low',
        'note':'ancient ocean hook'
    },
    {
        'id':'02',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot02_seriously_fossil_proof_v01.jpeg',
        'duration':2.303,
        'caption':'SERIOUSLY.',
        'move':'macro_push',
        'note':'fossil proof close-up'
    },
    {
        'id':'03',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot03_apple_squirrel_nut_v01.jpeg',
        'duration':3.685,
        'caption':'BEFORE APPLES.\nBEFORE SQUIRRELS.',
        'move':'tiny_pan_right',
        'note':'literal gag objects'
    },
    {
        'id':'04',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot04_deep_time_rock_layers_sharks_v01.jpeg',
        'duration':3.570,
        'caption':'OVER 400 MILLION\nYEARS AGO',
        'move':'vertical_reveal',
        'note':'deep-time geology timeline'
    },
    {
        'id':'05',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot05_first_trees_coastline_v01.jpeg',
        'duration':3.225,
        'caption':'THEN FORESTS\nFINALLY ARRIVED',
        'move':'slow_push_high',
        'note':'first forest/land change'
    },
    {
        'id':'06',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot06_kid_aquarium_deep_time_v01.jpeg',
        'duration':3.685,
        'caption':'AND TODAY...\nTHEY ARE STILL HERE',
        'move':'aquarium_push',
        'note':'modern viewer/aquarium wonder'
    },
    {
        'id':'07',
        'path': ROOT/'assets/gpt_image_2_manual_v23/04_final_predator_got_here_first.png',
        'duration':3.916,
        'caption':'SURVIVOR\nFROM A WORLD\nBEFORE FORESTS',
        'move':'final_hold',
        'note':'final predator got here first image, matched to survivor caption'
    },
]

font_candidates = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
]
FONT_PATH = next((p for p in font_candidates if Path(p).exists()), None)
FONT_BIG = ImageFont.truetype(FONT_PATH, 72) if FONT_PATH else ImageFont.load_default()
FONT_SMALL = ImageFont.truetype(FONT_PATH, 42) if FONT_PATH else ImageFont.load_default()


def ease(t):
    return 3*t*t - 2*t*t*t


def cover_crop_params(img_w, img_h, scale, cx, cy):
    # Crop window in source pixels that will cover W x H after resizing.
    crop_w = min(img_w, int(img_w / scale))
    crop_h = min(img_h, int(crop_w * H / W))
    if crop_h > img_h:
        crop_h = min(img_h, int(img_h / scale))
        crop_w = int(crop_h * W / H)
    x = int(cx * (img_w - crop_w))
    y = int(cy * (img_h - crop_h))
    x = max(0, min(img_w - crop_w, x))
    y = max(0, min(img_h - crop_h, y))
    return (x, y, x+crop_w, y+crop_h)


def motion_params(move, u):
    e = ease(u)
    # scale is gentle: 1.00-1.075 max. No AI wobble.
    if move == 'slow_push_low':
        return 1.00 + 0.055*e, 0.50, 0.42 + 0.05*e
    if move == 'macro_push':
        return 1.02 + 0.070*e, 0.50, 0.52
    if move == 'tiny_pan_right':
        return 1.035, 0.43 + 0.14*e, 0.50
    if move == 'vertical_reveal':
        return 1.04, 0.50, 0.33 + 0.18*e
    if move == 'slow_push_high':
        return 1.00 + 0.055*e, 0.50, 0.42
    if move == 'aquarium_push':
        return 1.01 + 0.060*e, 0.50, 0.50
    if move == 'final_hold':
        return 1.00 + 0.035*e, 0.50, 0.47
    return 1.0, 0.5, 0.5


def draw_caption(frame, text, shot_id):
    draw = ImageDraw.Draw(frame)
    lines = text.split('\n')
    # Caption zone: top for most; final lower third is okay but keep consistent.
    line_h = 84
    y = 116 if shot_id != '07' else 128
    # dark translucent rounded plate
    widths = [draw.textbbox((0,0), line, font=FONT_BIG, stroke_width=0)[2] for line in lines]
    plate_w = min(W-96, max(widths)+96)
    plate_h = len(lines)*line_h + 44
    x0 = (W-plate_w)//2
    overlay = Image.new('RGBA', frame.size, (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([x0, y-24, x0+plate_w, y-24+plate_h], radius=28, fill=(0,0,0,118), outline=(255,255,255,36), width=2)
    frame.alpha_composite(overlay)
    draw = ImageDraw.Draw(frame)
    for i,line in enumerate(lines):
        bbox = draw.textbbox((0,0), line, font=FONT_BIG, stroke_width=4)
        tw = bbox[2]-bbox[0]
        tx = (W-tw)//2
        ty = y + i*line_h
        draw.text((tx,ty), line, font=FONT_BIG, fill=(255,248,224,255), stroke_width=5, stroke_fill=(0,0,0,210))
    # No watermark/shot marker: this is still a probe, but should feel close enough to judge.


def add_vignette(frame):
    # subtle edge darkening for premium cohesion, no distracting wobble/effects
    vign = Image.new('RGBA',(W,H),(0,0,0,0))
    vd = ImageDraw.Draw(vign)
    for i in range(90):
        x0, y0 = i*6, i*10
        x1, y1 = W - i*6, H - i*10
        if x1 <= x0 or y1 <= y0:
            break
        a = max(0, 112 - int(i*1.25))
        vd.rectangle([x0, y0, x1, y1], outline=(0,0,0,a), width=8)
    frame.alpha_composite(vign)

frame_index = 0
manifest = {'created_at':datetime.datetime.now().isoformat(timespec='seconds'), 'fps':FPS, 'width':W, 'height':H, 'shots':[]}

for shot in SHOTS:
    im = Image.open(shot['path']).convert('RGB')
    n = int(round(shot['duration']*FPS))
    start_frame = frame_index
    for j in range(n):
        u = j / max(1, n-1)
        scale, cx, cy = motion_params(shot['move'], u)
        crop = cover_crop_params(im.width, im.height, scale, cx, cy)
        frame = im.crop(crop).resize((W,H), Image.Resampling.LANCZOS).convert('RGBA')
        add_vignette(frame)
        draw_caption(frame, shot['caption'], shot['id'])
        # quick crossfade in/out via black overlay for cut softness
        fade_len = min(8, n//5)
        alpha = 0
        if j < fade_len:
            alpha = int(255*(1 - j/fade_len))
        elif j >= n-fade_len:
            alpha = int(255*((j-(n-fade_len))/fade_len))
        if alpha:
            fade = Image.new('RGBA',(W,H),(0,0,0,alpha//2))
            frame.alpha_composite(fade)
        frame.convert('RGB').save(FRAMEDIR / f'frame_{frame_index:05d}.jpg', quality=91)
        frame_index += 1
    manifest['shots'].append({**shot, 'path':str(shot['path'].relative_to(ROOT)), 'frames':n, 'start_frame':start_frame, 'end_frame':frame_index-1})

manifest_path = OUTDIR/'motion_probe_manifest.json'
manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')

silent_out = OUTDIR/'sharks_older_than_trees_v26_final_predator_silent.mp4'
out = OUTDIR/'sharks_older_than_trees_v26_final_predator_audio.mp4'
cmd = [
    'ffmpeg','-y','-framerate',str(FPS),'-i',str(FRAMEDIR/'frame_%05d.jpg'),
    '-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart',
    '-crf','18','-preset','medium',str(silent_out)
]
subprocess.run(cmd, check=True)
voice = ROOT/'outputs/voice_auditions/01_warm_older_brother_uncle.mp3'
subprocess.run(['ffmpeg','-y','-i',str(silent_out),'-i',str(voice),'-c:v','copy','-c:a','aac','-b:a','160k','-ar','48000','-shortest','-movflags','+faststart',str(out)], check=True)
print(json.dumps({'video':str(out), 'silent_video':str(silent_out), 'voice':str(voice), 'manifest':str(manifest_path), 'frames':frame_index, 'duration_seconds':round(frame_index/FPS,2)}, indent=2))
