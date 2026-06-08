# WAYS QC Gate Runner Checklist

Use `python3 tools/ways_qc_gate_runner.py --board <board.json> --root <repo> --out <report.json>` before moving cards.

## Gate 1 - Script
- Hook appears in the first caption/beat so payoff lands in 1-2 seconds.
- Beat list exists, has no filler/sensational wording, and each spoken beat has a visual/proxy.
- At least one citable source is recorded.

## Gate 3 - Render QA
- Every expected clip path exists.
- Per-shot report has no generated text/logo, catastrophic morphing/anatomy issue, or lane artifact.
- Re-render only the failing shot; paid escalation still requires approval.

## Gate 4 - Spec / Assembly QA
- ffprobe says 1080x1920, H.264, 24fps, AAC 48kHz, duration 5-60s.
- publish candidate, contact sheet, captions.ass, and captions.srt exist.
- Captions are phone-readable with no double captions or non-caption text.
- Visual reset max is <=3 seconds and audio peak is < -0.5 dB.

## WIP limits
- Plate Generation + Render combined <= 3 videos.
- Plate QC <= 5 plates.
- Human Final Review <= 3 videos.
- Ready-to-Publish target is 10; flag Josh below 5.

Human gates (Gate 2, Gate 5, Gate 6) remain blocked/advisory unless explicit human approval fields are recorded.
