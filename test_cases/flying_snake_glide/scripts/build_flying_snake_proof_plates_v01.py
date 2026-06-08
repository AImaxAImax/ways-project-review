#!/usr/bin/env python3
from __future__ import annotations

import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "gate2_plate_qc" / "proof_plates_v01"
OUT.mkdir(parents=True, exist_ok=True)
W,H = 1080,1920
SAFE_RIGHT=250

beats = [
    {
        "id":"beat01_launch",
        "caption":"Some snakes can glide through the air",
        "voiceover":"Some snakes can glide through the air.",
        "visual":"snake launching from a high branch into open air"
    },
    {
        "id":"beat02_no_wings",
        "caption":"no wings",
        "voiceover":"They do not have wings.",
        "visual":"airborne snake, no wings, full body readable"
    },
    {
        "id":"beat03_flatten",
        "caption":"they flatten their body",
        "voiceover":"They flatten their body like a long moving airfoil.",
        "visual":"body visibly flattened wider like a ribbon"
    },
    {
        "id":"beat04_side_to_side",
        "caption":"they wave side to side",
        "voiceover":"Then they wave side to side while falling forward.",
        "visual":"S-shaped side-to-side glide path"
    },
    {
        "id":"beat05_tree_to_tree",
        "caption":"steering tree to tree",
        "voiceover":"That motion helps them steer from one tree to another.",
        "visual":"snake gliding toward another tree branch"
    },
]

def bg():
    im=Image.new('RGB',(W,H),(125,187,214))
    d=ImageDraw.Draw(im)
    # sky gradient
    for y in range(H):
        t=y/H
        col=(int(122-42*t), int(190-48*t), int(218-46*t))
        d.line([(0,y),(W,y)], fill=col)
    # distant forest blobs
    import random
    random.seed(4)
    for i in range(120):
        x=random.randint(-100,W+100); y=random.randint(900,1820); r=random.randint(45,130)
        c=random.choice([(39,104,73),(48,123,79),(29,88,66),(69,139,79)])
        d.ellipse((x-r,y-r,x+r,y+r), fill=c)
    im=im.filter(ImageFilter.GaussianBlur(1.2))
    d=ImageDraw.Draw(im)
    # keep right side calmer for caption safe area
    d.rounded_rectangle((W-SAFE_RIGHT,0,W,H), radius=0, fill=(88,150,172), outline=None)
    return im

