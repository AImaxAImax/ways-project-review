import datetime as dt
import json
from pathlib import Path

import pytest

from tools import ways_publish_review as ways


def test_draft_pack_defaults_private_category_and_not_made_for_kids(tmp_path):
    desc = tmp_path / "description.txt"
    video = tmp_path / "candidate.mp4"
    captions = tmp_path / "captions.srt"
    thumb = tmp_path / "thumb.jpg"
    desc.write_text("description", encoding="utf-8")
    video.write_bytes(b"fake mp4 bytes")
    captions.write_text("1\n00:00:00,000 --> 00:00:01,000\nHI\n", encoding="utf-8")
    thumb.write_bytes(b"jpg")

    result = ways.write_draft_pack(
        outdir=tmp_path / "pack",
        title="Sharks Are Older Than Trees #Shorts",
        description_file=desc,
        video=video,
        captions_srt=captions,
        thumbnail_candidate=thumb,
        tags=["science", "shorts"],
    )

    meta = json.loads((tmp_path / "pack" / "youtube_metadata.json").read_text(encoding="utf-8"))
    assert meta["categoryId"] == "28"
    assert meta["privacyStatus"] == "private"
    assert meta["selfDeclaredMadeForKids"] is False
    assert result["status"]["public_publish_gate"] == "blocked_until_explicit_josh_authorization"
    assert (tmp_path / "pack" / "description_upload.txt").read_text(encoding="utf-8") == "description"


def test_non_private_or_made_for_kids_pack_is_rejected(tmp_path):
    desc = tmp_path / "description.txt"
    video = tmp_path / "candidate.mp4"
    desc.write_text("description", encoding="utf-8")
    video.write_bytes(b"fake")

    with pytest.raises(ValueError, match="privacyStatus='private'"):
        ways.build_youtube_metadata(
            title="x",
            description_file=desc,
            video=video,
            privacy_status="public",
        )
    with pytest.raises(ValueError, match="selfDeclaredMadeForKids=false"):
        ways.build_youtube_metadata(
            title="x",
            description_file=desc,
            video=video,
            self_declared_made_for_kids=True,
        )


def test_public_publish_requires_explicit_josh_authorization():
    assert not ways.validate_public_authorization("please publish this")["authorized"]
    assert ways.validate_public_authorization("Josh approved public publish for KLwp-KbIr9I")["authorized"]


def test_schedule_is_one_per_day_until_buffer_then_two_spaced():
    low = ways.schedule_slots(
        start_date=dt.date(2026, 6, 6),
        ready_buffer_count=10,
        count=3,
        morning_utc="14:00",
        evening_utc="23:00",
    )
    assert low["daily_limit"] == 1
    assert [s["publish_at_utc"] for s in low["slots"]] == [
        "2026-06-06T14:00:00Z",
        "2026-06-07T14:00:00Z",
        "2026-06-08T14:00:00Z",
    ]

    high = ways.schedule_slots(
        start_date=dt.date(2026, 6, 6),
        ready_buffer_count=50,
        count=3,
        morning_utc="14:00",
        evening_utc="23:00",
    )
    assert high["daily_limit"] == 2
    assert [s["publish_at_utc"] for s in high["slots"]] == [
        "2026-06-06T14:00:00Z",
        "2026-06-06T23:00:00Z",
        "2026-06-07T14:00:00Z",
    ]

    with pytest.raises(ValueError, match="at least 6h spacing"):
        ways.schedule_slots(
            start_date=dt.date(2026, 6, 6),
            ready_buffer_count=50,
            count=2,
            morning_utc="14:00",
            evening_utc="15:00",
        )


def test_performance_review_maps_swipe_timestamp_and_promotes_class_lesson(tmp_path):
    manifest = tmp_path / "storyboard_manifest.json"
    manifest.write_text(json.dumps({"shots": [
        {"id": "shot01", "duration": 2.0, "caption": "HOOK"},
        {"id": "shot02", "duration": 3.0, "caption": "PROOF"},
    ]}), encoding="utf-8")
    skill = tmp_path / "SKILL.md"

    result = ways.record_performance_review(
        outdir=tmp_path / "reviews",
        video_id="abc123",
        retention_pct_viewed=68.4,
        swipe_away_timestamp=2.4,
        storyboard_manifest=manifest,
        lesson="If proof beat dips, cut fossil setup under 2 seconds.",
        class_level=True,
        skill_path=skill,
        dry_run_skill=False,
    )

    review = result["review"]
    assert review["retention_pct_viewed"] == 68.4
    assert review["mapped_beat_or_shot"]["shot_id"] == "shot02"
    assert review["skill_promotion"]["promoted"] is True
    assert "If proof beat dips" in skill.read_text(encoding="utf-8")
    assert (tmp_path / "reviews" / "performance_reviews.jsonl").exists()


def test_class_level_review_requires_skill_path(tmp_path):
    with pytest.raises(ValueError, match="require --skill-path"):
        ways.record_performance_review(
            outdir=tmp_path,
            video_id="abc123",
            retention_pct_viewed=50,
            swipe_away_timestamp=None,
            storyboard_manifest=None,
            lesson="General caption lesson",
            class_level=True,
            skill_path=None,
            dry_run_skill=False,
        )
