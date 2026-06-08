#!/usr/bin/env python3
"""Controlled v6 paper-cut reference frames: exact say-dog-see-dog + locked style.
These are art-direction keyframes/reference plates, not final generative polish.
"""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import random, math, json

ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
OUT=ROOT/'assets'/'v6_controlled_papercut_refs'
OUT.mkdir(parents=True, exist_ok=True)
W,H=1080,1920
COL={
 'bg':'#10252b','teal':'#2eb7b2','deep':'#0f6e77','foam':'#b9f0d8','sand':'#d7a953','sand2':'#f0cc74','rock':'#9b6a3e','rock2':'#6a4630','amber':'#e28b3a','paper':'#f5d887','dark':'#142126','bone':'#f0e3c0','apple':'#d94133','squirrel':'#b8662d','leaf':'#68b66c','plant':'#64a772','glass':'#92e0d9'}

def img(seed):
    random.seed(seed)
    im=Image.new('RGB',(W,H),COL['bg'])
    d=ImageDraw.Draw(im,'RGBA')
    # paper grain
    pix=im.load()
    for _ in range(9000):
        x=random.randrange(W); y=random.randrange(H); a=random.randrange(8,22)
        d.point((x,y), fill=(255,245,205,a))
    return im,d

def shadow_poly(d, pts, fill, shadow=(0,0,0,80), offset=(12,16)):
    d.polygon([(x+offset[0],y+offset[1]) for x,y in pts], fill=shadow)
    d.polygon(pts, fill=fill)

def ellipse_shadow(d, box, fill):
    x1,y1,x2,y2=box
    d.ellipse((x1+12,y1+16,x2+12,y2+16), fill=(0,0,0,80))
    d.ellipse(box, fill=fill)

def shark(d,cx,cy,s=1,flip=False,color=(82,150,150,255)):
    sx=-1 if flip else 1
    body=[(cx-170*s*sx,cy),(cx-80*s*sx,cy-48*s),(cx+120*s*sx,cy-42*s),(cx+205*s*sx,cy),(cx+120*s*sx,cy+42*s),(cx-80*s*sx,cy+48*s)]
    shadow_poly(d,body,color)
    d.polygon([(cx+188*s*sx,cy),(cx+260*s*sx,cy-65*s),(cx+240*s*sx,cy),(cx+260*s*sx,cy+65*s)],fill=color)
    d.polygon([(cx-20*s*sx,cy-30*s),(cx+35*s*sx,cy-125*s),(cx+68*s*sx,cy-20*s)],fill=(65,126,134,255))
    d.polygon([(cx+20*s*sx,cy+35*s),(cx+80*s*sx,cy+105*s),(cx+60*s*sx,cy+25*s)],fill=(65,126,134,255))
    ellipse_shadow(d,(cx-124*s,cy-10*s,cx-106*s,cy+8*s),(10,30,35,255))

def water(d,y, color=COL['teal']):
    pts=[(0,y)]
    for x in range(0,W+80,80): pts.append((x,y+random.randint(-35,35)))
    pts += [(W,H),(0,H)]
    shadow_poly(d,pts,color)
    for _ in range(12):
        yy=random.randint(y+60,H-80)
        x0=random.randint(-50,W-250)
        x1=x0+random.randint(240,520)
        d.arc((x0,yy,x1,yy+60),0,180,fill=(255,255,255,45),width=5)

