#!/usr/bin/env python3
from __future__ import annotations
import json, time, uuid, subprocess, shutil
from pathlib import Path
import requests
import sys

REPO_ROOT = Path('/mnt/c/dev/curious-shorts')
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from scripts.render_wan_harness import HarnessConfig, run_preflight

COMFY = 'http://127.0.0.1:8188'
ROOT = Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees')
WORKFLOW = Path('/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json')
OUTDIR = ROOT / 'outputs' / 'wan22_v27_animated_frames'
CLIPDIR = OUTDIR / 'clips'
FRAMEDIR = OUTDIR / 'frames'

FPS = 24
W, H = 1080, 1920
# Short local Wan pass. Wombat v2 lesson: start with true motion clips, then stretch/interpolate in edit if full-length clips are too slow.
WAN_W, WAN_H, WAN_LEN = 432, 768, 25
VOICE = ROOT / 'outputs/voice_auditions/01_warm_older_brother_uncle.mp3'


def run_preflight_or_die() -> None:
    cfg = HarnessConfig.from_dict({
        'project_root': str(ROOT),
        'slug': 'sharks_older_than_trees',
        'output_dir': str(OUTDIR),
        'voiceover': str(VOICE),
        'workflow': str(WORKFLOW),
        'comfy_url': COMFY,
        'negative_prompt': 'text, subtitles, readable letters, watermark, logo, UI, hard cut, scene transition, horror, blood, attack, morphing animal anatomy, duplicated fins, distorted face, melted geometry, jitter, flicker, low quality, blurry, compression artifacts',
        'render_settings': {'fps': FPS, 'wan_width': WAN_W, 'wan_height': WAN_H, 'wan_length_frames': WAN_LEN},
        'workflow_overrides': {'39.inputs.vae_name': 'wan_2.1_vae.safetensors'},
        'required_nodes': ['6', '7', '39', '57', '58', '61', '62', '63'],
        'required_vae': 'wan_2.1_vae.safetensors',
        'writable_dirs': [str(CLIPDIR), str(FRAMEDIR)],
        'shots': [
            {
                'id': shot['id'],
                'image': str(shot['path']),
                'duration': shot['duration'],
                'caption': shot['caption'],
                'seed': shot['seed'],
                'prompt': shot['prompt'],
            }
            for shot in SHOTS
        ],
    }, base_dir=ROOT)
    print(json.dumps({'preflight': run_preflight(cfg)}, default=str), flush=True)

SHOTS = [
    {
        'id':'01',
        'path': ROOT/'assets/gpt_image_2_manual_v23/shot01_gpt_image2_hook_before_trees_v01.jpeg',
        'duration':3.570,
        'caption':'SHARKS WERE HERE\nBEFORE TREES',
        'seed': 627101,
        'prompt':'premium natural-history documentary image-to-video. Ancient shark glides calmly through blue-green prehistoric ocean, subtle tail swish and fin motion, drifting particles, slow parallax water shimmer, sunlight rays move gently. Preserve exact shark anatomy, framing, colors, and realistic documentary style. No attack, no blood, no text, no logos, no scene cut, no morphing.'
    },
    {
        'id':'02',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot02_seriously_fossil_proof_v01.jpeg',
        'duration':2.303,
        'caption':'SERIOUSLY.',
        'seed': 627102,
        'prompt':'documentary macro image-to-video of fossil shark tooth proof. Keep the original fossil and stone slab exactly intact while camera makes a tiny macro push, dust motes drift, shallow depth of field breathes subtly, museum-light shimmer. No new text, no labels, no hands, no morphing, no cracks changing, no scene cut.'
    },
    {
        'id':'03',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot03_apple_squirrel_nut_v01.jpeg',
        'duration':3.685,
        'caption':'BEFORE APPLES.\nBEFORE SQUIRRELS.',
        'seed': 627103,
        'prompt':'premium surreal documentary image-to-video from the exact still. Preserve the apple, squirrel, and nut/seed objects clearly. Add only subtle camera drift, gentle foreground/background parallax, small dust particles and soft light movement. Objects remain anatomically/physically stable. No extra animals, no text, no logos, no object morphing, no scene cut.'
    },
    {
        'id':'04',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot04_deep_time_rock_layers_sharks_v01.jpeg',
        'duration':3.570,
        'caption':'OVER 400 MILLION\nYEARS AGO',
        'seed': 627104,
        'prompt':'cinematic deep-time geology image-to-video. Preserve the exact layered rock/ocean composition. Slow vertical reveal feel, atmospheric haze, tiny suspended particles, water shimmer, distant volcanic glow pulses subtly. No readable text, no numbers, no labels, no extra symbols, no scene cut, no warping strata.'
    },
    {
        'id':'05',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot05_first_trees_coastline_v01.jpeg',
        'duration':3.225,
        'caption':'THEN FORESTS\nFINALLY ARRIVED',
        'seed': 627105,
        'prompt':'premium natural-history image-to-video of first primitive forests near ancient coast. Preserve the exact landscape and composition. Gentle wind movement in primitive plants, soft mist drift, water ripple, slow cinematic camera creep. No modern objects, no text, no logos, no morphing trees into fantasy shapes, no scene cut.'
    },
    {
        'id':'06',
        'path': ROOT/'assets/gpt_image_2_manual_v24/shot06_kid_aquarium_deep_time_v01.jpeg',
        'duration':3.685,
        'caption':'AND TODAY...\nTHEY ARE STILL HERE',
        'seed': 627106,
        'prompt':'realistic aquarium documentary image-to-video. Preserve the child, glass plane, shark, and framing. Shark moves subtly behind the glass only, water particles drift, reflections shimmer, child remains stable and believable, tiny camera creep. Do not let shark cross the glass, no horror, no text, no logos, no face morphing, no scene cut.'
    },
    {
        'id':'07',
        'path': ROOT/'assets/gpt_image_2_manual_v23/04_final_predator_got_here_first.png',
        'duration':3.916,
        'caption':'SURVIVOR\nFROM A WORLD\nBEFORE FORESTS',
        'seed': 627107,
        'prompt':'premium natural-history documentary image-to-video from the exact still. The realistic shark slowly glides toward camera with subtle tail and fin motion, deep ocean particles drift, shafts of light shimmer, distant volcanic glow barely moves. Preserve exact anatomy and calm confident tone. No lunge, no open bloody mouth, no monster look, no text, no logos, no morphing, no scene cut.'
    },
]

