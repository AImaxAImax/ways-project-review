#!/usr/bin/env python3
"""Calibrate the WAYS local-video QA thresholds against human labels.

This script is intentionally live-tree only: it runs where the media files live
(`/mnt/c/dev/curious-shorts`) and may write configs/artifacts that reference live
paths. It does not run the model campaign.
"""
from __future__ import annotations

import argparse
import itertools
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path('/mnt/c/dev/curious-shorts')
DEFAULT_CALIB = ROOT / 'calib' / 'ways_scoring_harness_20260608'
DEFAULT_THRESHOLDS = ROOT / 'config' / 'qa_thresholds.json'

DEFAULT_CLIPS = [
    # clear/known winners or current best WAYS-format candidates
    {'slug':'shark_v27', 'human':'pass', 'human_score':9, 'input':'test_cases/sharks_older_than_trees/outputs/wan22_harness_v27/sharks_older_than_trees_wan22_silent_1080.mp4', 'note':'published/strong shark lane'},
    {'slug':'frog_v17', 'human':'pass', 'human_score':9, 'input':'test_cases/wood_frog_freeze_survival/outputs/wan22_v17_elevenlabs_george/wood_frog_freeze_survival_v17_elevenlabs_george_clean_1080.mp4', 'note':'published/strong frog lane'},
    {'slug':'frog_v16', 'human':'pass', 'human_score':8, 'input':'test_cases/wood_frog_freeze_survival/outputs/wan22_v16_final_vo/wood_frog_freeze_survival_v16_final_vo_clean_1080.mp4', 'note':'near-final frog candidate'},
    {'slug':'frog_v15', 'human':'pass', 'human_score':8, 'input':'test_cases/wood_frog_freeze_survival/outputs/wan22_v15_polished_middle/wood_frog_freeze_survival_v15_wan22_silent_1080.mp4', 'note':'polished frog candidate'},
    {'slug':'mantis_v30', 'human':'pass', 'human_score':8, 'input':'test_cases/mantis_shrimp_cavitation_punch/outputs/say_dog_v30_feed_hook_reset/mantis_say_dog_v30_feed_hook_reset_silent_1080.mp4', 'note':'posted/reset mantis shrimp candidate'},
    {'slug':'owl_v03', 'human':'pass', 'human_score':8, 'input':'test_cases/owl_head_turn/outputs/owl_draft_v03_neck_safe/owl_head_turn_neck_safe_clean_v03.mp4', 'note':'neck-safe owl draft'},
    {'slug':'owl_v04', 'human':'pass', 'human_score':8, 'input':'test_cases/owl_head_turn/outputs/owl_draft_v04_all_moving/owl_head_turn_all_moving_clean_v04.mp4', 'note':'all-moving owl draft'},
    {'slug':'octopus_v01', 'human':'pass', 'human_score':8, 'input':'test_cases/octopus_three_hearts/outputs/wan22_template_v01/octopus_three_hearts_wan22_silent_1080.mp4', 'note':'strong-prior animal lane candidate'},
    # known weak/rejected or process/scale-heavy lanes
    {'slug':'wombat_v01', 'human':'fail', 'human_score':4, 'input':'test_cases/wombat_cube_poop/outputs/wan22_template_v01/wombat_cube_poop_wan22_silent_1080.mp4', 'note':'published weak retention/process-heavy'},
    {'slug':'tardigrade_v01', 'human':'fail', 'human_score':4, 'input':'test_cases/tardigrade_survival_mode/outputs/wan22_template_v01/tardigrade_survival_mode_wan22_silent_1080.mp4', 'note':'rework_status: do_not_upload, artifacts/fake anatomy'},
    {'slug':'saturn_v01', 'human':'fail', 'human_score':4, 'input':'test_cases/saturn_hexagon_storm/outputs/wan22_template_v01/saturn_hexagon_storm_wan22_silent_1080.mp4', 'note':'scale/process-heavy weak lane'},
    {'slug':'saturn_v02', 'human':'fail', 'human_score':4, 'input':'test_cases/saturn_hexagon_storm/outputs/wan22_template_v02_plain/saturn_hexagon_storm_wan22_silent_1080.mp4', 'note':'scale/process-heavy weak lane'},
    {'slug':'mantis_v04', 'human':'fail', 'human_score':4, 'input':'test_cases/mantis_shrimp_cavitation_punch/outputs/say_dog_v04_proof_hybrid/mantis_say_dog_v04_silent_1080.mp4', 'note':'early mantis say-dog fail'},
    {'slug':'mantis_v11', 'human':'fail', 'human_score':5, 'input':'test_cases/mantis_shrimp_cavitation_punch/outputs/say_dog_v11_clean_mechanics/mantis_say_dog_v11_silent_1080.mp4', 'note':'pre-reset mantis fail'},
    {'slug':'mantis_v17', 'human':'fail', 'human_score':5, 'input':'test_cases/mantis_shrimp_cavitation_punch/outputs/say_dog_v17_premium_abstract_mechanism/mantis_say_dog_v17_silent_1080.mp4', 'note':'premium abstract mechanism fail'},
    {'slug':'mantis_v25', 'human':'fail', 'human_score':5, 'input':'test_cases/mantis_shrimp_cavitation_punch/outputs/say_dog_v25_mechanism_closeup/mantis_say_dog_v25_silent_1080.mp4', 'note':'late mechanism closeup fail'},
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_labels(labels_path: Path, calib: Path) -> tuple[list[dict[str, Any]], str]:
    if labels_path.exists():
        data = json.loads(labels_path.read_text(encoding='utf-8'))
        clips = data.get('clips', [])
        note = str(data.get('note') or '')
        if clips:
            return clips, note
    legacy_labels_path = calib / 'labels.json'
    if labels_path != legacy_labels_path and legacy_labels_path.exists():
        data = json.loads(legacy_labels_path.read_text(encoding='utf-8'))
        clips = data.get('clips', [])
        note = str(data.get('note') or '')
        if clips:
            return clips, note
    return DEFAULT_CLIPS, 'Calibration uses first video frame as source proxy when approved per-shot plates are not consistently available.'


def write_labels(labels_path: Path, clips: list[dict[str, Any]], note: str) -> None:
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    labels_path.write_text(json.dumps({'note': note, 'clips': clips}, indent=2) + '\n', encoding='utf-8')


def source_for_clip(calib: Path, clip: dict[str, Any], *, source_policy: str) -> Path:
    explicit = clip.get('source') or clip.get('source_image') or clip.get('source_plate')
    if explicit:
        src = ROOT / str(explicit)
        if not src.exists():
            raise FileNotFoundError(f"explicit source for {clip['slug']} missing: {src}")
        return src
    if source_policy != 'first_frame_proxy':
        raise FileNotFoundError(f"{clip['slug']} has no explicit source image and source_policy={source_policy}")
    sources = calib / 'sources'
    out = sources / f"{clip['slug']}_first_frame.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg','-y','-v','error','-i',str(ROOT/clip['input']),'-frames:v','1','-q:v','2',str(out)])
    return out


def metric_val(metrics: dict[str, Any], name: str, field: str = 'mean') -> float | None:
    m = metrics.get(name) or {}
    if not m.get('available'):
        return None
    v = m.get(field)
    return float(v) if v is not None else None


def ffprobe_duration(path: Path) -> float:
    proc = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(path)
    ], cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return float(proc.stdout.strip())


