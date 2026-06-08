import json

from tools import ways_discord_qa as qa


def test_parse_final_review_discord_reply():
    payload = qa.parse_discord_qa_reply(
        'QA sharks_older_than_trees approve-private score=8.5 notes="good private draft, not public"'
    )
    decision = qa.decision_from_payload(payload)

    assert decision["slug"] == "sharks_older_than_trees"
    assert decision["action"] == "approve-private"
    assert decision["score"] == "8.5"
    assert decision["gate"] == "Gate 5 final video review"
    assert decision["source"] == "discord"
    assert decision["discord_thread_id"] == qa.REVIEW_THREAD_ID


def test_plate_approval_requires_lane_and_marks_vlm_advisory():
    payload = qa.parse_discord_qa_reply('QA mantis_shrimp__shot03 approve-plate lane=wan_i2v score=9 notes="clean"')
    decision = qa.decision_from_payload(payload)

    assert decision["gate"] == "Gate 2 human plate QC"
    assert decision["confirmed_lane"] == "wan_i2v"
    assert decision["vlm_was_advisory_only"] is True


def test_plate_approval_without_lane_rejected():
    try:
        qa.parse_discord_qa_reply('QA mantis approve-plate score=9 notes="looks good"')
    except ValueError as exc:
        assert "approve-plate requires lane" in str(exc)
    else:
        raise AssertionError("expected lane validation failure")


def test_publish_reply_records_explicit_authorization():
    payload = qa.parse_discord_qa_reply('QA sharks publish notes="go public now"')
    decision = qa.decision_from_payload(payload)

    assert decision["action"] == "authorize-public-publish"
    assert decision["gate"] == "Gate 6 public publish authorization"
    assert "Josh authorizes public publish" in decision["explicit_public_publish_authorization"]


def test_persist_decision(tmp_path):
    decision = qa.decision_from_payload(qa.parse_discord_qa_reply('QA shark reject notes="shot 4 fails"'))
    path = tmp_path / "review_decisions.json"
    qa.persist_decision(decision, path)

    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["decisions"]["shark:reject-rework"]["notes"] == "shot 4 fails"


def test_build_outbox_dedupes_duplicate_human_gate_cards(tmp_path):
    report = {
        "cards": [
            {
                "slug": "shark/run/manifest_partial",
                "topic": "Shark",
                "blocking_gate": "Gate 5 - Human Final Review",
                "contact_sheet": "same.jpg",
                "model_lane": "Unknown / internal",
            },
            {
                "slug": "shark/run",
                "topic": "Shark",
                "blocking_gate": "Gate 5 - Human Final Review",
                "contact_sheet": "same.jpg",
                "model_lane": "C - Local I2V / Wan2.2",
            },
        ]
    }
    path = tmp_path / "report.json"
    out = tmp_path / "outbox.md"
    path.write_text(json.dumps(report), encoding="utf-8")

    prompts = qa.build_outbox(path, out)

    assert [p["slug"] for p in prompts] == ["shark/run"]
    assert "manifest_partial" not in out.read_text(encoding="utf-8")

