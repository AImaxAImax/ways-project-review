
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import math, json, subprocess, random, shutil
CASE=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT=CASE/'outputs/say_dog_v04_proof_hybrid'
FRAMES=OUT/'frames'
OUT.mkdir(parents=True, exist_ok=True)
if FRAMES.exists(): shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)
W,H=1080,1920; FPS=24
beats=[
 ('01_hook_flash','THIS SHRIMP PUNCH\\nMAKES WATER FLASH',3.92,'real_mantis_flash'),
 ('02_club_speed','ITS CLUB MOVES\\nINSANELY FAST',3.91,'club_path'),
 ('03_cavitation','THAT FLASH\\nIS CAVITATION',3.92,'bubble_form'),
 ('04_first_hit','THE PUNCH\\nHITS FIRST',3.91,'first_impact'),
 ('05_second_hit','THEN THE BUBBLE\\nCOLLAPSES',3.91,'bubble_collapse'),
 ('06_high_speed','SCIENTISTS FILMED IT\\nIN HIGH SPEED',3.92,'high_speed_sequence'),
 ('07_not_just_prey','IT DOES NOT JUST\\nPUNCH PREY',3.92,'pullback'),
 ('08_water_punches','THE WATER\\nPUNCHES TOO',3.91,'final_replay'),
]
plates=CASE/'assets/wan_motion_v03_clean_plates'
plate_files=[plates/f'shot{i:02d}_clean_mantis_photo_plate.png' for i in range(1,9)]
base_imgs=[]
for p in plate_files:
    im=Image.open(p).convert('RGB').resize((W,H), Image.LANCZOS)
    im=ImageEnhance.Color(im).enhance(1.12)
    im=ImageEnhance.Contrast(im).enhance(1.08)
    base_imgs.append(im)