def resolve_source_path(value: str, slug: str) -> Path:
    src = ROOT / str(value)
    if not src.exists():
        raise FileNotFoundError(f"explicit source for {slug} missing: {src}")
    return src


def explicit_source_values(clip: dict[str, Any]) -> list[str]:
    if clip.get('sources'):
        values=[]
        for item in clip['sources']:
            if isinstance(item, str):
                values.append(item)
            elif isinstance(item, dict):
                values.append(str(item.get('source') or item.get('source_image') or item.get('source_plate') or ''))
        return [v for v in values if v]
    single = clip.get('source') or clip.get('source_image') or clip.get('source_plate')
    return [str(single)] if single else []


def aggregate_numeric(values: list[float | None], reducer: str) -> float | None:
    vals = [float(v) for v in values if v is not None]
    if not vals:
        return None
    if reducer == 'min':
        return round(min(vals), 6)
    if reducer == 'max':
        return round(max(vals), 6)
    return round(sum(vals) / len(vals), 6)


def evaluate_single_source_clip(inp: Path, source: Path, outdir: Path, sample_fps: str) -> tuple[dict[str, float | None], str, list[dict[str, Any]]]:
    run([sys.executable,'tools/local_video_qa.py','--input',str(inp),'--source-image',str(source),'--report-only','--frame-sample-fps',str(sample_fps),'--no-require-audio','--outdir',str(outdir)])
    report=json.loads((outdir/'qa_report.json').read_text(encoding='utf-8'))
    metrics=report.get('metrics',{})
    return {
        'clip_min': metric_val(metrics,'clip_preservation','min'),
        'clip_mean': metric_val(metrics,'clip_preservation','mean'),
        'dino_min': metric_val(metrics,'dino_structure','min'),
        'dino_mean': metric_val(metrics,'dino_structure','mean'),
        'temporal': metric_val(metrics,'temporal_consistency','mean'),
        'motion': metric_val(metrics,'motion_magnitude','mean'),
    }, rel(outdir/'qa_report.json'), []


