#!/usr/bin/env python3
"""Render a source-photo static-first WAYS internal candidate.

This is intentionally conservative: it emits a private/internal draft from real source
images, captions, ffprobe, contact sheet, and manifest. It does not upload or publish.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

W, H = 1080, 1920
FPS = 24


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def fit_cover(img: Image.Image, w: int, h: int) -> Image.Image:
    img = img.convert("RGB")
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def make_panel(src: Path, out: Path, idx: int) -> None:
    base = fit_cover(Image.open(src), W, H)
    # cinematic grade, no text
    base = ImageEnhance.Color(base).enhance(1.08)
    base = ImageEnhance.Contrast(base).enhance(1.12)
    vignette = Image.new("L", (W, H), 0)
    # simple vertical caption-safe darkening, not text
    overlay = Image.new("RGB", (W, H), (0, 0, 0))
    mask = Image.new("L", (W, H), 0)
    # center caption readability band, soft blur
    for y in range(H):
        d = abs(y - int(H * 0.57)) / (H * 0.22)
        val = int(max(0, 105 * (1 - d)))
        if val:
            for x in range(W):
                mask.putpixel((x, y), val)
    mask = mask.filter(ImageFilter.GaussianBlur(80))
    base = Image.composite(overlay, base, mask)
    out.parent.mkdir(parents=True, exist_ok=True)
    base.save(out, quality=94)


def build_ass(beats: list[dict], duration: float, out: Path) -> None:
    per = duration / len(beats)
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Caption,DejaVu Sans,92,&H00FFFFFF,&H0000D7FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,8,3,5,90,90,120,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]
    for i, beat in enumerate(beats):
        start = i * per
        end = duration if i == len(beats) - 1 else (i + 1) * per
        text = str(beat.get("caption") or beat.get("voiceover") or "").replace(" / ", r"\N")
        # highlight first 1-2 key words only, keep inactive white
        parts = text.split()
        if parts:
            n = min(2, len(parts))
            text = r"{\c&H0000D7FF&}" + " ".join(parts[:n]) + r"{\c&H00FFFFFF&}" + (" " + " ".join(parts[n:]) if len(parts) > n else "")
        lines.append(f"Dialogue: 6,{ass_time(start)},{ass_time(end)},Caption,,0,0,0,,{text}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_srt(beats: list[dict], duration: float, out: Path) -> None:
    per = duration / len(beats)
    def srt_time(t: float) -> str:
        h = int(t // 3600); m = int((t % 3600)//60); s = int(t%60); ms=int((t-int(t))*1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    chunks=[]
    for i,b in enumerate(beats,1):
        start=(i-1)*per; end=duration if i==len(beats) else i*per
        text=str(b.get('caption') or b.get('voiceover') or '').replace(' / ', '\n')
        chunks.append(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{text}\n")
    out.write_text("\n".join(chunks), encoding='utf-8')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir", type=Path)
    ap.add_argument("--run-name", default="auto_static_v01")
    args = ap.parse_args()
    project = args.project_dir
    outdir = project / "outputs" / args.run_name
    outdir.mkdir(parents=True, exist_ok=True)
    board_script = json.loads((project / "storyboard_manifest.json").read_text(encoding="utf-8"))
    # Prefer active_wip_board detailed beats if present.
    active = Path("ops/ways-video-lab-discord/active_wip_board.json")
    beats = []
    if active.exists():
        board = json.loads(active.read_text(encoding="utf-8"))
        for card in board.get("cards", []):
            if card.get("slug") == project.name:
                beats = card.get("beats") or card.get("script", {}).get("beats") or []
    if not beats:
        beats = board_script.get("shots", [])
    voice = outdir / "voiceover.mp3"
    if not voice.exists():
        raise SystemExit(f"missing voiceover: {voice}")
    dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(voice)], text=True).strip())
    manifest_path = project / "assets" / "source_stills" / "source_manifest.json"
    sources = json.loads(manifest_path.read_text(encoding="utf-8"))
    panels=[]
    for i, beat in enumerate(beats):
        src = Path(sources[i % len(sources)]["path"])
        panel = outdir / "panels" / f"panel_{i+1:02d}.jpg"
        make_panel(src, panel, i+1)
        panels.append(panel)
    per = dur / len(panels)
    concat = outdir / "frames.concat"
    concat.write_text("".join(f"file '{p.resolve()}'\nduration {per:.3f}\n" for p in panels) + f"file '{panels[-1].resolve()}'\n", encoding="utf-8")
    no_caption = outdir / "clean_master.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-i",str(voice),"-vf",f"scale={W}:{H}:flags=lanczos,format=yuv420p","-r",str(FPS),"-map","0:v","-map","1:a","-shortest","-c:v","libx264","-preset","medium","-crf","19","-profile:v","high","-c:a","aac","-b:a","160k","-ar","48000","-movflags","+faststart",str(no_caption)])
    ass = outdir / "captions.ass"; srt=outdir / "captions.srt"
    build_ass(beats, dur, ass); build_srt(beats, dur, srt)
    captioned = outdir / "publish_candidate_captioned.mp4"
    run(["ffmpeg","-y","-i",str(no_caption),"-vf",f"ass={ass.resolve()}","-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-profile:v","high","-c:a","copy","-movflags","+faststart",str(captioned)])
    preview = outdir / "discord_preview_captioned.mp4"
    run(["ffmpeg","-y","-i",str(captioned),"-vf","scale=720:1280:flags=lanczos","-c:v","libx264","-preset","medium","-crf","23","-pix_fmt","yuv420p","-profile:v","high","-level","3.1","-c:a","aac","-b:a","96k","-ar","48000","-movflags","+faststart",str(preview)])
    probe = outdir / "ffprobe_publish.json"
    subprocess.run(["ffprobe","-v","error","-print_format","json","-show_format","-show_streams",str(captioned)], check=True, stdout=probe.open("w"))
    # contact sheet every ~4 seconds
    sheet = outdir / "contact_sheet.jpg"
    run(["ffmpeg","-y","-i",str(captioned),"-vf","fps=1/4,scale=270:480,tile=4x3","-frames:v","1",str(sheet)])
    vol = subprocess.run(["ffmpeg","-i",str(captioned),"-af","volumedetect","-f","null","-"], text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    (outdir / "audio_report.txt").write_text(vol.stderr, encoding="utf-8")
    (outdir / "render_manifest.json").write_text(json.dumps({"mode":"static_source_internal_candidate","duration":dur,"beats":len(beats),"sources_manifest":str(manifest_path),"outputs":{"clean_master":str(no_caption),"publish_candidate_captioned":str(captioned),"discord_preview_captioned":str(preview),"contact_sheet":str(sheet),"ffprobe_publish":str(probe),"captions_ass":str(ass),"captions_srt":str(srt)}}, indent=2), encoding="utf-8")
    print(json.dumps({"ok":True,"project":str(project),"run_dir":str(outdir),"captioned":str(captioned),"preview":str(preview),"contact_sheet":str(sheet)}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
