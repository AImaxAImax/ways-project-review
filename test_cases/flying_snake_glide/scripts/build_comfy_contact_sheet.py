#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw
import json, textwrap, sys
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/flying_snake_glide')
ver=sys.argv[1] if len(sys.argv)>1 else 'v02'
manifest_path=ROOT/f'outputs/gate2_plate_qc/comfy_candidates_manifest_{ver}.json'
manifest=json.loads(manifest_path.read_text())
items=[m for m in manifest if 'file' in m]
thumb_w, thumb_h = 260, 455
cols=5
rows=(len(items)+cols-1)//cols
label_h=80
sheet=Image.new('RGB',(cols*thumb_w, rows*(thumb_h+label_h)),(16,18,20))
d=ImageDraw.Draw(sheet)
for i,m in enumerate(items):
    im=Image.open(m['file']).convert('RGB')
    im.thumbnail((thumb_w,thumb_h), Image.LANCZOS)
    bg=Image.new('RGB',(thumb_w,thumb_h),(45,55,60))
    bg.paste(im,((thumb_w-im.width)//2,(thumb_h-im.height)//2))
    col=i%cols; row=i//cols; x=col*thumb_w; y=row*(thumb_h+label_h)
    sheet.paste(bg,(x,y))
    label=f"{m['shot']} v{m['variant']}"
    ty=y+thumb_h+12
    for line in textwrap.wrap(label.replace('_',' '), 22):
        d.text((x+12,ty),line,fill=(240,240,230)); ty+=24
out=ROOT/f'outputs/gate2_plate_qc/comfy_candidates_contact_sheet_{ver}.jpg'
sheet.save(out, quality=92)
print(out)
