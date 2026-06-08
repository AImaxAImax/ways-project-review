#!/usr/bin/env python3
import json, subprocess, pathlib, time, urllib.request
CASE=pathlib.Path('/mnt/c/dev/curious-shorts/test_cases/flying_snake_glide')
BASE=CASE/'outputs/higgsfield_frames_v02'
CLI='/home/<user>/.hermes/node/bin/higgsfield'
pack=json.loads((BASE/'higgsfield_prompt_pack_v02.json').read_text())
(BASE/'raw').mkdir(parents=True, exist_ok=True)
(BASE/'meta').mkdir(parents=True, exist_ok=True)
for c in pack['candidates']:
    out_json=BASE/'meta'/f"{c['id']}.json"
    cmd=[CLI,'generate','create',c['model'],'--prompt',c['prompt'],'--wait','--wait-timeout','10m','--json']
    ref=c.get('ref')
    if ref:
        cmd += ['--image', str(CASE/ref)]
    for k,v in c.get('params',{}).items(): cmd += [f'--{k}', str(v)]
    print('RUN', c['id'], c['model'], 'ref', ref, flush=True)
    for attempt in range(1,3):
        p=subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=700)
        out=p.stdout.strip()
        (BASE/'meta'/f"{c['id']}_attempt{attempt}.log").write_text(out)
        try:
            data=json.loads(out)
            if isinstance(data,list) and data and data[0].get('result_url'):
                out_json.write_text(json.dumps(data, indent=2))
                print('OK', c['id'], data[0]['result_url'], flush=True)
                break
        except Exception: pass
        print('FAIL', c['id'], 'attempt', attempt, out[:500], flush=True)
        time.sleep(15)
for p in sorted((BASE/'meta').glob('*.json')):
    try:
        data=json.loads(p.read_text())
        if isinstance(data,list) and data and data[0].get('result_url'):
            raw=BASE/'raw'/f"{p.stem}.png"
            if not raw.exists(): urllib.request.urlretrieve(data[0]['result_url'], raw)
    except Exception as e: print('skip', p, e)
summary=[]
for p in sorted((BASE/'meta').glob('*.json')):
    try:
        data=json.loads(p.read_text())
        if isinstance(data,list) and data:
            r=data[0]
            summary.append({'id':p.stem,'job_id':r.get('id'),'model':r.get('job_set_type'),'status':r.get('status'),'url':r.get('result_url'),'params':r.get('params',{})})
    except Exception: pass
(BASE/'higgsfield_generation_manifest_v02.json').write_text(json.dumps({'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'results':summary}, indent=2))
print('SUMMARY', len(summary))
