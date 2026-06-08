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

THRESHOLD_KEYS = {
    "clip_preservation_min",
    "dino_structure_min",
    "temporal_consistency_max",
    "motion_magnitude_low",
    "motion_magnitude_high",
}


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
    """Legacy helper kept for compatibility tests and emergency debugging only."""
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


def load_thresholds(path: Path | None) -> tuple[dict[str, Any] | None, dict[str, Any], bool]:
    """Return (thresholds, thresholds_used_echo, metric_report_only)."""
    if not path:
        return None, {"mode": "report_only", "path": None, "loaded": False, "reason": "no thresholds file supplied"}, True
    path = path.resolve()
    if not path.exists():
        return None, {"mode": "report_only", "path": str(path), "loaded": False, "reason": "thresholds file missing"}, True
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise QAError(f"malformed thresholds file: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise QAError(f"malformed thresholds file: {path}: expected JSON object")
    for key in THRESHOLD_KEYS:
        if key in data:
            try:
                float(data[key])
            except Exception as exc:
                raise QAError(f"malformed thresholds file: {path}: {key} must be numeric") from exc
    if "fail_closed" in data and not isinstance(data["fail_closed"], bool):
        raise QAError(f"malformed thresholds file: {path}: fail_closed must be boolean")
    if "blocking_enabled" in data and not isinstance(data["blocking_enabled"], bool):
        raise QAError(f"malformed thresholds file: {path}: blocking_enabled must be boolean")
    data.setdefault("fail_closed", True)
    data.setdefault("blocking_enabled", True)
    metric_report_only = not bool(data["blocking_enabled"])
    mode = "blocking" if not metric_report_only else "advisory"
    reason = None if not metric_report_only else "threshold config has blocking_enabled=false"
    echo = {"mode": mode, "path": str(path), "loaded": True, **data}
    if reason:
        echo["reason"] = reason
    return data, echo, metric_report_only


def extract_sample_frames(video: Path, outdir: Path, sample_fps: float) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    fps = max(0.1, float(sample_fps))
    pattern = outdir / "frame_%05d.jpg"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf", f"fps={fps}", "-q:v", "2", str(pattern)])
    return sorted(outdir.glob("frame_*.jpg"))


def _round_or_none(value: float | None, ndigits: int = 6) -> float | None:
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return round(float(value), ndigits)


def _cosine(a: Any, b: Any) -> float:
    import torch
    return float(torch.nn.functional.cosine_similarity(a, b, dim=-1).detach().cpu().item())


def compute_clip_preservation(source_image: Path, frames: list[Path]) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        import torch
        import open_clip
        from PIL import Image
    except Exception as exc:
        return {"available": False, "error": f"open_clip_torch/PIL unavailable: {exc}"}, {"per_frame": []}
    if not frames:
        return {"available": False, "error": "no sampled frames"}, {"per_frame": []}
    try:
        model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
        model.eval()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        with torch.no_grad():
            src = preprocess(Image.open(source_image).convert("RGB")).unsqueeze(0).to(device)
            src_emb = model.encode_image(src)
            src_emb = src_emb / src_emb.norm(dim=-1, keepdim=True)
            values = []
            per_frame = []
            for frame in frames:
                img = preprocess(Image.open(frame).convert("RGB")).unsqueeze(0).to(device)
                emb = model.encode_image(img)
                emb = emb / emb.norm(dim=-1, keepdim=True)
                val = _cosine(src_emb, emb)
                values.append(val)
                per_frame.append({"frame": frame.name, "cosine": round(val, 6)})
        return {"available": True, "method": "open_clip ViT-B-32/laion2b_s34b_b79k", "min": round(min(values), 6), "mean": round(sum(values) / len(values), 6)}, {"per_frame": per_frame}
    except Exception as exc:
        return {"available": False, "error": str(exc)}, {"per_frame": []}


def compute_dino_structure(source_image: Path, frames: list[Path]) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        import torch
        from PIL import Image
        from torchvision import transforms
    except Exception as exc:
        return {"available": False, "error": f"torch/torchvision/PIL unavailable: {exc}"}, {"per_frame": []}
    if not frames:
        return {"available": False, "error": "no sampled frames"}, {"per_frame": []}
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14", pretrained=True)
        model.eval().to(device)
        preprocess = transforms.Compose([
            transforms.Resize(256, interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ])
        with torch.no_grad():
            src = preprocess(Image.open(source_image).convert("RGB")).unsqueeze(0).to(device)
            src_emb = model(src)
            src_emb = src_emb / src_emb.norm(dim=-1, keepdim=True)
            values = []
            per_frame = []
            for frame in frames:
                img = preprocess(Image.open(frame).convert("RGB")).unsqueeze(0).to(device)
                emb = model(img)
                emb = emb / emb.norm(dim=-1, keepdim=True)
                val = _cosine(src_emb, emb)
                values.append(val)
                per_frame.append({"frame": frame.name, "cosine": round(val, 6)})
        return {"available": True, "method": "DINOv2 vits14 via torch.hub", "min": round(min(values), 6), "mean": round(sum(values) / len(values), 6)}, {"per_frame": per_frame}
    except Exception as exc:
        return {"available": False, "error": str(exc)}, {"per_frame": []}


def compute_motion_and_temporal(frames: list[Path]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if len(frames) < 2:
        unavailable = {"available": False, "error": "need at least two sampled frames"}
        return unavailable, unavailable, {"per_pair": []}
    try:
        import cv2
        import numpy as np
    except Exception as exc:
        unavailable = {"available": False, "error": f"opencv/numpy unavailable: {exc}"}
        return unavailable, unavailable, {"per_pair": []}

    lpips_model = None
    lpips_error = None
    try:
        import lpips
        import torch
        lpips_model = lpips.LPIPS(net="alex")
        lpips_model.eval()
        if torch.cuda.is_available():
            lpips_model = lpips_model.cuda()
    except Exception as exc:  # LPIPS is optional; Farneback still gives motion and absdiff fallback.
        lpips_error = str(exc)

    def lpips_tensor(rgb: Any) -> Any:
        import torch
        tensor = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0).float()
        tensor = (tensor * 2.0) - 1.0
        if lpips_model is not None and next(lpips_model.parameters()).is_cuda:
            tensor = tensor.cuda()
        return tensor

    pair_debug: list[dict[str, Any]] = []
    flow_values: list[float] = []
    diff_values: list[float] = []
    lpips_values: list[float] = []
    prev_gray = None
    prev_rgb = None
    for frame in frames:
        bgr = cv2.imread(str(frame))
        if bgr is None:
            continue
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype("float32") / 255.0
        if prev_gray is not None and prev_rgb is not None:
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            flow_mean = float(np.mean(mag))
            diff_mean = float(np.mean(np.abs(rgb - prev_rgb)))
            flow_values.append(flow_mean)
            diff_values.append(diff_mean)
            item = {"to_frame": frame.name, "flow_mean": round(flow_mean, 6), "frame_absdiff_mean": round(diff_mean, 6)}
            if lpips_model is not None:
                try:
                    with __import__("torch").no_grad():
                        lpips_val = float(lpips_model(lpips_tensor(prev_rgb), lpips_tensor(rgb)).detach().cpu().item())
                    lpips_values.append(lpips_val)
                    item["lpips"] = round(lpips_val, 6)
                except Exception as exc:
                    lpips_error = str(exc)
            pair_debug.append(item)
        prev_gray = gray
        prev_rgb = rgb

    if not flow_values:
        unavailable = {"available": False, "error": "could not compute frame pairs"}
        return unavailable, unavailable, {"per_pair": pair_debug}
    motion = {"available": True, "method": "opencv Farneback optical flow", "mean": round(sum(flow_values) / len(flow_values), 6)}
    if lpips_values:
        temporal = {"available": True, "method": "LPIPS alex frame-to-frame mean", "mean": round(sum(lpips_values) / len(lpips_values), 6)}
    else:
        temporal = {
            "available": True,
            "method": "mean frame-to-frame absolute difference proxy; install lpips for neural LPIPS scoring",
            "mean": round(sum(diff_values) / len(diff_values), 6),
        }
        if lpips_error:
            temporal["lpips_unavailable"] = lpips_error
    return temporal, motion, {"per_pair": pair_debug}


def compute_metric_bundle(video: Path, source_image: Path | None, frame_sample_fps: float) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    warnings: list[str] = []
    metrics: dict[str, Any] = {
        "clip_preservation": {"available": False, "skipped": True, "reason": "no source image provided"},
        "dino_structure": {"available": False, "skipped": True, "reason": "no source image provided"},
        "temporal_consistency": {"available": False, "error": "not computed"},
        "motion_magnitude": {"available": False, "error": "not computed"},
        "artifact_flags": [],
    }
    debug: dict[str, Any] = {"frame_sample_fps": frame_sample_fps, "frames": [], "clip_preservation": {}, "dino_structure": {}, "motion_temporal": {}}
    with tempfile.TemporaryDirectory(prefix="ways_qa_frames_") as td:
        frames = extract_sample_frames(video, Path(td), frame_sample_fps)
        debug["frames"] = [f.name for f in frames]
        temporal, motion, mt_debug = compute_motion_and_temporal(frames)
        metrics["temporal_consistency"] = temporal
        metrics["motion_magnitude"] = motion
        debug["motion_temporal"] = mt_debug
        if source_image:
            if not source_image.exists():
                warnings.append(f"source image missing; preservation metrics skipped: {source_image}")
                metrics["clip_preservation"] = {"available": False, "skipped": True, "reason": f"source image missing: {source_image}"}
                metrics["dino_structure"] = {"available": False, "skipped": True, "reason": f"source image missing: {source_image}"}
            else:
                clip, clip_debug = compute_clip_preservation(source_image, frames)
                dino, dino_debug = compute_dino_structure(source_image, frames)
                metrics["clip_preservation"] = clip
                metrics["dino_structure"] = dino
                debug["clip_preservation"] = clip_debug
                debug["dino_structure"] = dino_debug
                if not clip.get("available"):
                    warnings.append(f"CLIP preservation unavailable: {clip.get('error', clip.get('reason', 'unknown'))}")
                if not dino.get("available"):
                    warnings.append(f"DINO structure unavailable: {dino.get('error', dino.get('reason', 'unknown'))}")
        if not temporal.get("available"):
            warnings.append(f"temporal consistency unavailable: {temporal.get('error', 'unknown')}")
        if not motion.get("available"):
            warnings.append(f"motion magnitude unavailable: {motion.get('error', 'unknown')}")
    return metrics, debug, warnings


def threshold_value(thresholds: dict[str, Any] | None, key: str) -> float | None:
    if not thresholds or key not in thresholds:
        return None
    return float(thresholds[key])


def metric_number(metric: dict[str, Any], field: str = "mean") -> float | None:
    if not isinstance(metric, dict) or not metric.get("available"):
        return None
    value = metric.get(field)
    return float(value) if value is not None else None


def metric_unavailable_reason(metric: dict[str, Any]) -> str:
    if not isinstance(metric, dict):
        return "metric block missing"
    return str(metric.get("error") or metric.get("reason") or "metric unavailable")


def required_metric_value(
    metrics: dict[str, Any],
    metric_name: str,
    field: str,
    blockers: list[str],
    *,
    fail_closed: bool,
) -> float | None:
    metric = metrics.get(metric_name, {})
    val = metric_number(metric, field)
    if val is None and fail_closed:
        blockers.append(f"{metric_name} {field} unavailable while blocking thresholds require it: {metric_unavailable_reason(metric)}")
    return val


def apply_metric_thresholds(metrics: dict[str, Any], thresholds: dict[str, Any] | None, *, report_only: bool) -> list[str]:
    if report_only or not thresholds:
        return []
    blockers: list[str] = []
    fail_closed = bool(thresholds.get("fail_closed", True))
    clip_min = threshold_value(thresholds, "clip_preservation_min")
    if clip_min is not None:
        val = required_metric_value(metrics, "clip_preservation", "min", blockers, fail_closed=fail_closed)
        if val is not None and val < clip_min:
            blockers.append(f"clip_preservation min {val:.4f} below threshold {clip_min:.4f}")
    dino_min = threshold_value(thresholds, "dino_structure_min")
    if dino_min is not None:
        val = required_metric_value(metrics, "dino_structure", "min", blockers, fail_closed=fail_closed)
        if val is not None and val < dino_min:
            blockers.append(f"dino_structure min {val:.4f} below threshold {dino_min:.4f}")
    temporal_max = threshold_value(thresholds, "temporal_consistency_max")
    if temporal_max is not None:
        val = required_metric_value(metrics, "temporal_consistency", "mean", blockers, fail_closed=fail_closed)
        if val is not None and val > temporal_max:
            blockers.append(f"temporal_consistency mean {val:.4f} above threshold {temporal_max:.4f}")
    motion_low = threshold_value(thresholds, "motion_magnitude_low")
    if motion_low is not None:
        val = required_metric_value(metrics, "motion_magnitude", "mean", blockers, fail_closed=fail_closed)
        if val is not None and val < motion_low:
            blockers.append(f"motion_magnitude mean {val:.4f} below threshold {motion_low:.4f}")
    motion_high = threshold_value(thresholds, "motion_magnitude_high")
    if motion_high is not None:
        val = required_metric_value(metrics, "motion_magnitude", "mean", blockers, fail_closed=fail_closed)
        if val is not None and val > motion_high:
            blockers.append(f"motion_magnitude mean {val:.4f} above threshold {motion_high:.4f}")
    return blockers


def metric_warnings(metrics: dict[str, Any], thresholds: dict[str, Any] | None) -> list[str]:
    warnings: list[str] = []
    motion_low = threshold_value(thresholds, "motion_magnitude_low")
    motion = metric_number(metrics.get("motion_magnitude", {}), "mean")
    if motion_low is not None and motion is not None and motion < motion_low:
        warnings.append(f"dead-render warning: motion_magnitude mean {motion:.4f} below low band {motion_low:.4f}")
    return warnings


def artifact_flags_from_vlm(vlm_scan: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    if not isinstance(vlm_scan, dict):
        return flags
    for key in ("visual_artifacts", "anatomy_or_morphing_issues", "caption_readability_issues"):
        value = vlm_scan.get(key)
        if isinstance(value, list):
            flags.extend(str(v) for v in value if str(v).strip())
    if vlm_scan.get("text_or_logo_present") is True:
        flags.append("text_or_logo_present")
    if str(vlm_scan.get("severity", "")).lower() == "block":
        flags.append("vlm_severity_block")
    return flags


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
    lines += ["", "## Metrics"]
    metrics = report.get("metrics") or {}
    if metrics:
        for key in ("clip_preservation", "dino_structure", "temporal_consistency", "motion_magnitude"):
            metric = metrics.get(key, {})
            lines.append(f"- `{key}`: `{json.dumps(metric, sort_keys=True)}`")
        lines.append(f"- `artifact_flags`: `{json.dumps(metrics.get('artifact_flags', []))}`")
        lines.append(f"- Thresholds: `{json.dumps(report.get('thresholds_used', {}), sort_keys=True)}`")
    else:
        lines.append("- none")
    lines += ["", "## Artifacts", f"- JSON report: `{Path(report['json_report']).name}`", f"- ffprobe: `{Path(report['ffprobe_json']).name}`"]
    sheet = report.get("checks", {}).get("contact_sheet", {}).get("path")
    if sheet:
        lines.append(f"- Contact sheet: `{Path(sheet).name}`")
    if report.get("metrics_debug_json"):
        lines.append(f"- Metrics debug: `{Path(report['metrics_debug_json']).name}`")
    lines += [
        "",
        "## Required manual/human review before publish",
        "- Play the full candidate at phone size; first 2 seconds must read instantly.",
        "- Inspect contact sheet for generated text, logos, watermarks, UI, double captions, malformed animals, duplicated fins/limbs, melting, shimmer, or jitter.",
        "- Verify captions are intentional, readable, and not colliding with platform UI.",
        "- Treat CLIP/DINO/temporal/motion metrics as advisory unless thresholds show calibration agreement with human labels.",
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
    parser.add_argument("--source-image", type=Path, help="Optional approved source still for CLIP/DINO preservation metrics")
    parser.add_argument("--thresholds", type=Path, help="Calibrated QA thresholds JSON. Missing/omitted file leaves new metrics report-only.")
    parser.add_argument("--report-only", action="store_true", help="Compute metrics and warnings but do not add metric blockers.")
    parser.add_argument("--frame-sample-fps", type=float, default=4.0, help="FPS used to sample frames for metric computation")
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
    metrics_debug_json = outdir / "metrics_debug.json"
    readme = outdir / "README_QA.md"

    try:
        thresholds, thresholds_used, metric_report_only = load_thresholds(args.thresholds)
        metric_report_only = bool(metric_report_only or args.report_only)
        if args.report_only:
            thresholds_used = {**thresholds_used, "mode": "report_only", "forced_by_flag": True}

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
            "metrics_debug_json": str(metrics_debug_json),
            "readme_qa": str(readme),
            "publish_action": "none",
            "thresholds_used": thresholds_used,
        })

        metrics, metrics_debug, metric_compute_warnings = compute_metric_bundle(
            video,
            args.source_image.resolve() if args.source_image else None,
            args.frame_sample_fps,
        )
        report["metrics"] = metrics
        report["warnings"].extend(metric_compute_warnings)

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
        report["metrics"]["artifact_flags"] = artifact_flags_from_vlm(vlm_scan)
        if str(vlm_scan.get("severity", "")).lower() == "block":
            report["blockers"].append("VLM scan reported blocking visual issues")
            report["score"] = max(0, report["score"] - 20)
        elif str(vlm_scan.get("severity", "")).lower() == "warn":
            if vlm_scan.get("mode") != "not_configured":
                report["warnings"].append("VLM scan reported warnings; inspect contact sheet")
                report["score"] = max(0, report["score"] - 5)

        report["warnings"].extend(metric_warnings(report["metrics"], thresholds))
        metric_blockers = apply_metric_thresholds(report["metrics"], thresholds, report_only=metric_report_only)
        if metric_blockers:
            report["blockers"].extend(metric_blockers)
            report["score"] = max(0, report["score"] - (10 * len(metric_blockers)))

        metrics_debug_json.write_text(json.dumps(metrics_debug, indent=2), encoding="utf-8")
        json_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        write_readme(readme, report)
        print(json.dumps({
            "score": report["score"],
            "blockers": report["blockers"],
            "warnings": report["warnings"],
            "metrics": report["metrics"],
            "thresholds_used": report["thresholds_used"],
            "report": str(json_report),
            "readme_qa": str(readme),
        }, indent=2))
        return 1 if report["blockers"] else 0
    except QAError as exc:
        error_report = {
            "input": str(video),
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
            "score": 0,
            "blockers": [str(exc)],
            "warnings": [],
            "checks": {},
            "metrics": {},
            "thresholds_used": {},
            "json_report": str(json_report),
            "ffprobe_json": str(ffprobe_path),
            "metrics_debug_json": str(metrics_debug_json),
            "readme_qa": str(readme),
            "publish_action": "none",
        }
        json_report.write_text(json.dumps(error_report, indent=2), encoding="utf-8")
        write_readme(readme, error_report)
        print(json.dumps(error_report, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
