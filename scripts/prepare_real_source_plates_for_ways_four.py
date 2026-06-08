#!/usr/bin/env python3
from __future__ import annotations
import json, urllib.request, urllib.parse, subprocess, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
ROOT=Path('/mnt/c/dev/curious-shorts')
UA={'User-Agent':'Hermes WAYS media prep educational internal draft'}
W,H=1080,1920

def get_json(url):
 return json.loads(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read().decode())
def dl(url,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists() and dest.stat().st_size>1000: return dest
 data=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=120).read(); dest.write_bytes(data); return dest

def inat_photos(taxon_id, limit=5):
 url='https://api.inaturalist.org/v1/observations?'+urllib.parse.urlencode({'taxon_id':taxon_id,'photos':'true','quality_grade':'research','per_page':30,'order_by':'votes','order':'desc'})
 data=get_json(url); out=[]
 for obs in data.get('results',[]):
  for ph in obs.get('photos',[]):
   u=ph.get('url','').replace('square.','original.').replace('small.','original.').replace('medium.','original.')
   if u: out.append({'url':u,'license':ph.get('license_code'),'attribution':ph.get('attribution'),'obs_uri':obs.get('uri')})
   if len(out)>=limit: return out
 return out

def fit_cover(img):
 img=img.convert('RGB'); iw,ih=img.size; scale=max(W/iw,H/ih); nw,nh=int(iw*scale),int(ih*scale)
 img=img.resize((nw,nh), Image.Resampling.LANCZOS); return img.crop(((nw-W)//2,(nh-H)//2,(nw-W)//2+W,(nh-H)//2+H))
def polish(img):
 img=ImageEnhance.Color(img).enhance(1.08); img=ImageEnhance.Contrast(img).enhance(1.12); img=ImageEnhance.Sharpness(img).enhance(1.05)
 # caption-safe mid gradient
 ov=Image.new('RGBA',(W,H),(0,0,0,0)); px=ov.load(); cy=int(H*.48)
 for y in range(H):
  a=int(max(0,80*(1-abs(y-cy)/(H*.32))))
  if a:
   for x in range(W): px[x,y]=(0,0,0,a)
 return Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
def draw_cube_scat(img):
 ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
 for k in range(8):
  x=280+k*62; y=1315+(k%3)*28; s=42
  d.rounded_rectangle((x,y,x+s,y+s*.82),radius=8,fill=(77,54,35,238),outline=(128,96,61,220),width=3)
  d.polygon([(x,y),(x+12,y-10),(x+s+12,y-10),(x+s,y)],fill=(105,76,48,230))
  d.polygon([(x+s,y),(x+s+12,y-10),(x+s+12,y+s*.82-10),(x+s,y+s*.82)],fill=(56,40,28,210))
 return Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
def draw_hearts(img, mode):
 ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
 pts={'two':[(420,850),(660,850)],'one':[(540,925)],'three':[(420,850),(660,850),(540,925)]}[mode]
 for x,y in pts:
  d.ellipse((x-34,y-34,x+34,y+34),outline=(255,80,100,210),width=7)
  d.ellipse((x-14,y-14,x+14,y+14),fill=(255,80,100,70))
 return Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
def draw_tun_bubbles(img):
 ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
 for k in range(14):
  x=170+(k*77)%760; y=520+(k*137)%900; r=10+(k%4)*8
  d.ellipse((x-r,y-r,x+r,y+r),outline=(200,245,255,95),width=3,fill=(90,180,220,30))
 return Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
def make_sheet(slug, files):
 thumbs=[]
 for f in files:
  im=Image.open(f); im.thumbnail((216,384)); c=Image.new('RGB',(216,424),(18,18,18)); c.paste(im,((216-im.width)//2,0)); ImageDraw.Draw(c).text((8,392),f.name[:28],fill=(255,255,255)); thumbs.append(c)
 sheet=Image.new('RGB',(216*len(thumbs),424),(0,0,0))
 for i,t in enumerate(thumbs): sheet.paste(t,(216*i,0))
 out=files[0].parent/f'{slug}_real_source_plate_contact_sheet.jpg'; sheet.save(out,quality=90); return out

def main():
 topics={
  'wombat_cube_poop': {'taxon':43009,'captions':['Wombats poop cubes','not perfect toy blocks','the shape forms inside','corners before landing','bathroom fact plus physics']},
  'octopus_three_hearts': {'taxon':49315,'captions':['An octopus has three hearts','two push through the gills','one powers the body','swimming slows one down','crawling can be easier']},
 }
 made={}
 for slug,meta in topics.items():
  proj=ROOT/'test_cases'/slug; srcdir=proj/'assets/inat_source_v01'; platedir=proj/'assets/real_wan_template_v01_plates'; platedir.mkdir(parents=True,exist_ok=True); srcdir.mkdir(parents=True,exist_ok=True)
  ph=inat_photos(meta['taxon'],5); (srcdir/'source_manifest.json').write_text(json.dumps(ph,indent=2))
  files=[]
  for i,p in enumerate(ph,1):
   ext='.jpg' if '.jpg' in p['url'] or '.jpeg' in p['url'] else '.png'
   src=dl(p['url'],srcdir/f'source{i:02d}{ext}')
   im=polish(fit_cover(Image.open(src)))
   if slug=='wombat_cube_poop' and i in (2,3,4): im=draw_cube_scat(im)
   if slug=='octopus_three_hearts': im=draw_hearts(im, ['three','two','one','three','one'][i-1])
   out=platedir/f'shot{i:02d}_{slug}_real_plate.jpg'; im.save(out,quality=94); files.append(out)
  made[slug]=[str(f) for f in files]; print('sheet',make_sheet(slug,files))
 # Tardigrade: use existing SDXL plates but harden with no labels + bubbles; these are illustrative microscope plates because open real photos are scarce.
 slug='tardigrade_survival_mode'; proj=ROOT/'test_cases'/slug; srcs=sorted((proj/'assets/sdxl_wan_template_v01_plates').glob('shot*.png'))[:5]; outdir=proj/'assets/real_wan_template_v01_plates'; outdir.mkdir(parents=True,exist_ok=True); files=[]
 for i,src in enumerate(srcs,1):
  im=polish(fit_cover(Image.open(src)))
  if i in (2,3,4): im=draw_tun_bubbles(im)
  out=outdir/f'shot{i:02d}_{slug}_plate.jpg'; im.save(out,quality=94); files.append(out)
 made[slug]=[str(f) for f in files]; print('sheet',make_sheet(slug,files))
 print(json.dumps(made,indent=2))
if __name__=='__main__': main()
