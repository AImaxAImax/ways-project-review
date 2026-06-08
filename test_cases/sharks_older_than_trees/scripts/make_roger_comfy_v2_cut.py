#!/usr/bin/env python3
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import json, subprocess, math, shutil

ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
W,H=1080,1920
FPS=30
AUDIO=ROOT/'outputs/voice_auditions/01_warm_older_brother_uncle.mp3'
OUT=ROOT/'outputs/sharks_older_than_trees_roger_comfy_v2.mp4'
FRAMES=ROOT/'assets/video_v2_frames'
FRAMES.mkdir(parents=True, exist_ok=True)
for old in FRAMES.glob('frame_*.jpg'):
    old.unlink()

orig=json.loads((ROOT/'outputs/comfy_shot_set_v1_manifest.json').read_text())
soft=json.loads((ROOT/'outputs/comfy_soft_regen_manifest.json').read_text())

def find(manifest, shot, variant):
    return Path(next(m['file'] for m in manifest if m['shot']==shot and m['variant']==variant))

shots=[
    {
      'id':'01_before_trees_hook',
      'image':find(orig,'01_before_trees_hook',1),
      'duration':3.0,
      'caption':'SHARKS WERE HERE\nBEFORE TREES.',
      'small':'Seriously.',
      'anchor':'bottom'
    },
    {
      'id':'02_empty_land_before_forests',
      'image':find(soft,'02_empty_land_before_forests_soft',5),
      'duration':4.1,
      'caption':'BEFORE FORESTS.\nBEFORE APPLES.',
      'small':'Before squirrels had anywhere to hide nuts.',
      'anchor':'bottom'
    },
    {
      'id':'03_shark_older_than_trees',
      'image':find(soft,'03_shark_older_than_trees_soft',5),
      'duration':3.8,
      'caption':'400+ MILLION\nYEARS AGO',
      'small':'The first sharks showed up first.',
      'anchor':'bottom'
    },
    {
      'id':'04_trees_arrive_later',
      'image':find(orig,'04_trees_arrive_later',3),
      'duration':3.8,
      'caption':'TREES TOOK\nTHEIR TIME.',
      'small':'They arrived tens of millions of years later.',
      'anchor':'bottom'
    },
    {
      'id':'05_survival_through_ages',
      'image':find(soft,'05_survival_through_ages_soft',4),
      'duration':4.0,
      'caption':'NOT JUST\nAN ANIMAL.',
      'small':'A survivor through deep time.',
      'anchor':'bottom'
    },
    {
      'id':'06_world_before_forests',
      'image':find(soft,'06_world_before_forests_soft',1),
      'duration':5.254286,
      'caption':'A WORLD\nBEFORE FORESTS',
      'small':'',
      'anchor':'bottom'
    },
]

def font(size,bold=True):
    paths=[
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
    ]
    for p in paths:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

BIG=font(82,True)
SMALL=font(34,False)
TAG=font(24,False)

def cover_resize(im, scale=1.0, pan_x=0, pan_y=0):
    # resize to cover, then crop with optional pan in -1..1
    base=max(W/im.width, H/im.height)*scale
    nw,nh=int(im.width*base), int(im.height*base)
    im=im.resize((nw,nh), Image.Resampling.LANCZOS)
    max_x=max(0,nw-W); max_y=max(0,nh-H)
    x=int(max_x*(0.5+0.5*pan_x)); y=int(max_y*(0.5+0.5*pan_y))
    x=max(0,min(max_x,x)); y=max(0,min(max_y,y))
    return im.crop((x,y,x+W,y+H))

def draw_text_panel(im, caption, small, shot_num):
    overlay=Image.new('RGBA',(W,H),(0,0,0,0))
    od=ImageDraw.Draw(overlay)
    panel_h=380 if small else 300
    y0=H-panel_h
    # gradient-ish shadow blocks
    for i in range(panel_h):
        alpha=int(185*(i/panel_h)**1.7)
        od.line([(0,y0+i),(W,y0+i)], fill=(0,0,0,alpha))
    # subtle top vignette
    for i in range(240):
        alpha=int(70*(1-i/240))
        od.line([(0,i),(W,i)], fill=(0,0,0,alpha))
    im=Image.alpha_composite(im.convert('RGBA'), overlay)
    d=ImageDraw.Draw(im)
    x=70; y=H-panel_h+54
    # shot label
    d.rounded_rectangle((70,60,210,104), radius=14, fill=(0,0,0,130))
    d.text((88,68), f'SHOT {shot_num}', font=TAG, fill=(220,240,235,230))
    # caption shadow + main
    for dx,dy in [(4,4),(0,5)]:
        d.multiline_text((x+dx,y+dy), caption, font=BIG, fill=(0,0,0,210), spacing=8)
    d.multiline_text((x,y), caption, font=BIG, fill=(245,255,245,255), spacing=8)
    if small:
        sy=y+caption.count('\n')*92+112
        d.text((x+2,sy+2), small, font=SMALL, fill=(0,0,0,210))
        d.text((x,sy), small, font=SMALL, fill=(210,235,230,235))
    return im.convert('RGB')

frame_idx=0
selected_manifest=[]
for si,shot in enumerate(shots,1):
    src=Image.open(shot['image']).convert('RGB')
    n=round(shot['duration']*FPS)
    selected_manifest.append({k:(str(v) if k=='image' else v) for k,v in shot.items()})
    for j in range(n):
        t=j/max(1,n-1)
        # slow push-in, alternating tiny pan
        scale=1.015 + 0.055*t
        pan_x=(-0.18+0.36*t) if si%2 else (0.18-0.36*t)
        pan_y=-0.10+0.20*t
        fr=cover_resize(src,scale,pan_x,pan_y)
        fr=draw_text_panel(fr,shot['caption'],shot['small'],si)
        fr.save(FRAMES/f'frame_{frame_idx:05d}.jpg', quality=92)
        frame_idx+=1

(ROOT/'outputs/comfy_selected_v2_manifest.json').write_text(json.dumps({'shots':selected_manifest,'frame_count':frame_idx,'fps':FPS,'audio':str(AUDIO),'output':str(OUT)},indent=2))
cmd=['ffmpeg','-y','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-i',str(AUDIO),'-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest',str(OUT)]
subprocess.run(cmd,check=True)
print(json.dumps({'output':str(OUT),'frames':frame_idx,'duration':frame_idx/FPS},indent=2))
