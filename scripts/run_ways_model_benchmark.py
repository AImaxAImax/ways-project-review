#!/usr/bin/env python3
"""Run and score WAYS model benchmark cells.

Currently implements the proven wan22_i2v lane using the existing render_wan_harness.
Other model IDs are deliberately refused until Phase 0 smoke verifies their true
I2V/T2V conditioning path. This prevents silently scoring invalid workflows.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path('/mnt/c/dev/curious-shorts')
MANIFEST = ROOT / 'benchmark/config/benchmark_manifest.json'
RUN_ROOT = ROOT / 'benchmark/runs'
RESULTS = ROOT / 'benchmark/results'
WAN_WORKFLOW = Path('/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json')


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding='utf-8'))


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=check)


def wan_config(cell_dir: Path, plate: dict[str, Any], seed: int) -> Path:
    cfg = {
        'project_root': str(ROOT),
        'slug': f"bench_{plate['id']}_wan22_i2v_seed{seed}",
        'output_dir': str(cell_dir.relative_to(ROOT)),
        'voiceover': '',
        'workflow': str(WAN_WORKFLOW),
        'comfy_url': 'http://127.0.0.1:8188',
        'negative_prompt': plate.get('negative', ''),
        'render_settings': {
            'fps': 24,
            'wan_width': 432,
            'wan_height': 768,
            'wan_length_frames': 25,
            'master_width': 1080,
            'master_height': 1920,
            'master_crf': 18,
            'audio_bitrate': '160k',
            'audio_sample_rate': 48000,
            'preview_width': 720,
            'preview_height': 1280,
            'preview_crf': 24,
            'preview_audio_bitrate': '96k',
        },
        'workflow_overrides': {'39.inputs.vae_name': 'wan_2.1_vae.safetensors'},
        'required_vae': 'wan_2.1_vae.safetensors',
        'shots': [{
            'id': '01',
            'image': plate['locked_path'],
            'prompt': plate['prompt'],
            'duration': 2.0,
            'seed': seed,
        }],
    }
    cell_dir.mkdir(parents=True, exist_ok=True)
    path = cell_dir / 'render_wan_config.json'
    path.write_text(json.dumps(cfg, indent=2) + '\n', encoding='utf-8')
    return path


def score_output(cell_dir: Path, plate: dict[str, Any], rendered: Path, *, report_only: bool) -> dict[str, Any]:
    outdir = cell_dir / 'qa'
    cmd = [
        sys.executable, 'tools/local_video_qa.py',
        '--input', str(rendered),
        '--source-image', str(ROOT / plate['locked_path']),
        '--thresholds', 'config/qa_thresholds.json',
        '--frame-sample-fps', '6',
        '--no-require-audio',
        '--outdir', str(outdir),
    ]
    if report_only:
        cmd.append('--report-only')
    proc = run(cmd, check=False)
    report = outdir / 'qa_report.json'
    data = json.loads(report.read_text(encoding='utf-8')) if report.exists() else {'error': proc.stdout}
    return {'exit_code': proc.returncode, 'qa_report': str(report), 'qa_stdout_tail': proc.stdout[-2000:], 'qa': data}


def existing_complete_result(cell_dir: Path) -> dict[str, Any] | None:
    result_path = cell_dir / 'benchmark_result.json'
    if not result_path.exists():
        return None
    try:
        result = json.loads(result_path.read_text(encoding='utf-8'))
    except Exception:
        return None
    rendered = result.get('rendered')
    qa_report = ((result.get('score') or {}).get('qa_report'))
    if rendered and qa_report and Path(rendered).exists() and Path(qa_report).exists():
        result['skipped_existing'] = True
        return result
    return None


def run_cell(model_id: str, plate: dict[str, Any], seed: int, *, dry_run: bool, report_only: bool, force: bool) -> dict[str, Any]:
    cell_dir = RUN_ROOT / f"cat{plate['category']}" / plate['id'] / model_id / f'seed_{seed}'
    if model_id != 'wan22_i2v':
        raise SystemExit(f"Refusing to run {model_id}: Phase 0 I2V/T2V workflow smoke not implemented/verified yet.")
    if not force and not dry_run:
        existing = existing_complete_result(cell_dir)
        if existing is not None:
            return existing
    cfg = wan_config(cell_dir, plate, seed)
    if dry_run:
        proc = run([sys.executable, 'scripts/render_wan_harness.py', str(cfg), '--dry-run', '--no-assemble'], check=False)
        return {'model': model_id, 'plate': plate['id'], 'seed': seed, 'dry_run': True, 'config': str(cfg), 'exit_code': proc.returncode, 'stdout_tail': proc.stdout[-2000:]}
    started = time.time()
    proc = run([sys.executable, 'scripts/render_wan_harness.py', str(cfg), '--no-assemble'], check=False)
    elapsed = round(time.time() - started, 3)
    manifest_path = cell_dir / 'manifest.json'
    rendered = None
    if manifest_path.exists():
        m = json.loads(manifest_path.read_text(encoding='utf-8'))
        # render_wan_harness stores each shot clip under either shot['clip'] or shot['outputs']['clip'] depending on version.
        for shot in m.get('shots', []):
            cand = shot.get('clip') or shot.get('output') or shot.get('path')
            if not cand and isinstance(shot.get('outputs'), dict):
                cand = shot['outputs'].get('clip') or shot['outputs'].get('video')
            if cand:
                cp = Path(cand)
                if not cp.is_absolute():
                    cp = ROOT / cp
                if cp.exists():
                    rendered = cp
                    break
    if rendered is None:
        for p in cell_dir.rglob('*.mp4'):
            rendered = p
            break
    result = {'model': model_id, 'plate': plate['id'], 'seed': seed, 'dry_run': False, 'config': str(cfg), 'render_exit_code': proc.returncode, 'render_seconds': elapsed, 'stdout_tail': proc.stdout[-2000:]}
    if proc.returncode == 0 and rendered:
        result['rendered'] = str(rendered)
        result['score'] = score_output(cell_dir, plate, rendered, report_only=report_only)
    return result


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {'cells': len(results), 'by_plate_model': {}}
    for r in results:
        key = f"{r['plate']}::{r['model']}"
        summary['by_plate_model'].setdefault(key, []).append(r)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='wan22_i2v')
    parser.add_argument('--category', type=int, action='append')
    parser.add_argument('--plate-id', action='append')
    parser.add_argument('--seeds', default=','.join(str(x) for x in [627101,627102,627103,627104,627105]))
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--report-only', action='store_true', help='score advisory even if thresholds exist')
    parser.add_argument('--force', action='store_true', help='rerender cells even when benchmark_result.json + QA already exist')
    args = parser.parse_args(argv)

    manifest = load_manifest()
    seeds = [int(x) for x in args.seeds.split(',') if x.strip()]
    plates = manifest['plates']
    if args.category:
        plates = [p for p in plates if p['category'] in args.category]
    if args.plate_id:
        plates = [p for p in plates if p['id'] in set(args.plate_id)]
    tasks = [(p, s) for p in plates for s in seeds]
    if args.limit:
        tasks = tasks[:args.limit]
    RESULTS.mkdir(parents=True, exist_ok=True)
    results = []
    for p, s in tasks:
        result = run_cell(args.model, p, s, dry_run=args.dry_run, report_only=args.report_only, force=args.force)
        result_path = RUN_ROOT / f"cat{p['category']}" / p['id'] / args.model / f'seed_{s}' / 'benchmark_result.json'
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        results.append(result)
        print(json.dumps({'done': result_path.as_posix(), 'exit': result.get('render_exit_code', result.get('exit_code'))}), flush=True)
    batch = {'results': results, 'summary': summarize(results)}
    out = RESULTS / 'latest_benchmark_batch.json'
    out.write_text(json.dumps(batch, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'batch': str(out), 'cells': len(results)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
