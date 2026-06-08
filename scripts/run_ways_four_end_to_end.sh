#!/usr/bin/env bash
set -euo pipefail
cd /mnt/c/dev/curious-shorts
for c in saturn_hexagon_storm wombat_cube_poop octopus_three_hearts tardigrade_survival_mode; do
  echo "=== RENDER $c $(date -Is) ==="
  python3 scripts/render_wan_harness.py "test_cases/$c/render_wan22_harness_config.json"
  echo "=== POLISH $c $(date -Is) ==="
  python3 tools/final_polish_pack.py \
    --input "test_cases/$c/outputs/wan22_template_v01/${c}_wan22_master_1080.mp4" \
    --manifest "test_cases/$c/outputs/wan22_template_v01/manifest.json" \
    --outdir "test_cases/$c/outputs/final_polish_wan22_template_v01" \
    --title "$c"
  echo "=== DONE $c $(date -Is) ==="
done
python3 - <<'PY'
import json,subprocess
from pathlib import Path
ROOT=Path('/mnt/c/dev/curious-shorts')
summary={}
for c in ['saturn_hexagon_storm','wombat_cube_poop','octopus_three_hearts','tardigrade_survival_mode']:
 p=ROOT/'test_cases'/c/'outputs/final_polish_wan22_template_v01/publish_candidate_captioned.mp4'
 sheet=ROOT/'test_cases'/c/'outputs/final_polish_wan22_template_v01/contact_sheet_final_polish.jpg'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=index,codec_type,codec_name,width,height,sample_rate','-of','json',str(p)],text=True))
 summary[c]={'mp4':str(p),'contact_sheet':str(sheet),'ffprobe':probe}
(ROOT/'ops/ways-video-lab-discord/ways_four_wan22_end_to_end_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
PY
