#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

TOKEN = Path.home() / ".hermes/youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
ROOT = Path("/mnt/c/dev/curious-shorts/test_cases/wood_frog_freeze_survival")
OUT = ROOT / "outputs/wan22_v17_elevenlabs_george"
PACK = OUT / "youtube_public_pack_v17_20260607"
VIDEO = OUT / "wood_frog_freeze_survival_v17_elevenlabs_george_captioned_1080.mp4"
CLEAN = OUT / "wood_frog_freeze_survival_v17_elevenlabs_george_clean_1080.mp4"
ASS = ROOT / "outputs/wan22_v16_final_vo/captions.ass"
SRT = PACK / "captions_v17.srt"
META = PACK / "youtube_metadata.json"
UPLOAD = PACK / "youtube_upload_result.json"
VERIFY = PACK / "youtube_verification.json"
PUBLIC_EVENT = PACK / "youtube_public_publish_event.json"
TITLE = "This Frog Can Freeze Solid #Shorts"
TAGS = [
    "Wait Are You Serious",
    "WAYS",
    "science",
    "facts",
    "Shorts",
    "wood frog",
    "frog facts",
    "animal facts",
    "biology",
    "survival chemistry",
]
DESCRIPTION = """This frog can freeze solid and wake back up.

Wood frogs survive winter by letting much of their body freeze while glucose-rich fluids help protect their cells until spring thaw.

#Shorts #science #facts #animals

Sources:
- Costanzo et al., Freeze tolerance in the wood frog, Journal of Experimental Biology.
- Storey & Storey, Freeze tolerance and glucose cryoprotection in amphibians.
"""
AUTHORIZATION_TEXT = "Josh said in Discord thread: Let's post it"


def stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def yt_client():
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def run(cmd: list[str]) -> str:
    proc = subprocess.run([str(c) for c in cmd], text=True, capture_output=True, check=True)
    return proc.stdout


def srt_time_from_ass(value: str) -> str:
    h, m, rest = value.split(":")
    sec, cs = rest.split(".")
    ms = int(cs.ljust(3, "0")[:3])
    return f"{int(h):02}:{int(m):02}:{int(sec):02},{ms:03}"


def ass_text_to_plain(text: str) -> str:
    text = re.sub(r"\{[^}]*\}", "", text)
    return text.replace("\\N", "\n").strip()


def write_srt_from_ass() -> None:
    PACK.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    idx = 1
    for raw in ASS.read_text(encoding="utf-8").splitlines():
        if not raw.startswith("Dialogue:"):
            continue
        parts = raw.split(",", 9)
        if len(parts) < 10:
            continue
        start, end, text = parts[1], parts[2], parts[9]
        lines += [str(idx), f"{srt_time_from_ass(start)} --> {srt_time_from_ass(end)}", ass_text_to_plain(text), ""]
        idx += 1
    SRT.write_text("\n".join(lines), encoding="utf-8")


def verify_local() -> dict:
    if not VIDEO.exists():
        raise SystemExit(f"missing video {VIDEO}")
    if not CLEAN.exists():
        raise SystemExit(f"missing clean video {CLEAN}")
    if not ASS.exists():
        raise SystemExit(f"missing captions {ASS}")
    info = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size,bit_rate", "-show_streams", "-of", "json", VIDEO]))
    streams = info.get("streams", [])
    v = next(s for s in streams if s.get("codec_type") == "video")
    a = next(s for s in streams if s.get("codec_type") == "audio")
    if (v.get("width"), v.get("height")) != (1080, 1920):
        raise SystemExit(f"bad dimensions {v.get('width')}x{v.get('height')}")
    if a.get("codec_name") != "aac":
        raise SystemExit(f"audio not AAC: {a.get('codec_name')}")
    return info


