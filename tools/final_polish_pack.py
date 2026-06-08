#!/usr/bin/env python3
"""Create a captioned final-polish upload pack from a clean Wan/short master.

Input is intentionally read-only. The script writes a new output directory containing:
- clean_master_unmodified.mp4 (copy of the clean source)
- captions.ass and captions.srt
- publish_candidate_captioned.mp4
- discord_preview_captioned.mp4
- contact_sheet_final_polish.jpg
- ffprobe JSON files
- upload_metadata.json
- PUBLISH_GATE.md

Caption timing defaults to cumulative shot durations from a Wan manifest. If a future
word-timestamp JSON is supplied, this script can be extended without changing the
pack contract.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

STYLE_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,104,&H00FFFFFF,&H0000D7FF,&H00000000,&H80000000,-1,0,0,0,100,100,-1,0,1,8,3,5,90,90,650,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

FILLER = {"A", "AN", "AND", "ARE", "BEFORE", "FROM", "HERE", "THE", "THEY", "THEN", "TODAY", "WERE", "WORLD"}


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+ " + " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def capture_json(cmd: list[str]) -> Any:
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def ts_ass(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    cs = int(round(seconds * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ts_srt(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", r"\N")


def choose_keyword(caption: str) -> str | None:
    words = re.findall(r"[A-Za-z0-9]+", caption.upper())
    candidates = [w for w in words if w not in FILLER]
    if not candidates:
        candidates = words
    if not candidates:
        return None
    # Prefer numbers and punchy/long nouns; deterministic for reproducibility.
    return sorted(candidates, key=lambda w: (bool(re.search(r"\d", w)), len(w)), reverse=True)[0]


def style_caption(caption: str, keyword: str | None) -> str:
    text = ass_escape(caption.upper())
    if not keyword:
        return text
    # ASS colors are BGR. Yellow #FFD700 => &H0000D7FF&.
    pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
    return pattern.sub(r"{\\c&H0000D7FF&}" + keyword + r"{\\c&H00FFFFFF&}", text, count=1)


def load_segments(manifest_path: Path) -> list[dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    shots = manifest.get("shots")
    if not isinstance(shots, list) or not shots:
        raise SystemExit(f"manifest has no shots[]: {manifest_path}")
    t = 0.0
    segments: list[dict[str, Any]] = []
    for idx, shot in enumerate(shots, 1):
        duration = float(shot.get("duration") or 0)
        caption = str(shot.get("caption") or "").strip()
        if duration <= 0:
            raise SystemExit(f"shot {idx} has invalid duration: {duration}")
        if caption:
            segments.append({
                "index": idx,
                "shot_id": shot.get("id", f"{idx:02d}"),
                "start": t,
                "end": t + duration,
                "caption": caption,
                "keyword": choose_keyword(caption),
            })
        t += duration
    return segments


def write_captions(segments: list[dict[str, Any]], ass_path: Path, srt_path: Path) -> None:
    lines = [STYLE_HEADER]
    srt_lines: list[str] = []
    for i, seg in enumerate(segments, 1):
        start = ts_ass(seg["start"])
        end = ts_ass(seg["end"])
        styled = style_caption(seg["caption"], seg.get("keyword"))
        lines.append(f"Dialogue: 0,{start},{end},Caption,,0,0,0,,{styled}\n")
        srt_lines.extend([
            str(i),
            f"{ts_srt(seg['start'])} --> {ts_srt(seg['end'])}",
            seg["caption"].upper(),
            "",
        ])
    ass_path.write_text("".join(lines), encoding="utf-8")
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final caption/polish upload pack from a clean short master.")
    parser.add_argument("--input", required=True, type=Path, help="Clean source MP4. Never overwritten.")
    parser.add_argument("--manifest", required=True, type=Path, help="Wan/template manifest with shots[].duration and shots[].caption.")
    parser.add_argument("--outdir", required=True, type=Path, help="Output pack directory.")
    parser.add_argument("--title", default="untitled-short")
    parser.add_argument("--crf", default="18")
    args = parser.parse_args()

    src = args.input.resolve()
    manifest_path = args.manifest.resolve()
    outdir = args.outdir.resolve()
    if not src.exists():
        raise SystemExit(f"missing input: {src}")
    if not manifest_path.exists():
        raise SystemExit(f"missing manifest: {manifest_path}")

    outdir.mkdir(parents=True, exist_ok=True)
    clean_copy = outdir / "clean_master_unmodified.mp4"
    ass_path = outdir / "captions.ass"
    srt_path = outdir / "captions.srt"
    master = outdir / "publish_candidate_captioned.mp4"
    preview = outdir / "discord_preview_captioned.mp4"
    sheet = outdir / "contact_sheet_final_polish.jpg"

    segments = load_segments(manifest_path)
    write_captions(segments, ass_path, srt_path)
    if not clean_copy.exists() or clean_copy.stat().st_size != src.stat().st_size:
        shutil.copy2(src, clean_copy)

    # Escape path for ffmpeg ass filter. Use a relative filename by running in outdir.
    run([
        "ffmpeg", "-y", "-i", str(clean_copy),
        "-vf", "ass=captions.ass",
        "-af", "highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,loudnorm=I=-15:LRA=7:TP=-1",
        "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf), "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", str(master.name)
    ], cwd=outdir)

    run([
        "ffmpeg", "-y", "-i", str(master), "-vf", "scale=720:1280:flags=lanczos",
        "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "3.1",
        "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-movflags", "+faststart", str(preview)
    ])

    run([
        "ffmpeg", "-y", "-i", str(master), "-vf", "fps=1,scale=270:480:flags=lanczos,tile=6x4", "-frames:v", "1", "-update", "1", str(sheet)
    ])

    src_probe = capture_json(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(clean_copy)])
    master_probe = capture_json(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(master)])
    preview_probe = capture_json(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(preview)])
    (outdir / "ffprobe_clean_master.json").write_text(json.dumps(src_probe, indent=2), encoding="utf-8")
    (outdir / "ffprobe_publish_candidate.json").write_text(json.dumps(master_probe, indent=2), encoding="utf-8")
    (outdir / "ffprobe_discord_preview.json").write_text(json.dumps(preview_probe, indent=2), encoding="utf-8")

    metadata = {
        "title": args.title,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_clean_master": str(src),
        "clean_master_copy": str(clean_copy),
        "manifest": str(manifest_path),
        "caption_mode": "shot-accurate key-word styled ASS from manifest durations; use CapCut/Whisper word timestamps for true active-word karaoke if required",
        "audio_polish": "highpass 80 Hz, light compression, loudnorm target I=-15 LRA=7 TP=-1, AAC 48kHz",
        "outputs": {
            "publish_candidate": str(master),
            "discord_preview": str(preview),
            "captions_ass": str(ass_path),
            "captions_srt": str(srt_path),
            "contact_sheet": str(sheet),
        },
        "segments": segments,
    }
    (outdir / "upload_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    gate = f"""# Publish gate: {args.title}

Generated: {metadata['created_at']}

## Pack contract

- Clean master preserved: `{clean_copy.name}`
- Captioned candidate: `{master.name}`
- Platform preview: `{preview.name}`
- Editable captions: `{ass_path.name}` and `{srt_path.name}`
- Contact sheet: `{sheet.name}`

## Required human/agent review before publish

- [ ] Play full candidate at phone size; first 2 seconds hook is readable.
- [ ] Captions are accurate to voiceover and do not collide with platform UI.
- [ ] Yellow emphasis is on useful key words; if true spoken active-word karaoke is required, replace/patch ASS with Whisper/CapCut word timings.
- [ ] No generated text, logos, labels, lower thirds, or double captions in the source visuals.
- [ ] Audio is speech-forward, normalized, and not clipping.
- [ ] Contact sheet has visual reset/interest every 2-3 seconds.
- [ ] Clean master remains available for future recaptioning or CapCut import.

Decision: HOLD until every box above is checked. Passing this script creates a publish candidate, not an automatic publish approval.
"""
    (outdir / "PUBLISH_GATE.md").write_text(gate, encoding="utf-8")

    print(json.dumps({"outdir": str(outdir), "publish_candidate": str(master), "preview": str(preview), "segments": len(segments)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
