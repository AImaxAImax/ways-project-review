#!/usr/bin/env python3
"""WAYS publish/status follow-up helpers.

This tool is deliberately publish-safe by default. It writes draft upload packs,
validates public-publish requests against the WAYS human gates, proposes scheduled
cadence, and records 48-72h performance reviews. It does not call the YouTube API.

Gate defaults come from ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md:
- YouTube draft category is 28 (Science & Technology).
- selfDeclaredMadeForKids is false (kid-friendly/general audience, not made for kids).
- Public publish requires explicit Josh authorization.
- Small backlog cadence is one public video/day; once the 50-buffer exists, at most
  two/day, spaced apart.
- Performance reviews map retention/swipe-away to a storyboard beat/shot and may
  promote class-level lessons into a production SKILL.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path
from typing import Any

DEFAULT_CATEGORY_ID = "28"
DEFAULT_MADE_FOR_KIDS = False
DEFAULT_PRIVACY = "private"
PUBLIC_AUTH_RE = re.compile(r"\bJosh\b.*\b(authorizes|authorized|approves|approved)\b.*\b(public|publish)\b", re.I)
MIN_TWO_PER_DAY_SPACING_HOURS = 6
BUFFER_THRESHOLD_FOR_TWO_PER_DAY = 50
RESERVE_WARNING_THRESHOLD = 5


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def require_path(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.exists():
        raise SystemExit(f"missing {label}: {resolved}")
    return resolved


def normalize_tags(tags: str | list[str] | None) -> list[str]:
    if tags is None:
        return []
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if str(t).strip()]
    return [t.strip() for t in tags.split(",") if t.strip()]


def build_youtube_metadata(
    *,
    title: str,
    description_file: Path,
    video: Path,
    captions_srt: Path | None = None,
    thumbnail_candidate: Path | None = None,
    tags: list[str] | None = None,
    category_id: str = DEFAULT_CATEGORY_ID,
    privacy_status: str = DEFAULT_PRIVACY,
    self_declared_made_for_kids: bool = DEFAULT_MADE_FOR_KIDS,
) -> dict[str, Any]:
    if privacy_status != "private":
        raise ValueError("draft upload pack must default to privacyStatus='private'; public publish is a separate human-authorized action")
    if str(category_id) != DEFAULT_CATEGORY_ID:
        raise ValueError("WAYS draft upload pack categoryId must default to '28' (Science & Technology)")
    if bool(self_declared_made_for_kids) is not DEFAULT_MADE_FOR_KIDS:
        raise ValueError("WAYS drafts must set selfDeclaredMadeForKids=false")
    metadata = {
        "title": title,
        "description_file": str(description_file.resolve()),
        "tags": tags or [],
        "categoryId": DEFAULT_CATEGORY_ID,
        "privacyStatus": DEFAULT_PRIVACY,
        "selfDeclaredMadeForKids": DEFAULT_MADE_FOR_KIDS,
        "audience_note": "Kid-friendly/general audience, not made for kids.",
        "video": str(video.resolve()),
    }
    if captions_srt:
        metadata["captions_srt"] = str(captions_srt.resolve())
    if thumbnail_candidate:
        metadata["thumbnail_candidate"] = str(thumbnail_candidate.resolve())
    return metadata


def write_draft_pack(
    *,
    outdir: Path,
    title: str,
    description_file: Path,
    video: Path,
    captions_srt: Path | None,
    thumbnail_candidate: Path | None,
    tags: list[str],
) -> dict[str, Any]:
    outdir = outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    description_file = require_path(description_file, "description file")
    video = require_path(video, "video")
    captions_srt = require_path(captions_srt, "captions_srt") if captions_srt else None
    thumbnail_candidate = require_path(thumbnail_candidate, "thumbnail_candidate") if thumbnail_candidate else None

    metadata = build_youtube_metadata(
        title=title,
        description_file=description_file,
        video=video,
        captions_srt=captions_srt,
        thumbnail_candidate=thumbnail_candidate,
        tags=tags,
    )
    write_json(outdir / "youtube_metadata.json", metadata)
    shutil.copy2(description_file, outdir / "description_upload.txt")
    if thumbnail_candidate:
        # Preserve the source extension so upload scripts can infer media type.
        shutil.copy2(thumbnail_candidate, outdir / f"thumbnail_candidate{thumbnail_candidate.suffix.lower()}")

    status = {
        "created_at": utc_now_iso(),
        "status": "private_draft_pack_ready",
        "public_publish_gate": "blocked_until_explicit_josh_authorization",
        "required_defaults": {
            "categoryId": DEFAULT_CATEGORY_ID,
            "privacyStatus": DEFAULT_PRIVACY,
            "selfDeclaredMadeForKids": DEFAULT_MADE_FOR_KIDS,
        },
        "next_steps": [
            "Upload only as private draft.",
            "Verify categoryId=28, privacyStatus=private, and selfDeclaredMadeForKids=false after upload.",
            "Do not set public/scheduled without a Josh authorization record.",
        ],
    }
    write_json(outdir / "publish_status.json", status)
    return {"outdir": str(outdir), "metadata": metadata, "status": status}


def validate_public_authorization(authorization: str | None) -> dict[str, Any]:
    text = (authorization or "").strip()
    authorized = bool(text and PUBLIC_AUTH_RE.search(text))
    return {
        "authorized": authorized,
        "authorization_text": text,
        "required_pattern": "Josh authorizes/approves public publish",
        "reason": None if authorized else "public publish requires explicit Josh authorization; keep video private draft",
    }


def parse_hhmm(value: str) -> dt.time:
    hour, minute = (int(x) for x in value.split(":", 1))
    return dt.time(hour=hour, minute=minute, tzinfo=dt.timezone.utc)


def schedule_slots(
    *,
    start_date: dt.date,
    ready_buffer_count: int,
    count: int,
    morning_utc: str = "14:00",
    evening_utc: str = "23:00",
) -> dict[str, Any]:
    if count < 0:
        raise ValueError("count must be non-negative")
    daily_limit = 2 if ready_buffer_count >= BUFFER_THRESHOLD_FOR_TWO_PER_DAY else 1
    morning = parse_hhmm(morning_utc)
    evening = parse_hhmm(evening_utc)
    spacing = abs(dt.datetime.combine(start_date, evening) - dt.datetime.combine(start_date, morning))
    if daily_limit == 2 and spacing < dt.timedelta(hours=MIN_TWO_PER_DAY_SPACING_HOURS):
        raise ValueError(f"two/day cadence requires at least {MIN_TWO_PER_DAY_SPACING_HOURS}h spacing")

    slots: list[dict[str, str]] = []
    current = start_date
    while len(slots) < count:
        times = [morning] if daily_limit == 1 else [morning, evening]
        for t in times:
            if len(slots) >= count:
                break
            slots.append({
                "slot_number": str(len(slots) + 1),
                "publish_at_utc": dt.datetime.combine(current, t).isoformat().replace("+00:00", "Z"),
            })
        current += dt.timedelta(days=1)
    return {
        "ready_buffer_count": ready_buffer_count,
        "daily_limit": daily_limit,
        "rule": "1/day until ready buffer reaches 50; then max 2/day spaced",
        "reserve_warning": ready_buffer_count < RESERVE_WARNING_THRESHOLD,
        "slots": slots,
    }


def load_storyboard_segments(path: Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    data = load_json(require_path(path, "storyboard manifest"))
    raw = data.get("shots") or data.get("segments") or []
    t = 0.0
    segments = []
    for idx, item in enumerate(raw, 1):
        duration = float(item.get("duration") or 0.0)
        start = float(item.get("start", t))
        end = float(item.get("end", start + duration))
        segments.append({
            "index": idx,
            "shot_id": item.get("id") or item.get("shot_id") or f"shot{idx:02d}",
            "caption": item.get("caption") or item.get("beat") or "",
            "start": round(start, 3),
            "end": round(end, 3),
        })
        t = end
    return segments


def map_timestamp_to_segment(timestamp: float | None, segments: list[dict[str, Any]]) -> dict[str, Any] | None:
    if timestamp is None or not segments:
        return None
    for seg in segments:
        if float(seg["start"]) <= timestamp < float(seg["end"]):
            return seg
    return min(segments, key=lambda s: abs(float(s["start"]) - timestamp))


def append_skill_lesson(skill_path: Path, lesson: str, *, dry_run: bool = False) -> dict[str, Any]:
    marker = "\n## WAYS performance lessons\n"
    entry = f"- {utc_now_iso()}: {lesson.strip()}\n"
    if dry_run:
        return {"promoted": False, "dry_run": True, "skill_path": str(skill_path), "entry": entry.strip()}
    if not skill_path.exists():
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text("# WAYS production skill\n" + marker + entry, encoding="utf-8")
    else:
        text = skill_path.read_text(encoding="utf-8")
        if lesson.strip() in text:
            return {"promoted": False, "duplicate": True, "skill_path": str(skill_path)}
        if marker not in text:
            text = text.rstrip() + marker
        text = text.rstrip() + "\n" + entry
        skill_path.write_text(text, encoding="utf-8")
    return {"promoted": True, "skill_path": str(skill_path), "entry": entry.strip()}


def record_performance_review(
    *,
    outdir: Path,
    video_id: str,
    retention_pct_viewed: float,
    swipe_away_timestamp: float | None,
    storyboard_manifest: Path | None,
    lesson: str,
    class_level: bool,
    skill_path: Path | None,
    dry_run_skill: bool,
) -> dict[str, Any]:
    if not (0 <= retention_pct_viewed <= 1000):
        raise ValueError("retention_pct_viewed must be a percentage number")
    segments = load_storyboard_segments(storyboard_manifest)
    mapped = map_timestamp_to_segment(swipe_away_timestamp, segments)
    review = {
        "reviewed_at": utc_now_iso(),
        "video_id": video_id,
        "retention_pct_viewed": retention_pct_viewed,
        "swipe_away_timestamp": swipe_away_timestamp,
        "mapped_beat_or_shot": mapped,
        "lesson": lesson,
        "class_level_lesson": class_level,
    }
    if class_level:
        if not skill_path:
            raise ValueError("class-level lessons require --skill-path so they are not stranded in task logs")
        review["skill_promotion"] = append_skill_lesson(skill_path.resolve(), lesson, dry_run=dry_run_skill)

    outdir = outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    reviews_jsonl = outdir / "performance_reviews.jsonl"
    with reviews_jsonl.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(review) + "\n")
    write_json(outdir / f"performance_review_{video_id}.json", review)
    return {"review": review, "reviews_jsonl": str(reviews_jsonl)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WAYS publish and 48-72h performance review helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("draft-pack", help="write a private-draft YouTube upload pack")
    p.add_argument("--outdir", required=True, type=Path)
    p.add_argument("--title", required=True)
    p.add_argument("--description-file", required=True, type=Path)
    p.add_argument("--video", required=True, type=Path)
    p.add_argument("--captions-srt", type=Path)
    p.add_argument("--thumbnail-candidate", type=Path)
    p.add_argument("--tags", default="")

    p = sub.add_parser("authorize-public", help="validate human authorization text before public publish/scheduling")
    p.add_argument("--authorization", default="")

    p = sub.add_parser("schedule", help="propose publish slots under WAYS cadence rules")
    p.add_argument("--start-date", required=True, help="YYYY-MM-DD, UTC")
    p.add_argument("--ready-buffer-count", required=True, type=int)
    p.add_argument("--count", required=True, type=int)
    p.add_argument("--morning-utc", default="14:00")
    p.add_argument("--evening-utc", default="23:00")

    p = sub.add_parser("record-review", help="record a 48-72h performance review")
    p.add_argument("--outdir", required=True, type=Path)
    p.add_argument("--video-id", required=True)
    p.add_argument("--retention-pct-viewed", required=True, type=float)
    p.add_argument("--swipe-away-timestamp", type=float)
    p.add_argument("--storyboard-manifest", type=Path)
    p.add_argument("--lesson", required=True)
    p.add_argument("--class-level", action="store_true")
    p.add_argument("--skill-path", type=Path)
    p.add_argument("--dry-run-skill", action="store_true")

    args = parser.parse_args(argv)
    if args.cmd == "draft-pack":
        result = write_draft_pack(
            outdir=args.outdir,
            title=args.title,
            description_file=args.description_file,
            video=args.video,
            captions_srt=args.captions_srt,
            thumbnail_candidate=args.thumbnail_candidate,
            tags=normalize_tags(args.tags),
        )
    elif args.cmd == "authorize-public":
        result = validate_public_authorization(args.authorization)
    elif args.cmd == "schedule":
        result = schedule_slots(
            start_date=dt.date.fromisoformat(args.start_date),
            ready_buffer_count=args.ready_buffer_count,
            count=args.count,
            morning_utc=args.morning_utc,
            evening_utc=args.evening_utc,
        )
    elif args.cmd == "record-review":
        result = record_performance_review(
            outdir=args.outdir,
            video_id=args.video_id,
            retention_pct_viewed=args.retention_pct_viewed,
            swipe_away_timestamp=args.swipe_away_timestamp,
            storyboard_manifest=args.storyboard_manifest,
            lesson=args.lesson,
            class_level=args.class_level,
            skill_path=args.skill_path,
            dry_run_skill=args.dry_run_skill,
        )
    else:  # pragma: no cover
        raise AssertionError(args.cmd)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