def build_pack() -> dict:
    PACK.mkdir(parents=True, exist_ok=True)
    local = verify_local()
    write_srt_from_ass()
    (PACK / "description_upload.txt").write_text(DESCRIPTION, encoding="utf-8")
    # Use captioned video itself for Shorts. Keep clean master in pack for archive/reference.
    shutil.copy2(CLEAN, PACK / CLEAN.name)
    metadata = {
        "title": TITLE,
        "description_file": str((PACK / "description_upload.txt").resolve()),
        "description": DESCRIPTION,
        "tags": TAGS,
        "categoryId": "28",
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": False,
        "audience_note": "Kid-friendly/general audience, not made for kids.",
        "video": str(VIDEO.resolve()),
        "captions_srt": str(SRT.resolve()),
        "voice": "elevenlabs_george",
        "gate_6_authorization_text": AUTHORIZATION_TEXT,
        "created_at": stamp(),
        "local_ffprobe": local,
    }
    META.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def verify_video(yt, video_id: str) -> dict:
    r = yt.videos().list(part="snippet,status,processingDetails,contentDetails", id=video_id).execute()
    if not r.get("items"):
        return {"video_id": video_id, "found": False}
    item = r["items"][0]
    return {
        "video_id": item["id"],
        "found": True,
        "title": item["snippet"].get("title"),
        "channelId": item["snippet"].get("channelId"),
        "channelTitle": item["snippet"].get("channelTitle"),
        "categoryId": item["snippet"].get("categoryId"),
        "tags": item["snippet"].get("tags"),
        "privacyStatus": item["status"].get("privacyStatus"),
        "uploadStatus": item["status"].get("uploadStatus"),
        "selfDeclaredMadeForKids": item["status"].get("selfDeclaredMadeForKids"),
        "processingStatus": item.get("processingDetails", {}).get("processingStatus"),
        "processingFailureReason": item.get("processingDetails", {}).get("processingFailureReason"),
        "duration": item.get("contentDetails", {}).get("duration"),
        "definition": item.get("contentDetails", {}).get("definition"),
        "caption": item.get("contentDetails", {}).get("caption"),
        "url": f"https://youtu.be/{item['id']}",
        "shorts_url": f"https://youtube.com/shorts/{item['id']}",
        "studio_url": f"https://studio.youtube.com/video/{item['id']}/edit",
    }


def upload_private(yt, meta: dict) -> dict:
    if UPLOAD.exists():
        old = json.loads(UPLOAD.read_text(encoding="utf-8"))
        vid = old.get("id") or old.get("video_id") or old.get("response", {}).get("id")
        if vid:
            return {"reused_existing_upload": True, "id": vid, "response": old}
    body = {
        "snippet": {"title": meta["title"], "description": DESCRIPTION, "tags": meta["tags"], "categoryId": "28"},
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "embeddable": True, "publicStatsViewable": True},
    }
    media = MediaFileUpload(str(VIDEO), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(json.dumps({"upload_progress": round(status.progress() * 100, 2)}), flush=True)
    UPLOAD.write_text(json.dumps(response, indent=2), encoding="utf-8")
    return {"reused_existing_upload": False, "id": response["id"], "response": response}


def attach_captions(yt, video_id: str) -> dict:
    media = MediaFileUpload(str(SRT), mimetype="application/x-subrip", resumable=False)
    body = {"snippet": {"videoId": video_id, "language": "en", "name": "English", "isDraft": False}}
    try:
        resp = yt.captions().insert(part="snippet", body=body, media_body=media).execute()
        return {"caption_inserted": True, "response": resp}
    except HttpError as e:
        return {"caption_inserted": False, "error": str(e)}


def wait_processed(yt, video_id: str, timeout_s: int = 900) -> dict:
    start = time.time()
    last = None
    while time.time() - start < timeout_s:
        info = verify_video(yt, video_id)
        last = info
        if info.get("uploadStatus") == "processed" and info.get("processingStatus") == "succeeded":
            return info
        print(json.dumps({"waiting_processing": info}), flush=True)
        time.sleep(20)
    return last or {"video_id": video_id, "found": False}


def publish_public(yt, video_id: str) -> dict:
    before = verify_video(yt, video_id)
    problems = []
    if before.get("uploadStatus") != "processed":
        problems.append(f"uploadStatus={before.get('uploadStatus')}")
    if before.get("processingStatus") != "succeeded":
        problems.append(f"processingStatus={before.get('processingStatus')}")
    if before.get("categoryId") != "28":
        problems.append(f"categoryId={before.get('categoryId')}")
    if before.get("selfDeclaredMadeForKids") is not False:
        problems.append("selfDeclaredMadeForKids not false")
    if problems:
        raise SystemExit("blocked before public publish: " + "; ".join(problems))
    yt.videos().update(
        part="status",
        body={"id": video_id, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False, "embeddable": True, "publicStatsViewable": True}},
    ).execute()
    time.sleep(3)
    after = verify_video(yt, video_id)
    event = {"executed_at": stamp(), "authorization_text": AUTHORIZATION_TEXT, "before": before, "after": after}
    PUBLIC_EVENT.write_text(json.dumps(event, indent=2), encoding="utf-8")
    return event


def main() -> int:
    meta = build_pack()
    yt = yt_client()
    up = upload_private(yt, meta)
    vid = up["id"]
    cap = attach_captions(yt, vid)
    processed = wait_processed(yt, vid)
    pub = publish_public(yt, vid)
    final = verify_video(yt, vid)
    verification = {"uploaded": up, "captions_attach": cap, "processed": processed, "public_publish": pub, "final": final}
    VERIFY.write_text(json.dumps(verification, indent=2), encoding="utf-8")
    print(json.dumps(verification, indent=2))
    if final.get("privacyStatus") != "public":
        raise SystemExit("publish did not verify public")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
