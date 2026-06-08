#!/usr/bin/env python3
"""Create a rough vertical Shorts timing prototype for Test Short 001.

This is intentionally not the final art pipeline. It makes a local placeholder
video with narration, readable captions, simple graphics, and timing markers so
we can judge pacing before spending GPU/paid generations.
"""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FRAMES = ASSETS / "rough_frames"
OUT = ROOT / "outputs"
for p in (ASSETS, FRAMES, OUT):
    p.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
FPS = 30
VOICE = "en-US-GuyNeural"  # local/free timing proxy, not final brand voice
PAUSE_BETWEEN_LINES = 0.45
SCRIPT = [
    ("Sharks were here before trees.", "BEFORE\nTREES"),
    ("Seriously.", "SERIOUSLY."),
    ("Before forests. Before apples. Before squirrels had anywhere to hide nuts.", "BEFORE\nFORESTS"),
    ("The first sharks showed up more than four hundred million years ago.", "400+ MILLION\nYEARS AGO"),
    ("Trees took their time. They didn’t really arrive until tens of millions of years later.", "TREES TOOK\nTHEIR TIME"),
    ("So when you look at a shark, you’re not just looking at an animal.", "NOT JUST\nAN ANIMAL"),
    ("You’re looking at a survivor from a world before forests.", "A WORLD\nBEFORE\nFORESTS"),
]


def font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def gradient_bg(c1, c2):
    img = Image.new("RGB", (W, H), c1)
    pix = img.load()
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
        for x in range(W):
            pix[x, y] = col
    return img


def draw_shark(draw, cx, cy, scale=1.0, fill=(15, 45, 65)):
    pts = [
        (cx - 260*scale, cy), (cx - 120*scale, cy - 90*scale), (cx + 170*scale, cy - 55*scale),
        (cx + 300*scale, cy), (cx + 170*scale, cy + 55*scale), (cx - 120*scale, cy + 90*scale),
    ]
    draw.polygon(pts, fill=fill)
    draw.polygon([(cx - 80*scale, cy - 65*scale), (cx - 20*scale, cy - 210*scale), (cx + 35*scale, cy - 50*scale)], fill=fill)
    draw.polygon([(cx - 260*scale, cy), (cx - 390*scale, cy - 95*scale), (cx - 350*scale, cy), (cx - 390*scale, cy + 95*scale)], fill=fill)
    draw.ellipse((cx + 200*scale, cy - 20*scale, cx + 225*scale, cy + 5*scale), fill=(230, 250, 255))


def draw_tree(draw, x, y, scale=1.0):
    draw.rectangle((x - 28*scale, y - 220*scale, x + 28*scale, y), fill=(91, 59, 35))
    for dx, dy, r in [(-80,-250,110),(0,-310,130),(90,-245,105),(-5,-185,115)]:
        draw.ellipse((x+dx*scale-r*scale, y+dy*scale-r*scale, x+dx*scale+r*scale, y+dy*scale+r*scale), fill=(40, 130, 82))


