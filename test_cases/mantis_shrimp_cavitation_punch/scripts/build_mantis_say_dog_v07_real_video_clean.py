from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import subprocess, shutil, json, math, random

CASE=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT=CASE/'outputs/say_dog_v07_real_video_clean'
FRAMES=OUT/'frames'
SRC=OUT/'src_frames'
VOICE=CASE/'outputs/auto_static_v01/voiceover.mp3'
VIDEO_DIR=CASE/'assets/source_commons_video'
W,H,FPS=1080,1920,24
for p in [OUT]: p.mkdir(parents=True,exist_ok=True)
for p in [FRAMES,SRC]:
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True)

# Cleaner asset strategy: use real Commons video for motion. No generated mantis frames.
sources={
    'peacock': VIDEO_DIR/'peacock_mantis.webm',
    'wide': VIDEO_DIR/'mantis_philippines.webm',
}
for name,path in sources.items():
    d=SRC/name; d.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(path),'-vf','fps=24',str(d/'f_%05d.jpg')],check=True)

cache={}
def load(name):
    if name not in cache:
        cache[name]=[Image.open(p).convert('RGB') for p in sorted((SRC/name).glob('f_*.jpg'))]
    return cache[name]

def cover_crop(im, focus_x=.34, focus_y=.50, zoom=1.0):
    iw,ih=im.size
    target=9/16
    # crop horizontal source to 9:16, then scale. focus_x follows subject left/right.
    crop_w=int(ih*target/zoom)
    crop_h=int(ih/zoom)
    if crop_w>iw:
        crop_w=iw; crop_h=int(iw/target)
    cx=int(iw*focus_x); cy=int(ih*focus_y)
    x=max(0,min(iw-crop_w,cx-crop_w//2)); y=max(0,min(ih-crop_h,cy-crop_h//2))
    return im.crop((x,y,x+crop_w,y+crop_h)).resize((W,H),Image.LANCZOS)

def grade(im):
    im=ImageEnhance.Color(im).enhance(1.05)
    im=ImageEnhance.Contrast(im).enhance(1.09)
    im=ImageEnhance.Brightness(im).enhance(.96)
    # de-noise very slightly from underwater compression
    im=im.filter(ImageFilter.UnsharpMask(radius=1.1,percent=70,threshold=4))
    mask=Image.new('L',(W,H),0); d=ImageDraw.Draw(mask)
    d.ellipse((-240,100,W+240,H+70), fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(170))
    dark=Image.new('RGB',(W,H),(2,16,20))
    return Image.composite(im,dark,mask)

def video_frame(name,t_global,beat_t,focus_x,zoom=1.0,offset=0):
    arr=load(name)
    # sample source continuously, no ping-pong loops. Different offsets make beats distinct.
    idx=int((offset*FPS + beat_t*len(arr)*.75)) % len(arr)
    return grade(cover_crop(arr[idx],focus_x=focus_x,zoom=zoom))

def bubbles(layer,cx,cy,t,seed=0,collapse=False,density=22,scale=.55,alpha=70):
    d=ImageDraw.Draw(layer,'RGBA'); rnd=random.Random(seed)
    for _ in range(density):
        a=rnd.random()*math.tau
        if collapse:
            dist=(1-t)*(20+rnd.random()*125)*scale; r=(1.2+rnd.random()*8)*(1-.55*t)*scale; al=int(alpha*(.45+.55*t)*(0.5+rnd.random()*0.5))
        else:
            dist=t*(20+rnd.random()*145)*scale; r=(1.2+rnd.random()*8)*(.4+.55*t)*scale; al=int(alpha*(.55+.45*(1-abs(t-.55)))*(0.5+rnd.random()*0.5))
        x=cx+math.cos(a)*dist+rnd.uniform(-8,8); y=cy+math.sin(a)*dist*.62+rnd.uniform(-6,6)
        if 0<x<W and 0<y<H:
            d.ellipse((x-r,y-r,x+r,y+r), outline=(235,255,255,al), width=max(1,int(1.8*scale)))

def flash(layer,cx,cy,t,peak=.30,strength=.35):
    p=max(0,1-abs(t-peak)/.13)
    if p<=0: return
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(3,0,-1):
        r=(36+k*28)*(.85+.3*p)
        d.ellipse((cx-r,cy-r*.45,cx+r,cy+r*.45), fill=(245,255,232,int(16*k*p*strength)))
    d.ellipse((cx-54*p,cy-24*p,cx+70*p,cy+30*p), fill=(255,255,235,int(58*p*strength)))

def ripple(layer,cx,cy,t,maxr=220,alpha=58,count=2):
    d=ImageDraw.Draw(layer,'RGBA')
    for k in range(count):
        r=maxr*(t*.88+k*.22)
        if 10<r<maxr:
            al=int(alpha*(1-r/maxr))
            d.ellipse((cx-r,cy-r*.52,cx+r,cy+r*.52), outline=(220,250,255,al), width=4)

def caption_shade(im):
    shade=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(shade,'RGBA')
    for y in range(680,1180,10):
        a=int(max(0,34*(1-abs(y-930)/250)))
        d.rectangle((0,y,W,y+10),fill=(0,0,0,a))
    return Image.alpha_composite(im.convert('RGBA'),shade).convert('RGB')

beats=[
 ('01_hook_flash','THIS SHRIMP PUNCH\\nMAKES WATER FLASH',3.92,'peacock',.31,1.03,0,'flash',(615,945)),
 ('02_club_speed','ITS CLUB MOVES\\nINSANELY FAST',3.91,'peacock',.40,1.08,2,'speed',(585,970)),
 ('03_cavitation','THAT FLASH\\nIS CAVITATION',3.92,'peacock',.35,1.15,4,'cavitation',(620,945)),
 ('04_first_hit','THE PUNCH\\nHITS FIRST',3.91,'peacock',.33,1.12,5,'impact',(600,960)),
 ('05_second_hit','THEN THE BUBBLE\\nCOLLAPSES',3.91,'peacock',.38,1.16,6,'collapse',(610,960)),
 ('06_high_speed','SCIENTISTS FILMED IT\\nIN HIGH SPEED',3.92,'peacock',.34,1.22,7,'replay',(605,955)),
 ('07_not_just_prey','IT DOES NOT JUST\\nPUNCH PREY',3.92,'wide',.32,1.00,1,'wide',(560,1010)),
 ('08_water_punches','THE WATER\\nPUNCHES TOO',3.91,'peacock',.36,1.12,8,'water',(620,950)),
]

def make_frame(beat,cap,dur,src,focus_x,zoom,offset,kind,loc,f,n):
    t=f/max(1,n-1)
    im=video_frame(src,0,t,focus_x,zoom,offset).convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0))
    cx,cy=loc
    # Effects are deliberately subtle. If you pause, it should still read as real footage, not graphics.
    if kind=='flash':
        flash(layer,cx,cy,t,.26,.55); bubbles(layer,cx,cy,min(1,t*1.15),seed=1,density=14,scale=.5,alpha=54); ripple(layer,cx,cy,max(0,(t-.25)/.75),240,44,2)
    elif kind=='speed':
        # no club drawing. A slight exposure smear only.
        flash(layer,cx-90,cy+30,t,.42,.18)
    elif kind=='cavitation':
        bubbles(layer,cx,cy,min(1,t*1.08),seed=3,density=22,scale=.58,alpha=64); flash(layer,cx,cy,t,.50,.22)
    elif kind=='impact':
        flash(layer,cx,cy,t,.31,.42); ripple(layer,cx,cy,max(0,(t-.28)/.50),220,60,2)
    elif kind=='collapse':
        bubbles(layer,cx,cy,t,seed=5,collapse=True,density=22,scale=.62,alpha=72)
        if t>.43: ripple(layer,cx+10,cy+5,(t-.43)/.57,300,70,3)
    elif kind=='replay':
        # stutter-free replay: quick micro-zooms using real video, no frame dividers/UI.
        if int(t*8)%2==0: flash(layer,cx,cy,.30,.30,.12)
        ripple(layer,cx,cy,t,250,36,2)
    elif kind=='wide':
        pass
    elif kind=='water':
        bubbles(layer,cx,cy,min(1,t*1.05),seed=8,density=16,scale=.55,alpha=56)
        if t>.35: bubbles(layer,cx+20,cy+12,(t-.35)/.65,seed=9,collapse=True,density=20,scale=.6,alpha=78); ripple(layer,cx+20,cy+12,(t-.35)/.65,340,82,3)
    im=Image.alpha_composite(im,layer)
    return caption_shade(im)

