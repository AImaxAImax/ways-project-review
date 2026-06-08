#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageEnhance
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/saturn_hexagon_storm')
W,H=1080,1920
def fit(img):
 img=img.convert('RGB'); iw,ih=img.size; scale=max(W/iw,H/ih); nw,nh=int(iw*scale),int(ih*scale)
 img=img.resize((nw,nh), Image.Resampling.LANCZOS)
 return img.crop(((nw-W)//2,(nh-H)//2,(nw-W)//2+W,(nh-H)//2+H))
srcs=sorted((ROOT/'assets/source_wan_template_v01').glob('*.jpg'))
out=ROOT/'assets/wan_template_plain_v02_plates'; out.mkdir(parents=True,exist_ok=True)
# choose varied views, no overlays, no shapes, no labels to prevent Wan text hallucination
order=[0,1,2,3,1]
for i,idx in enumerate(order,1):
 im=fit(Image.open(srcs[idx % len(srcs)]))
 im=ImageEnhance.Contrast(im).enhance(1.10)
 im=ImageEnhance.Sharpness(im).enhance(1.05)
 im.save(out/f'shot{i:02d}_saturn_hexagon_storm_plain_plate.jpg',quality=94)
print(out)
