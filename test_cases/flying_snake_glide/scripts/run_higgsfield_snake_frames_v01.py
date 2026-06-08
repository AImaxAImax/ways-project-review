#!/usr/bin/env python3
import json, subprocess, pathlib, time, sys, urllib.request
BASE=pathlib.Path('/mnt/c/dev/curious-shorts/test_cases/flying_snake_glide/outputs/higgsfield_frames_v01')
CLI='/home/joshn/.hermes/node/bin/higgsfield'
pack=json.loads((BASE/'higgsfield_prompt_pack_v01.json').read_text())
(BASE/'raw').mkdir(parents=True, exist_ok=True)
(BASE/'meta').mkdir(parents=True, exist_ok=True)
results=[]
for c in pack['candidates']:
    out_json=BASE/'meta'/f"{c['id']}.json"
    if out_json.exists() and out_json.read_text().strip().startswith('['):
        try:
            data=json.loads(out_json.read_text())
            if data and data[0].get('result_url'):
                print(f"SKIP {c['id']} existing {data[0]['result_url']}")
                results.append(data[0]); continue
        except Exception: pass
    cmd=[CLI,'generate','create',c['model'],'--prompt',c['prompt'],'--wait','--wait-timeout','10m','--json']
    for k,v in c.get('params',{}).items(): cmd += [f'--{k}', str(v)]
    print('RUN', c['id'], c['model'], flush=True)
    last=None
    for attempt in range(1,4):
        p=subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=700)
        out=p.stdout.strip()
        (BASE/'meta'/f"{c['id']}_attempt{attempt}.log").write_text(out)
        try:
            data=json.loads(out)
            if isinstance(data,list) and data and data[0].get('result_url'):
                out_json.write_text(json.dumps(data, indent=2))
                results.append(data[0])
                print('OK', c['id'], data[0]['result_url'], flush=True)
                break
        except Exception as e:
            last=e
        print('FAIL', c['id'], 'attempt', attempt, out[:500], flush=True)
        time.sleep(12*attempt)
    else:
        print('GIVEUP', c['id'], last, flush=True)
# include manually generated nano_01
for p in sorted((BASE/'meta').glob('*.json')):
    try:
        data=json.loads(p.read_text())
        if isinstance(data,list) and data and data[0].get('result_url'):
            r=data[0]
            raw=BASE/'raw'/f"{p.stem}.png"
            if not raw.exists():
                print('DOWNLOAD', raw.name)
                urllib.request.urlretrieve(r['result_url'], raw)
    except Exception as e:
        print('download skip', p, e)
summary=[]
for p in sorted((BASE/'meta').glob('*.json')):
    try:
        data=json.loads(p.read_text())
        if isinstance(data,list) and data:
            r=data[0]
            summary.append({'id':p.stem,'job_id':r.get('id'),'model':r.get('job_set_type'),'status':r.get('status'),'url':r.get('result_url'),'params':r.get('params',{})})
    except Exception: pass
(BASE/'higgsfield_generation_manifest_v01.json').write_text(json.dumps({'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'results':summary}, indent=2))
print('SUMMARY', len(summary), 'completed metadata files')
