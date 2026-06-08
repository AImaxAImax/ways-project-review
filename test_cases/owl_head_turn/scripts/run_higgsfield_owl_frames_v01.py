#!/usr/bin/env python3
import json, subprocess, pathlib, time, urllib.request, shutil, math
from PIL import Image, ImageDraw, ImageFont

CASE=pathlib.Path('/mnt/c/dev/curious-shorts/test_cases/owl_head_turn')
BASE=CASE/'outputs/higgsfield_frames_v01'
CLI='/home/joshn/.hermes/node/bin/higgsfield'
pack=json.loads((BASE/'higgsfield_prompt_pack_v01.json').read_text())
raw=BASE/'raw'; meta=BASE/'meta'; review=CASE/'assets/pending_human_plate_review/higgsfield_v01'
raw.mkdir(parents=True, exist_ok=True); meta.mkdir(parents=True, exist_ok=True); review.mkdir(parents=True, exist_ok=True)

for c in pack['candidates']:
    out_json=meta/f"{c['id']}.json"
    if out_json.exists():
        try:
            data=json.loads(out_json.read_text())
            if isinstance(data,list) and data and data[0].get('result_url'):
                print('SKIP', c['id'], data[0]['result_url'], flush=True)
                continue
        except Exception:
            pass
    cmd=[CLI,'generate','create',c['model'],'--prompt',c['prompt'],'--wait','--wait-timeout','10m','--json']
    for k,v in c.get('params',{}).items(): cmd += [f'--{k}', str(v)]
    print('RUN', c['id'], c['model'], flush=True)
    for attempt in range(1,3):
        p=subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=700)
        out=p.stdout.strip()
        (meta/f"{c['id']}_attempt{attempt}.log").write_text(out)
        try:
            data=json.loads(out)
            if isinstance(data,list) and data and data[0].get('result_url'):
                out_json.write_text(json.dumps(data, indent=2))
                print('OK', c['id'], data[0]['result_url'], flush=True)
                break
        except Exception:
            pass
        print('FAIL', c['id'], 'attempt', attempt, out[:500], flush=True)
        time.sleep(15)

summary=[]
for p in sorted(meta.glob('*.json')):
    try:
        data=json.loads(p.read_text())
        if isinstance(data,list) and data and data[0].get('result_url'):
            r=data[0]
            img=raw/f"{p.stem}.png"
            if not img.exists():
                print('DOWNLOAD', img.name, flush=True)
                urllib.request.urlretrieve(r['result_url'], img)
            summary.append({'id':p.stem,'job_id':r.get('id'),'model':r.get('job_set_type'),'status':r.get('status'),'url':r.get('result_url'),'local_path':str(img.relative_to(CASE)),'params':r.get('params',{})})
    except Exception as e:
        print('skip', p, e)
manifest={'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'project':'owl_head_turn', 'results':summary}
(BASE/'higgsfield_generation_manifest_v01.json').write_text(json.dumps(manifest, indent=2))

# Build contact sheet
imgs=[]
for item in summary:
    p=CASE/item['local_path']
    if p.exists(): imgs.append((item['id'],p))
if imgs:
    cellw, cellh = 360, 700
    cols=2; rows=math.ceil(len(imgs)/cols)
    sheet=Image.new('RGB',(cols*cellw, rows*cellh),(18,18,18))
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    except Exception: font=None
    for idx,(name,p) in enumerate(imgs):
        im=Image.open(p).convert('RGB'); im.thumbnail((cellw,640))
        x=(idx%cols)*cellw+(cellw-im.width)//2; y=(idx//cols)*cellh+10
        sheet.paste(im,(x,y))
        d=ImageDraw.Draw(sheet); d.text(((idx%cols)*cellw+12,(idx//cols)*cellh+654),name,fill=(255,255,255),font=font)
    contact=BASE/'higgsfield_owl_candidates_contact_sheet_v01.jpg'
    sheet.save(contact, quality=92)

# Copy best-review set: all candidates for human gate, since semantic head-turn quality needs human eye.
for _,p in imgs:
    shutil.copy2(p, review/p.name)

qa=BASE/'QA_HIGGSFIELD_FRAMES_V01.md'
qa.write_text(f"""# Gate 2 QA — owl_head_turn Higgsfield frames v01

Generated: {manifest['generated_at']}
Candidates generated: {len(summary)}
Contact sheet: `higgsfield_owl_candidates_contact_sheet_v01.jpg`
Pending review folder: `{review.relative_to(CASE)}`

## Locked visual requirement
One owl only, body mostly still, head visibly rotated far over one shoulder. The clip must read immediately at phone size as an owl doing the impossible-looking head turn.

## Hard blockers
- text, logo, watermark, UI, labels, arrows
- anatomy cutaway, x-ray, skeleton, diagram-first explanation
- extra owls, duplicate heads, melted eyes/beak/talons
- horror/gore or broken-neck read
- weak head-turn read where the owl just looks sideways

## Gate 2 recommendation
Human plate approval required before I2V. Pick 1-2 plates with the cleanest owl anatomy and clearest over-shoulder head position. Do not proceed to video from weak plates.
""")
print(json.dumps({'ok':True,'generated':len(summary),'contact_sheet':str(contact if imgs else ''),'review_dir':str(review),'manifest':str(BASE/'higgsfield_generation_manifest_v01.json'),'qa':str(qa)}, indent=2))
