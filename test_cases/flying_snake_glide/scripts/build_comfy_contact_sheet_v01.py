#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw
import json, textwrap
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/flying_snake_glide')
manifest_path=ROOT/'outputs/gate2_plate_qc/comfy_candidates_manifest_v01.json'
manifest=json.loads(manifest_path.read_text())
items=[m for m in manifest if 'file' in m]
thumb_w, thumb_h = 300, 525
pad=16
label_h=110
sheet=Image.new('RGB',(len(items)*thumb_w, thumb_h+label_h),(16,18,20))
d=ImageDraw.Draw(sheet)
for i,m in enumerate(items):
    im=Image.open(m['file']).convert('RGB')
    im.thumbnail((thumb_w,thumb_h), Image.LANCZOS)
    bg=Image.new('RGB',(thumb_w,thumb_h),(45,55,60))
    bg.paste(im,((thumb_w-im.width)//2,(thumb_h-im.height)//2))
    x=i*thumb_w
    sheet.paste(bg,(x,0))
    label=f"{i+1}. {m['shot'].replace('_',' ')}"
    y=thumb_h+16
    for line in textwrap.wrap(label, 22):
        d.text((x+14,y),line,fill=(240,240,230))
        y+=26
out=ROOT/'outputs/gate2_plate_qc/comfy_candidates_contact_sheet_v01.jpg'
out.parent.mkdir(parents=True, exist_ok=True)
sheet.save(out, quality=92)
print(out)
