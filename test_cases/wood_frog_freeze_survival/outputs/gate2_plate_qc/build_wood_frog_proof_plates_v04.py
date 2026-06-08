from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ROOT = Path('/mnt/c/dev/curious-shorts')
CASE = ROOT / 'test_cases/wood_frog_freeze_survival'
SRC_DIR = CASE / 'assets/source_stills'
OUT_DIR = CASE / 'outputs/gate2_plate_qc'
W, H = 1080, 1920


def cover_crop(im, size=(W, H), focus=(0.50, 0.52)):
    im = im.convert('RGB')
    sw, sh = im.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    cx = int(nw * focus[0]); cy = int(nh * focus[1])
    left = max(0, min(nw - tw, cx - tw // 2))
    top = max(0, min(nh - th, cy - th // 2))
    return im.crop((left, top, left + tw, top + th))


def cold_grade(im):
    im = ImageEnhance.Color(im).enhance(0.62)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    wash = Image.new('RGB', im.size, (120, 180, 220))
    return Image.blend(im, wash, 0.18)


def draw_crystals(draw, origin, length, angle, depth, color, width=4):
    if depth <= 0 or length < 16:
        return
    x, y = origin
    x2 = x + math.cos(angle) * length
    y2 = y + math.sin(angle) * length
    draw.line((x, y, x2, y2), fill=color, width=width)
    for sign in (-1, 1):
        draw_crystals(draw, (x2, y2), length * 0.58, angle + sign * 0.72, depth - 1, color, max(1, width - 1))


def frog_body_mask():
    mask = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(mask)
    # Broad, non-anatomical frog-body silhouette over the real frog source; no labels/text.
    d.ellipse((220, 575, 900, 1245), fill=210)
    d.ellipse((165, 690, 520, 1125), fill=180)
    d.ellipse((575, 650, 960, 1120), fill=175)
    d.ellipse((385, 450, 735, 760), fill=190)
    d.polygon([(235,1120),(90,1425),(285,1375),(455,1165)], fill=145)
    d.polygon([(815,1080),(980,1375),(820,1430),(655,1160)], fill=145)
    return mask.filter(ImageFilter.GaussianBlur(26))


def add_frost_edge(base):
    frost = Image.new('RGBA', (W, H), (0,0,0,0))
    d = ImageDraw.Draw(frost)
    for i in range(0, W, 48):
        y = 110 + int(42 * math.sin(i * 0.021))
        d.line((i, 0, i+90, y), fill=(225,248,255,68), width=3)
    for i in range(0, W, 60):
        y = H - 135 + int(35 * math.sin(i * 0.017 + 1.7))
        d.line((i, H, i+105, y), fill=(225,248,255,58), width=3)
    return Image.alpha_composite(base.convert('RGBA'), frost)


def make_freeze_through_body():
    base = cold_grade(cover_crop(Image.open(SRC_DIR/'source_02.jpg'), focus=(0.45,0.52))).convert('RGBA')
    base = add_frost_edge(base)
    mask = frog_body_mask()
    blue = Image.new('RGBA', (W,H), (95, 190, 235, 92))
    base = Image.composite(Image.alpha_composite(base, blue), base, mask)
    veins = Image.new('RGBA', (W,H), (0,0,0,0))
    d = ImageDraw.Draw(veins)
    for seed in [(315,760,210,-0.10),(480,690,270,0.32),(620,750,260,0.95),(735,900,230,2.35),(390,990,230,-2.42)]:
        x,y,l,a = seed
        draw_crystals(d, (x,y), l, a, 4, (236,252,255,185), 5)
    # translucent cutaway window implies ice through much of body, not just surface frost.
    d.ellipse((310,650,795,1125), outline=(242,254,255,160), width=8)
    d.ellipse((355,715,750,1075), outline=(185,230,250,105), width=5)
    veins = Image.composite(veins, Image.new('RGBA',(W,H),(0,0,0,0)), mask)
    base = Image.alpha_composite(base, veins)
    return base.convert('RGB')


def heart_points(cx, cy, s):
    pts=[]
    for i in range(160):
        t=2*math.pi*i/160
        x=16*math.sin(t)**3
        y=-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))
        pts.append((cx+x*s, cy+y*s))
    return pts


def make_heart_stop():
    base = cold_grade(cover_crop(Image.open(SRC_DIR/'source_01.jpg'), focus=(0.50,0.50))).convert('RGBA')
    base = add_frost_edge(base)
    mask = frog_body_mask()
    chill = Image.new('RGBA',(W,H),(80,150,205,68))
    base = Image.composite(Image.alpha_composite(base,chill), base, mask)
    overlay = Image.new('RGBA',(W,H),(0,0,0,0))
    d = ImageDraw.Draw(overlay)
    # Frozen heart icon, desaturated and crossed by ice crystals: visual proof of stopped heartbeat without text/UI.
    hp = heart_points(540, 820, 10.0)
    d.polygon(hp, fill=(88,120,145,205), outline=(230,250,255,230))
    d.line((455,820,625,820), fill=(235,252,255,230), width=7)
    d.line((540,725,540,915), fill=(225,246,255,155), width=5)
    for x in [510, 570]:
        d.rounded_rectangle((x, 775, x+22, 865), radius=8, fill=(230,250,255,180))
    # Fading pulse motif dissolves into flat line, deliberately no numbers/letters.
    pts=[(245,1065),(330,1065),(365,1015),(405,1115),(445,1065),(835,1065)]
    d.line(pts, fill=(226,250,255,145), width=8, joint='curve')
    for i in range(5):
        x = 715 + i*38
        d.line((x,1065,x+18,1065), fill=(226,250,255,90-i*13), width=8)
    draw_crystals(d, (475,780), 120, -0.65, 3, (238,253,255,190), 4)
    draw_crystals(d, (592,850), 110, 2.55, 3, (238,253,255,180), 4)
    overlay = Image.composite(overlay, Image.new('RGBA',(W,H),(0,0,0,0)), mask)
    base = Image.alpha_composite(base, overlay)
    return base.convert('RGB')


def thumb(im, target=(360,640)):
    return cover_crop(im, target)


def make_contact(paths):
    margin=24; cols=3; cellw=330; cellh=586
    rows=math.ceil(len(paths)/cols)
    sheet=Image.new('RGB',(cols*cellw+(cols+1)*margin, rows*cellh+(rows+1)*margin),(18,24,28))
    for idx,p in enumerate(paths):
        im=Image.open(p).convert('RGB')
        t=cover_crop(im,(cellw,cellh))
        x=margin+(idx%cols)*(cellw+margin); y=margin+(idx//cols)*(cellh+margin)
        sheet.paste(t,(x,y))
    out=OUT_DIR/'wood_frog_source_contact_sheet_v04.jpg'
    sheet.save(out, quality=92)
    return out


def main():
    p2 = SRC_DIR/'source_06_freeze_through_body_graphic.jpg'
    p3 = SRC_DIR/'source_07_heart_stop_graphic.jpg'
    make_freeze_through_body().save(p2, quality=94)
    make_heart_stop().save(p3, quality=94)
    paths = sorted(SRC_DIR.glob('source_*.jpg'))
    contact = make_contact(paths)
    print(json.dumps({'created':[str(p2),str(p3),str(contact)], 'count':len(paths)}, indent=2))

if __name__ == '__main__':
    main()