def evaluate_per_shot_sources(inp: Path, clip: dict[str, Any], outdir: Path, sample_fps: str) -> tuple[dict[str, float | None], list[str], list[str], list[dict[str, Any]]]:
    sources = clip.get('sources') or []
    if not sources:
        source = source_for_clip(outdir.parent.parent, clip, source_policy='explicit_sources')
        metrics, report, _ = evaluate_single_source_clip(inp, source, outdir, sample_fps)
        return metrics, [rel(source)], [report], []
    total = ffprobe_duration(inp)
    provided_durations = [float(s.get('duration', 0.0)) for s in sources if isinstance(s, dict)]
    has_durations = len(provided_durations) == len(sources) and sum(provided_durations) > 0
    cursor = 0.0
    shot_rows=[]
    metric_rows=[]
    reports=[]
    source_paths=[]
    segdir = outdir / 'shot_segments'
    for idx, item in enumerate(sources, start=1):
        if isinstance(item, str):
            src_value = item
            duration = total / len(sources)
            shot_id = f'{idx:02d}'
        else:
            src_value = str(item.get('source') or item.get('source_image') or item.get('source_plate'))
            duration = float(item.get('duration') or (total / len(sources)))
            shot_id = str(item.get('id') or f'{idx:02d}')
        if not has_durations:
            duration = total / len(sources)
        # Clamp final segment to available duration.
        if idx == len(sources):
            duration = max(0.1, total - cursor)
        src = resolve_source_path(src_value, clip['slug'])
        segment = segdir / f'shot_{idx:02d}.mp4'
        segment.parent.mkdir(parents=True, exist_ok=True)
        run(['ffmpeg','-y','-v','error','-ss',f'{cursor:.3f}','-i',str(inp),'-t',f'{duration:.3f}','-an','-c:v','libx264','-preset','veryfast','-crf','18',str(segment)])
        shot_out = outdir / f'shot_{idx:02d}_qa'
        metrics, report, _ = evaluate_single_source_clip(segment, src, shot_out, sample_fps)
        metric_rows.append(metrics)
        reports.append(report)
        source_paths.append(rel(src))
        shot_rows.append({'id': shot_id, 'source': rel(src), 'segment': rel(segment), 'duration': round(duration, 3), 'qa_report': report, **metrics})
        cursor += duration
    aggregated = {
        'clip_min': aggregate_numeric([m['clip_min'] for m in metric_rows], 'min'),
        'clip_mean': aggregate_numeric([m['clip_mean'] for m in metric_rows], 'mean'),
        'dino_min': aggregate_numeric([m['dino_min'] for m in metric_rows], 'min'),
        'dino_mean': aggregate_numeric([m['dino_mean'] for m in metric_rows], 'mean'),
        'temporal': aggregate_numeric([m['temporal'] for m in metric_rows], 'max'),
        'motion': aggregate_numeric([m['motion'] for m in metric_rows], 'mean'),
    }
    (outdir/'per_shot_summary.json').write_text(json.dumps({'shots': shot_rows, 'aggregated': aggregated}, indent=2) + '\n', encoding='utf-8')
    return aggregated, source_paths, reports, shot_rows


def gate(row: dict[str, Any], thresholds: dict[str, float]) -> tuple[str, list[str]]:
    reasons=[]
    if row['clip_min'] is None or row['clip_min'] < thresholds['clip_preservation_min']:
        reasons.append('clip')
    if row['dino_min'] is None or row['dino_min'] < thresholds['dino_structure_min']:
        reasons.append('dino')
    if row['temporal'] is None or row['temporal'] > thresholds['temporal_consistency_max']:
        reasons.append('temporal')
    if row['motion'] is None or row['motion'] < thresholds['motion_magnitude_low']:
        reasons.append('motion_low')
    if row['motion'] is None or row['motion'] > thresholds['motion_magnitude_high']:
        reasons.append('motion_high')
    return ('fail' if reasons else 'pass'), reasons


