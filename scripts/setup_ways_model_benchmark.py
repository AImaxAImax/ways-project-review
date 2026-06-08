#!/usr/bin/env python3
"""Create the WAYS local model benchmark scaffold.

This script implements the protocol's locked golden plate set and the manifest
that later runners consume. It intentionally does not render video by itself.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path('/mnt/c/dev/curious-shorts')
BENCH = ROOT / 'benchmark'
PLATES_DIR = BENCH / 'plates'
CONFIG_DIR = BENCH / 'config'
RESULTS_DIR = BENCH / 'results'

SEED_BANK = [627101, 627102, 627103, 627104, 627105]

# Existing accepted/best-available WAYS stills. The current plate set uses locked
# copies under benchmark/plates; do not regenerate these mid-test.
PLATES: list[dict[str, Any]] = [
    {
        'id': 'cat1_shark_a', 'category': 1, 'slot': 'a', 'slug': 'shark_realism_hold',
        'use_case': 'Strong-prior realism hold',
        'source': 'test_cases/sharks_older_than_trees/assets/selected_frames_v15/shot01_before_trees_clean_bg_submerged_shark_v15_v03_selected.png',
        'prompt': 'Premium natural-history shot of an ancient shark moving subtly underwater, identity preserved, slow parallax, realistic anatomy, no text.',
        'negative': 'text, logo, watermark, extra fins, melted anatomy, fake diagram, subtitles, blurry, flicker',
    },
    {
        'id': 'cat1_octopus_b', 'category': 1, 'slot': 'b', 'slug': 'octopus_realism_hold',
        'use_case': 'Strong-prior realism hold',
        'source': 'test_cases/octopus_three_hearts/assets/sdxl_wan_template_v01_plates/shot01_octopus_three_hearts_sdxl_plate.png',
        'prompt': 'Macro natural-history octopus portrait, subtle breathing and arm movement, preserve the same octopus and composition, cinematic water motion, no text.',
        'negative': 'text, logo, watermark, extra arms, melting, cartoon, diagram labels, flicker',
    },
    {
        'id': 'cat2_owl_a', 'category': 2, 'slot': 'a', 'slug': 'owl_head_turn_270',
        'use_case': 'Large controlled motion',
        'source': 'test_cases/owl_head_turn/assets/pending_human_plate_review/higgsfield_v02_top_picks/01_ref_nano04_turn_01.png',
        'prompt': 'Real owl calmly turning its head in a controlled arc, natural neck anatomy, body stable, feathers coherent, cinematic close-up, no text.',
        'negative': 'twisted neck, broken anatomy, extra heads, warped beak, text, logo, flicker, melted feathers',
    },
    {
        'id': 'cat2_owl_b', 'category': 2, 'slot': 'b', 'slug': 'owl_body_turn',
        'use_case': 'Large controlled motion',
        'source': 'test_cases/owl_head_turn/assets/pending_human_plate_review/higgsfield_v02_top_picks/03_seedream_body_front_face_back_01.png',
        'prompt': 'Full-body owl rotates and looks back with controlled motion, grounded body, realistic wing and neck anatomy, no text.',
        'negative': 'broken neck, extra wings, duplicated face, body morph, text, logo, watermark, flicker',
    },
    {
        'id': 'cat3_frog_a', 'category': 3, 'slot': 'a', 'slug': 'wood_frog_freeze_reveal',
        'use_case': 'Subtle reveal / transformation',
        'source': 'test_cases/wood_frog_freeze_survival/outputs/wan22_v15_polished_middle/frames/frame_00090.jpg',
        'prompt': 'Wood frog in icy environment, subtle freeze-to-survival reveal, tiny frost sparkle and breath-like movement, preserve frog anatomy, no text.',
        'negative': 'text, logo, extra limbs, melting frog, fake plastic, captions, flicker, chaotic transformation',
    },
    {
        'id': 'cat3_frog_b', 'category': 3, 'slot': 'b', 'slug': 'wood_frog_thaw_reveal',
        'use_case': 'Subtle reveal / transformation',
        'source': 'test_cases/wood_frog_freeze_survival/outputs/wan22_v15_polished_middle/frames/frame_00480.jpg',
        'prompt': 'Wood frog thaw reveal with controlled tiny movement and melting ice highlights, same frog preserved, realistic macro science visual, no text.',
        'negative': 'text, logo, extra limbs, melting anatomy, cartoon, diagram labels, overdone morphing, flicker',
    },
    {
        'id': 'cat4_mantis_a', 'category': 4, 'slot': 'a', 'slug': 'mantis_water_flash',
        'use_case': 'Dynamic effect / payoff',
        'source': 'test_cases/mantis_shrimp_cavitation_punch/assets/wan_motion_v03_clean_plates/shot04_clean_mantis_photo_plate.png',
        'prompt': 'Mantis shrimp strike energy, clean water flash and cavitation burst, subject remains believable, dynamic payoff, no text or graphic labels.',
        'negative': 'text, labels, arrows, logo, fake HUD, extra claws, melted shrimp, noisy artifacts, flicker',
    },
    {
        'id': 'cat4_mantis_b', 'category': 4, 'slot': 'b', 'slug': 'mantis_cavitation_bubble',
        'use_case': 'Dynamic effect / payoff',
        'source': 'test_cases/mantis_shrimp_cavitation_punch/assets/wan_motion_v03_clean_plates/shot06_clean_mantis_photo_plate.png',
        'prompt': 'Mantis shrimp cavitation bubble payoff, energetic water burst, natural macro footage feel, no overlay text, no labels.',
        'negative': 'text, labels, arrows, logo, fake diagram, extra limbs, melted anatomy, flicker, compression artifacts',
    },
    {
        'id': 'cat5_saturn_a', 'category': 5, 'slot': 'a', 'slug': 'saturn_scale_establishing',
        'use_case': 'Cinematic establishing / scale',
        'source': 'test_cases/saturn_hexagon_storm/assets/wan_template_plain_v02_plates/shot01_saturn_hexagon_storm_plain_plate.jpg',
        'prompt': 'Cinematic establishing shot of Saturn scale and atmosphere, grand camera drift, coherent clouds and rings, awe, no text.',
        't2v_prompt': 'Cinematic establishing shot of Saturn scale and atmosphere, grand camera drift through space toward the planet, coherent clouds and rings, awe, no text.',
        'negative': 'text, logo, watermark, labels, diagrams, incoherent planet, broken rings, flicker',
    },
    {
        'id': 'cat5_saturn_b', 'category': 5, 'slot': 'b', 'slug': 'saturn_hexagon_scale',
        'use_case': 'Cinematic establishing / scale',
        'source': 'test_cases/saturn_hexagon_storm/assets/wan_template_plain_v02_plates/shot03_saturn_hexagon_storm_plain_plate.jpg',
        'prompt': 'Cinematic scale shot over Saturn hexagon storm, elegant camera travel, coherent atmosphere, no text or labels.',
        't2v_prompt': 'Cinematic scale shot flying over Saturn hexagon storm, elegant camera travel, coherent atmosphere, awe, no text or labels.',
        'negative': 'text, logo, watermark, labels, diagram, broken geometry, noisy flicker',
    },
    {
        'id': 'cat6_mantis_a', 'category': 6, 'slot': 'a', 'slug': 'mantis_process_probe',
        'use_case': 'Process / concept probe',
        'source': 'test_cases/mantis_shrimp_cavitation_punch/assets/wan_motion_v03_clean_plates/shot03_clean_mantis_photo_plate.png',
        'prompt': 'Internal mechanism/process beat for mantis shrimp punch shown as clean physical motion without labels, source subject preserved, no text.',
        'negative': 'text, labels, arrows, anatomy diagram, fake UI, melting animal, extra limbs, watermark, flicker',
    },
    {
        'id': 'cat6_tardigrade_b', 'category': 6, 'slot': 'b', 'slug': 'tardigrade_process_probe',
        'use_case': 'Process / concept probe',
        'source': 'test_cases/tardigrade_survival_mode/assets/sdxl_wan_template_v01_plates/shot03_tardigrade_survival_mode_sdxl_plate.png',
        'prompt': 'Tardigrade survival process beat, credible microscope-style motion, controlled transformation, realistic anatomy, no text.',
        'negative': 'text, logo, fake anatomy, melted body, extra legs, diagram labels, watermark, flicker',
    },
]

MODELS = {
    'wan22_i2v': {
        'type': 'I2V', 'status': 'installed', 'categories': [1,2,3,4,5,6],
        'workflow': '/mnt/c/dev/vj-engine/comfyui/workflows/wan2_2_a14b_gguf_lightning_i2v_smoke.json',
        'notes': 'Baseline. Requires wan_2.1_vae.safetensors and high/low GGUF two-stage.',
    },
    'ltx23_fp8': {
        'type': 'I2V', 'status': 'installed_smoke_needed', 'categories': [1,2,3,4,5,6],
        'workflow': None, 'notes': 'Checkpoint installed; I2V workflow/conditioning verification still required.',
    },
    'ltx23_distilled': {
        'type': 'I2V', 'status': 'installed_smoke_needed', 'categories': [1,2,3,4,5,6],
        'workflow': None, 'notes': 'GGUF installed; I2V workflow/conditioning verification still required.',
    },
    'wan22_t2v': {
        'type': 'T2V', 'status': 'installed_smoke_needed', 'categories': [5],
        'workflow': None, 'notes': 'Category 5 only. Never score preservation against a source plate.',
    },
    'hunyuan15': {
        'type': 'I2V', 'status': 'workflow_present_model_missing_or_unverified', 'categories': [2,5],
        'workflow': '/mnt/c/dev/vj-engine/comfyui/workflows/hunyuan15_i2v_gguf_smoke.json',
        'notes': 'Sparse challenger; Phase 0 smoke required before bracket entry.',
    },
    'wan22_i2v_hi': {
        'type': 'I2V', 'status': 'missing', 'categories': [1,3],
        'workflow': None, 'notes': 'Quant ablation only. Need Q8/fp8/fp16 higher precision Wan2.2 I2V weights.',
    },
    'cogvideox15': {
        'type': 'I2V', 'status': 'missing', 'categories': ['long_clip_probe'],
        'workflow': None, 'notes': 'Long-clip probe only; not part of short realism grid.',
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    PLATES_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    locked = []
    for item in PLATES:
        src = ROOT / item['source']
        if not src.exists():
            raise FileNotFoundError(f"missing source plate for {item['id']}: {src}")
        dest = PLATES_DIR / f"{item['id']}.png"
        # Keep the locked copy byte-for-byte if already PNG. Convert by extension only
        # would require PIL and can change pixels; prefer exact copies and extension-true dest.
        if src.suffix.lower() == '.png':
            shutil.copy2(src, dest)
        else:
            # Preserve JPEG bytes with .jpg extension when source is JPEG.
            dest = PLATES_DIR / f"{item['id']}{src.suffix.lower()}"
            shutil.copy2(src, dest)
        rec = dict(item)
        rec['locked_path'] = str(dest.relative_to(ROOT))
        rec['source_sha256'] = sha256(src)
        rec['locked_sha256'] = sha256(dest)
        rec['source_exists'] = True
        locked.append(rec)
    manifest = {
        'benchmark_version': 'ways-local-video-model-benchmark-v1',
        'protocol': 'docs/WAYS_MODEL_BENCHMARK_PROTOCOL.md',
        'qa_thresholds': 'config/qa_thresholds.json',
        'seed_bank': SEED_BANK,
        'fps': 24,
        'wan_dims': {'width': 432, 'height': 768, 'frames': 25},
        'upscale_path': 'hold existing 432x768 to 1080x1920 path constant',
        'models': MODELS,
        'plates': locked,
        'human_review': {'blind_required': True, 'phone_review_authoritative': True},
        'notes': [
            'T2V entries are category 5 only and do not receive source-preservation scores.',
            'wan22_i2v_hi and native-res are separate ablations, not main matrix cells.',
            'Do not regenerate locked plates mid-test; replace only by creating benchmark_version v2.',
        ],
    }
    (CONFIG_DIR / 'benchmark_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'manifest': str(CONFIG_DIR / 'benchmark_manifest.json'), 'plates': len(locked), 'models': len(MODELS)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
