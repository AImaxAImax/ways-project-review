import json
from pathlib import Path

from tools import ways_qc_gate_runner


def test_gate1_blocks_script_without_source_and_early_hook(tmp_path):
    board = {
        "cards": [
            {
                "slug": "weak_hook",
                "status_column": "Idea Pool",
                "hook": "Did you know this animal fact?",
                "script": {
                    "beats": [
                        {"caption": "First, meet the animal", "voiceover": "First, meet the animal.", "visual": "animal"},
                        {"caption": "It does the surprising thing", "voiceover": "It does the surprising thing.", "visual": "the surprising thing"},
                    ],
                    "sources": [],
                },
            }
        ]
    }

    report = ways_qc_gate_runner.evaluate_board(board, root=tmp_path)

    card = report["cards"][0]
    assert card["gate_results"]["gate1_script"]["status"] == "block"
    assert card["blocking_gate"] == "Gate 1 - Script"
    assert "citable source" in card["rework_reason"]
    assert "first 1-2 seconds" in card["rework_reason"]
    assert report["summary"]["blocked_cards"] == 1


def test_gate3_blocks_missing_expected_clip_and_generated_text(tmp_path):
    existing_clip = tmp_path / "clips" / "shot01.mp4"
    existing_clip.parent.mkdir()
    existing_clip.write_bytes(b"fake mp4 placeholder")
    board = {
        "cards": [
            {
                "slug": "render_card",
                "status_column": "Render",
                "render": {
                    "expected_clips": ["clips/shot01.mp4", "clips/shot02.mp4"],
                    "shot_reports": [
                        {"shot_id": "shot01", "text_or_logo_present": False, "morphing_or_anatomy_issue": False},
                        {"shot_id": "shot02", "text_or_logo_present": True, "morphing_or_anatomy_issue": False},
                    ],
                },
            }
        ]
    }

    report = ways_qc_gate_runner.evaluate_board(board, root=tmp_path)

    card = report["cards"][0]
    assert card["gate_results"]["gate3_render_qa"]["status"] == "block"
    assert card["blocking_gate"] == "Gate 3 - Render QA"
    assert "missing expected clip: clips/shot02.mp4" in card["rework_reason"]
    assert "generated text/logo" in card["rework_reason"]


def test_gate4_blocks_bad_specs_and_missing_artifacts(tmp_path):
    ffprobe = tmp_path / "ffprobe_publish.json"
    ffprobe.write_text(json.dumps({
        "streams": [
            {"codec_type": "video", "codec_name": "h264", "width": 720, "height": 1280, "avg_frame_rate": "30/1"},
            {"codec_type": "audio", "codec_name": "aac", "sample_rate": "44100"},
        ],
        "format": {"duration": "14.2"},
    }), encoding="utf-8")
    board = {
        "cards": [
            {
                "slug": "assembled_card",
                "status_column": "Assembly & Caption",
                "artifact_folder": ".",
                "outputs": {
                    "ffprobe_publish": "ffprobe_publish.json",
                    "contact_sheet": "contact_sheet.jpg",
                    "publish_candidate_captioned": "publish.mp4",
                    "captions_ass": "captions.ass",
                    "captions_srt": "captions.srt",
                    "audio_report": {"mean_lufs": -15.0, "true_peak_db": -0.2},
                },
                "assembly_qa": {
                    "caption_readability": "pass",
                    "double_captions": False,
                    "non_caption_text": False,
                    "visual_reset_seconds_max": 2.6,
                },
            }
        ]
    }

    report = ways_qc_gate_runner.evaluate_board(board, root=tmp_path)

    card = report["cards"][0]
    assert card["gate_results"]["gate4_spec_assembly_qa"]["status"] == "block"
    assert card["blocking_gate"] == "Gate 4 - Spec / Assembly QA"
    assert "not 1080x1920" in card["rework_reason"]
    assert "audio sample rate is 44100 Hz" in card["rework_reason"]
    assert "missing artifact: contact_sheet.jpg" in card["rework_reason"]


def test_wip_limits_flag_overages_and_low_publish_buffer(tmp_path):
    cards = []
    for idx in range(6):
        cards.append({"slug": f"render_{idx}", "status_column": "Render"})
    for idx in range(6):
        cards.append({"slug": f"plate_{idx}", "status_column": "Plate QC"})
    for idx in range(4):
        cards.append({"slug": f"review_{idx}", "status_column": "Human Final Review"})
    for idx in range(4):
        cards.append({"slug": f"ready_{idx}", "status_column": "Ready to Publish"})

    report = ways_qc_gate_runner.evaluate_board({"cards": cards}, root=tmp_path)

    assert report["wip_limits"]["plate_generation_render"]["status"] == "block"
    assert report["wip_limits"]["plate_qc"]["status"] == "block"
    assert report["wip_limits"]["human_final_review"]["status"] == "block"
    assert report["wip_limits"]["ready_to_publish_buffer"]["status"] == "warn"
    assert report["summary"]["wip_blocks"] == 3
    assert report["summary"]["wip_warnings"] == 1


def test_human_gates_are_advisory_not_auto_approved(tmp_path):
    board = {
        "cards": [
            {"slug": "plate_waiting", "status_column": "Plate QC", "human_approved": False},
            {"slug": "final_waiting", "status_column": "Human Final Review", "human_approved": False},
        ]
    }

    report = ways_qc_gate_runner.evaluate_board(board, root=tmp_path)

    by_slug = {card["slug"]: card for card in report["cards"]}
    assert by_slug["plate_waiting"]["human_gate"]["status"] == "blocked_advisory"
    assert by_slug["plate_waiting"]["blocking_gate"] == "Gate 2 - Human Plate QC"
    assert by_slug["final_waiting"]["human_gate"]["status"] == "blocked_advisory"
    assert by_slug["final_waiting"]["blocking_gate"] == "Gate 5 - Human Final Review"


def test_internal_automation_policy_can_advance_gate2_and_gate5_without_public_publish(tmp_path):
    board = {
        "cards": [
            {
                "slug": "plate_auto",
                "status_column": "Plate QC",
                "automation_policy": "auto_advance_internal_until_5_active_ready",
                "gate_1_status": "auto_approved_internal",
            },
            {
                "slug": "final_auto",
                "status_column": "Human Final Review",
                "automation_policy": "auto_advance_internal_until_5_active_ready",
                "draft_score": 6.5,
            },
            {
                "slug": "publish_still_blocked",
                "status_column": "Ready to Publish",
                "automation_policy": "auto_advance_internal_until_5_active_ready",
            },
        ]
    }

    report = ways_qc_gate_runner.evaluate_board(board, root=tmp_path)

    by_slug = {card["slug"]: card for card in report["cards"]}
    assert by_slug["plate_auto"]["human_gate"]["status"] == "auto_internal"
    assert by_slug["plate_auto"]["blocking_gate"] is None
    assert by_slug["final_auto"]["human_gate"]["status"] == "auto_internal"
    assert by_slug["final_auto"]["blocking_gate"] is None
    assert by_slug["publish_still_blocked"]["human_gate"]["status"] == "blocked_advisory"
    assert by_slug["publish_still_blocked"]["blocking_gate"] == "Gate 6 - Publish Authorization"
