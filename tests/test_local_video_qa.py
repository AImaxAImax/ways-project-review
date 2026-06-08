import json
import subprocess
from pathlib import Path

from tools import local_video_qa


def _make_short(path: Path, seconds: float = 1.2) -> None:
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"testsrc2=size=720x1280:rate=24:duration={seconds}",
        "-f", "lavfi", "-i", f"sine=frequency=440:sample_rate=48000:duration={seconds}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "96k", "-shortest", str(path),
    ], check=True)


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
    assert report["checks"]["audio"]["sample_rate"] == 48000
    assert (outdir / "contact_sheet.jpg").exists()
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