def candidate_values(values: list[float | None], include_zero: bool = False) -> list[float]:
    vals = sorted({round(float(v), 6) for v in values if v is not None})
    if not vals:
        return [0.0]
    mids = [(a+b)/2 for a,b in zip(vals, vals[1:])]
    out = [min(vals)-1e-6, *vals, *mids, max(vals)+1e-6]
    if include_zero:
        out.append(0.0)
    return sorted({round(x, 6) for x in out})


def fit(rows: list[dict[str, Any]]) -> tuple[dict[str, float], list[dict[str, Any]]]:
    clip_cands = candidate_values([r['clip_min'] for r in rows], True)
    dino_cands = candidate_values([r['dino_min'] for r in rows], True)
    temporal_cands = candidate_values([r['temporal'] for r in rows], True)
    motion_vals = [r['motion'] for r in rows if r['motion'] is not None]
    low_cands = candidate_values(motion_vals, True)
    high_cands = candidate_values(motion_vals, True)
    best=None
    for clip_min, dino_min, temp_max, motion_low, motion_high in itertools.product(clip_cands, dino_cands, temporal_cands, low_cands, high_cands):
        if motion_low > motion_high:
            continue
        th = {
            'clip_preservation_min': clip_min,
            'dino_structure_min': dino_min,
            'temporal_consistency_max': temp_max,
            'motion_magnitude_low': motion_low,
            'motion_magnitude_high': motion_high,
        }
        matches=0; false_pos=0; false_neg=0; disagreements=[]
        for r in rows:
            pred, reasons = gate(r, th)
            if pred == r['human']:
                matches += 1
            else:
                disagreements.append({'slug':r['slug'],'human':r['human'],'predicted':pred,'reasons':reasons})
                if pred == 'fail': false_pos += 1
                else: false_neg += 1
        # Penalize false positives more: do not block known-good winners.
        score = (matches, -false_pos*2 - false_neg, -sum(1 for x in th.values() if x != 0.0))
        if best is None or score > best[0]:
            best = (score, th, disagreements)
    assert best is not None
    return best[1], best[2]


