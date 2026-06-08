#!/usr/bin/env python3
"""Swap the v16 Edge TTS track to ElevenLabs George and rebuild deliverables.

Requires ELEVENLABS_API_KEY in the environment. Does not store secrets.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "outputs" / "wan22_v16_final_vo"
OUT_DIR = ROOT / "outputs" / "wan22_v17_elevenlabs_george"
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George - Warm, Captivating Storyteller
VOICE_NAME = "George - Warm, Captivating Storyteller"
MODEL_ID = "eleven_multilingual_v2"
BEATS = [
    {"file": "beat01.mp3", "text": "A frog can freeze solid.", "target_s": 2.35},
    {"file": "beat02.mp3", "text": "In winter, ice can form through much of its body.", "target_s": 3.40},
    {"file": "beat03.mp3", "text": "Its heart can stop for a while.", "target_s": 3.10},
    {"file": "beat04.mp3", "text": "Sugar-like fluids help protect the cells.", "target_s": 3.60},
    {"file": "beat05.mp3", "text": "Then spring warms it up, and the frog starts moving again.", "target_s": 4.45},
    {"file": "beat06.mp3", "text": "It is not magic. It is survival chemistry.", "target_s": 3.70},
]


def run(cmd: list[str]) -> None:
    print("RUN", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True).strip()
    return float(out)


def atempo_chain(ratio: float) -> str:
    # atempo supports 0.5..100 in current ffmpeg, but chaining keeps it safe/portable.
    parts = []
    r = ratio
    while r > 2.0:
        parts.append("atempo=2.0")
        r /= 2.0
    while r < 0.5:
        parts.append("atempo=0.5")
        r /= 0.5
    parts.append(f"atempo={r:.6f}")
    return ",".join(parts)


def elevenlabs_tts(api_key: str, text: str, out: Path) -> None:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128"
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.50,
            "similarity_boost": 0.78,
            "style": 0.12,
            "use_speaker_boost": True,
        },
    }
    r = requests.post(
        url,
        headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        json=payload,
        timeout=90,
    )
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs TTS failed status={r.status_code}: {r.text[:500]}")
    out.write_bytes(r.content)


def main() -> int:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("ELEVENLABS_API_KEY is required")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_dir = OUT_DIR / "raw"
    fit_dir = OUT_DIR / "fit"
    raw_dir.mkdir(exist_ok=True)
    fit_dir.mkdir(exist_ok=True)

    report: dict = {
        "provider": "elevenlabs",
        "voice": "elevenlabs_george",
        "voice_name": VOICE_NAME,
        "voice_id": VOICE_ID,
        "model_id": MODEL_ID,
        "beats": [],
    }

    concat = fit_dir / "concat.txt"
    concat_lines = []
    for i, beat in enumerate(BEATS, start=1):
        raw = raw_dir / beat["file"]
        fitted = fit_dir / f"beat{i:02d}.wav"
        elevenlabs_tts(api_key, beat["text"], raw)
        raw_s = probe_duration(raw)
        target_s = float(beat["target_s"])
        ratio = raw_s / target_s
        # Fit tempo, trim/pad silence to exact segment duration, normalize loudness gently.
        af = f"{atempo_chain(ratio)},apad,atrim=0:{target_s:.3f},asetpts=N/SR/TB,loudnorm=I=-16:TP=-1.5:LRA=11"
        run(["ffmpeg", "-y", "-i", raw, "-af", af, "-ar", "48000", "-ac", "2", fitted])
        fit_s = probe_duration(fitted)
        concat_lines.append(f"file '{fitted.resolve()}'\n")
        report["beats"].append({
            "file": beat["file"],
            "text": beat["text"],
            "raw_s": round(raw_s, 3),
            "target_s": target_s,
            "fit_s": round(fit_s, 3),
            "tempo_ratio": round(ratio, 3),
        })
    concat.write_text("".join(concat_lines), encoding="utf-8")

    final_audio_wav = OUT_DIR / "final_voiceover_george.wav"
    final_audio_m4a = OUT_DIR / "final_voiceover_george.m4a"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c", "pcm_s16le", final_audio_wav])
    run(["ffmpeg", "-y", "-i", final_audio_wav, "-c:a", "aac", "-b:a", "160k", "-ar", "48000", final_audio_m4a])

    clean_in = SRC_DIR / "wood_frog_freeze_survival_v16_final_vo_clean_1080.mp4"
    captioned_in = SRC_DIR / "wood_frog_freeze_survival_v16_final_vo_captioned_1080.mp4"
    clean_out = OUT_DIR / "wood_frog_freeze_survival_v17_elevenlabs_george_clean_1080.mp4"
    captioned_out = OUT_DIR / "wood_frog_freeze_survival_v17_elevenlabs_george_captioned_1080.mp4"
    preview_out = OUT_DIR / "wood_frog_freeze_survival_v17_elevenlabs_george_captioned_720.mp4"

    run(["ffmpeg", "-y", "-i", clean_in, "-i", final_audio_m4a, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", clean_out])
    run(["ffmpeg", "-y", "-i", captioned_in, "-i", final_audio_m4a, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", captioned_out])
    run(["ffmpeg", "-y", "-i", captioned_out, "-vf", "scale=720:1280:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-movflags", "+faststart", preview_out])

    for label, path in [("captioned_master", captioned_out), ("captioned_preview", preview_out), ("clean_master", clean_out), ("final_audio", final_audio_m4a)]:
        report[label] = str(path.relative_to(ROOT))
        report[label + "_duration_s"] = round(probe_duration(path), 3)

    ffprobe_json = OUT_DIR / "ffprobe_captioned_master.json"
    with ffprobe_json.open("w", encoding="utf-8") as f:
        subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "stream=codec_name,codec_type,width,height,sample_rate:format=duration,size",
            "-of", "json", str(captioned_out)
        ], check=True, text=True, stdout=f)

    loud = subprocess.run(["ffmpeg", "-i", str(captioned_out), "-af", "volumedetect", "-f", "null", "-"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (OUT_DIR / "audio_volumedetect.txt").write_text(loud.stderr, encoding="utf-8")
    (OUT_DIR / "final_vo_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