def write_ass(path):
    def ts(t):
        return f"{int(t//3600)}:{int((t%3600)//60):02d}:{t%60:05.2f}"
    head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,102,&H00FFFFFF,&H0000D7FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,3,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    cur=0; lines=[]
    for _,cap,dur,*_ in beats:
        a,b=cap.split('\\n')
        text=r'{\c&H0000D7FF&}'+a+r'{\c&H00FFFFFF&}\N'+b
        lines.append(f'Dialogue: 0,{ts(cur)},{ts(cur+dur)},Caption,,0,0,0,,{text}')
        cur+=dur
    path.write_text(head+'\n'.join(lines)+'\n')

idx=0; beat_map=[]
for bi,b in enumerate(beats,1):
    bid,cap,dur,src,focus_x,zoom,offset,kind,loc=b
    n=round(dur*FPS)
    beat_map.append({'beat':bi,'id':bid,'caption':cap.replace('\\n',' / '),'source_video':src,'visual_kind':kind,'frames':n,'strategy':'real Commons video base, no generated animal frames, subtle no-text effects only'})
    for f in range(n):
        make_frame(*b,f,n).save(FRAMES/f'frame_{idx:05d}.jpg',quality=94)
        idx+=1
(OUT/'beat_map_v07.json').write_text(json.dumps(beat_map,indent=2))
ass=OUT/'captions_say_dog_v07.ass'; write_ass(ass)
silent=OUT/'mantis_say_dog_v07_silent_1080.mp4'; master=OUT/'mantis_say_dog_v07_captioned_1080.mp4'; preview=OUT/'mantis_say_dog_v07_captioned_720.mp4'; contact=OUT/'contact_sheet_mantis_say_dog_v07.jpg'
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(FRAMES/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','17','-preset','medium',str(silent)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(VOICE),'-vf',f'ass={ass}','-af','highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1','-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(master)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview),'-vf','fps=1,scale=270:480,tile=6x6','-frames:v','1','-update','1',str(contact)],check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size,bit_rate','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate,bit_rate','-of','json',str(preview)],text=True)
(OUT/'ffprobe_preview.json').write_text(probe)
(OUT/'README_QA.md').write_text(f'''# Mantis shrimp cavitation punch — v07 real-video clean candidate

Status: internal review candidate.

Built after Josh flagged artifacts in v05. This version uses only real Commons video for the animal footage and no generated animal frames. It keeps no non-caption labels and uses only subtle no-text effect cues for flash/cavitation/collapse.

Source video assets:
- `Peacock mantis shrimp (Odontodactylus scyllarus).webm`, CC BY 2.0, artist: jeff~
- `Mantis shrimp in the Philippines.webm`, CC BY 2.0, artist: jeff~

Outputs:
- Preview: `{preview}`
- Master: `{master}`
- Contact sheet: `{contact}`
- Beat map: `{OUT/'beat_map_v07.json'}`
''')
print(json.dumps({'preview':str(preview),'master':str(master),'contact_sheet':str(contact),'frames':idx,'ffprobe':json.loads(probe)},indent=2))