def post_json(path, payload, timeout=30):
    r = requests.post(COMFY + path, json=payload, timeout=timeout)
    if r.status_code >= 400:
        raise RuntimeError(f'{path} {r.status_code}: {r.text[:4000]}')
    return r.json()

def upload_image(path: Path) -> str:
    with path.open('rb') as f:
        r = requests.post(f'{COMFY}/upload/image', files={'image': (path.name, f, 'image/png')}, data={'type':'input','overwrite':'true'}, timeout=180)
    if r.status_code >= 400:
        raise RuntimeError(r.text[:4000])
    return r.json().get('name') or path.name

def queue_workflow(wf: dict) -> str:
    data = post_json('/prompt', {'prompt': wf, 'client_id': str(uuid.uuid4())}, timeout=60)
    if data.get('node_errors'):
        raise RuntimeError(json.dumps(data['node_errors'], indent=2)[:8000])
    return data['prompt_id']

def wait_for(pid: str, timeout=7200) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        hist = requests.get(f'{COMFY}/history/{pid}', timeout=30).json()
        if pid in hist:
            status = hist[pid].get('status', {})
            if status.get('status_str') == 'error':
                raise RuntimeError(json.dumps(status.get('messages', []), indent=2)[:12000])
            return hist[pid]
        print(json.dumps({'waiting_s': round(time.time()-start, 1), 'prompt_id': pid}), flush=True)
        time.sleep(10)
    raise TimeoutError(pid)

def output_items(entry: dict):
    out=[]
    for node_id, node_out in entry.get('outputs', {}).items():
        for key in ('videos','gifs','images'):
            for item in node_out.get(key, []) or []:
                if isinstance(item, dict) and 'filename' in item:
                    out.append({**item, '_node_id':node_id, '_kind':key})
    return out

def download_output(item: dict, dest: Path):
    r = requests.get(f'{COMFY}/view', params={'filename': item['filename'], 'subfolder': item.get('subfolder',''), 'type': item.get('type','output')}, timeout=600)
    r.raise_for_status()
    dest.write_bytes(r.content)

run_preflight_or_die()

# Free VRAM before the batch.
try:
    post_json('/free', {'unload_models': True, 'free_memory': True}, timeout=30)
except Exception as e:
    print(json.dumps({'free_warning': repr(e)}), flush=True)
print(json.dumps({'system': requests.get(f'{COMFY}/system_stats', timeout=10).json()['devices'][0], 'shots': len(SHOTS)}), flush=True)

