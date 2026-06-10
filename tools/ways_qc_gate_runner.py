#!/usr/bin/env python3
"""WAYS kanban/QC gate runner.

Reads a board JSON file, evaluates the automated WAYS gates, records each card's
blocking_gate/rework_reason in the report, and checks factory WIP limits. Josh's
current operating policy is to keep at least five internal WAYS candidates moving;
agent/automation review can advance internal Plate QC and Final Review evidence,
but public publish authorization is still never auto-approved.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any

GATE1 = "Gate 1 - Script"
GATE2 = "Gate 2 - Human Plate QC"
GATE3 = "Gate 3 - Render QA"
GATE4 = "Gate 4 - Spec / Assembly QA"
GATE5 = "Gate 5 - Human Final Review"
GATE6 = "Gate 6 - Publish Authorization"

WIP_LIMITS = {
    "plate_generation_render": {
        "columns": {"Plate Generation", "Render"},
        "max": 5,
        "label": "Plate Generation + Render combined",
    },
    "plate_qc": {"columns": {"Plate QC"}, "max": 5, "label": "Plate QC"},
    "human_final_review": {"columns": {"Human Final Review"}, "max": 3, "label": "Human Final Review"},
}
READY_BUFFER_TARGET = 10
READY_BUFFER_WARN_BELOW = 5
KNOWN_COLUMNS = {
    "Idea Pool",
    "Script Locked",
    "Plate Generation",
    "Plate QC",
    "Render",
    "Assembly & Caption",
    "Auto-QA",
    "Human Final Review",
    "Ready to Publish",
    "Published / Scheduled",
    "Parked / Rework",
    "Killed",
    "Monitor Only",
    "Unknown",
}
COLUMN_STATUS_ALIASES = {
    "publish-gated": "Human Final Review",
    "promoted": "Ready to Publish",
    "ready": "Ready to Publish",
    "blocked": "Parked / Rework",
    "internal": "Render",
}
GATE4_COLUMNS = {"Assembly & Caption", "Auto-QA", "Human Final Review", "Ready to Publish", "Published / Scheduled"}


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, str) and "/" in value:
            a, b = value.split("/", 1)
            denom = float(b)
            return float(a) / denom if denom else default
        return float(value)
    except Exception:
        return default


def normalize_column(card: dict[str, Any]) -> str:
    column = card.get("status_column") or card.get("column") or card.get("kanban_column")
    if column:
        value = str(column).strip()
        return value if value in KNOWN_COLUMNS else "Unknown"
    status = str(card.get("status", "")).strip().lower()
    return COLUMN_STATUS_ALIASES.get(status, "Unknown" if status else "Unknown")


def raw_column(card: dict[str, Any]) -> str:
    column = card.get("status_column") or card.get("column") or card.get("kanban_column")
    if column:
        return str(column).strip()
    status = str(card.get("status", "")).strip().lower()
    return COLUMN_STATUS_ALIASES.get(status, status.title() if status else "Unknown")


def evaluate_column(card: dict[str, Any], column: str) -> dict[str, Any]:
    original = raw_column(card)
    if column == "Unknown" or original not in KNOWN_COLUMNS:
        return result("block", [f"unknown status_column: {original}"], {"raw_column": original})
    return result("pass", [], {"raw_column": original})


def cards_from_board(board: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(board.get("cards"), list):
        return board["cards"]
    if isinstance(board.get("candidates"), list):
        return board["candidates"]
    raise ValueError("board JSON must contain cards[] or candidates[]")


def card_slug(card: dict[str, Any], index: int) -> str:
    return str(card.get("slug") or card.get("id") or card.get("title") or f"card_{index:03d}")


def result(status: str, reasons: list[str], checks: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"status": status, "reasons": reasons, "checks": checks or {}}


def first_caption_text(card: dict[str, Any]) -> str:
    script = card.get("script") or {}
    beats = script.get("beats") or card.get("beats") or []
    if beats:
        first = beats[0]
        if isinstance(first, dict):
            return str(first.get("caption") or first.get("voiceover") or first.get("text") or "")
        return str(first)
    return str(card.get("first_caption") or card.get("hook") or "")


def source_count(card: dict[str, Any]) -> int:
    script = card.get("script") or {}
    sources = script.get("sources", card.get("sources", []))
    if isinstance(sources, str):
        return 1 if sources.strip() else 0
    if isinstance(sources, list):
        return len([s for s in sources if s])
    return 1 if sources else 0


def evaluate_gate1(card: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    script = card.get("script") or {}
    beats = script.get("beats") or card.get("beats") or []
    hook = str(card.get("hook") or "").strip()
    first_caption = first_caption_text(card).strip()

    if not hook:
        reasons.append("missing hook")
    if not first_caption:
        reasons.append("missing first caption/beat")
    elif hook and hook.lower().rstrip(".!?") not in first_caption.lower():
        reasons.append("hook payoff does not land in first 1-2 seconds / first caption line")
    if source_count(card) == 0:
        reasons.append("missing citable source")
    if not beats:
        reasons.append("missing beat list")

    filler_words = {"basically", "actually", "in conclusion", "you won't believe", "did you know"}
    combined = " ".join(
        str((b.get("voiceover") or b.get("caption") or b.get("text") or b) if isinstance(b, dict) else b)
        for b in beats
    ).lower()
    if any(word in combined for word in filler_words):
        reasons.append("script contains filler/sensational wording")

    for idx, beat in enumerate(beats, 1):
        if not isinstance(beat, dict):
            continue
        spoken = str(beat.get("voiceover") or beat.get("caption") or "").strip()
        visual = str(beat.get("visual") or beat.get("shot") or beat.get("proxy") or "").strip()
        if spoken and not visual:
            reasons.append(f"beat {idx} lacks say-dog-see-dog visual/proxy")

    return result("block" if reasons else "pass", reasons, {"beats": len(beats), "sources": source_count(card)})


def resolve_path(root: Path, artifact_folder: Path | None, value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    if path.is_absolute():
        return path
    base = artifact_folder if artifact_folder else root
    return base / path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evaluate_gate3(card: dict[str, Any], root: Path) -> dict[str, Any]:
    reasons: list[str] = []
    render = card.get("render") or card.get("render_qa") or {}
    artifact_folder = resolve_path(root, None, card.get("artifact_folder")) if card.get("artifact_folder") else root

    expected_clips = render.get("expected_clips") or card.get("expected_clips") or []
    for clip in expected_clips:
        clip_path = resolve_path(root, artifact_folder, clip)
        if clip_path and not clip_path.exists():
            reasons.append(f"missing expected clip: {clip}")

    shot_reports = render.get("shot_reports") or render.get("clips") or []
    for idx, shot in enumerate(shot_reports, 1):
        if not isinstance(shot, dict):
            continue
        shot_id = shot.get("shot_id") or shot.get("id") or f"shot{idx:02d}"
        severity = str(shot.get("severity") or "").lower()
        if shot.get("text_or_logo_present") or shot.get("generated_text_or_logo"):
            reasons.append(f"{shot_id}: generated text/logo present")
        if shot.get("morphing_or_anatomy_issue") or shot.get("catastrophic_morphing"):
            reasons.append(f"{shot_id}: catastrophic morphing/anatomy issue")
        if shot.get("motion_graphic_artifact") or shot.get("i2v_texture_artifact"):
            reasons.append(f"{shot_id}: motion-graphic lane/render artifact")
        if severity in {"block", "fail"}:
            reasons.append(f"{shot_id}: render QA severity={severity}")

    if not expected_clips and not shot_reports:
        reasons.append("missing render QA expected_clips/shot_reports")

    return result("block" if reasons else "pass", reasons, {"expected_clips": len(expected_clips), "shot_reports": len(shot_reports)})


def run_ffprobe(path: Path | None) -> tuple[dict[str, Any] | None, str | None]:
    if not path:
        return None, "missing publish candidate path"
    if not path.exists():
        return None, f"missing publish candidate: {path}"
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-print_format",
            "json",
            str(path),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        return None, f"ffprobe failed for publish candidate: {proc.stderr.strip() or proc.stdout.strip()}"
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"ffprobe returned invalid JSON: {exc}"


def stream(probe: dict[str, Any], kind: str) -> dict[str, Any] | None:
    return next((s for s in probe.get("streams", []) if s.get("codec_type") == kind), None)


def evaluate_gate4(card: dict[str, Any], root: Path) -> dict[str, Any]:
    reasons: list[str] = []
    outputs = card.get("outputs") or {}
    assembly = card.get("assembly_qa") or card.get("spec_qa") or {}
    artifact_folder = resolve_path(root, None, card.get("artifact_folder")) if card.get("artifact_folder") else root

    publish_candidate_value = outputs.get("publish_candidate_captioned") or outputs.get("publish_candidate")
    publish_candidate_path = resolve_path(root, artifact_folder, publish_candidate_value)
    probe, probe_error = run_ffprobe(publish_candidate_path)
    if probe_error:
        reasons.append(probe_error)
    if probe:
        video = stream(probe, "video")
        audio = stream(probe, "audio")
        if not video:
            reasons.append("missing video stream")
        else:
            width, height = int(video.get("width") or 0), int(video.get("height") or 0)
            fps = as_float(video.get("avg_frame_rate") or video.get("r_frame_rate"), 0.0)
            if (width, height) != (1080, 1920):
                reasons.append(f"not 1080x1920: {width}x{height}")
            if str(video.get("codec_name") or "").lower() not in {"h264", "avc1"}:
                reasons.append(f"video codec is {video.get('codec_name')}; expected h264")
            if fps and not math.isclose(fps, 24.0, abs_tol=0.15):
                reasons.append(f"frame rate is {fps:.2f} fps; expected 24 fps")
        if not audio:
            reasons.append("missing audio stream")
        else:
            if str(audio.get("codec_name") or "").lower() != "aac":
                reasons.append(f"audio codec is {audio.get('codec_name')}; expected aac")
            sample_rate = int(audio.get("sample_rate") or 0)
            if sample_rate != 48000:
                reasons.append(f"audio sample rate is {sample_rate} Hz; expected 48000 Hz")
        duration = as_float(probe.get("format", {}).get("duration"), 0.0)
        if duration and not (5.0 <= duration <= 60.0):
            reasons.append(f"duration {duration:.2f}s outside target Shorts range 5-60s")

    required_outputs = {
        "contact_sheet": outputs.get("contact_sheet"),
        "publish_candidate_captioned": outputs.get("publish_candidate_captioned") or outputs.get("publish_candidate"),
        "captions_ass": outputs.get("captions_ass") or outputs.get("ass"),
        "captions_srt": outputs.get("captions_srt") or outputs.get("srt"),
        "qa_report": outputs.get("qa_report") or outputs.get("qa_report_json"),
    }
    resolved_outputs: dict[str, Path] = {}
    for label, value in required_outputs.items():
        if not value:
            reasons.append(f"missing artifact field: {label}")
            continue
        path = resolve_path(root, artifact_folder, value)
        if path and not path.exists():
            reasons.append(f"missing artifact: {value}")
        elif path:
            resolved_outputs[label] = path

    qa_report_path = resolved_outputs.get("qa_report")
    if qa_report_path and publish_candidate_path and publish_candidate_path.exists():
        try:
            qa_report = json.loads(qa_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            reasons.append(f"qa_report invalid JSON: {exc}")
        else:
            expected_hash = qa_report.get("input_sha256") or qa_report.get("source_sha256") or qa_report.get("video_sha256")
            if not expected_hash:
                reasons.append("qa_report missing input_sha256/source_sha256/video_sha256")
            else:
                actual_hash = sha256_file(publish_candidate_path)
                if str(expected_hash).lower() != actual_hash.lower():
                    reasons.append("qa_report hash does not match publish candidate")

    audio_report = outputs.get("audio_report") or assembly.get("audio_report") or {}
    if isinstance(audio_report, dict):
        peak = audio_report.get("true_peak_db", audio_report.get("peak_db"))
        if peak is not None and as_float(peak, -99) >= -0.5:
            reasons.append(f"audio peak {peak} dB is clipped/too hot; expected < -0.5 dB")
        mean_lufs = audio_report.get("mean_lufs", audio_report.get("integrated_lufs"))
        if mean_lufs is not None and not (-17.5 <= as_float(mean_lufs) <= -12.5):
            reasons.append(f"audio loudness {mean_lufs} LUFS outside speech target around -15")

    if str(assembly.get("caption_readability", "pass")).lower() not in {"pass", "ok", "true"}:
        reasons.append("captions not readable at phone size")
    if assembly.get("double_captions"):
        reasons.append("double captions detected")
    if assembly.get("non_caption_text"):
        reasons.append("non-caption on-screen text detected")
    reset_max = assembly.get("visual_reset_seconds_max")
    if reset_max is not None and as_float(reset_max) > 3.0:
        reasons.append(f"visual reset gap {reset_max}s exceeds 2-3 seconds")

    return result("block" if reasons else "pass", reasons, {"publish_candidate": str(publish_candidate_path) if publish_candidate_path else None})


def evaluate_human_gate(card: dict[str, Any], column: str) -> dict[str, Any] | None:
    if column == "Plate QC":
        if card.get("human_approved") is True and card.get("lane_assigned"):
            return {"gate": GATE2, "status": "human_approved", "reason": "human plate approval and lane assignment recorded"}
        return {"gate": GATE2, "status": "blocked_advisory", "reason": "requires Josh human plate approve/deny plus lane confirmation; automation_policy cannot self-approve"}
    if column == "Human Final Review":
        if card.get("human_approved") is True and (card.get("draft_score") or card.get("publish_score")):
            return {"gate": GATE5, "status": "human_approved", "reason": "human phone-size review score recorded"}
        return {"gate": GATE5, "status": "blocked_advisory", "reason": "requires Josh phone-size final review; automation_policy cannot self-approve"}
    if column in {"Ready to Publish", "Published / Scheduled"} and card.get("publish_authorized") is not True:
        return {"gate": GATE6, "status": "blocked_advisory", "reason": "public publish requires explicit human authorization; default remains private"}
    return None


def should_run_gate1(card: dict[str, Any], column: str) -> bool:
    return column in {"Idea Pool", "Script Locked"} or bool(card.get("script") or card.get("beats"))


def should_run_gate3(card: dict[str, Any], column: str) -> bool:
    return column == "Render" or bool(card.get("render") or card.get("render_qa") or card.get("expected_clips"))


def should_run_gate4(card: dict[str, Any], column: str) -> bool:
    return column in GATE4_COLUMNS or bool(card.get("assembly_qa") or card.get("spec_qa"))


def evaluate_card(card: dict[str, Any], root: Path, index: int) -> dict[str, Any]:
    column = normalize_column(card)
    out = copy.deepcopy(card)
    out["slug"] = card_slug(card, index)
    out["status_column"] = column
    out["gate_results"] = {}
    out["blocking_gate"] = None
    out["rework_reason"] = None

    out["gate_results"]["column_validation"] = evaluate_column(card, column)
    if should_run_gate1(card, column):
        out["gate_results"]["gate1_script"] = evaluate_gate1(card)
    if should_run_gate3(card, column):
        out["gate_results"]["gate3_render_qa"] = evaluate_gate3(card, root)
    if should_run_gate4(card, column):
        out["gate_results"]["gate4_spec_assembly_qa"] = evaluate_gate4(card, root)

    human_gate = evaluate_human_gate(card, column)
    if human_gate:
        out["human_gate"] = human_gate

    ordered = [
        ("column_validation", "Board column validation"),
        ("gate1_script", GATE1),
        ("gate3_render_qa", GATE3),
        ("gate4_spec_assembly_qa", GATE4),
    ]
    for key, label in ordered:
        gate_result = out["gate_results"].get(key)
        if gate_result and gate_result["status"] == "block":
            out["blocking_gate"] = label
            out["rework_reason"] = "; ".join(gate_result["reasons"])
            break

    if not out["blocking_gate"] and human_gate and human_gate["status"] == "blocked_advisory":
        out["blocking_gate"] = human_gate["gate"]
        out["rework_reason"] = human_gate["reason"]

    # Preserve explicit board-level blockers/rejections that are not represented
    # as an artifact QA failure yet (for example source-acquisition partial pass
    # cards waiting on enough proof plates/VO). Artifact existence or a clean
    # script check must not silently clear the card's known blocking gate.
    if not out["blocking_gate"] and card.get("blocking_gate"):
        out["blocking_gate"] = card.get("blocking_gate")
        preserved_reason = card.get("rework_reason") or card.get("source_quality_requirements") or "pre-existing board blocker preserved"
        out["rework_reason"] = preserved_reason if isinstance(preserved_reason, str) else json.dumps(preserved_reason, ensure_ascii=False)

    return out


def evaluate_wip_limits(cards: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for card in cards:
        column = normalize_column(card)
        counts[column] = counts.get(column, 0) + 1

    limits: dict[str, Any] = {}
    for key, spec in WIP_LIMITS.items():
        count = sum(counts.get(col, 0) for col in spec["columns"])
        max_count = int(spec["max"])
        over_by = max(0, count - max_count)
        limits[key] = {
            "label": spec["label"],
            "columns": sorted(spec["columns"]),
            "count": count,
            "max": max_count,
            "status": "block" if over_by else "pass",
            "reason": f"{spec['label']} WIP {count}/{max_count}" + (f"; over by {over_by}" if over_by else ""),
        }

    ready_count = counts.get("Ready to Publish", 0)
    limits["ready_to_publish_buffer"] = {
        "label": "Ready to Publish buffer",
        "columns": ["Ready to Publish"],
        "count": ready_count,
        "target": READY_BUFFER_TARGET,
        "warn_below": READY_BUFFER_WARN_BELOW,
        "status": "warn" if ready_count < READY_BUFFER_WARN_BELOW else "pass",
        "reason": (
            f"Ready-to-Publish buffer {ready_count}/{READY_BUFFER_TARGET}; flag Josh because below {READY_BUFFER_WARN_BELOW}"
            if ready_count < READY_BUFFER_WARN_BELOW
            else f"Ready-to-Publish buffer {ready_count}/{READY_BUFFER_TARGET}"
        ),
    }
    return limits


def metric_gate_effective_mode(root: Path) -> str:
    thresholds_path = root / "config" / "qa_thresholds.json"
    if not thresholds_path.exists():
        return "unknown_no_threshold_config"
    try:
        thresholds = json.loads(thresholds_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "error_malformed_threshold_config"
    if thresholds.get("gate_mode") == "advisory" or thresholds.get("blocking_enabled") is False:
        return "advisory"
    return "blocking" if thresholds.get("blocking_enabled") is True else "unknown"


def evaluate_board(board: dict[str, Any], root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root).resolve()
    source_cards = cards_from_board(board)
    evaluated_cards = [evaluate_card(card, root_path, idx) for idx, card in enumerate(source_cards, 1)]
    wip_limits = evaluate_wip_limits(evaluated_cards)
    blocked_cards = sum(1 for card in evaluated_cards if card.get("blocking_gate"))
    wip_blocks = sum(1 for item in wip_limits.values() if item["status"] == "block")
    wip_warnings = sum(1 for item in wip_limits.values() if item["status"] == "warn")
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "root": str(root_path),
        "metric_gate_effective_mode": metric_gate_effective_mode(root_path),
        "summary": {
            "cards_evaluated": len(evaluated_cards),
            "blocked_cards": blocked_cards,
            "wip_blocks": wip_blocks,
            "wip_warnings": wip_warnings,
            "status": "block" if blocked_cards or wip_blocks else "warn" if wip_warnings else "pass",
        },
        "wip_limits": wip_limits,
        "cards": evaluated_cards,
    }


def write_checklist(path: Path) -> None:
    path.write_text(
        "# WAYS QC Gate Runner Checklist\n\n"
        "Use `python3 tools/ways_qc_gate_runner.py --board <board.json> --root <repo> --out <report.json>` before moving cards.\n\n"
        "## Gate 1 - Script\n"
        "- Hook appears in the first caption/beat so payoff lands in 1-2 seconds.\n"
        "- Beat list exists, has no filler/sensational wording, and each spoken beat has a visual/proxy.\n"
        "- At least one citable source is recorded.\n\n"
        "## Gate 3 - Render QA\n"
        "- Every expected clip path exists.\n"
        "- Per-shot report has no generated text/logo, catastrophic morphing/anatomy issue, or lane artifact.\n"
        "- Re-render only the failing shot; paid escalation still requires approval.\n\n"
        "## Gate 4 - Spec / Assembly QA\n"
        "- ffprobe says 1080x1920, H.264, 24fps, AAC 48kHz, duration 5-60s.\n"
        "- publish candidate, contact sheet, captions.ass, and captions.srt exist.\n"
        "- Captions are phone-readable with no double captions or non-caption text.\n"
        "- Visual reset max is <=3 seconds and audio peak is < -0.5 dB.\n\n"
        "## WIP limits\n"
        "- Plate Generation + Render combined <= 5 videos while the WAYS active/ready queue is below the five-video floor.\n"
        "- Plate QC <= 5 plates.\n"
        "- Human Final Review <= 3 videos.\n"
        "- Ready-to-Publish target is 10; flag Josh below 5.\n\n"
        "Internal Gate 2/Gate 5 work may advance via automation evidence under the five-video-floor policy. Gate 6 public publish remains explicit-human-only.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate WAYS automated QC gates and WIP limits.")
    parser.add_argument("--board", required=True, type=Path, help="Board JSON with cards[] or dashboard data with candidates[]")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root used to resolve relative artifacts")
    parser.add_argument("--out", type=Path, help="Write JSON report here")
    parser.add_argument("--checklist-out", type=Path, help="Write the human-readable runner checklist here")
    args = parser.parse_args(argv)

    board = json.loads(args.board.read_text(encoding="utf-8"))
    report = evaluate_board(board, root=args.root)
    payload = json.dumps(report, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    if args.checklist_out:
        args.checklist_out.parent.mkdir(parents=True, exist_ok=True)
        write_checklist(args.checklist_out)
    return 1 if report["summary"]["status"] == "block" else 0


if __name__ == "__main__":
    raise SystemExit(main())
