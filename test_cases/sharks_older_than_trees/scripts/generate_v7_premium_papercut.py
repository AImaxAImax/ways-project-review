#!/usr/bin/env python3
"""v7 premium paper-cut diorama frames.
Renders oversized frames with paper texture, layered shadows, vignette, and downsampled finals.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from pathlib import Path
import random, math, json

ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
OUT=ROOT/'assets'/'v7_premium_papercut'
OUT.mkdir(parents=True, exist_ok=True)
W,H=2160,3840
S=2
COL={
 'navy':(13,31,37,255),'teal':(42,173,172,255),'teal2':(14,111,122,255),'foam':(196,241,220,255),
 'sand':(220,173,80,255),'sand2':(239,202,116,255),'ochre':(187,123,56,255),'rock':(117,78,49,255),
 'dark':(8,20,26,255),'bone':(239,224,188,255),'cream':(246,224,155,255),'apple':(214,58,48,255),
 'squirrel':(185,102,43,255),'squirrel2':(222,139,68,255),'leaf':(101,176,105,255),'plant':(88,153,105,255),
 'glass':(132,220,213,140),'white':(255,246,210,255)
}

def paper_texture(size, base, seed=0, strength=28):
    # Fast procedural paper: low-res noise upscaled + sparse fibers.
    random.seed(seed)
    w,h=size
    small=(max(1,w//8), max(1,h//8))
    noise=Image.effect_noise(small, strength).convert('L').resize(size, Image.Resampling.BILINEAR)
    im=Image.new('RGBA',size,base)
    r,g,b,a=base
    tint=Image.merge('RGBA',(
        noise.point(lambda p:max(0,min(255,r + (p-128)//5))),
        noise.point(lambda p:max(0,min(255,g + (p-128)//5))),
        noise.point(lambda p:max(0,min(255,b + (p-128)//5))),
        Image.new('L',size,a)
    ))
    im=Image.blend(im,tint,0.65)
    d=ImageDraw.Draw(im,'RGBA')
    for _ in range(180):
        x=random.randint(0,w); y=random.randint(0,h); ln=random.randint(20,180)
        d.line((x,y,x+ln,y+random.randint(-3,3)),fill=(255,255,230,random.randint(7,18)),width=random.choice([1,1,2]))
    return im.filter(ImageFilter.GaussianBlur(0.18))

def scene_bg(seed):
    bg=paper_texture((W,H),COL['navy'],seed,14)
    overlay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(overlay,'RGBA')
    # warm spotlight
    for r in range(1800,100,-80):
        a=int(32*(1-r/1800))
        d.ellipse((W//2-r,H//3-r,W//2+r,H//3+r),fill=(255,196,95,max(0,a)))
    # vignette
    vign=Image.new('L',(W,H),0); vd=ImageDraw.Draw(vign)
    vd.ellipse((-450,-300,W+450,H+500),fill=255)
    vign=ImageChops.invert(vign.filter(ImageFilter.GaussianBlur(260)))
    dark=Image.new('RGBA',(W,H),(0,0,0,125)); bg=Image.composite(dark,bg,vign)
    return Image.alpha_composite(bg,overlay)

def layer(base, shape, fill, seed=0, shadow=34, blur=18, offset=(24,30), outline=None):
    mask=Image.new('L',(W,H),0); md=ImageDraw.Draw(mask)
    typ, data = shape
    if typ=='poly': md.polygon(data,fill=255)
    elif typ=='ellipse': md.ellipse(data,fill=255)
    elif typ=='rect': md.rounded_rectangle(data[0],radius=data[1],fill=255)
    tex=paper_texture((W,H),fill,seed,18)
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); sm=ImageChops.offset(mask,offset[0],offset[1]).filter(ImageFilter.GaussianBlur(blur))
    sh.putalpha(sm.point(lambda p:int(p*shadow/255)))
    base.alpha_composite(sh)
    base.paste(tex,(0,0),mask)
    if outline:
        od=ImageDraw.Draw(base,'RGBA')
        if typ=='poly': od.line(data+[data[0]],fill=outline,width=5*S)
        elif typ=='ellipse': od.ellipse(data,outline=outline,width=5*S)
        elif typ=='rect': od.rounded_rectangle(data[0],radius=data[1],outline=outline,width=5*S)

def poly(base, pts, fill, seed=0, **kw): layer(base,('poly',pts),fill,seed,**kw)
def ell(base, box, fill, seed=0, **kw): layer(base,('ellipse',box),fill,seed,**kw)
def rr(base, box, radius, fill, seed=0, **kw): layer(base,('rect',(box,radius)),fill,seed,**kw)

def draw_water(base,y,seed=0):
    random.seed(seed)
    pts=[(0,y)] + [(x,y+random.randint(-55*S,55*S)) for x in range(0,W+120*S,120*S)] + [(W,H),(0,H)]
    poly(base,pts,COL['teal'],seed,shadow=28,blur=24)
    d=ImageDraw.Draw(base,'RGBA')
    for _ in range(24):
        yy=random.randint(y+80*S,H-100*S); x=random.randint(-100*S,W-200*S); ww=random.randint(350*S,850*S)
        d.arc((x,yy,x+ww,yy+70*S),0,180,fill=(255,255,230,38),width=random.randint(4*S,8*S))
    for _ in range(160):
        bx=random.randint(0,W-8); by=random.randint(y,H-8)
        d.ellipse((bx,by,bx+4*S,by+4*S),fill=(255,255,255,30))

def island(base,cx,cy,w,h,seed=0):
    pts=[(cx-w//2,cy+h//4),(cx-w//3,cy-h//4),(cx,cy-h//2),(cx+w//3,cy-h//5),(cx+w//2,cy+h//5),(cx+w//4,cy+h//2),(cx-w//4,cy+h//2)]
    poly(base,pts,COL['sand'],seed,shadow=42,blur=18)
    random.seed(seed)
    for i in range(5):
        rx=cx+random.randint(-w//3,w//3); ry=cy+random.randint(-h//5,h//4)
        ell(base,(rx-45*S,ry-25*S,rx+45*S,ry+25*S),COL['rock'],seed+i+20,shadow=18,blur=9)

def shark(base,cx,cy,s=1,flip=False,color=(73,147,153,255),seed=0):
    sx=-1 if flip else 1
    pts=[(cx-int(180*s*S)*sx,cy),(cx-int(90*s*S)*sx,cy-int(50*s*S)),(cx+int(120*s*S)*sx,cy-int(45*s*S)),(cx+int(210*s*S)*sx,cy),(cx+int(120*s*S)*sx,cy+int(45*s*S)),(cx-int(90*s*S)*sx,cy+int(50*s*S))]
    poly(base,pts,color,seed,shadow=32,blur=14)
    d=ImageDraw.Draw(base,'RGBA')
    tail=[(cx+int(195*s*S)*sx,cy),(cx+int(270*s*S)*sx,cy-int(70*s*S)),(cx+int(245*s*S)*sx,cy),(cx+int(270*s*S)*sx,cy+int(70*s*S))]
    poly(base,tail,color,seed+1,shadow=24,blur=10)
    fin=[(cx-int(10*s*S)*sx,cy-int(35*s*S)),(cx+int(45*s*S)*sx,cy-int(130*s*S)),(cx+int(75*s*S)*sx,cy-int(20*s*S))]
    poly(base,fin,(48,112,123,255),seed+2,shadow=20,blur=8)
    ell(base,(cx-int(125*s*S),cy-int(13*s*S),cx-int(107*s*S),cy+int(5*s*S)),COL['dark'],seed+3,shadow=0,blur=0)

def plant(base,x,y,s=1,seed=0):
    d=ImageDraw.Draw(base,'RGBA')
    d.line((x,y,x,y-int(115*s*S)),fill=COL['plant'],width=max(6,int(9*s*S)))
    for i in range(6):
        yy=y-int((25+i*16)*s*S); dx=int((44+5*i)*s*S)
        d.line((x,yy,x-dx,yy-int(24*s*S)),fill=COL['plant'],width=max(4,int(6*s*S)))
        d.line((x,yy,x+dx,yy-int(24*s*S)),fill=COL['plant'],width=max(4,int(6*s*S)))

def tree(base,x,y,s=1,bare=False,seed=0):
    d=ImageDraw.Draw(base,'RGBA')
    d.rounded_rectangle((x-int(16*s*S),y-int(230*s*S),x+int(16*s*S),y+int(25*s*S)),radius=int(14*s*S),fill=COL['rock'])
    for i,a in enumerate([-65,-35,25,58]):
        x2=x+int(math.cos(math.radians(a))*95*s*S); y2=y-int(145*s*S)+int(math.sin(math.radians(a))*60*s*S)
        d.line((x,y-int(125*s*S),x2,y2),fill=COL['rock'],width=max(8,int(14*s*S)))
        if not bare:
            ell(base,(x2-int(65*s*S),y2-int(48*s*S),x2+int(65*s*S),y2+int(48*s*S)),COL['leaf'],seed+i,shadow=20,blur=9)

def apple(base,x,y,s=1,seed=0):
    ell(base,(x-int(55*s*S),y-int(42*s*S),x+int(55*s*S),y+int(62*s*S)),COL['apple'],seed,shadow=34,blur=14)
    d=ImageDraw.Draw(base,'RGBA'); d.line((x,y-int(42*s*S),x+int(22*s*S),y-int(88*s*S)),fill=COL['rock'],width=max(6,int(8*s*S)))
    ell(base,(x+int(10*s*S),y-int(100*s*S),x+int(65*s*S),y-int(58*s*S)),COL['leaf'],seed+1,shadow=18,blur=8)

def acorn(base,x,y,s=1,seed=0):
    ell(base,(x-int(42*s*S),y-int(12*s*S),x+int(42*s*S),y+int(82*s*S)),(171,101,48,255),seed,shadow=30,blur=12)
    d=ImageDraw.Draw(base,'RGBA'); d.pieslice((x-int(52*s*S),y-int(48*s*S),x+int(52*s*S),y+int(40*s*S)),180,360,fill=COL['rock'])

def squirrel(base,x,y,s=1,seed=0):
    ell(base,(x-int(105*s*S),y-int(140*s*S),x-int(5*s*S),y+int(55*s*S)),COL['squirrel2'],seed,shadow=32,blur=13)
    ell(base,(x-int(50*s*S),y-int(70*s*S),x+int(50*s*S),y+int(70*s*S)),COL['squirrel'],seed+1,shadow=32,blur=13)
    ell(base,(x+int(20*s*S),y-int(125*s*S),x+int(90*s*S),y-int(50*s*S)),COL['squirrel'],seed+2,shadow=24,blur=9)
    d=ImageDraw.Draw(base,'RGBA'); d.polygon([(x+int(42*s*S),y-int(120*s*S)),(x+int(58*s*S),y-int(165*s*S)),(x+int(70*s*S),y-int(110*s*S))],fill=COL['squirrel'])
    d.ellipse((x+int(57*s*S),y-int(94*s*S),x+int(68*s*S),y-int(83*s*S)),fill=COL['dark'])

def finish(im,name):
    # add subtle global contrast and downsample
    im=im.filter(ImageFilter.UnsharpMask(radius=2,percent=115,threshold=4)).convert('RGB')
    hi=OUT/f'{name}_2160x3840.png'; im.save(hi)
    lo=im.resize((1080,1920),Image.Resampling.LANCZOS)
    path=OUT/f'{name}.png'; lo.save(path)
    return str(path)

files=[]
# 1
im=scene_bg(101); draw_water(im,1710,1)
for vals in [(390,1340,530,360,11),(1270,1480,700,420,12),(1780,1030,430,330,13),(960,820,360,240,14)]: island(im,*vals)
shark(im,1050,2440,1.25,seed=15); files.append(finish(im,'01_before_trees_barren_land_premium'))
# 2
im=scene_bg(102); rr(im,(220,450,1940,3260),70*S,(70,46,30,255),20); rr(im,(330,600,1830,3000),38*S,COL['sand'],21)
for y in [920,1320,1720,2120,2520]: ImageDraw.Draw(im,'RGBA').line((420,y,1740,y),fill=COL['rock'],width=34*S)
for x in [650,1080,1510]: ImageDraw.Draw(im,'RGBA').line((x,700,x,2860),fill=COL['rock'],width=24*S)
for cx,cy,s in [(1080,1320,1.18),(690,2070,.7),(1460,2230,.75)]: shark(im,cx,cy,s,color=COL['bone'],seed=int(cx))
ell(im,(1400,700,1660,960),COL['bone'],31,shadow=18,blur=8); ImageDraw.Draw(im,'RGBA').line((1610,920,1780,1090),fill=COL['bone'],width=32*S)
files.append(finish(im,'02_seriously_fossil_museum_premium'))
# 3
im=scene_bg(103); rr(im,(0,0,W,2360),0,COL['sand2'],25,shadow=0); draw_water(im,2600,3)
for vals in [(460,1840,600,310,31),(1360,1950,680,350,32),(1050,1360,470,270,33)]: island(im,*vals)
apple(im,520,1250,2.0,41); squirrel(im,1080,1510,1.7,42); acorn(im,1570,1280,2.0,43)
for x in [230,1900]: tree(im,x,2200,.75,bare=True,seed=x)
files.append(finish(im,'03_apples_squirrel_nuts_gag_premium'))
# 4
im=scene_bg(104); rr(im,(220,290,1940,3480),60*S,(65,45,30,255),50)
for i,y in enumerate(range(520,3080,400)):
    rr(im,(340,y,1820,y+270),28*S,COL['sand'] if i%2 else (200,142,67,255),55+i)
    if i<2: shark(im,1020,y+150,.52,color=COL['bone'],seed=60+i)
    if i==4:
        for x in [650,1040,1450]: plant(im,x,y+245,.75,seed=x)
    ell(im,(1480,y+45,1650,y+215),COL['bone'],70+i,shadow=12,blur=5)
    d=ImageDraw.Draw(im,'RGBA'); d.line((1565,y+130,1565,y+70),fill=COL['rock'],width=8*S); d.line((1565,y+130,1620,y+150),fill=COL['rock'],width=8*S)
files.append(finish(im,'04_geologic_deep_time_timeline_premium'))
# 5
im=scene_bg(105); draw_water(im,2320,5)
for x in [230,460,720,1080,1430,1760,2000]: tree(im,x,2220,random.uniform(.9,1.28),False,seed=x)
for _ in range(34): plant(im,random.randint(60,W-60),random.randint(1820,2920),random.uniform(.55,1.1),seed=random.randint(0,9999))
shark(im,1390,2920,.65,seed=80); files.append(finish(im,'05_primitive_forest_arrives_premium'))
# 6
im=scene_bg(106); rr(im,(150,300,2010,3300),45*S,(76,175,168,210),91); ImageDraw.Draw(im,'RGBA').rectangle((150,300,2010,3300),outline=COL['cream'],width=38*S)
for x in [550,1080,1610]: ImageDraw.Draw(im,'RGBA').line((x,300,x,3300),fill=(240,220,170,95),width=12*S)
for cx,cy,s in [(1280,1240,1.0),(670,1840,.6),(1530,2360,.55)]: shark(im,cx,cy,s,color=(67,139,149,255),seed=int(cx))
d=ImageDraw.Draw(im,'RGBA')
for cx,cy,s in [(840,3150,1.25),(1180,3210,.85),(1420,3180,1.0)]:
    d.ellipse((cx-int(42*s*S),cy-int(270*s*S),cx+int(42*s*S),cy-int(185*s*S)),fill=COL['dark'])
    d.rounded_rectangle((cx-int(46*s*S),cy-int(185*s*S),cx+int(46*s*S),cy),radius=int(34*s*S),fill=COL['dark'])
files.append(finish(im,'06_modern_viewer_aquarium_premium'))
# 7
im=scene_bg(107); draw_water(im,1180,7); island(im,1580,900,650,250,101); island(im,520,860,440,210,102)
ell(im,(1520,340,1840,660),(235,197,105,170),110,shadow=0); shark(im,1080,2220,1.35,seed=111)
files.append(finish(im,'07_survivor_world_before_forests_premium'))

(ROOT/'outputs/v7_premium_papercut_manifest.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
print(json.dumps({'count':len(files),'files':files},indent=2))
