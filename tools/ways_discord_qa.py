#!/usr/bin/env python3
"""Discord-first WAYS QA decision helpers.

The WAYS human gates live in Discord. This module provides a tiny, testable
contract for the two interaction modes we can safely support without relying on
Discord message components:

1. Build concise review cards/prompts that can be pasted/sent to Discord.
2. Parse Josh's Discord replies into the same persisted decision schema used by
   the review dashboard server.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS = ROOT / "dashboard" / "review_decisions.json"
DEFAULT_OUTBOX = ROOT / "ops" / "ways-video-lab-discord" / "discord_qa_outbox.md"
DEFAULT_MEDIA_DIR = ROOT / "ops" / "ways-video-lab-discord" / "discord_media"
DISCORD_MAX_BYTES = 24 * 1024 * 1024

REVIEW_THREAD_ID = "1512650920373256232"
QA_CHANNEL_ID = "1512649734769348690"

FINAL_ACTIONS = {
    "approve-private",
    "approve-public-quality",
    "reject-rework",
}
PUBLISH_ACTIONS = {"authorize-public-publish", "keep-private"}
PLATE_ACTIONS = {"approve-plate", "deny-plate"}
ALLOWED_ACTIONS = FINAL_ACTIONS | PUBLISH_ACTIONS | PLATE_ACTIONS
LANES = {"wan_i2v", "motion_graphic", "still_motion", "regenerate", "hold"}

ACTION_ALIASES = {
    "private": "approve-private",
    "approve-private": "approve-private",
    "draft": "approve-private",
    "9": "approve-public-quality",
    "9+": "approve-public-quality",
    "public-quality": "approve-public-quality",
    "approve-public-quality": "approve-public-quality",
    "reject": "reject-rework",
    "rework": "reject-rework",
    "reject-rework": "reject-rework",
    "publish": "authorize-public-publish",
    "authorize-public-publish": "authorize-public-publish",
    "keep-private": "keep-private",
    "hold": "keep-private",
    "approve-plate": "approve-plate",
    "plate-approve": "approve-plate",
    "deny-plate": "deny-plate",
    "plate-deny": "deny-plate",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "unknown"


def resolve_artifact_path(value: Any, card: dict[str, Any]) -> Path | None:
    """Resolve a QC-card artifact path to a local filesystem path."""
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    path = Path(raw)
    if path.is_absolute():
        return path if path.exists() else None
    candidates = [ROOT / raw]
    artifact_folder = card.get("artifact_folder")
    if isinstance(artifact_folder, str) and artifact_folder.strip():
        candidates.append(ROOT / artifact_folder.strip().strip("/") / raw)
    slug = card.get("slug") or card.get("id")
    if isinstance(slug, str) and slug.strip():
        candidates.append(ROOT / "test_cases" / slug / raw)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _run_ffmpeg(cmd: list[str]) -> bool:
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def prepare_discord_media(path: Path, slug: str, media_dir: Path = DEFAULT_MEDIA_DIR) -> Path | None:
    """Create a Discord-safe, downscaled copy and return its path.

    WAYS review cards must work when Josh is away from the workstation, so the
    outbox includes native Discord attachments instead of local-only paths.
    """
    if not path.exists() or not path.is_file():
        return None
    media_dir = media_dir / _safe_slug(slug)
    media_dir.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    stem = _safe_slug(path.stem)
    if suffix in {".mp4", ".mov", ".m4v", ".webm"}:
        out = media_dir / f"{stem}_discord_720p.mp4"
        ok = _run_ffmpeg([
            "ffmpeg", "-y", "-i", str(path),
            "-vf", "scale='min(720,iw)':-2:flags=lanczos",
            "-c:v", "libx264", "-preset", "medium", "-crf", "25",
            "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "3.1",
            "-c:a", "aac", "-b:a", "96k", "-ar", "48000",
            "-movflags", "+faststart", str(out),
        ])
        if ok and out.exists() and out.stat().st_size <= DISCORD_MAX_BYTES:
            return out
        tiny = media_dir / f"{stem}_discord_540p.mp4"
        ok = _run_ffmpeg([
            "ffmpeg", "-y", "-i", str(path),
            "-vf", "scale='min(540,iw)':-2:flags=lanczos",
            "-c:v", "libx264", "-preset", "medium", "-crf", "30",
            "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "3.1",
            "-c:a", "aac", "-b:a", "64k", "-ar", "48000",
            "-movflags", "+faststart", str(tiny),
        ])
        return tiny if ok and tiny.exists() and tiny.stat().st_size <= DISCORD_MAX_BYTES else None
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        out = media_dir / f"{stem}_discord.jpg"
        ok = _run_ffmpeg([
            "ffmpeg", "-y", "-i", str(path), "-frames:v", "1", "-update", "1",
            "-vf", "scale='min(1600,iw)':-2:flags=lanczos", "-q:v", "4", str(out),
        ])
        return out if ok and out.exists() and out.stat().st_size <= DISCORD_MAX_BYTES else None
    return None


def collect_discord_media(card: dict[str, Any], limit: int = 4) -> list[Path]:
    slug = str(card.get("slug") or card.get("id") or "unknown")
    candidates: list[Any] = []
    candidates.extend([card.get("contact_sheet"), card.get("latest_internal_candidate")])
    outputs = card.get("outputs") or {}
    if isinstance(outputs, dict):
        candidates.extend([
            outputs.get("contact_sheet"),
            outputs.get("discord_preview_captioned"),
            outputs.get("publish_candidate_captioned"),
            outputs.get("thumbnail_candidate"),
        ])
    elif isinstance(outputs, list):
        candidates.extend(outputs)

    prepared: list[Path] = []
    seen: set[Path] = set()
    for value in candidates:
        original = resolve_artifact_path(value, card)
        if not original:
            continue
        if original.suffix.lower() in {".mp4", ".mov", ".m4v"}:
            sibling_preview = original.parent / "discord_preview_captioned.mp4"
            if sibling_preview.exists():
                original = sibling_preview
        safe = prepare_discord_media(original, slug)
        if safe and safe not in seen:
            prepared.append(safe)
            seen.add(safe)
        if len(prepared) >= limit:
            break
    return prepared


def _token_value(text: str, key: str) -> str:
    # Accept key=value, key:"quoted text", and key='quoted text'.
    pattern = rf"(?:^|\s){re.escape(key)}\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s]+))"
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if not m:
        return ""
    return next((g for g in m.groups() if g is not None), "").strip()


def _strip_token(text: str, key: str) -> str:
    pattern = rf"(?:^|\s){re.escape(key)}\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s]+)"
    return re.sub(pattern, " ", text, flags=re.IGNORECASE).strip()


def normalize_action(raw: str) -> str:
    action = ACTION_ALIASES.get(raw.strip().lower(), raw.strip().lower())
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"unknown WAYS QA action: {raw}")
    return action


def parse_discord_qa_reply(text: str, reviewer: str = "Josh") -> dict[str, Any]:
    """Parse a Discord reply into a normalized decision payload.

    Accepted forms:
      WAYSQA sharks_older_than_trees approve-private score=8.5 notes="good private draft"
      QA shot03 approve-plate lane=wan_i2v score=9 notes="clean silhouette"
      QA sharks publish notes="go public today"
    """
    raw = text.strip()
    m = re.match(r"^(?:WAYSQA|QA)\s+(\S+)\s+(\S+)(.*)$", raw, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        raise ValueError("expected: QA <slug-or-plate-id> <action> [score=] [lane=] [notes=]")
    slug, raw_action, rest = m.groups()
    action = normalize_action(raw_action)
    score = _token_value(rest, "score")
    lane = _token_value(rest, "lane")
    notes = _token_value(rest, "notes")
    if not notes:
        # Anything after removing known tokens becomes freeform notes.
        tail = _strip_token(_strip_token(rest, "score"), "lane").strip()
        notes = tail
    if lane and lane not in LANES:
        raise ValueError(f"unknown WAYS lane: {lane}")
    if action == "approve-plate" and lane not in {"wan_i2v", "motion_graphic", "still_motion"}:
        raise ValueError("approve-plate requires lane=wan_i2v|motion_graphic|still_motion")
    if action == "deny-plate" and not lane:
        lane = "regenerate"
    return {
        "slug": slug,
        "action": action,
        "score": score,
        "notes": notes,
        "reviewer": reviewer,
        "source": "discord",
        "discord_thread_id": REVIEW_THREAD_ID,
        "confirmed_lane": lane,
    }


def decision_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    slug = str(payload.get("slug") or "").strip()
    action = normalize_action(str(payload.get("action") or ""))
    if not slug:
        raise ValueError("missing slug")
    reviewed_at = now_iso()
    gate = "Gate 5 final video review"
    if action in PUBLISH_ACTIONS:
        gate = "Gate 6 public publish authorization"
    elif action in PLATE_ACTIONS:
        gate = "Gate 2 human plate QC"

    explicit_authorization = None
    if action == "authorize-public-publish":
        explicit_authorization = f"Josh authorizes public publish for {slug} via Discord WAYS QA at {reviewed_at}"

    decision = {
        "schema_version": 2,
        "decision_id": f"{slug}:{action}",
        "slug": slug,
        "gate": gate,
        "action": action,
        "score": str(payload.get("score") or "").strip(),
        "notes": str(payload.get("notes") or "").strip(),
        "reviewer": str(payload.get("reviewer") or "Josh").strip() or "Josh",
        "reviewed_at": reviewed_at,
        "source": str(payload.get("source") or "dashboard"),
        "discord_thread_id": str(payload.get("discord_thread_id") or REVIEW_THREAD_ID),
        "explicit_public_publish_authorization": explicit_authorization,
        "requires_agent_followup": action in {"authorize-public-publish", "reject-rework", "approve-public-quality", "approve-plate", "deny-plate"},
    }
    lane = str(payload.get("confirmed_lane") or "").strip()
    if lane:
        if lane not in LANES:
            raise ValueError(f"unknown WAYS lane: {lane}")
        decision["confirmed_lane"] = lane
        if action in PLATE_ACTIONS:
            decision["vlm_was_advisory_only"] = True
    return decision


def persist_decision(decision: dict[str, Any], path: Path = DEFAULT_DECISIONS) -> dict[str, Any]:
    decisions = read_json(path, {"version": 1, "decisions": {}})
    decisions.setdefault("version", 1)
    decisions.setdefault("decisions", {})[decision["decision_id"]] = decision
    decisions["updated_at"] = decision["reviewed_at"]
    atomic_write_json(path, decisions)
    return decisions


def discord_command_for_review(slug: str, gate: str) -> str:
    if gate.startswith("Gate 2"):
        return f"QA {slug} approve-plate lane=wan_i2v score=9 notes=\"approved because ...\""
    if gate.startswith("Gate 6"):
        return f"QA {slug} publish notes=\"explicitly authorize public publish\""
    return f"QA {slug} approve-private score=8.5 notes=\"private draft OK because ...\""


def build_discord_prompt(card: dict[str, Any]) -> str:
    slug = str(card.get("slug") or card.get("id") or "unknown")
    gate = str(card.get("blocking_gate") or card.get("human_gate", {}).get("gate") or "Gate 5")
    topic = str(card.get("topic") or card.get("title") or slug)
    contact = card.get("contact_sheet") or ""
    outputs = card.get("outputs") or []
    if isinstance(outputs, dict):
        output_lines = [f"- `{k}`: `{v}`" for k, v in outputs.items() if v]
    else:
        output_lines = [f"- `{x}`" for x in outputs[:6]]
    media = collect_discord_media(card)
    media_lines = [f"- MEDIA:{p}" for p in media]
    cmd = discord_command_for_review(slug, gate)
    return "\n".join([
        f"## WAYS QA needed: {topic}",
        f"**Gate:** {gate}",
        f"**Slug:** `{slug}`",
        f"**Current blocker:** {card.get('rework_reason') or card.get('qa_blockers') or 'Human decision required.'}",
        f"**Contact sheet:** `{contact}`" if contact else "**Contact sheet:** missing",
        "**Discord-ready attachments:**",
        *(media_lines or ["- none prepared; do not send this card until media is attached or a blocker explains why"]),
        "**Local source paths, for audit only:**",
        *(output_lines or ["- none recorded"]),
        "",
        "Reply in this thread with one of these:",
        f"- `{cmd}`",
        f"- `QA {slug} reject notes=\"what failed and exact rework\"`",
        f"- `QA {slug} keep-private notes=\"hold reason\"`",
        "",
        "I will treat that Discord reply as the source of truth and persist it to `dashboard/review_decisions.json`.",
    ])


def _canonical_rank(card: dict[str, Any]) -> tuple[int, int, int]:
    slug = str(card.get("slug") or card.get("id") or "")
    source = str(card.get("source") or "")
    lane = str(card.get("model_lane") or "")
    partial_penalty = 1 if "partial" in slug or "partial" in source else 0
    unknown_penalty = 1 if "unknown" in lane.lower() else 0
    # Shorter slugs are usually the canonical video/run card rather than a nested helper manifest.
    return (partial_penalty, unknown_penalty, slug.count("/"))


def _dedupe_human_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for card in cards:
        gate = str(card.get("blocking_gate") or "")
        key = (
            str(card.get("topic") or card.get("title") or card.get("slug") or ""),
            gate,
            str(card.get("contact_sheet") or ""),
        )
        current = groups.get(key)
        if current is None or _canonical_rank(card) < _canonical_rank(current):
            groups[key] = card
    return sorted(groups.values(), key=lambda c: (str(c.get("blocking_gate") or ""), str(c.get("updated") or "")), reverse=True)


def build_outbox(report_path: Path, out_path: Path = DEFAULT_OUTBOX, limit: int = 8) -> list[dict[str, str]]:
    report = read_json(report_path, {})
    cards = report.get("cards") or []
    human_cards = _dedupe_human_cards([
        c for c in cards
        if str(c.get("blocking_gate") or "").startswith(("Gate 2", "Gate 5", "Gate 6"))
    ])[:limit]
    prompts = [{"slug": str(c.get("slug") or c.get("id")), "prompt": build_discord_prompt(c)} for c in human_cards]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    body = ["# WAYS Discord QA Outbox", "", f"Generated: {now_iso()}", "", f"Target thread: `{REVIEW_THREAD_ID}`", ""]
    for item in prompts:
        body.extend(["---", "", item["prompt"], ""])
    out_path.write_text("\n".join(body), encoding="utf-8")
    return prompts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WAYS Discord QA decision helper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_parse = sub.add_parser("parse", help="Parse and persist one Discord QA reply")
    p_parse.add_argument("text")
    p_parse.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    p_outbox = sub.add_parser("outbox", help="Build Discord prompt outbox from QC report")
    p_outbox.add_argument("--report", type=Path, required=True)
    p_outbox.add_argument("--out", type=Path, default=DEFAULT_OUTBOX)
    p_outbox.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)

    if args.cmd == "parse":
        payload = parse_discord_qa_reply(args.text)
        decision = decision_from_payload(payload)
        persist_decision(decision, args.decisions)
        print(json.dumps({"ok": True, "decision": decision, "decisions_path": str(args.decisions)}, indent=2))
        return 0
    if args.cmd == "outbox":
        prompts = build_outbox(args.report, args.out, args.limit)
        print(json.dumps({"ok": True, "count": len(prompts), "out": str(args.out)}, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