workflow_base = json.loads(WORKFLOW.read_text())
manifest = {'created_at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'comfy_url': COMFY, 'workflow': str(WORKFLOW), 'wan': {'width': WAN_W, 'height': WAN_H, 'length': WAN_LEN, 'fps': FPS}, 'shots': []}

for shot in SHOTS:
    assert shot['path'].exists(), shot['path']
    image_name = upload_image(shot['path'])
    wf = json.loads(json.dumps(workflow_base))
    # Proven local recovery for this A14B GGUF I2V lane: keep the original
    # WanImageToVideo workflow and use the 2.1 VAE. The newer 2.2 VAE and
    # ad-hoc Wan22ImageToVideoLatent patches throw channel/latent mismatches
    # in the current C:\dev\ComfyUI install.
    wf['39']['inputs']['vae_name'] = 'wan_2.1_vae.safetensors'
    wf['62']['inputs']['image'] = image_name
    wf['63']['inputs']['width'] = WAN_W
    wf['63']['inputs']['height'] = WAN_H
    wf['63']['inputs']['length'] = WAN_LEN
    wf['6']['inputs']['text'] = shot['prompt']
    wf['7']['inputs']['text'] = 'text, subtitles, readable letters, watermark, logo, UI, hard cut, scene transition, horror, blood, attack, morphing animal anatomy, duplicated fins, distorted face, melted geometry, jitter, flicker, low quality, blurry, compression artifacts'
    wf['57']['inputs']['noise_seed'] = shot['seed']
    wf['58']['inputs']['noise_seed'] = shot['seed'] + 1000
    wf['61']['inputs']['filename_prefix'] = f"ways_shark_v27_wan22/{shot['id']}_{shot['seed']}"
    pid = queue_workflow(wf)
    print(json.dumps({'queued': pid, 'shot': shot['id'], 'seed': shot['seed'], 'image_name': image_name}), flush=True)
    entry = wait_for(pid)
    outs = output_items(entry)
    if not outs:
        raise RuntimeError(f'no output for {shot["id"]}')
    dest = CLIPDIR / f"shot{shot['id']}_wan22_432x768_25f_seed{shot['seed']}.mp4"
    download_output(outs[0], dest)
    meta = {**shot, 'source_image': str(shot['path'].relative_to(ROOT)), 'prompt_id': pid, 'uploaded_image': image_name, 'comfy_output': outs[0], 'clip': str(dest.relative_to(ROOT))}
    (CLIPDIR / f"shot{shot['id']}_wan22_432x768_25f_seed{shot['seed']}.json").write_text(json.dumps(meta, indent=2, default=str))
    manifest['shots'].append(meta)
    (OUTDIR / 'manifest_partial.json').write_text(json.dumps(manifest, indent=2, default=str))
    print(json.dumps({'saved': str(dest), 'bytes': dest.stat().st_size}), flush=True)

(OUTDIR / 'manifest.json').write_text(json.dumps(manifest, indent=2, default=str))

# Assemble clean animated base by stretching each short true-motion clip to its beat duration, then mux VO.
if FRAMEDIR.exists():
    shutil.rmtree(FRAMEDIR)
FRAMEDIR.mkdir(parents=True)
frame_idx = 0
for shot in manifest['shots']:
    clip = ROOT / shot['clip']
    n = int(round(shot['duration'] * FPS))
    tmp = OUTDIR / f"tmp_shot{shot['id']}_%05d.jpg"
    # Stretch to exact duration and scale to 9:16 master.
    src_dur = WAN_LEN / FPS
    speed_factor = shot['duration'] / src_dur
    vf = f"setpts={speed_factor:.6f}*PTS,fps={FPS},scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=increase,crop={W}:{H}"
    subprocess.run(['ffmpeg','-y','-i',str(clip),'-vf',vf,'-frames:v',str(n),str(tmp)], check=True)
    for p in sorted(OUTDIR.glob(f"tmp_shot{shot['id']}_*.jpg")):
        p.rename(FRAMEDIR / f'frame_{frame_idx:05d}.jpg')
        frame_idx += 1

silent = OUTDIR / 'sharks_older_than_trees_v27_wan22_animated_silent.mp4'
master = OUTDIR / 'sharks_older_than_trees_v27_wan22_animated_audio.mp4'
preview = OUTDIR / 'sharks_older_than_trees_v27_wan22_animated_discord.mp4'
sheet = OUTDIR / 'contact_sheet_v27_wan22.jpg'
subprocess.run(['ffmpeg','-y','-framerate',str(FPS),'-i',str(FRAMEDIR/'frame_%05d.jpg'),'-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','18','-preset','medium',str(silent)], check=True)
subprocess.run(['ffmpeg','-y','-i',str(silent),'-i',str(VOICE),'-c:v','copy','-c:a','aac','-b:a','160k','-ar','48000','-shortest','-movflags','+faststart',str(master)], check=True)
subprocess.run(['ffmpeg','-y','-i',str(master),'-vf','scale=720:1280:flags=lanczos','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-profile:v','high','-level','3.1','-c:a','aac','-b:a','96k','-ar','48000','-movflags','+faststart',str(preview)], check=True)
subprocess.run(['ffmpeg','-y','-i',str(master),'-vf','fps=1,scale=270:480,tile=6x4','-frames:v','1','-update','1',str(sheet)], check=True)
probe = subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate','-of','json',str(master)], text=True)
(OUTDIR/'ffprobe_master.json').write_text(probe)
print(json.dumps({'done': True, 'master': str(master), 'preview': str(preview), 'contact_sheet': str(sheet), 'frames': frame_idx, 'duration_seconds': round(frame_idx/FPS, 3)}, indent=2), flush=True)