def underwater_bg(seed=0):
    rnd=random.Random(seed)
    img=Image.new('RGB',(W,H),(5,30,45)); d=ImageDraw.Draw(img,'RGBA')
    # Fast gradient bands
    for y in range(0,H,6):
        t=y/H; v=int(26+42*(1-t)+8*math.sin(y*.012))
        col=(max(0,3+v//6), max(12,35+v), max(30,68+v))
        d.rectangle((0,y,W,y+6), fill=col)
    for _ in range(520):
        x=rnd.randrange(W); y=rnd.randrange(H); r=rnd.choice([1,1,2,2,3]); a=rnd.randrange(20,80)
        d.ellipse((x-r,y-r,x+r,y+r), fill=(180,230,255,a))
    for _ in range(10):
        x=rnd.randrange(-100,W); y=rnd.randrange(200,H-100)
        d.line((x,y,x+rnd.randrange(120,320),y-rnd.randrange(20,80)), fill=(90,180,210,35), width=rnd.randrange(2,6))
    return img.filter(ImageFilter.GaussianBlur(0.15))

def draw_shell(d,x,y,scale=1.0,alpha=255):
    pts=[]
    for i in range(42):
        ang=i/42*2*math.pi; rr=scale*(74+18*math.sin(3*ang))
        pts.append((x+rr*math.cos(ang), y+rr*0.62*math.sin(ang)))
    d.polygon(pts, fill=(205,172,123,alpha), outline=(80,55,35,alpha))
    for i in range(5):
        yy=y-scale*28+i*scale*14
        d.arc((x-scale*75, yy-scale*30, x+scale*75, yy+scale*30), 200, 340, fill=(112,75,45,alpha), width=max(2,int(4*scale)))

def draw_club(d, x0,y0,x1,y1,width=34,alpha=255, color=(250,170,80)):
    d.line((x0,y0,x1,y1), fill=(*color,alpha), width=width)
    r=width*1.2; cx,cy=x1,y1
    d.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(255,205,95,alpha), outline=(70,30,15,alpha), width=3)
    d.ellipse((x0-width*.65,y0-width*.65,x0+width*.65,y0+width*.65), fill=(210,80,50,alpha))

def draw_ripples(d,cx,cy,t,maxr=360,color=(190,245,255),alpha=180,count=4):
    for k in range(count):
        r=maxr*(t*0.9+k*0.14)
        if r<12 or r>maxr: continue
        a=int(alpha*(1-r/maxr))
        d.ellipse((cx-r,cy-r*0.62,cx+r,cy+r*0.62), outline=(*color,a), width=8)

def draw_bubbles(d,cx,cy,t,scale=1.0,collapse=False):
    rnd=random.Random(10)
    for i in range(46):
        ang=rnd.random()*2*math.pi
        if collapse:
            dist=(1-t)*(30+rnd.random()*180)*scale; rr=(2+rnd.random()*16)*(1-t*.65)*scale
        else:
            dist=t*(25+rnd.random()*210)*scale; rr=(2+rnd.random()*18)*(0.4+t)*scale
        x=cx+math.cos(ang)*dist+rnd.uniform(-18,18)*scale
        y=cy+math.sin(ang)*dist*0.65+rnd.uniform(-12,12)*scale
        a=int(55+155*(1-abs(t-.55))) if not collapse else int(65+160*t)
        d.ellipse((x-rr,y-rr,x+rr,y+rr), outline=(235,255,255,a), width=max(2,int(3*scale)))
        if rr>7: d.ellipse((x-rr*.3,y-rr*.45,x-rr*.05,y-rr*.2), fill=(255,255,255,min(150,a)))

def make_frame(kind, beat_i, f, n):
    t=f/max(1,n-1)
    if kind in ('real_mantis_flash','pullback'):
        img=base_imgs[0 if kind=='real_mantis_flash' else 6].copy(); d=ImageDraw.Draw(img,'RGBA')
        if kind=='real_mantis_flash':
            cx,cy=660,980; draw_shell(d,740,1000,0.9,220); grow=min(1,t*2.2); draw_bubbles(d,cx,cy,grow,1.1)
            if .18<t<.62:
                a=int(210*(1-abs(t-.38)/.24))
                d.ellipse((cx-100,cy-64,cx+170,cy+80), fill=(255,255,235,a), outline=(255,255,255,min(255,a+35)), width=8)
                draw_ripples(d,cx,cy,t,280,alpha=a)
        else:
            draw_shell(d,705,1045,0.82,225); draw_bubbles(d,620,990,.72,0.8)
        return img
    bg=underwater_bg(beat_i); d=ImageDraw.Draw(bg,'RGBA')
    if kind=='high_speed_sequence':
        for j in range(4):
            x=90+j*225; y=620; box=(x,y,x+190,y+420)
            d.rounded_rectangle(box, radius=28, fill=(10,45,58,210), outline=(105,200,220,180), width=4)
            tt=min(1,max(0,(t*4-j)))
            cx=x+92; cy=y+238; draw_shell(d,cx+52,cy+8,0.28,230)
            d.ellipse((cx-70,cy-34,cx+20,cy+36), fill=(70,190,150,220), outline=(10,60,55,220), width=3)
            draw_club(d,cx-5,cy,cx+18+tt*85,cy-8+tt*12,width=10,alpha=230)
            if tt>.45: draw_bubbles(d,cx+100,cy,min(1,(tt-.45)/.55),.32)
        draw_ripples(d,540,1095,t,420,alpha=125,count=4); return bg
    d.ellipse((120,835,505,1120), fill=(75,190,150,230), outline=(6,60,55,240), width=6)
    d.ellipse((85,820,215,900), fill=(110,230,165,235), outline=(10,70,55,230), width=5)
    d.ellipse((135,760,170,805), fill=(245,255,245,235)); d.ellipse((148,773,162,790), fill=(20,20,20,255))
    d.line((180,820,70,720), fill=(255,180,105,220), width=8); d.line((215,840,135,730), fill=(255,180,105,220), width=8)
    target=(760,980); draw_shell(d,*target,1.0,240)
    if kind=='club_path':
        start=(365,930); end=(start[0]+(target[0]-start[0])*(0.25+0.75*t), start[1]+(target[1]-start[1])*(0.25+0.75*t))
        for k in range(5):
            tt=max(0,t-k*.055); ex=start[0]+(target[0]-start[0])*(0.25+0.75*tt); ey=start[1]+(target[1]-start[1])*(0.25+0.75*tt)
            draw_club(d,start[0],start[1],ex,ey,width=36-k*4,alpha=55+k*35)
        draw_club(d,start[0],start[1],end[0],end[1],width=34,alpha=255)
        if t>.6: draw_bubbles(d,target[0]-30,target[1],(t-.6)/.4,.7)
    elif kind=='bubble_form':
        draw_club(d,365,930,710,970,width=28,alpha=235); draw_bubbles(d,740,975,t,1.15); draw_ripples(d,740,975,t,300,alpha=120)
    elif kind=='first_impact':
        draw_club(d,365,930,735,975,width=35,alpha=250)
        if t>.22:
            p=min(1,(t-.22)/.25); d.polygon([(705,950),(790,900),(760,980),(825,1035),(720,1015)], fill=(255,242,185,int(200*(1-p*.25))))
            draw_ripples(d,748,980,p,220,alpha=190)
            for a in [-.8,-.25,.35,.8]: d.line((760,980,760+math.cos(a)*90*p,980+math.sin(a)*62*p), fill=(60,35,25,190), width=4)
    elif kind=='bubble_collapse':
        draw_club(d,365,930,710,970,width=25,alpha=180); draw_bubbles(d,740,975,t,1.05,collapse=True)
        if t>.45:
            p=(t-.45)/.55; d.ellipse((700-70*p,940-45*p,800+70*p,1015+45*p), outline=(255,255,255,int(230*(1-p))), width=8)
            draw_ripples(d,750,980,p,360,alpha=220,count=5); d.line((800,980,885,982), fill=(255,235,160,int(190*(1-p*.3))), width=12)
    elif kind=='final_replay':
        draw_club(d,345,920,725,965,width=30,alpha=240); draw_bubbles(d,720,965,min(1,t*1.6),0.75)
        if t>.42:
            p=(t-.42)/.58; draw_bubbles(d,800,1015,p,0.75,collapse=True); draw_ripples(d,800,1015,p,390,alpha=220,count=5); d.ellipse((760,980,845,1040), fill=(255,255,230,int(120*(1-p))))
    return bg

def write_ass(path):
    def ts(t):
        h=int(t//3600); m=int((t%3600)//60); s=t%60; return f"{h}:{m:02d}:{s:05.2f}"
    head="[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Caption,Arial,102,&H00FFFFFF,&H0000D7FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,3,5,80,80,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    lines=[]; cur=0
    for _,cap,dur,_ in beats:
        a,b=cap.split('\\n'); safe=r'{\c&H0000D7FF&}'+a+r'{\c&H00FFFFFF&}\N'+b
        lines.append(f"Dialogue: 0,{ts(cur)},{ts(cur+dur)},Caption,,0,0,0,,{safe}"); cur+=dur
    path.write_text(head+'\n'.join(lines)+'\n')

idx=0; beat_map=[]
for bi,(bid,cap,dur,kind) in enumerate(beats,1):
    n=round(dur*FPS); beat_map.append({'beat':bi,'id':bid,'caption':cap.replace('\\n',' / '),'visual_kind':kind,'frames':n})
    for f in range(n):
        im=make_frame(kind,bi,f,n).convert('RGBA')
        overlay=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(overlay,'RGBA')
        od.rounded_rectangle((70,720,W-70,1210), radius=40, fill=(0,0,0,35))
        Image.alpha_composite(im, overlay).convert('RGB').save(FRAMES/f'frame_{idx:05d}.jpg', quality=92)
        idx+=1
(OUT/'beat_map_v04.json').write_text(json.dumps(beat_map,indent=2))
ass=OUT/'captions_say_dog_v04.ass'; write_ass(ass)
silent=OUT/'mantis_say_dog_v04_silent_1080.mp4'; master=OUT/'mantis_say_dog_v04_captioned_1080.mp4'; preview=OUT/'mantis_say_dog_v04_captioned_720.mp4'; contact=OUT/'contact_sheet_mantis_say_dog_v04.jpg'; voice=CASE/'outputs/auto_static_v01/voiceover.mp3'
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','18','-preset','medium',str(silent)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(voice),'-vf',f'ass={ass}','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-shortest','-movflags','+faststart',str(master)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview),'-vf','fps=1,scale=270:480,tile=6x6','-frames:v','1','-update','1',str(contact)],check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate','-of','json',str(preview)],text=True)
(OUT/'ffprobe_preview.json').write_text(probe)
(OUT/'README_QA.md').write_text(f"""# Mantis say-dog-see-dog v04 proof hybrid\n\nStatus: internal review candidate, not public-upload final.\n\nThis rebuild fixes repeated macro-shot fatigue by giving each claim a distinct visual/action. It uses a hybrid lane: real mantis source plates for context plus a clean no-text proof animation for the strike, cavitation bubble formation, bubble collapse, and second shock. It should not be represented as real high-speed footage.\n\nOutputs:\n- Discord preview: `{preview}`\n- Master: `{master}`\n- Contact sheet: `{contact}`\n- Beat map: `{OUT/'beat_map_v04.json'}`\n\nQA target: say-dog-see-dog direction check. Public upload still requires Gate 5/6 and likely a more premium final-art pass if Josh likes the structure.\n""")
print(json.dumps({'preview':str(preview),'master':str(master),'contact_sheet':str(contact),'frames':idx,'ffprobe':json.loads(probe)},indent=2))