def archive_existing_thresholds(path: Path, archive_dir: Path) -> str | None:
    if not path.exists():
        return None
    archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = archive_dir / f'qa_thresholds_before_calibration_{stamp}.json'
    shutil.copy2(path, dest)
    return rel(dest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--calib-dir', default=str(DEFAULT_CALIB))
    parser.add_argument('--labels-file', default=None, help='Optional labels JSON. Defaults to <calib-dir>/labels.json.')
    parser.add_argument('--thresholds-out', default=str(DEFAULT_THRESHOLDS))
    parser.add_argument('--source-policy', choices=['first_frame_proxy', 'explicit_sources'], default='first_frame_proxy')
    parser.add_argument('--frame-sample-fps', default='0.5')
    parser.add_argument('--enable-blocking', action='store_true', help='Only use after approved source plates and strong agreement.')
    parser.add_argument('--no-archive-thresholds', action='store_true')
    args = parser.parse_args()

    calib = Path(args.calib_dir)
    if not calib.is_absolute():
        calib = ROOT / calib
    thresholds_out = Path(args.thresholds_out)
    if not thresholds_out.is_absolute():
        thresholds_out = ROOT / thresholds_out
    labels_path = Path(args.labels_file) if args.labels_file else calib / 'labels.json'
    if not labels_path.is_absolute():
        labels_path = ROOT / labels_path
    runs = calib / 'runs'
    calib.mkdir(parents=True, exist_ok=True)
    runs.mkdir(parents=True, exist_ok=True)

    clips, note = load_labels(labels_path, calib)
    write_labels(labels_path, clips, note)

    missing_inputs = []
    missing_sources = []
    for clip in clips:
        inp = ROOT / clip['input']
        if not inp.exists():
            missing_inputs.append(f"{clip['slug']}: {inp}")
        if args.source_policy == 'explicit_sources' and not explicit_source_values(clip):
            missing_sources.append(clip['slug'])
    if missing_inputs or missing_sources:
        if missing_inputs:
            print('Missing calibration inputs:', file=sys.stderr)
            print('\n'.join(missing_inputs), file=sys.stderr)
        if missing_sources:
            print('Missing explicit source images in labels.json:', file=sys.stderr)
            print('\n'.join(missing_sources), file=sys.stderr)
            print('Add source/source_image/source_plate per clip, or run with --source-policy first_frame_proxy for advisory calibration.', file=sys.stderr)
        return 2

    rows=[]
    for clip in clips:
        inp = ROOT / clip['input']
        outdir = runs / clip['slug']
        if args.source_policy == 'explicit_sources' and clip.get('sources'):
            metric_row, source_paths, qa_reports, shot_rows = evaluate_per_shot_sources(inp, clip, outdir, str(args.frame_sample_fps))
            row={
                **clip,
                'sources': source_paths,
                'source_policy': 'explicit_sources_per_shot',
                **metric_row,
                'qa_report': rel(outdir/'per_shot_summary.json'),
                'shot_reports': qa_reports,
                'shot_metrics': shot_rows,
            }
        else:
            source = source_for_clip(calib, clip, source_policy=args.source_policy)
            metric_row, qa_report, _ = evaluate_single_source_clip(inp, source, outdir, str(args.frame_sample_fps))
            row={
                **clip,
                'source': rel(source),
                'source_policy': args.source_policy,
                **metric_row,
                'qa_report': qa_report,
            }
        rows.append(row)

    thresholds, _ = fit(rows)
    for r in rows:
        pred, reasons = gate(r, thresholds)
        r['predicted']=pred
        r['block_reasons']=reasons
        r['match']=(pred==r['human'])
    matches=sum(r['match'] for r in rows)
    disagreements=[r for r in rows if not r['match']]
    agreement_rate = round(matches/len(rows), 4) if rows else 0
    agreement_fraction = f"{matches}/{len(rows)}"
    source_policy_note = (
        'first-frame source proxy; calibrated result is advisory until rerun with approved source plates per shot'
        if args.source_policy == 'first_frame_proxy'
        else 'explicit source images from labels.json'
    )
    blocking_enabled = bool(args.enable_blocking and args.source_policy == 'explicit_sources' and agreement_rate >= 0.9)
    decision = (
        'Blocking enabled: explicit sources were used and agreement met the >=90% bar.'
        if blocking_enabled else
        'Hold advisory: rerun with approved explicit source plates before enabling blocking.'
        if args.source_policy == 'first_frame_proxy' else
        'Hold advisory: agreement below bar or --enable-blocking not set.'
    )
    archived = None if args.no_archive_thresholds else archive_existing_thresholds(thresholds_out, calib / 'archives')
    threshold_config = {
        **thresholds,
        'fail_closed': True,
        'blocking_enabled': blocking_enabled,
        'gate_mode': 'blocking' if blocking_enabled else 'advisory',
        'calibrated_against': f"{len(rows)} labeled clips, {sum(r['human']=='pass' for r in rows)} pass / {sum(r['human']=='fail' for r in rows)} fail; calibration_dir={calib}",
        'agreement': f"{agreement_fraction} ({agreement_rate*100:.1f}%); disagreements: " + json.dumps([
            {
                'slug': r['slug'],
                'human': r['human'],
                'predicted': r['predicted'],
                'metrics': {
                    'clip_min': r['clip_min'],
                    'dino_min': r['dino_min'],
                    'temporal': r['temporal'],
                    'motion': r['motion'],
                },
            }
            for r in disagreements
        ]),
        'source_policy': source_policy_note,
        'human_review_authoritative': True,
        'decision': decision,
    }
    if archived:
        threshold_config['archived_previous_thresholds'] = archived

    thresholds_out.parent.mkdir(parents=True, exist_ok=True)
    thresholds_out.write_text(json.dumps(threshold_config, indent=2) + '\n', encoding='utf-8')
    summary={
        'calibration_dir': str(calib),
        'source_policy': source_policy_note,
        'n': len(rows),
        'pass': sum(r['human']=='pass' for r in rows),
        'fail': sum(r['human']=='fail' for r in rows),
        'thresholds': thresholds,
        'thresholds_out': str(thresholds_out),
        'threshold_config': threshold_config,
        'agreement_fraction': agreement_fraction,
        'agreement_rate': agreement_rate,
        'disagreements': disagreements,
        'blocking_enabled': blocking_enabled,
        'decision': decision,
        'rows': rows,
    }
    (calib/'calibration_results.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
