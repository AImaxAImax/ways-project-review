#!/usr/bin/env python3
"""Phase 0 inventory/smoke status for the WAYS model benchmark."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path('/mnt/c/dev/curious-shorts')
MANIFEST = ROOT / 'benchmark/config/benchmark_manifest.json'
OUT = ROOT / 'benchmark/results/phase0_status.json'
COMFY = 'http://127.0.0.1:8188'


def get_json(url: str, timeout: int = 20) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.load(r)


def model_list(folder: str) -> list[str]:
    try:
        return list(get_json(f'{COMFY}/models/{folder}', timeout=10))
    except Exception:
        return []


def object_info() -> dict[str, Any]:
    try:
        return dict(get_json(f'{COMFY}/object_info', timeout=30))
    except Exception:
        return {}


def workflow_refs(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return [{'error': f'missing workflow: {path}'}]
    wf = json.loads(path.read_text(encoding='utf-8'))
    refs = []
    for node_id, node in wf.items():
        if not isinstance(node, dict):
            continue
        cls = node.get('class_type', '')
        inputs = node.get('inputs', {}) or {}
        for key in ('unet_name','vae_name','ckpt_name','clip_name','clip_name1','clip_name2','clip_name3','lora_name'):
            if key in inputs and isinstance(inputs[key], str):
                refs.append({'node': str(node_id), 'class_type': cls, 'input': key, 'name': inputs[key]})
    return refs


def contains_name(available: list[str], name: str) -> bool:
    n = name.replace('/', '\\').lower()
    return any(x.replace('/', '\\').lower() == n or x.replace('/', '\\').lower().endswith(n) for x in available)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        stats = get_json(f'{COMFY}/system_stats')
        comfy_ok = True
    except Exception as e:
        stats = {'error': repr(e)}
        comfy_ok = False
    models = {
        'checkpoints': model_list('checkpoints'),
        'vae': model_list('vae'),
        'diffusion_models': model_list('diffusion_models'),
        'text_encoders': model_list('text_encoders'),
    }
    obj = object_info()
    # Pull GGUF model options from object_info because /models/unet is 404 on this setup.
    gguf = []
    for cls in ('UnetLoaderGGUF','UnetLoaderGGUFAdvanced'):
        try:
            gguf.extend(obj[cls]['input']['required']['unet_name'][0])
        except Exception:
            pass
    models['gguf_unet'] = sorted(set(gguf))
    workflow_status = {}
    for mid, m in manifest['models'].items():
        wf = m.get('workflow')
        refs = workflow_refs(Path(wf)) if wf else []
        missing = []
        for ref in refs:
            name = ref.get('name')
            if not name: continue
            key = ref['input']
            pools = []
            if 'vae' in key: pools = models['vae']
            elif 'ckpt' in key: pools = models['checkpoints']
            elif 'clip' in key: pools = models['text_encoders'] + models['checkpoints']
            elif 'unet' in key: pools = models['gguf_unet'] + models['diffusion_models']
            elif 'lora' in key:
                # Loras are exposed via object_info but not /models here. Treat as present if a node option listed it.
                pools = json.dumps(obj).split('"')
            if pools and not contains_name(pools, name):
                # Known case mismatch in old template: Wan2.1_VAE vs wan_2.1_vae.
                if name.lower() == 'wan2.1_vae.safetensors' and contains_name(pools, 'wan_2.1_vae.safetensors'):
                    continue
                missing.append(ref)
        workflow_exists = bool(wf and Path(wf).exists())
        workflow_status[mid] = {
            'declared_status': m.get('status'),
            'workflow': wf,
            'workflow_exists': workflow_exists,
            'refs': refs,
            'missing_refs': missing,
            'phase0_entry_ok': bool(comfy_ok and workflow_exists and not missing),
        }
    confounds = {
        'wan_vae_available': contains_name(models['vae'], 'wan_2.1_vae.safetensors'),
        'wan22_vae_available_but_not_to_use': contains_name(models['vae'], 'wan2.2_vae.safetensors'),
        'ltx_dims_divisible_by_32_required': True,
        't2v_category5_only': True,
        'qa_thresholds_exists': (ROOT/'config/qa_thresholds.json').exists(),
    }
    status = {
        'comfy_url': COMFY,
        'comfy_ok': comfy_ok,
        'system_stats': stats,
        'models': models,
        'workflow_status': workflow_status,
        'confounds': confounds,
        'next_actions': [
            'Run scripts/run_ways_model_benchmark.py --dry-run first.',
            'Only wan22_i2v has a proven executable path today; LTX/Hunyuan need I2V conditioning smoke workflows before scoring.',
            'Download/verify wan22_i2v_hi and cogvideox15 before their ablation/probe entries.',
        ],
    }
    OUT.write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'comfy_ok': comfy_ok, 'wan_vae_available': confounds['wan_vae_available'], 'workflow_models': list(workflow_status)}, indent=2))
    return 0 if comfy_ok else 2


if __name__ == '__main__':
    raise SystemExit(main())