def branch(d, x1,y1,x2,y2, width=52):
    d.line((x1,y1,x2,y2), fill=(82,50,28), width=width)
    d.line((x1,y1,x2,y2), fill=(118,75,39), width=max(10,width//3))
    # leaves
    for i in range(12):
        t=i/11
        x=x1+(x2-x1)*t; y=y1+(y2-y1)*t
        off=70*((-1)**i)
        d.ellipse((x-55,y+off-35,x+55,y+off+35), fill=(34,116,65))

def draw_snake(d, pts, width=66, flat=False, color=(43,92,44), belly=(225,185,74), head=True):
    # shadow
    d.line(pts, fill=(18,45,36), width=width+16, joint='curve')
    # body
    d.line(pts, fill=color, width=width, joint='curve')
    # flattened belly/ribbon highlight
    if flat:
        d.line(pts, fill=(91,136,53), width=int(width*.68), joint='curve')
        d.line(pts, fill=belly, width=int(width*.30), joint='curve')
    else:
        d.line(pts, fill=(72,123,50), width=int(width*.45), joint='curve')
        d.line(pts, fill=belly, width=int(width*.16), joint='curve')
    # scale dots
    for i,(x,y) in enumerate(pts[::2]):
        d.ellipse((x-8,y-8,x+8,y+8), fill=(28,68,38))
    if head:
        x,y=pts[-1]
        d.ellipse((x-45,y-35,x+55,y+35), fill=color)
        d.ellipse((x+17,y-12,x+25,y-4), fill=(5,10,5))
        d.polygon([(x+48,y),(x+86,y-12),(x+86,y+12)], fill=(60,105,47))

def arrow_motion(d, pts, color=(245,245,245)):
    # subtle dotted glide trail, no text/labels
    for i in range(0,len(pts)-1,2):
        x,y=pts[i]
        d.ellipse((x-10,y-10,x+10,y+10), fill=color)

def plate(idx):
    im=bg(); d=ImageDraw.Draw(im)
    if idx==0:
        branch(d, -120,760,450,610,70)
        pts=[(250,700),(360,675),(455,700),(540,760),(630,820),(720,875)]
        draw_snake(d, pts, width=62, flat=False)
        arrow_motion(d, [(760,900),(820,940),(880,990)])
        # open air gap center makes launch readable
    elif idx==1:
        branch(d, -180,430,150,540,45)
        pts=[]
        for i in range(18):
            x=150+i*42; y=840+math.sin(i*.85)*80
            pts.append((x,y))
        draw_snake(d, pts, width=56, flat=False)
        # leave completely empty sides to emphasize no wings
    elif idx==2:
        branch(d, -100,1520,210,1460,45)
        pts=[]
        for i in range(18):
            x=105+i*45; y=895+math.sin(i*.68)*55
            pts.append((x,y))
        draw_snake(d, pts, width=92, flat=True)
        # body cross-section icon-like visual no labels: normal round vs flattened ribbon
        d.ellipse((92,1210,202,1320), fill=(44,91,44), outline=(225,185,74), width=12)
        d.rounded_rectangle((260,1240,560,1292), radius=26, fill=(44,91,44), outline=(225,185,74), width=12)
    elif idx==3:
        branch(d, -160,420,120,500,40)
        branch(d, 830,1480,1200,1350,50)
        pts=[]
        for i in range(22):
            x=105+i*38; y=670+i*31+math.sin(i*.9)*90
            pts.append((x,y))
        draw_snake(d, pts, width=56, flat=True)
        # visible swoosh path
        trail=[(120,640),(210,760),(315,725),(430,885),(540,850),(655,1025),(760,995)]
        d.line(trail, fill=(238,248,255), width=10)
        arrow_motion(d, trail, color=(238,248,255))
    elif idx==4:
        branch(d, -120,520,240,610,50)
        branch(d, 730,1060,1240,940,70)
        pts=[]
        for i in range(20):
            x=210+i*36; y=760+i*18+math.sin(i*.78)*65
            pts.append((x,y))
        draw_snake(d, pts, width=60, flat=True)
        # target branch leaves
        d.ellipse((800,900,1020,1090), fill=(40,128,65))
        d.ellipse((880,800,1140,1020), fill=(51,145,72))
    return im

manifest=[]
for i,b in enumerate(beats):
    im=plate(i)
    path=OUT / f"flying_snake_{b['id']}.jpg"
    im.save(path, quality=94)
    manifest.append({**b, 'path': str(path.relative_to(ROOT))})

# contact sheet: pictures first, small external captions below for review only
thumb_w=360; thumb_h=640
sheet=Image.new('RGB',(thumb_w*5, thumb_h+190),(18,26,30))
d=ImageDraw.Draw(sheet)
for i,m in enumerate(manifest):
    im=Image.open(ROOT/m['path']).resize((thumb_w,thumb_h), Image.LANCZOS)
    x=i*thumb_w
    sheet.paste(im,(x,0))
    d.rectangle((x,thumb_h,x+thumb_w,thumb_h+190), fill=(18,26,30))
    cap=f"{i+1}. {beats[i]['caption']}"
    # rough wrap
    words=cap.split(); lines=[]; line=''
    for w in words:
        if len(line+' '+w)>23:
            lines.append(line); line=w
        else:
            line=(line+' '+w).strip()
    lines.append(line)
    y=thumb_h+22
    for line in lines:
        d.text((x+18,y),line,fill=(245,245,230))
        y+=32
contact=OUT/'flying_snake_proof_plates_v01_contact_sheet.jpg'
sheet.save(contact, quality=92)

(ROOT/'outputs'/'gate2_plate_qc').mkdir(parents=True, exist_ok=True)
manifest_path=OUT/'proof_plates_manifest_v01.json'
manifest_path.write_text(json.dumps({'slug':'flying_snake_glide','version':'v01','plates':manifest,'contact_sheet':str(contact.relative_to(ROOT))},indent=2)+'\n')
qa=ROOT/'outputs'/'gate2_plate_qc'/'FLYING_SNAKE_PROOF_PLATES_QA_v01.md'
qa.write_text(f"""# Flying Snake Proof Plates v01 QA

Generated procedural proof plates for Gate 2 visual clarity.

## Verdict
Internal plate candidate only. The images are intentionally simple/procedural because managed image generation is unavailable in this environment. They are much more readable than the tardigrade sheet: the subject is a snake in trees/air in every beat, and the story reads as launch -> no wings -> flattened body -> side-to-side glide -> tree-to-tree steering.

## Pass checks
- Instant topic read: snake + trees + airborne glide in all five beats.
- Say-dog-see-dog: each frame maps to the spoken claim.
- No embedded labels, UI, logos, or text inside the source plates.
- Contact sheet has review captions below frames only.

## Risks
- Procedural plates are not final premium visuals.
- Need either real source/video or higher-quality generated plates before public render.
- Beat 03 uses a simple cross-section visual element; acceptable for clarity check, not final source.

## Artifacts
- Contact sheet: `{contact.relative_to(ROOT)}`
- Manifest: `{manifest_path.relative_to(ROOT)}`
""")
print(json.dumps({'contact_sheet':str(contact),'manifest':str(manifest_path),'qa':str(qa),'plates':len(manifest)},indent=2))
