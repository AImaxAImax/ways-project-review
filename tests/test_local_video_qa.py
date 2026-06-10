import importlib.util
import json
import math
import subprocess
from pathlib import Path

import pytest

from tools import local_video_qa


def _make_short(path: Path, seconds: float = 1.2) -> None:
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"testsrc2=size=720x1280:rate=24:duration={seconds}",
        "-f", "lavfi", "-i", f"sine=frequency=440:sample_rate=48000:duration={seconds}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "96k", "-shortest", str(path),
    ], check=True)


def _metrics(clip_min=0.9, dino_min=0.9, temporal=0.02, motion=1.0):
    return {
        "clip_preservation": {"available": True, "min": clip_min, "mean": clip_min},
        "dino_structure": {"available": True, "min": dino_min, "mean": dino_min},
        "temporal_consistency": {"available": True, "mean": temporal},
        "motion_magnitude": {"available": True, "mean": motion},
        "artifact_flags": [],
    }


def test_local_video_qa_writes_json_readme_and_contact_sheet(tmp_path):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    _make_short(video)

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--expected-duration", "1.2",
        "--duration-tolerance", "0.5",
    ])

    assert rc == 0
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert report["score"] >= 80
    assert report["blockers"] == []
    assert report["publish_action"] == "none"
    assert len(report["input_sha256"]) == 64
    assert report["checks"]["audio"]["sample_rate"] == 48000
    assert "metrics" in report
    assert report["thresholds_used"]["mode"] == "report_only"
    assert (outdir / "contact_sheet.jpg").exists()
    assert (outdir / "metrics_debug.json").exists()
    readme = (outdir / "README_QA.md").read_text(encoding="utf-8")
    assert "This QA proxy does not auto-publish" in readme


def test_local_video_qa_blocks_duration_mismatch(tmp_path):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    _make_short(video, seconds=1.0)

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--expected-duration", "4.0",
        "--duration-tolerance", "0.1",
    ])

    assert rc == 1
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert any("duration mismatch" in b for b in report["blockers"])


def test_report_only_metrics_do_not_block(tmp_path, monkeypatch):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    thresholds = tmp_path / "thresholds.json"
    _make_short(video)
    thresholds.write_text(json.dumps({
        "clip_preservation_min": 0.8,
        "dino_structure_min": 0.8,
        "temporal_consistency_max": 0.1,
        "motion_magnitude_low": 0.5,
        "motion_magnitude_high": 4.0,
        "calibrated_against": "test fixture",
        "agreement": "test fixture",
    }), encoding="utf-8")
    monkeypatch.setattr(local_video_qa, "compute_metric_bundle", lambda *args, **kwargs: (_metrics(clip_min=0.1), {"frames": []}, []))

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--thresholds", str(thresholds),
        "--report-only",
    ])

    assert rc == 0
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert report["thresholds_used"]["mode"] == "report_only"
    assert not any("clip_preservation" in b for b in report["blockers"])


def test_thresholds_file_blocks_low_clip_preservation(tmp_path, monkeypatch):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    thresholds = tmp_path / "thresholds.json"
    _make_short(video)
    thresholds.write_text(json.dumps({
        "clip_preservation_min": 0.8,
        "dino_structure_min": 0.0,
        "temporal_consistency_max": 1.0,
        "motion_magnitude_low": 0.0,
        "motion_magnitude_high": 10.0,
        "calibrated_against": "test fixture",
        "agreement": "test fixture",
    }), encoding="utf-8")
    monkeypatch.setattr(local_video_qa, "compute_metric_bundle", lambda *args, **kwargs: (_metrics(clip_min=0.2), {"frames": []}, []))

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--thresholds", str(thresholds),
    ])

    assert rc == 1
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert any("clip_preservation" in b for b in report["blockers"])
    assert report["thresholds_used"]["fail_closed"] is True


def test_thresholds_fail_closed_when_required_metric_unavailable(tmp_path, monkeypatch):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    thresholds = tmp_path / "thresholds.json"
    _make_short(video)
    thresholds.write_text(json.dumps({
        "clip_preservation_min": 0.8,
        "dino_structure_min": 0.0,
        "temporal_consistency_max": 1.0,
        "motion_magnitude_low": 0.0,
        "motion_magnitude_high": 10.0,
        "calibrated_against": "test fixture",
        "agreement": "test fixture",
    }), encoding="utf-8")
    metrics = _metrics()
    metrics["clip_preservation"] = {"available": False, "error": "open_clip unavailable in test"}
    monkeypatch.setattr(local_video_qa, "compute_metric_bundle", lambda *args, **kwargs: (metrics, {"frames": []}, []))

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--thresholds", str(thresholds),
    ])

    assert rc == 1
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert any("clip_preservation min unavailable" in b for b in report["blockers"])


def test_thresholds_can_explicitly_fail_open_for_report_compatibility(tmp_path, monkeypatch):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    thresholds = tmp_path / "thresholds.json"
    _make_short(video)
    thresholds.write_text(json.dumps({
        "clip_preservation_min": 0.8,
        "fail_closed": False,
        "calibrated_against": "legacy report-only compatibility fixture",
        "agreement": "test fixture",
    }), encoding="utf-8")
    metrics = _metrics()
    metrics["clip_preservation"] = {"available": False, "error": "open_clip unavailable in test"}
    monkeypatch.setattr(local_video_qa, "compute_metric_bundle", lambda *args, **kwargs: (metrics, {"frames": []}, []))

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--thresholds", str(thresholds),
    ])

    assert rc == 0
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert report["thresholds_used"]["fail_closed"] is False
    assert not any("clip_preservation" in b for b in report["blockers"])