def draw_slide(idx: int, headline: str, narration: str, duration: float):
    palettes = [
        ((7, 57, 78), (12, 119, 132)),
        ((5, 39, 64), (12, 103, 126)),
        ((1, 35, 56), (15, 87, 109)),
        ((16, 61, 65), (69, 126, 77)),
        ((4, 48, 72), (93, 111, 72)),
        ((6, 48, 66), (42, 102, 91)),
    ]
    img = gradient_bg(*palettes[idx % len(palettes)])
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-250, 150, 800, 1200), fill=(74, 210, 220, 45))
    gd.ellipse((500, 850, 1350, 1900), fill=(170, 235, 132, 35))
    img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(70))).convert("RGB")
    draw = ImageDraw.Draw(img)

    if idx in [0,1,2,4,5]:
        draw_shark(draw, 560 if idx != 0 else 360, 1050 if idx != 5 else 950, 0.9 if idx != 5 else 1.05, fill=(10, 46, 62))
    if idx in [0,3,5]:
        draw_tree(draw, 780 if idx != 5 else 260, 1280 if idx != 3 else 1320, 1.0 if idx != 3 else 0.8)
    if idx == 3:
        y = 1040
        draw.line((140,y,940,y), fill=(232, 248, 230), width=10)
        draw.ellipse((245,y-35,315,y+35), fill=(82,206,226))
        draw.ellipse((705,y-35,775,y+35), fill=(124,218,130))
        small = font(38, True)
        draw.text((210,y+65), "SHARKS", fill="white", font=small)
        draw.text((685,y+65), "TREES", fill="white", font=small)

    title_font = font(94 if idx != 5 else 76, True)
    lines = headline.split("\n")
    y = 170
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font, stroke_width=3)
        x = (W - (bbox[2]-bbox[0]))//2
        draw.text((x, y), line, font=title_font, fill=(255,255,244), stroke_width=4, stroke_fill=(2,26,38))
        y += int((bbox[3]-bbox[1]) * 1.15) + 18

    cap_font = font(42, False)
    cap_lines = wrap_text(draw, narration, cap_font, 900)
    box_h = 70 + len(cap_lines)*58
    draw.rounded_rectangle((70, H-box_h-90, W-70, H-90), radius=32, fill=(0, 20, 30), outline=(235,255,240), width=2)
    yy = H-box_h-55
    for line in cap_lines:
        bbox = draw.textbbox((0,0), line, font=cap_font)
        draw.text(((W-(bbox[2]-bbox[0]))//2, yy), line, font=cap_font, fill=(245,255,248))
        yy += 58

    mini = font(28, False)
    draw.text((40, 40), f"Rough timing slide {idx+1}/6 • {duration:.1f}s", font=mini, fill=(220,245,245))
    return img


async def make_line_voice(i: int, text: str):
    out = ASSETS / f"rough_voice_line_{i+1:02d}.mp3"
    communicate = edge_tts.Communicate(text, VOICE, rate="-18%")
    await communicate.save(str(out))
    return out


def run(cmd):
    print("$", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True)


def probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True).strip()
    return float(out)


def make_voice_and_durations():
    line_files = []
    durations = []
    for i, (text, _) in enumerate(SCRIPT):
        lf = asyncio.run(make_line_voice(i, text))
        line_files.append(lf)
        durations.append(probe_duration(lf) + PAUSE_BETWEEN_LINES)

    silence = ASSETS / "pause.wav"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", "-t", str(PAUSE_BETWEEN_LINES), silence])
    concat = ASSETS / "audio_concat.txt"
    lines = []
    for lf in line_files:
        lines.append(f"file '{lf}'\n")
        lines.append(f"file '{silence}'\n")
    concat.write_text("".join(lines), encoding="utf-8")
    voice = ASSETS / "rough_voice_edge_tts_timed.mp3"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c:a", "libmp3lame", "-ar", "24000", "-ac", "1", voice])
    return voice, durations


def main():
    (ROOT / "script.txt").write_text("\n\n".join([s[0] for s in SCRIPT]), encoding="utf-8")
    voice, durations = make_voice_and_durations()

    slide_paths = []
    concat_lines = []
    for i, ((narration, headline), duration) in enumerate(zip(SCRIPT, durations)):
        img = draw_slide(i, headline, narration, duration)
        p = FRAMES / f"slide_{i+1:02d}.png"
        img.save(p)
        slide_paths.append(p)
        concat_lines.append(f"file '{p}'\n")
        concat_lines.append(f"duration {duration:.3f}\n")
    concat_lines.append(f"file '{slide_paths[-1]}'\n")
    concat_file = ASSETS / "rough_concat.txt"
    concat_file.write_text("".join(concat_lines), encoding="utf-8")

    silent_video = OUT / "rough_visuals.mp4"
    final = OUT / "sharks_older_than_trees_rough_cut.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-movflags", "+faststart", silent_video])
    run(["ffmpeg", "-y", "-i", silent_video, "-i", voice, "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", final])

    meta = {
        "final": str(final),
        "final_duration_sec": probe_duration(final),
        "voice": str(voice),
        "voice_duration_sec": probe_duration(voice),
        "slides": [str(p) for p in slide_paths],
        "slide_durations_sec": durations,
        "voice_proxy": VOICE,
        "note": "Rough local timing prototype only; replace art and voice for final benchmark."
    }
    (OUT / "rough_cut_manifest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
