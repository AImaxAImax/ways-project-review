#!/usr/bin/env python3
from __future__ import annotations
import json, math, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import subprocess

ROOT = Path('/mnt/c/dev/curious-shorts')
WORKFLOW = '/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json'
NEG = 'text, subtitles, readable letters, watermark, logo, UI, hard cut, scene transition, horror, blood, attack, morphing animal anatomy, duplicated limbs, distorted face, melted geometry, jitter, flicker, low quality, blurry, compression artifacts'
W,H=1080,1920

TOPICS = {
 'saturn_hexagon_storm': {
  'search': None,
  'source_urls': [
   ('PIA21052_orig.jpg','https://images-assets.nasa.gov/image/PIA21052/PIA21052~orig.jpg'),
   ('PIA17122_orig.jpg','https://images-assets.nasa.gov/image/PIA17122/PIA17122~orig.jpg'),
   ('PIA14646_orig.jpg','https://images-assets.nasa.gov/image/PIA14646/PIA14646~orig.jpg'),
   ('PIA20507_orig.jpg','https://images-assets.nasa.gov/image/PIA20507/PIA20507~orig.jpg')],
  'captions': ['Saturn has a hexagon storm','not a drawing / a real jet stream','each side is wider than Earth','storms keep spinning inside','a strange shape / made of weather'],
  'prompt_base': 'premium NASA Cassini science-documentary image-to-video from the exact still. Preserve Saturn north pole, hexagon geometry, cloud bands, colors and realistic planetary style. Add subtle true motion: slow orbital camera creep, gentle cloud drift, parallax, atmospheric shimmer. No labels, no text, no UI, no logos, no scene cut.'
 },
 'wombat_cube_poop': {
  'search': 'Common wombat animal photo',
  'captions': ['Wombats poop cubes','little cube shaped pellets','uneven stretching / inside the intestine','the corners form first','bathroom fact / plus physics'],
  'prompt_base': 'premium natural-history documentary image-to-video from the exact wombat still. Preserve real wombat anatomy and natural ground. Add subtle true motion: tiny camera creep, grass movement, soft light, gentle body or fur movement where believable. Keep cube scat props stable. No labels, no text, no logos, no morphing, no scene cut.'
 },
 'octopus_three_hearts': {
  'search': 'Octopus underwater photo',
  'captions': ['An octopus has three hearts','two hearts / push through the gills','the third / powers the body','when it swims / one heart slows','crawling can be easier'],
  'prompt_base': 'premium underwater documentary image-to-video from the exact octopus still. Preserve octopus anatomy, all arms attached, realistic color, glass/water depth. Add subtle true motion: water particles, gentle arm movement, slow camera creep, soft pulse glow stays fixed to body. No detached tentacles, no labels, no text, no logos, no scene cut.'
 },
 'tardigrade_survival_mode': {
  'search': 'Tardigrade microscope image',
  'captions': ['Tardigrades can pause their bodies','too dry / tiny tun','metabolism drops / like pause','water returns / they wake up','nature\'s strangest / survival trick'],
  'prompt_base': 'premium microscope science documentary image-to-video from the exact tardigrade still. Preserve tiny water bear body shape and microscope texture. Add subtle true motion: microscope focus breathing, tiny particle drift, gentle water shimmer or dry-to-wet mood. No labels, no text, no UI, no logos, no morphing, no scene cut.'
 }
}


def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000: return dest
    req=urllib.request.Request(url, headers={'User-Agent':'Hermes WAYS media prep'})
    with urllib.request.urlopen(req, timeout=60) as r:
        dest.write_bytes(r.read())
    return dest

def commons_image_urls(query, limit=4):
    api='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','generator':'search','gsrsearch':query,'gsrnamespace':'6','gsrlimit':limit,'prop':'imageinfo','iiprop':'url|mime|extmetadata','format':'json'})
    req=urllib.request.Request(api, headers={'User-Agent':'Hermes WAYS media prep/1.0 (educational video source lookup)'})
    data=json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
    pages=list((data.get('query') or {}).get('pages', {}).values())
    out=[]
    for p in pages:
        ii=(p.get('imageinfo') or [{}])[0]
        url=ii.get('url','')
        if ii.get('mime','').startswith('image/') and url.lower().split('?')[0].endswith(('.jpg','.jpeg','.png')):
            out.append((Path(urllib.parse.urlparse(url).path).name, url))
    return out[:limit]