def test_thresholds_with_blocking_disabled_are_advisory(tmp_path, monkeypatch):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    thresholds = tmp_path / "thresholds.json"
    _make_short(video)
    thresholds.write_text(json.dumps({
        "clip_preservation_min": 0.8,
        "blocking_enabled": False,
        "fail_closed": True,
        "calibrated_against": "first-frame proxy calibration fixture",
        "agreement": "test fixture",
    }), encoding="utf-8")
    metrics = _metrics(clip_min=0.1)
    monkeypatch.setattr(local_video_qa, "compute_metric_bundle", lambda *args, **kwargs: (metrics, {"frames": []}, []))

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--thresholds", str(thresholds),
    ])

    assert rc == 0
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert report["thresholds_used"]["mode"] == "advisory"
    assert report["thresholds_used"]["blocking_enabled"] is False
    assert not any("clip_preservation" in b for b in report["blockers"])


def test_thresholds_reject_malformed_blocking_enabled(tmp_path):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    thresholds = tmp_path / "thresholds.json"
    _make_short(video)
    thresholds.write_text(json.dumps({
        "clip_preservation_min": 0.8,
        "blocking_enabled": "false",
        "calibrated_against": "bad fixture",
        "agreement": "test fixture",
    }), encoding="utf-8")

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--thresholds", str(thresholds),
    ])

    assert rc == 2
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert any("blocking_enabled must be boolean" in b for b in report["blockers"])


def test_zero_motion_flags_dead_render_warning(tmp_path, monkeypatch):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    thresholds = tmp_path / "thresholds.json"
    _make_short(video)
    thresholds.write_text(json.dumps({
        "clip_preservation_min": 0.0,
        "dino_structure_min": 0.0,
        "temporal_consistency_max": 1.0,
        "motion_magnitude_low": 0.5,
        "motion_magnitude_high": 10.0,
        "calibrated_against": "test fixture",
        "agreement": "test fixture",
    }), encoding="utf-8")
    monkeypatch.setattr(local_video_qa, "compute_metric_bundle", lambda *args, **kwargs: (_metrics(motion=0.0), {"frames": []}, []))

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--thresholds", str(thresholds),
    ])

    assert rc == 1
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert any("dead-render warning" in w for w in report["warnings"])
    assert any("motion_magnitude" in b for b in report["blockers"])


def test_missing_source_plate_skips_preservation_metrics_without_crashing(tmp_path):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    _make_short(video)

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--source-image", str(tmp_path / "missing.png"),
    ])

    assert rc == 0
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert report["metrics"]["clip_preservation"].get("skipped") is True
    assert report["metrics"]["dino_structure"].get("skipped") is True


def test_malformed_thresholds_returns_tooling_error(tmp_path):
    video = tmp_path / "candidate.mp4"
    outdir = tmp_path / "qa"
    thresholds = tmp_path / "thresholds.json"
    _make_short(video)
    thresholds.write_text("{not-json", encoding="utf-8")

    rc = local_video_qa.main([
        "--input", str(video),
        "--outdir", str(outdir),
        "--thresholds", str(thresholds),
    ])

    assert rc == 2
    report = json.loads((outdir / "qa_report.json").read_text(encoding="utf-8"))
    assert any("malformed thresholds file" in b for b in report["blockers"])


def test_vlm_command_failures_are_blocking(tmp_path):
    contact_sheet = tmp_path / "contact.jpg"
    contact_sheet.write_bytes(b"not a real jpg but path exists")

    payload = local_video_qa.run_vlm_command("python3 -c 'import sys; sys.exit(1)'", contact_sheet)

    assert payload["severity"] == "block"
    assert payload["reason"] == "vlm_unavailable_or_invalid_output"
    assert "vlm_unavailable_or_invalid_output" in local_video_qa.artifact_flags_from_vlm(payload)


def test_vlm_unparseable_output_is_blocking(tmp_path):
    contact_sheet = tmp_path / "contact.jpg"
    contact_sheet.write_bytes(b"not a real jpg but path exists")

    payload = local_video_qa.run_vlm_command("python3 -c 'print(\"not-json\")'", contact_sheet)

    assert payload["severity"] == "block"
    assert payload["reason"] == "vlm_unavailable_or_invalid_output"


@pytest.mark.slow
def test_real_model_metric_bundle_populates_finite_numbers(tmp_path):
    missing = [name for name in ("open_clip", "PIL", "torch", "torchvision", "cv2", "numpy") if importlib.util.find_spec(name) is None]
    if missing:
        pytest.skip(f"real model dependencies unavailable: {', '.join(missing)}")
    if importlib.util.find_spec("lpips") is None:
        pytest.skip("lpips unavailable; install it before trusting neural temporal-consistency coverage")

    video = tmp_path / "candidate.mp4"
    source = tmp_path / "source.jpg"
    _make_short(video, seconds=1.0)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", "testsrc2=size=720x1280:rate=1:duration=1",
        "-frames:v", "1", str(source),
    ], check=True)

    metrics, debug, warnings = local_video_qa.compute_metric_bundle(video, source, frame_sample_fps=2.0)
    assert warnings == []
    assert debug["frames"]
    for metric_name, field in (
        ("clip_preservation", "min"),
        ("dino_structure", "min"),
        ("temporal_consistency", "mean"),
        ("motion_magnitude", "mean"),
    ):
        metric = metrics[metric_name]
        assert metric.get("available") is True, metric
        value = metric.get(field)
        assert isinstance(value, (int, float)), metric
        assert math.isfinite(float(value)), metric
