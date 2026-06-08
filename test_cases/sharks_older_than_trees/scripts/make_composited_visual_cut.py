#!/usr/bin/env python3
"""Create a better local visual storyboard cut using Roger VO.

This is a fallback/prototype visual pass: composited 9:16 stills with custom
illustration layers, captions, and Ken Burns movement. It does not require a
running image model, so it can unblock pacing/visual-direction review while the
AI still-generation lane is configured.
"""
from __future__ import annotations

import json
import math
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ROOT / "outputs"
STILLS = ASSETS / "generated_stills_v1"
FRAMES = ASSETS / "composited_frames_v1"
for p in (STILLS, FRAMES, OUT):
    p.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
FPS = 30
VOICE = OUT / "voice_auditions" / "01_warm_older_brother_uncle.mp3"
FINAL = OUT / "sharks_older_than_trees_roger_visual_v1.mp4"

SHOTS = [
    {
        "id": "shot_01_hook",
        "headline": "SHARKS WERE HERE\nBEFORE TREES",
        "caption": "Sharks were here before trees. Seriously.",
        "kind": "hook",
    },
    {
        "id": "shot_02_before_forests",
        "headline": "BEFORE FORESTS",
        "caption": "Before forests. Before apples. Before squirrels had anywhere to hide nuts.",
        "kind": "ocean_dive",
    },
    {
        "id": "shot_03_400m",
        "headline": "400+ MILLION\nYEARS AGO",
        "caption": "The first sharks showed up more than four hundred million years ago.",
        "kind": "ancient_shark",
    },
    {
        "id": "shot_04_trees_later",
        "headline": "TREES TOOK\nTHEIR TIME",
        "caption": "Trees took their time. They didn’t really arrive until tens of millions of years later.",
        "kind": "timeline",
    },
    {
        "id": "shot_05_not_animal",
        "headline": "NOT JUST\nAN ANIMAL",
        "caption": "So when you look at a shark, you’re not just looking at an animal.",
        "kind": "split_world",
    },
    {
        "id": "shot_06_survivor",
        "headline": "A WORLD\nBEFORE FORESTS",
        "caption": "You’re looking at a survivor from a world before forests.",
        "kind": "survivor",
    },
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


def run(cmd):
    subprocess.run([str(x) for x in cmd], check=True)


def probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True).strip()
    return float(out)


def gradient(top, bottom):
    img = Image.new("RGB", (W, H), top)
    pix = img.load()
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(W):
            pix[x, y] = col
    return img.convert("RGBA")


