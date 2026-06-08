#!/usr/bin/env python3
"""Publish a WAYS private YouTube draft only after Gate 6 authorization.

Default mode is verification/dry-run. Use --execute to actually switch privacy to
public. This script intentionally refuses to run without a matching
`authorize-public-publish` decision in dashboard/review_decisions.json.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path("/mnt/c/dev/curious-shorts")
TOKEN = Path.home() / ".hermes/youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
DEFAULT_DECISIONS = ROOT / "dashboard/review_decisions.json"
DEFAULT_OUT = ROOT / "ops/ways-video-lab-discord/public_publish_events.jsonl"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_authorization(decisions_path: Path, slug: str) -> dict[str, Any] | None:
    data = load_json(decisions_path)
    for decision in (data.get("decisions") or {}).values():
        if decision.get("slug") != slug:
            continue
        if decision.get("action") != "authorize-public-publish":
            continue
        if decision.get("explicit_public_publish_authorization"):
            return decision
    return None


def youtube_client():
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def verify_video(yt, video_id: str) -> dict[str, Any]:
    resp = yt.videos().list(part="snippet,status,processingDetails,contentDetails", id=video_id).execute()
    if not resp.get("items"):
        raise SystemExit(f"video not found: {video_id}")
    item = resp["items"][0]
    return {
        "video_id": item["id"],
        "title": item["snippet"].get("title"),
        "channelId": item["snippet"].get("channelId"),
        "channelTitle": item["snippet"].get("channelTitle"),
        "categoryId": item["snippet"].get("categoryId"),
        "privacyStatus": item["status"].get("privacyStatus"),
        "uploadStatus": item["status"].get("uploadStatus"),
        "selfDeclaredMadeForKids": item["status"].get("selfDeclaredMadeForKids"),
        "processingStatus": item.get("processingDetails", {}).get("processingStatus"),
        "definition": item.get("contentDetails", {}).get("definition"),
        "duration": item.get("contentDetails", {}).get("duration"),
        "caption": item.get("contentDetails", {}).get("caption"),
        "url": f"https://youtu.be/{item['id']}",
        "studio_url": f"https://studio.youtube.com/video/{item['id']}/edit",
    }


def preflight(info: dict[str, Any]) -> list[str]:
    problems = []
    if info.get("privacyStatus") not in {"private", "public"}:
        problems.append(f"unexpected privacyStatus={info.get('privacyStatus')}")
    if info.get("uploadStatus") != "processed":
        problems.append(f"uploadStatus must be processed, got {info.get('uploadStatus')}")
    if info.get("processingStatus") != "succeeded":
        problems.append(f"processingStatus must be succeeded, got {info.get('processingStatus')}")
    if info.get("categoryId") != "28":
        problems.append(f"categoryId must be 28, got {info.get('categoryId')}")
    if info.get("selfDeclaredMadeForKids") is not False:
        problems.append("selfDeclaredMadeForKids must be false")
    if info.get("caption") != "true":
        problems.append(f"caption should be true before public publish, got {info.get('caption')}")
    return problems


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate-checked WAYS public publish helper")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--video-id", required=True)
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--execute", action="store_true", help="Actually switch privacyStatus to public")
    args = parser.parse_args(argv)

    authorization = find_authorization(args.decisions, args.slug)
    if not authorization:
        raise SystemExit(f"blocked: no matching Gate 6 authorize-public-publish decision for slug={args.slug}")

    yt = youtube_client()
    before = verify_video(yt, args.video_id)
    problems = preflight(before)
    if problems:
        raise SystemExit("blocked preflight: " + "; ".join(problems))

    event = {
        "slug": args.slug,
        "video_id": args.video_id,
        "authorization": authorization,
        "before": before,
        "executed": bool(args.execute),
    }

    if args.execute and before.get("privacyStatus") != "public":
        yt.videos().update(part="status", body={
            "id": args.video_id,
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
                "embeddable": True,
                "publicStatsViewable": True,
            },
        }).execute()
        time.sleep(2)

    after = verify_video(yt, args.video_id)
    event["after"] = after
    append_event(args.out, event)
    print(json.dumps(event, indent=2, ensure_ascii=False))
    if args.execute and after.get("privacyStatus") != "public":
        raise SystemExit("publish attempted but verification did not return privacyStatus=public")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