def island(d,cx,cy,w,h,plants=False):
    pts=[(cx-w//2,cy+h//4),(cx-w//3,cy-h//4),(cx,cy-h//2),(cx+w//3,cy-h//5),(cx+w//2,cy+h//5),(cx+w//4,cy+h//2),(cx-w//4,cy+h//2)]
    shadow_poly(d,pts,COL['sand'])
    for _ in range(4):
        rx=cx+random.randint(-w//3,w//3); ry=cy+random.randint(-h//4,h//4)
        ellipse_shadow(d,(rx-25,ry-16,rx+25,ry+16),COL['rock'])
    if plants:
        for _ in range(8): draw_plant(d,cx+random.randint(-w//3,w//3),cy+random.randint(-h//4,h//5),random.uniform(.5,1.1))

def draw_tree(d,x,y,s=1,bare=False):
    d.rounded_rectangle((x-12*s,y-190*s,x+12*s,y+20*s),radius=12,fill=COL['rock2'])
    for a in [-60,-25,25,60]:
        x2=x+math.cos(math.radians(a))*75*s; y2=y-120*s+math.sin(math.radians(a))*45*s
        d.line((x,y-110*s,x2,y2),fill=COL['rock2'],width=int(13*s))
        if not bare: ellipse_shadow(d,(x2-55*s,y2-45*s,x2+55*s,y2+45*s),COL['leaf'])

def draw_plant(d,x,y,s=1):
    d.line((x,y,x,y-90*s),fill=COL['plant'],width=int(8*s))
    for i in range(5):
        yy=y-20*s-i*14*s
        d.line((x,yy,x-45*s,yy-20*s),fill=COL['plant'],width=int(5*s))
        d.line((x,yy,x+45*s,yy-20*s),fill=COL['plant'],width=int(5*s))

def apple(d,x,y,s=1):
    ellipse_shadow(d,(x-45*s,y-38*s,x+45*s,y+52*s),COL['apple'])
    d.line((x,y-40*s,x+18*s,y-80*s),fill=COL['rock2'],width=int(7*s))
    ellipse_shadow(d,(x+12*s,y-85*s,x+58*s,y-52*s),COL['leaf'])

def acorn(d,x,y,s=1):
    ellipse_shadow(d,(x-35*s,y-15*s,x+35*s,y+70*s),'#a96c35')
    d.pieslice((x-43*s,y-40*s,x+43*s,y+30*s),180,360,fill='#5c3b26')

def squirrel(d,x,y,s=1):
    ellipse_shadow(d,(x-50*s,y-65*s,x+45*s,y+55*s),COL['squirrel'])
    ellipse_shadow(d,(x-92*s,y-120*s,x-10*s,y+40*s),'#d78a42')
    ellipse_shadow(d,(x+20*s,y-115*s,x+82*s,y-50*s),COL['squirrel'])
    d.polygon([(x+42*s,y-115*s),(x+58*s,y-155*s),(x+66*s,y-110*s)],fill=COL['squirrel'])
    d.ellipse((x+55*s,y-92*s,x+65*s,y-82*s),fill='black')

def save(im,name):
    im=im.filter(ImageFilter.UnsharpMask(radius=1,percent=80))
    path=OUT/f'{name}.png'; im.save(path); return str(path)

files=[]
# 1 before trees
im,d=img(1); water(d,850); 
for vals in [(190,690,260,190,False),(640,760,360,220,False),(890,520,240,260,False),(500,430,190,130,False)]: island(d,*vals)
shark(d,520,1220,1.0); files.append(save(im,'01_before_trees_barren_land'))
# 2 museum fossil
im,d=img(2); d.rounded_rectangle((110,240,970,1650),radius=35,fill=(63,42,28,255)); d.rounded_rectangle((160,310,920,1530),radius=20,fill=COL['sand'])
for y in [480,720,960,1200]: d.line((210,y,870,y),fill=COL['rock'],width=20)
for x in [300,540,780]: d.line((x,360,x,1450),fill=COL['rock'],width=15)
for cx,cy,s in [(540,690,1.0),(355,1060,.65),(720,1130,.7)]: shark(d,cx,cy,s,color=(236,222,188,255))
d.ellipse((705,350,840,485),outline=COL['bone'],width=16); d.line((820,470,900,560),fill=COL['bone'],width=18)
files.append(save(im,'02_seriously_fossil_museum'))
# 3 gag
im,d=img(3); water(d,1180); d.rectangle((0,0,W,1180),fill='#d9b35f')
for vals in [(230,920,300,180,False),(690,980,360,200,False),(500,690,250,160,False)]: island(d,*vals)
apple(d,255,650,1.9); squirrel(d,545,760,1.6); acorn(d,790,690,1.8)
for x in [120,930]: draw_tree(d,x,1070,0.7,bare=True)
files.append(save(im,'03_apples_squirrel_nuts_gag'))
# 4 timeline
im,d=img(4); d.rounded_rectangle((110,160,970,1740),radius=28,fill=(70,49,32,255))
for i,y in enumerate(range(260,1600,220)):
    d.rounded_rectangle((170,y,910,y+150),radius=16,fill=COL['sand'] if i%2 else '#c6904a')
    if i<2: shark(d,530,y+80,.48,color=(236,222,188,255))
    if i==4:
        for x in [300,520,740]: draw_plant(d,x,y+138,.55)
    d.ellipse((760,y+25,850,y+115),outline=COL['bone'],width=8); d.line((805,y+70,805,y+38),fill=COL['bone'],width=5); d.line((805,y+70,835,y+80),fill=COL['bone'],width=5)
files.append(save(im,'04_geologic_deep_time_timeline'))
# 5 trees arrive
im,d=img(5); water(d,1120)
for x in [130,260,390,560,720,900]: draw_tree(d,x,1080,random.uniform(.85,1.25),bare=False)
for _ in range(18): draw_plant(d,random.randint(30,W-30),random.randint(900,1450),random.uniform(.5,1.1))
shark(d,690,1430,.55); files.append(save(im,'05_primitive_forest_arrives'))
# 6 modern viewer
im,d=img(6); d.rectangle((80,160,1000,1660),fill=(64,190,180,160)); d.rectangle((80,160,1000,1660),outline=(235,215,160,255),width=22)
for x in [280,540,800]: d.line((x,160,x,1660),fill=(220,210,170,120),width=8)
for cx,cy,s in [(650,620,.9),(350,950,.55),(760,1180,.45)]: shark(d,cx,cy,s,color=(73,142,150,255))
# silhouettes
for cx,cy,s in [(430,1500,1.15),(600,1530,.8),(720,1515,.9)]:
    d.ellipse((cx-35*s,cy-245*s,cx+35*s,cy-175*s),fill=(10,20,25,255)); d.rounded_rectangle((cx-38*s,cy-175*s,cx+38*s,cy),radius=30,fill=(10,20,25,255))
files.append(save(im,'06_modern_viewer_aquarium'))
# 7 final
im,d=img(7); water(d,580); island(d,795,450,350,140,False); island(d,240,430,230,120,False)
shark(d,540,1100,1.05); d.ellipse((760,190,920,350),fill=(235,201,115,190)); files.append(save(im,'07_survivor_world_before_forests'))

(ROOT/'outputs/v6_controlled_papercut_manifest.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
print(json.dumps({'count':len(files),'files':files},indent=2))
