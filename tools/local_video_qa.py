#!/usr/bin/env python3
"""First-pass QA proxy for local short-form video candidates.

The tool is intentionally publish-safe: it reads a candidate video and writes a QA
folder with ffprobe JSON, a contact sheet, optional VLM/visual-preservation notes,
and a machine-readable score/blocker report. It never uploads or publishes.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import math
import os
import shlex
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_REVIEW_PROMPT = (
    "Review this contact sheet for a vertical short-form video. Return JSON with "
    "keys: text_or_logo_present (bool), visual_artifacts (array), anatomy_or_morphing_issues "
    "(array), caption_readability_issues (array), summary (string), severity (pass|warn|block). "
    "Be harsh: generated text, logos, watermarks, malformed animals, duplicated limbs/fins, "
    "jitter/melting, double captions, or clutter are blockers."
)


class QAError(RuntimeError):
    pass


def run(cmd: list[str], *, capture: bool = False, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            check=True,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
    except FileNotFoundError as exc:
        raise QAError(f"missing command: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise QAError(f"command failed: {' '.join(cmd)}\n{detail}") from exc


def capture_json(cmd: list[str]) -> Any:
    proc = run(cmd, capture=True)
    return json.loads(proc.stdout)


def ffprobe(video: Path) -> dict[str, Any]:
    return capture_json([
        "ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(video)
    ])


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, str) and "/" in value:
            a, b = value.split("/", 1)
            return float(a) / float(b) if float(b) else default
        return float(value)
    except Exception:
        return default


def video_stream(probe: dict[str, Any]) -> dict[str, Any] | None:
    return next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), None)


def audio_streams(probe: dict[str, Any]) -> list[dict[str, Any]]:
    return [s for s in probe.get("streams", []) if s.get("codec_type") == "audio"]


def load_expected_duration(args: argparse.Namespace) -> float | None:
    if args.expected_duration is not None:
        return float(args.expected_duration)
    if not args.manifest:
        return None
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    shots = data.get("shots") or data.get("segments") or []
    total = 0.0
    for item in shots:
        total += as_float(item.get("duration"), 0.0)
    return total or None


def generate_contact_sheet(video: Path, out: Path, every: float, columns: int, rows: int) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = f"fps=1/{every},scale=270:-1:flags=lanczos,tile={columns}x{rows}"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf", vf, "-frames:v", "1", str(out)])


def extract_rgb(path: Path, *, seconds: float | None = None, size: int = 64) -> bytes:
    cmd = ["ffmpeg", "-v", "error"]
    if seconds is not None:
        cmd += ["-ss", f"{seconds:.3f}"]
    cmd += ["-i", str(path), "-frames:v", "1", "-vf", f"scale={size}:{size}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    proc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.stdout


def rgb_similarity(a: bytes, b: bytes) -> dict[str, float]:
    n = min(len(a), len(b))
    if n == 0:
        return {"rmse": 1.0, "cosine": 0.0, "score": 0.0}
    a = a[:n]
    b = b[:n]
    sse = sum((x - y) ** 2 for x, y in zip(a, b))
    rmse = math.sqrt(sse / n) / 255.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    cosine = dot / (na * nb) if na and nb else 0.0
    score = max(0.0, min(1.0, (cosine * 0.65) + ((1.0 - rmse) * 0.35)))
    return {"rmse": round(rmse, 4), "cosine": round(cosine, 4), "score": round(score, 4)}


def source_preservation_proxy(source_image: Path, video: Path, duration: float) -> dict[str, Any]:
    source_rgb = extract_rgb(source_image)
    sample_times = sorted(set([0.1, max(0.1, duration / 2), max(0.1, duration - 0.25)]))
    samples = []
    for t in sample_times:
        frame_rgb = extract_rgb(video, seconds=t)
        samples.append({"time": round(t, 3), **rgb_similarity(source_rgb, frame_rgb)})
    avg = sum(s["score"] for s in samples) / len(samples)
    return {
        "method": "64x64 RGB cosine/RMSE proxy; use CLIP/DINO when available for semantic preservation",
        "source_image": str(source_image),
        "samples": samples,
        "average_score": round(avg, 4),
        "severity": "warn" if avg < 0.55 else "pass",
    }


def run_vlm_command(command_template: str, contact_sheet: Path) -> dict[str, Any]:
    command = command_template.format(image=shlex.quote(str(contact_sheet)), contact_sheet=shlex.quote(str(contact_sheet)))
    proc = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        return {"mode": "command", "severity": "warn", "error": proc.stderr.strip() or proc.stdout.strip()}
    text = proc.stdout.strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = {"raw_output": text}
    payload.setdefault("mode", "command")
    payload.setdefault("severity", "warn")
    return payload


def run_openai_vlm(base_url: str, model: str, api_key: str, contact_sheet: Path, prompt: str) -> dict[str, Any]:
    image_b64 = base64.b64encode(contact_sheet.read_bytes()).decode("ascii")
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ],
        }],
        "temperature": 0,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"mode": "openai-compatible", "severity": "warn", "error": str(exc)}
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {"raw_output": content}
    parsed.setdefault("mode", "openai-compatible")
    parsed.setdefault("severity", "warn")
    return parsed


def evaluate(args: argparse.Namespace, probe: dict[str, Any], contact_sheet: Path | None) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}
    score = 100

    vs = video_stream(probe)
    audios = audio_streams(probe)
    duration = as_float(probe.get("format", {}).get("duration"), 0.0)
    expected_duration = load_expected_duration(args)

    if not vs:
        blockers.append("no video stream")
        score -= 60
    else:
        width, height = int(vs.get("width") or 0), int(vs.get("height") or 0)
        fps = as_float(vs.get("avg_frame_rate") or vs.get("r_frame_rate"), 0.0)
        checks["video"] = {
            "codec": vs.get("codec_name"),
            "width": width,
            "height": height,
            "fps": round(fps, 3),
            "duration": duration,
            "pix_fmt": vs.get("pix_fmt"),
        }
        if height <= width:
            blockers.append(f"not vertical: {width}x{height}")
            score -= 25
        elif width < args.min_width or height < args.min_height:
            warnings.append(f"low resolution for Shorts: {width}x{height}; preferred >= {args.min_width}x{args.min_height}")
            score -= 8
        if fps and fps < args.min_fps:
            warnings.append(f"low frame rate: {fps:.2f} fps")
            score -= 5

    checks["duration"] = {"actual": duration, "expected": expected_duration, "tolerance": args.duration_tolerance}
    if expected_duration is not None:
        delta = abs(duration - expected_duration)
        checks["duration"]["delta"] = round(delta, 3)
        if delta > args.duration_tolerance:
            blockers.append(f"duration mismatch: actual {duration:.3f}s vs expected {expected_duration:.3f}s")
            score -= 20

    if args.require_audio and not audios:
        blockers.append("missing audio stream")
        score -= 25
    elif audios:
        a = audios[0]
        checks["audio"] = {
            "codec": a.get("codec_name"),
            "sample_rate": int(a.get("sample_rate") or 0),
            "channels": int(a.get("channels") or 0),
        }
        if checks["audio"]["sample_rate"] and checks["audio"]["sample_rate"] != 48000:
            warnings.append(f"audio sample rate is {checks['audio']['sample_rate']} Hz; preferred 48000 Hz")
            score -= 3
    else:
        checks["audio"] = None

    if contact_sheet:
        checks["contact_sheet"] = {"path": str(contact_sheet), "generated": contact_sheet.exists()}
        if not contact_sheet.exists():
            blockers.append("contact sheet was not generated")
            score -= 15
    else:
        checks["contact_sheet"] = {"generated": False}

    score = max(0, min(100, score))
    return {"score": score, "blockers": blockers, "warnings": warnings, "checks": checks}


def write_readme(path: Path, report: dict[str, Any]) -> None:
    verdict = "BLOCK" if report["blockers"] else "PASS_WITH_WARNINGS" if report["warnings"] else "PASS"
    lines = [
        f"# Local video QA: {Path(report['input']).name}",
        "",
        f"Generated: {report['generated_at']}",
        f"Verdict: **{verdict}**",
        f"Score: **{report['score']}/100**",
        "",
        "## Blockers",
    ]
    lines += [f"- {b}" for b in report["blockers"]] or ["- none"]
    lines += ["", "## Warnings"]
    lines += [f"- {w}" for w in report["warnings"]] or ["- none"]
    lines += ["", "## Artifacts", f"- JSON report: `{Path(report['json_report']).name}`", f"- ffprobe: `{Path(report['ffprobe_json']).name}`"]
    sheet = report.get("checks", {}).get("contact_sheet", {}).get("path")
    if sheet:
        lines.append(f"- Contact sheet: `{Path(sheet).name}`")
    lines += [
        "",
        "## Required manual/human review before publish",
        "- Play the full candidate at phone size; first 2 seconds must read instantly.",
        "- Inspect contact sheet for generated text, logos, watermarks, UI, double captions, malformed animals, duplicated fins/limbs, melting, shimmer, or jitter.",
        "- Verify captions are intentional, readable, and not colliding with platform UI.",
        "- For animal/source-preservation shots, prefer CLIP/DINO or full-frame VLM review if this proxy only ran RGB similarity.",
        "",
        "This QA proxy does not auto-publish.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QA local short-form video candidates without publishing.")
    parser.add_argument("--input", required=True, type=Path, help="Candidate .mp4/.mov/.webm to QA")
    parser.add_argument("--outdir", type=Path, help="QA output directory; default: <input parent>/qa_proxy_<stem>")
    parser.add_argument("--manifest", type=Path, help="Optional manifest with shots[].duration for duration alignment")
    parser.add_argument("--expected-duration", type=float, help="Expected total duration in seconds")
    parser.add_argument("--duration-tolerance", type=float, default=0.35)
    parser.add_argument("--min-width", type=int, default=720)
    parser.add_argument("--min-height", type=int, default=1280)
    parser.add_argument("--min-fps", type=float, default=23.0)
    parser.add_argument("--require-audio", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--contact-every", type=float, default=1.0, help="Seconds between contact-sheet samples")
    parser.add_argument("--tile", default="6x4", help="Contact sheet tile, e.g. 6x4")
    parser.add_argument("--source-image", type=Path, help="Optional source still for RGB preservation proxy")
    parser.add_argument("--vlm-command", help="Optional shell command for contact-sheet scan; use {image} placeholder; stdout should be JSON")
    parser.add_argument("--openai-vlm-url", help="Optional OpenAI-compatible base URL, e.g. http://host:8000/v1")
    parser.add_argument("--vlm-model", default=os.environ.get("QA_VLM_MODEL", "qwen2.5-vl"))
    parser.add_argument("--vlm-api-key", default=os.environ.get("QA_VLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or "none")
    parser.add_argument("--review-prompt", default=DEFAULT_REVIEW_PROMPT)
    args = parser.parse_args(argv)

    video = args.input.resolve()
    if not video.exists():
        raise SystemExit(f"missing input video: {video}")
    outdir = (args.outdir or (video.parent / f"qa_proxy_{video.stem}")).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    ffprobe_path = outdir / "ffprobe.json"
    contact_sheet = outdir / "contact_sheet.jpg"
    json_report = outdir / "qa_report.json"
    readme = outdir / "README_QA.md"

    try:
        probe = ffprobe(video)
        ffprobe_path.write_text(json.dumps(probe, indent=2), encoding="utf-8")
        cols, rows = (int(x) for x in args.tile.lower().split("x", 1))
        generate_contact_sheet(video, contact_sheet, args.contact_every, cols, rows)
        report = evaluate(args, probe, contact_sheet)
        report.update({
            "input": str(video),
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
            "json_report": str(json_report),
            "ffprobe_json": str(ffprobe_path),
            "readme_qa": str(readme),
            "publish_action": "none",
        })

        duration = report["checks"].get("duration", {}).get("actual") or 0.0
        if args.source_image:
            try:
                preservation = source_preservation_proxy(args.source_image.resolve(), video, duration)
                report["checks"]["source_preservation_proxy"] = preservation
                if preservation["severity"] == "warn":
                    report["warnings"].append("source preservation proxy is weak; run CLIP/DINO/VLM review for animal anatomy/source fidelity")
                    report["score"] = max(0, report["score"] - 5)
            except Exception as exc:
                report["warnings"].append(f"source preservation proxy failed: {exc}")

        if args.vlm_command:
            vlm = run_vlm_command(args.vlm_command, contact_sheet)
            report["checks"]["vlm_scan"] = vlm
        elif args.openai_vlm_url:
            vlm = run_openai_vlm(args.openai_vlm_url, args.vlm_model, args.vlm_api_key, contact_sheet, args.review_prompt)
            report["checks"]["vlm_scan"] = vlm
        else:
            report["checks"]["vlm_scan"] = {
                "mode": "not_configured",
                "severity": "warn",
                "summary": "Contact sheet generated; configure --vlm-command or --openai-vlm-url for automated text/logo/artifact scan.",
            }

        vlm_scan = report["checks"].get("vlm_scan") or {}
        if str(vlm_scan.get("severity", "")).lower() == "block":
            report["blockers"].append("VLM scan reported blocking visual issues")
            report["score"] = max(0, report["score"] - 20)
        elif str(vlm_scan.get("severity", "")).lower() == "warn":
            if vlm_scan.get("mode") != "not_configured":
                report["warnings"].append("VLM scan reported warnings; inspect contact sheet")
                report["score"] = max(0, report["score"] - 5)

        json_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        write_readme(readme, report)
        print(json.dumps({"score": report["score"], "blockers": report["blockers"], "warnings": report["warnings"], "report": str(json_report), "readme_qa": str(readme)}, indent=2))
        return 1 if report["blockers"] else 0
    except QAError as exc:
        error_report = {
            "input": str(video),
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
            "score": 0,
            "blockers": [str(exc)],
            "warnings": [],
            "checks": {},
            "json_report": str(json_report),
            "ffprobe_json": str(ffprobe_path),
            "readme_qa": str(readme),
            "publish_action": "none",
        }
        json_report.write_text(json.dumps(error_report, indent=2), encoding="utf-8")
        write_readme(readme, error_report)
        print(json.dumps(error_report, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
