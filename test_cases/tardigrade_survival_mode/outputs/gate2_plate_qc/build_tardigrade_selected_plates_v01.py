from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import json, math

ROOT = Path('/mnt/c/dev/curious-shorts')
CASE = ROOT / 'test_cases/tardigrade_survival_mode'
SRC = CASE / 'assets/source_rework'
SAMPLES = CASE / 'outputs/gate2_plate_qc/tardigrade_plate_select_v01'
OUT = CASE / 'outputs/gate2_plate_qc/selected_plates_v01'
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920

SELECT = [
    {
        'beat': '01_active_baseline',
        'role': 'active recognizable tardigrade hook/hero',
        'source_id': 'C007',
        'src': SAMPLES / 'C007_sample_002.jpg',
        'focus': (0.50, 0.50),
        'fit': 'cover',
    },
    {
        'beat': '02_desiccation_into_tun',
        'role': 'real source-supported desiccation/tucking/tun transition',
        'source_id': 'C002',
        'src': SAMPLES / 'C002_sample_006.jpg',
        'focus': (0.50, 0.50),
        'fit': 'contain',
    },
    {
        'beat': '03_dormant_tun_pause',
        'role': 'tun/dormant pause state; no HUD/text overlay',
        'source_id': 'C004',
        'src': SRC / 'C004_SEM_image_of_Milnesium_tardigradum_in_tun_state___journal_po.png',
        'focus': (0.50, 0.50),
        'fit': 'contain',
    },
    {
        'beat': '04_rehydration_reactivation',
        'role': 'C002 stage IV rehydration/reactivation fallback frame; no visible water-flow overclaim',
        'source_id': 'C002',
        'src': SAMPLES / 'C002_sample_014.jpg',
        'focus': (0.50, 0.50),
        'fit': 'contain',
    },
    {
        'beat': '05_final_survival_trick',
        'role': 'active/reactivated movement payoff from CC0 vertical microscope video',
        'source_id': 'C007',
        'src': SAMPLES / 'C007_sample_006.jpg',
        'focus': (0.50, 0.50),
        'fit': 'cover',
    },
]

def cover_crop(im, size=(W,H), focus=(0.5,0.5)):
    im = im.convert('RGB')
    sw, sh = im.size; tw, th = size
    scale = max(tw/sw, th/sh)
    nw, nh = int(sw*scale), int(sh*scale)
    im = im.resize((nw,nh), Image.Resampling.LANCZOS)
    left = max(0, min(nw-tw, int(nw*focus[0])-tw//2))
    top = max(0, min(nh-th, int(nh*focus[1])-th//2))
    return im.crop((left, top, left+tw, top+th))

def contain_on_blur(im):
    im = im.convert('RGB')
    bg = cover_crop(im).filter(ImageFilter.GaussianBlur(34))
    bg = ImageEnhance.Brightness(bg).enhance(0.72)
    sw, sh = im.size
    scale = min(W/sw, H/sh) * 0.94
    nw, nh = int(sw*scale), int(sh*scale)
    fg = im.resize((nw,nh), Image.Resampling.LANCZOS)
    x, y = (W-nw)//2, (H-nh)//2
    # soft matte behind microscope/SEM source so phone-size contact sheet keeps the subject readable.
    matte = Image.new('RGBA', (W,H), (0,0,0,0))
    d = ImageDraw.Draw(matte)
    d.rounded_rectangle((x-22,y-22,x+nw+22,y+nh+22), radius=28, fill=(0,0,0,96))
    out = Image.alpha_composite(bg.convert('RGBA'), matte).convert('RGB')
    out.paste(fg, (x,y))
    return out

def make_sheet(paths):
    cols=5; cellw=216; cellh=384; margin=18
    sheet=Image.new('RGB',(cols*cellw+(cols+1)*margin, cellh+2*margin),(18,24,28))
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB').resize((cellw,cellh), Image.Resampling.LANCZOS)
        x=margin+i*(cellw+margin); y=margin
        sheet.paste(im,(x,y))
    return sheet

def main():
    manifest=[]; plates=[]
    for idx, item in enumerate(SELECT, 1):
        im = Image.open(item['src']).convert('RGB')
        plate = cover_crop(im, focus=item['focus']) if item['fit']=='cover' else contain_on_blur(im)
        out = OUT / f'tardigrade_beat_{idx:02d}_{item["beat"]}.jpg'
        plate.save(out, quality=94)
        plates.append(out)
        manifest.append({
            'beat_index': idx,
            'beat': item['beat'],
            'role': item['role'],
            'source_id': item['source_id'],
            'source_path': str(item['src'].relative_to(ROOT)),
            'plate_path': str(out.relative_to(ROOT)),
            'dimensions': [W,H],
            'text_logo_ui_observed_in_crop': False,
            'lane_note': 'right-safe public/open source; deterministic crop/blur-background only; no AI generation; no paid credits',
            'qa_status': 'agent_selected_gate2_candidate_needs_harsh_phone_size_review_before_render'
        })
    contact = OUT / 'tardigrade_selected_plates_v01_contact_sheet.jpg'
    make_sheet(plates).save(contact, quality=92)
    manifest_path = OUT / 'selected_plates_manifest_v01.json'
    manifest_path.write_text(json.dumps({
        'created_utc': '2026-06-06T21:20:00Z',
        'slug': 'tardigrade_survival_mode',
        'status': 'gate2_selected_plate_candidate_not_render_ready',
        'render_performed': False,
        'paid_or_credit_lanes_used': False,
        'contact_sheet': str(contact.relative_to(ROOT)),
        'plates': manifest,
        'remaining_blockers': [
            'human/phone-size Gate 2 review of selected microscope/SEM crops',
            'approved elevenlabs_george VO is still absent; do not render with wrong voice',
            'Beat 04 uses source-supported rehydration/reactivation fallback, not a visible water droplet/flow shot'
        ]
    }, indent=2))
    print(json.dumps({'created':[str(p.relative_to(ROOT)) for p in plates] + [str(contact.relative_to(ROOT)), str(manifest_path.relative_to(ROOT))]}, indent=2))

if __name__ == '__main__':
    main()