def fit_cover(img):
    img=img.convert('RGB')
    iw,ih=img.size; scale=max(W/iw,H/ih); nw,nh=int(iw*scale),int(ih*scale)
    img=img.resize((nw,nh), Image.Resampling.LANCZOS)
    return img.crop(((nw-W)//2,(nh-H)//2,(nw-W)//2+W,(nh-H)//2+H))

def grade(img):
    img=ImageEnhance.Color(img).enhance(1.08)
    img=ImageEnhance.Contrast(img).enhance(1.14)
    return img

def overlay_dark_band(img):
    mask=Image.new('L',(W,H),0)
    px=mask.load()
    cy=int(H*.56)
    for y in range(H):
        d=abs(y-cy)/(H*.23)
        val=int(max(0,85*(1-d)))
        if val:
            for x in range(W): px[x,y]=val
    mask=mask.filter(ImageFilter.GaussianBlur(90))
    return Image.composite(Image.new('RGB',(W,H),(0,0,0)), img, mask)

def draw_hex(draw, color=(255,210,40), width=8):
    cx,cy=W//2,int(H*.43); r=330
    pts=[]
    for i in range(6):
        a=math.radians(30+i*60)
        pts.append((cx+r*math.cos(a), cy+r*math.sin(a)))
    draw.line(pts+[pts[0]], fill=color+(180,), width=width, joint='curve')

def make_plate(topic, src, out, idx, n):
    img=overlay_dark_band(grade(fit_cover(Image.open(src))))
    rgba=img.convert('RGBA'); ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    if topic=='saturn_hexagon_storm' and idx in (0,1,2,4):
        draw_hex(d, width=7 if idx!=4 else 5)
    if topic=='wombat_cube_poop' and idx in (1,3,4):
        # small non-text cube scat props near lower third, shaded and unobtrusive
        for k in range(5):
            x=330+k*70; y=1320+(k%2)*22
            d.rounded_rectangle((x,y,x+46,y+38), radius=7, fill=(86,62,42,235), outline=(130,100,70,230), width=3)
            d.polygon([(x,y),(x+14,y-11),(x+60,y-11),(x+46,y)], fill=(112,82,54,225))
    if topic=='octopus_three_hearts' and idx in (1,2,3):
        pts=[(420,910),(650,910)] if idx==1 else [(540,980)]
        if idx==3: pts=[(540,980),(420,910),(650,910)]
        for x,y in pts:
            d.ellipse((x-42,y-42,x+42,y+42), outline=(255,80,100,220), width=8)
            d.ellipse((x-18,y-18,x+18,y+18), fill=(255,80,100,95))
    if topic=='tardigrade_survival_mode' and idx in (1,3):
        for k in range(9):
            x=220+k*90; y=620+(k%3)*130
            d.ellipse((x-18,y-18,x+18,y+18), fill=(120,210,255,75), outline=(190,240,255,105), width=2)
    rgba=Image.alpha_composite(rgba, ov).convert('RGB')
    out.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(out, quality=94)

def ffprobe_duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)], text=True).strip())

def main():
    made=[]
    for slug,cfg in TOPICS.items():
        project=ROOT/'test_cases'/slug
        srcdir=project/'assets/source_wan_template_v01'
        platedir=project/'assets/wan_template_v01_plates'
        outdir=project/'outputs/wan22_template_v01'
        outdir.mkdir(parents=True, exist_ok=True)
        pairs=cfg.get('source_urls') or commons_image_urls(cfg['search'], 5)
        sources=[]
        for name,url in pairs:
            try:
                p=download(url, srcdir/name)
                Image.open(p).verify()
                sources.append({'path':str(p.relative_to(project)),'url':url})
            except Exception as e:
                print(json.dumps({'source_error':slug,'name':name,'error':repr(e)}), flush=True)
        if not sources: raise SystemExit(f'no sources for {slug}')
        (srcdir/'source_manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
        captions=cfg['captions']
        dur=ffprobe_duration(outdir/'voiceover.mp3')
        weights=[1]*len(captions)
        # hold proof/middle beats slightly longer
        if len(weights)>=5: weights=[.9,1.05,1.15,1.1,1.0]
        total=sum(weights)
        shots=[]
        for i,cap in enumerate(captions):
            src=project/sources[i%len(sources)]['path']
            plate=platedir/f'shot{i+1:02d}_{slug}_plate.jpg'
            make_plate(slug, src, plate, i, len(captions))
            shots.append({'id':f'{i+1:02d}','image':str(plate.relative_to(project)),'duration':round(dur*weights[i]/total,3),'caption':cap,'seed':840000 + list(TOPICS).index(slug)*100 + i+1,'prompt':cfg['prompt_base']})
        config={
          'project_root': str(project), 'slug': slug, 'output_dir': 'outputs/wan22_template_v01', 'voiceover': 'outputs/wan22_template_v01/voiceover.mp3',
          'workflow': WORKFLOW, 'comfy_url':'http://127.0.0.1:8188', 'negative_prompt': NEG,
          'render_settings': {'fps':24,'wan_width':432,'wan_height':768,'wan_length_frames':25,'master_width':1080,'master_height':1920,'master_crf':18,'audio_bitrate':'160k','audio_sample_rate':48000,'preview_width':720,'preview_height':1280,'preview_crf':24,'preview_audio_bitrate':'96k'},
          'workflow_overrides': {'39.inputs.vae_name':'wan_2.1_vae.safetensors'}, 'required_vae':'wan_2.1_vae.safetensors',
          'qa_gate':['actual I2V motion','no generated text/logos','captions added in final polish','per-shot visual match >=8/10','audio stream present'],
          'shots': shots
        }
        (project/'render_wan22_harness_config.json').write_text(json.dumps(config,indent=2)+'\n')
        made.append({'slug':slug,'sources':len(sources),'shots':len(shots),'duration':dur,'config':str(project/'render_wan22_harness_config.json')})
    print(json.dumps({'made':made}, indent=2))
if __name__=='__main__': main()