def add_light(img, seed=0):
    random.seed(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # soft sun bloom
    d.ellipse((120, -180, 970, 650), fill=(145, 235, 218, 52))
    d.ellipse((-260, 500, 520, 1560), fill=(55, 190, 210, 34))
    d.ellipse((560, 800, 1400, 2100), fill=(180, 235, 135, 28))
    layer = layer.filter(ImageFilter.GaussianBlur(70))
    img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    # water particles
    for _ in range(130):
        x = random.randint(20, W - 20)
        y = random.randint(200, H - 80)
        r = random.choice([1, 1, 2, 2, 3])
        a = random.randint(18, 70)
        d.ellipse((x-r, y-r, x+r, y+r), fill=(210, 255, 245, a))
    # light rays
    ray = Image.new("RGBA", (W, H), (0,0,0,0))
    rd = ImageDraw.Draw(ray)
    for x in [-80, 130, 340, 620, 890]:
        rd.polygon([(x,0), (x+90,0), (x+430,H)], fill=(210,255,235,18))
    img.alpha_composite(ray.filter(ImageFilter.GaussianBlur(15)))


def draw_shark(d, cx, cy, scale=1.0, fill=(9, 43, 58, 235), glow=True):
    if glow:
        # fake glow by drawing translucent bigger silhouette behind
        pts_g = [(cx - 285*scale, cy), (cx - 135*scale, cy - 105*scale), (cx + 185*scale, cy - 65*scale), (cx + 325*scale, cy), (cx + 185*scale, cy + 65*scale), (cx - 135*scale, cy + 105*scale)]
        d.polygon(pts_g, fill=(120, 230, 230, 32))
    pts = [
        (cx - 260*scale, cy), (cx - 120*scale, cy - 88*scale), (cx + 170*scale, cy - 54*scale),
        (cx + 300*scale, cy), (cx + 170*scale, cy + 54*scale), (cx - 120*scale, cy + 88*scale),
    ]
    d.polygon(pts, fill=fill)
    d.polygon([(cx - 80*scale, cy - 62*scale), (cx - 15*scale, cy - 205*scale), (cx + 42*scale, cy - 48*scale)], fill=fill)
    d.polygon([(cx - 245*scale, cy), (cx - 390*scale, cy - 98*scale), (cx - 348*scale, cy), (cx - 390*scale, cy + 98*scale)], fill=fill)
    d.ellipse((cx + 205*scale, cy - 16*scale, cx + 224*scale, cy + 3*scale), fill=(220, 248, 255, 210))
    # soft belly line
    d.arc((cx - 125*scale, cy - 45*scale, cx + 205*scale, cy + 80*scale), 5, 168, fill=(170, 220, 220, 72), width=max(2,int(4*scale)))


def draw_tree(d, x, y, scale=1.0, alpha=220):
    trunk = (92, 64, 41, alpha)
    leaf = (48, 132, 82, alpha)
    d.rounded_rectangle((x-30*scale, y-240*scale, x+30*scale, y), radius=12, fill=trunk)
    for dx, dy, r in [(-82,-270,110),(0,-340,140),(95,-270,112),(-6,-205,125)]:
        d.ellipse((x+dx*scale-r*scale, y+dy*scale-r*scale, x+dx*scale+r*scale, y+dy*scale+r*scale), fill=leaf)


def draw_early_plants(d):
    for x in [120, 210, 720, 830, 930]:
        base = 1290 + (x % 3) * 22
        d.line((x, base, x+18, base-92), fill=(112, 179, 100, 220), width=8)
        d.line((x+16, base-55, x+58, base-88), fill=(112, 179, 100, 180), width=5)
        d.line((x+10, base-38, x-30, base-70), fill=(112, 179, 100, 180), width=5)


def wrap_text(d, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textbbox((0,0), t, font=fnt)[2] <= max_width:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def add_text(img, headline, caption):
    d = ImageDraw.Draw(img)
    title = font(82 if len(headline) < 22 else 72, True)
    y = 150
    for line in headline.split("\n"):
        bbox = d.textbbox((0,0), line, font=title, stroke_width=3)
        x = (W - (bbox[2]-bbox[0])) // 2
        d.text((x, y), line, font=title, fill=(255, 255, 238, 255), stroke_width=5, stroke_fill=(2, 26, 36, 235))
        y += int((bbox[3]-bbox[1]) * 1.18) + 18
    cap_font = font(40, False)
    lines = wrap_text(d, caption, cap_font, 890)
    box_h = 70 + len(lines) * 56
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((65, H-box_h-90, W-65, H-90), radius=32, fill=(0, 20, 29, 210), outline=(232, 255, 238, 90), width=2)
    img.alpha_composite(overlay)
    yy = H - box_h - 55
    for line in lines:
        bbox = d.textbbox((0,0), line, font=cap_font)
        d.text(((W-(bbox[2]-bbox[0]))//2, yy), line, font=cap_font, fill=(246,255,248,255))
        yy += 56


def make_still(shot, idx):
    kind = shot["kind"]
    if kind in ("timeline", "split_world"):
        img = gradient((12, 65, 74), (85, 112, 67))
    else:
        img = gradient((3, 33, 55), (10, 107, 121))
    add_light(img, idx + 7)
    d = ImageDraw.Draw(img)

    if kind == "hook":
        draw_shark(d, 365, 1045, 0.93)
        draw_tree(d, 790, 1320, 1.05, 205)
        d.line((540, 720, 540, 1430), fill=(245,255,235,35), width=3)
    elif kind == "ocean_dive":
        draw_shark(d, 660, 1130, 0.65, fill=(7, 46, 64, 185))
        d.ellipse((120, 760, 980, 1450), outline=(205,255,245,35), width=5)
    elif kind == "ancient_shark":
        draw_shark(d, 540, 1030, 1.22)
        for x in [130, 220, 885]:
            d.arc((x, 1220, x+130, 1320), 200, 340, fill=(130, 215, 190, 110), width=5)
    elif kind == "timeline":
        y = 1040
        d.rounded_rectangle((130, y-10, 950, y+10), radius=8, fill=(232, 248, 230, 230))
        d.ellipse((230, y-50, 330, y+50), fill=(70, 200, 226, 255))
        draw_shark(d, 280, y-170, 0.32, fill=(4, 50, 65, 210), glow=False)
        d.ellipse((720, y-50, 820, y+50), fill=(108, 205, 104, 255))
        draw_tree(d, 770, y-120, 0.42, 230)
        small = font(38, True)
        d.text((190, y+88), "SHARKS", font=small, fill=(255,255,245,255))
        d.text((700, y+88), "TREES", font=small, fill=(255,255,245,255))
        d.text((215, y-115), "FIRST", font=font(28, True), fill=(230,255,250,220))
        d.text((690, y-115), "LATER", font=font(28, True), fill=(230,255,250,220))
    elif kind == "split_world":
        # water below, barren land above
        land = Image.new("RGBA", (W,H), (0,0,0,0))
        ld = ImageDraw.Draw(land)
        ld.polygon([(0,1020),(W,890),(W,1360),(0,1460)], fill=(110, 93, 64, 205))
        ld.polygon([(0,1035),(W,900),(W,975),(0,1110)], fill=(185, 160, 105, 95))
        img.alpha_composite(land)
        draw_shark(d, 535, 1420, 0.74, fill=(5, 44, 62, 210))
        draw_early_plants(d)
    elif kind == "survivor":
        draw_shark(d, 560, 1045, 1.12)
        # ghost future forest
        ghost = Image.new("RGBA", (W,H), (0,0,0,0))
        gd = ImageDraw.Draw(ghost)
        draw_tree(gd, 230, 1420, 0.75, 72)
        draw_tree(gd, 850, 1375, 0.88, 62)
        img.alpha_composite(ghost.filter(ImageFilter.GaussianBlur(1.5)))
    add_text(img, shot["headline"], shot["caption"])
    out = STILLS / f"{idx+1:02d}_{shot['id']}.png"
    img.convert("RGB").save(out, quality=95)
    return out


def make_video_from_stills(still_paths, durations):
    # Generate motion frames in Python: subtle zoom + pan, avoids complex ffmpeg graph escaping.
    frame_count = 0
    # clear old frames
    for old in FRAMES.glob("frame_*.jpg"):
        old.unlink()
    for i, (p, dur) in enumerate(zip(still_paths, durations)):
        base = Image.open(p).convert("RGB")
        n = max(1, int(round(dur * FPS)))
        for j in range(n):
            t = j / max(1, n - 1)
            ease = 0.5 - 0.5 * math.cos(math.pi * t)
            zoom = 1.035 + 0.045 * ease
            zw, zh = int(W / zoom), int(H / zoom)
            # Alternate pan directions, keep crop inside image.
            max_x, max_y = W - zw, H - zh
            if i % 2 == 0:
                x = int(max_x * ease)
                y = int(max_y * 0.35 * ease)
            else:
                x = int(max_x * (1 - ease))
                y = int(max_y * 0.65 * ease)
            crop = base.crop((x, y, x + zw, y + zh)).resize((W, H), Image.Resampling.LANCZOS)
            # tiny fade in/out per shot
            fade = min(1.0, j / max(1, FPS * 0.18), (n - 1 - j) / max(1, FPS * 0.18))
            if fade < 1:
                black = Image.new("RGB", (W,H), (1, 15, 23))
                crop = Image.blend(black, crop, fade)
            crop.save(FRAMES / f"frame_{frame_count:05d}.jpg", quality=91, optimize=False)
            frame_count += 1
    silent = OUT / "visual_v1_silent.mp4"
    run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "frame_%05d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", silent])
    run(["ffmpeg", "-y", "-i", silent, "-i", VOICE, "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", FINAL])
    return FINAL, silent, frame_count


def main():
    voice_dur = probe_duration(VOICE)
    selected_manifest = OUT / "selected_voice_manifest.json"
    old = json.loads(selected_manifest.read_text()) if selected_manifest.exists() else {}
    slide7 = old.get("slide_durations_sec") or [2.245, 1.683, 5.56, 3.384, 4.753, 3.341, 3.139]
    # 6 shots: combine first line and "Seriously" into hook shot.
    durations = [slide7[0] + slide7[1], slide7[2], slide7[3], slide7[4], slide7[5], slide7[6]]
    target = voice_dur + 0.20
    scale = target / sum(durations)
    durations = [d * scale for d in durations]
    stills = [make_still(shot, i) for i, shot in enumerate(SHOTS)]
    final, silent, frames = make_video_from_stills(stills, durations)
    meta = {
        "status": "success",
        "type": "local_composited_visual_storyboard",
        "note": "Fallback/prototype visual pass using custom generated illustration layers; not AI model still generation.",
        "selected_voice": "Roger - Laid-Back, Casual, Resonant",
        "voice_file": str(VOICE),
        "voice_duration_sec": round(voice_dur, 3),
        "final": str(final),
        "final_duration_sec": round(probe_duration(final), 3),
        "silent_video": str(silent),
        "stills": [str(p) for p in stills],
        "shot_durations_sec": [round(d, 3) for d in durations],
        "frames_rendered": frames,
        "fps": FPS,
        "resolution": f"{W}x{H}",
    }
    (OUT / "visual_v1_manifest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
