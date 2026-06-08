#!/usr/bin/env python3
"""Aggregate WAYS benchmark outputs into the protocol matrix skeleton."""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path('/mnt/c/dev/curious-shorts')
RUN_ROOT = ROOT / 'benchmark/runs'
OUT = ROOT / 'benchmark/results/model_matrix.md'

MODELS = ['wan22_i2v','ltx23_fp8','ltx23_distilled','wan22_t2v','hunyuan15']
CATS = {
    1: 'Realism hold',
    2: 'Large motion',
    3: 'Reveal',
    4: 'Effect',
    5: 'Cinematic/scale',
    6: 'Process (probe)',
}
NA = {
    1: {'wan22_t2v','hunyuan15'},
    2: {'wan22_t2v'},
    3: {'wan22_t2v','hunyuan15'},
    4: {'wan22_t2v','hunyuan15'},
    5: set(),
    6: {'wan22_t2v','hunyuan15'},
}


def load_results() -> list[dict[str, Any]]:
    rows=[]
    for p in RUN_ROOT.rglob('benchmark_result.json'):
        try:
            rows.append(json.loads(p.read_text(encoding='utf-8')))
        except Exception:
            pass
    return rows


def category_for(result: dict[str, Any]) -> int | None:
    plate = result.get('plate','')
    if plate.startswith('cat') and len(plate) > 3:
        try: return int(plate[3])
        except Exception: return None
    return None


def cell_summary(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ''
    clip=[]; flicker=[]; seconds=[]; blockers=0
    for r in rows:
        seconds.append(r.get('render_seconds')) if r.get('render_seconds') is not None else None
        qa = (((r.get('score') or {}).get('qa') or {}))
        if qa.get('blockers'): blockers += 1
        metrics = qa.get('metrics') or {}
        cp = (metrics.get('clip_preservation') or {}).get('min')
        fl = (metrics.get('temporal_consistency') or {}).get('mean')
        if cp is not None: clip.append(float(cp))
        if fl is not None: flicker.append(float(fl))
    parts=[]
    parts.append(f"n={len(rows)}")
    if clip: parts.append(f"CLIPmed={statistics.median(clip):.3f}")
    if flicker: parts.append(f"LPIPSmed={statistics.median(flicker):.3f}")
    if seconds: parts.append(f"secmed={statistics.median([x for x in seconds if x is not None]):.1f}")
    if blockers: parts.append(f"blockers={blockers}")
    return '<br>'.join(parts)


def main() -> int:
    rows = load_results()
    lines = []
    lines.append('# WAYS Local Video Model Benchmark Matrix')
    lines.append('')
    lines.append('Human blind scores are not filled by automation. Automated cells show available Tier-1 metrics from `benchmark_result.json`.')
    lines.append('')
    lines.append('|Category|' + '|'.join(MODELS) + '|Winner|Notes|')
    lines.append('|' + '|'.join(['---'] * (len(MODELS)+3)) + '|')
    for cat, name in CATS.items():
        vals=[]
        for m in MODELS:
            if m in NA.get(cat,set()):
                vals.append('n/a')
            else:
                vals.append(cell_summary([r for r in rows if r.get('model') == m and category_for(r) == cat]))
        lines.append(f"|{cat} {name}|" + '|'.join(vals) + '|||')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'matrix': str(OUT), 'result_files': len(rows)}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
