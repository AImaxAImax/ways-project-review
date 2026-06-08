from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class PreflightError(RuntimeError):
    """Raised when a GPU batch prerequisite is missing."""


@dataclass
class ShotConfig:
    id: str
    image: Path
    duration: float
    caption: str = ""
    seed: int = 0
    prompt: str = ""
    clip: Path | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, base_dir: Path) -> "ShotConfig":
        image_value = data.get("image") or data.get("path") or data.get("source_image")
        if not image_value:
            raise ValueError("shot is missing image/path/source_image")
        clip_value = data.get("clip")
        return cls(
            id=str(data["id"]),
            image=_resolve_path(image_value, base_dir),
            duration=float(data.get("duration", 0)),
            caption=str(data.get("caption", "")),
            seed=int(data.get("seed", 0)),
            prompt=str(data.get("prompt", "")),
            clip=_resolve_path(clip_value, base_dir) if clip_value else None,
        )

    def to_manifest_dict(self, project_root: Path | None = None) -> dict[str, Any]:
        image: str
        if project_root is not None:
            try:
                image = str(self.image.relative_to(project_root))
            except ValueError:
                image = str(self.image)
        else:
            image = str(self.image)
        out = {
            "id": self.id,
            "image": image,
            "duration": self.duration,
            "caption": self.caption,
            "seed": self.seed,
            "prompt": self.prompt,
        }
        if self.clip is not None:
            try:
                out["clip"] = str(self.clip.relative_to(project_root)) if project_root is not None else str(self.clip)
            except ValueError:
                out["clip"] = str(self.clip)
        return out


@dataclass
class HarnessConfig:
    project_root: Path
    slug: str
    output_dir: Path
    voiceover: Path
    workflow: Path
    comfy_url: str = "http://127.0.0.1:8188"
    negative_prompt: str = ""
    render_settings: dict[str, Any] = field(default_factory=dict)
    workflow_overrides: dict[str, Any] = field(default_factory=dict)
    shots: list[ShotConfig] = field(default_factory=list)
    qa_gate: list[str] = field(default_factory=list)
    required_nodes: list[str] = field(default_factory=lambda: ["6", "7", "39", "57", "58", "61", "62", "63"])
    required_node_classes: list[str] = field(default_factory=lambda: [
        "VAELoader",
        "UnetLoaderGGUF",
        "LoraLoaderModelOnly",
        "CLIPLoader",
        "CLIPTextEncode",
        "KSamplerAdvanced",
        "LoadImage",
        "WanImageToVideo",
        "SaveVideo",
    ])
    required_vae: str = "wan_2.1_vae.safetensors"
    writable_dirs: list[Path] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, base_dir: Path | None = None) -> "HarnessConfig":
        base = Path(base_dir or ".").resolve()
        project_root = _resolve_path(data.get("project_root", "."), base)
        output_dir = _resolve_path(data.get("output_dir", "outputs/wan22_render"), project_root)
        voiceover = _resolve_path(data.get("voiceover", "voiceover.mp3"), project_root)
        workflow = _resolve_path(data.get("workflow", "workflow.json"), project_root)
        shots = [ShotConfig.from_dict(item, base_dir=project_root) for item in data.get("shots", [])]
        return cls(
            project_root=project_root,
            slug=str(data.get("slug", project_root.name)),
            output_dir=output_dir,
            voiceover=voiceover,
            workflow=workflow,
            comfy_url=str(data.get("comfy_url", "http://127.0.0.1:8188")).rstrip("/"),
            negative_prompt=str(data.get("negative_prompt", "")),
            render_settings=dict(data.get("render_settings", {})),
            workflow_overrides=dict(data.get("workflow_overrides", {})),
            shots=shots,
            qa_gate=list(data.get("qa_gate", [])),
            required_nodes=list(data.get("required_nodes", ["6", "7", "39", "57", "58", "61", "62", "63"])),
            required_node_classes=list(data.get("required_node_classes", [
                "VAELoader",
                "UnetLoaderGGUF",
                "LoraLoaderModelOnly",
                "CLIPLoader",
                "CLIPTextEncode",
                "KSamplerAdvanced",
                "LoadImage",
                "WanImageToVideo",
                "SaveVideo",
            ])),
            required_vae=str(data.get("required_vae", "wan_2.1_vae.safetensors")),
            writable_dirs=[_resolve_path(item, project_root) for item in data.get("writable_dirs", [])],
        )

    def to_manifest_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "project_root": str(self.project_root),
            "output_dir": str(self.output_dir),
            "voiceover": str(self.voiceover),
            "workflow": str(self.workflow),
            "comfy_url": self.comfy_url,
            "render_settings": self.render_settings,
            "workflow_overrides": self.workflow_overrides,
            "writable_dirs": [str(path) for path in self.writable_dirs],
            "shots": [shot.to_manifest_dict(self.project_root) for shot in self.shots],
        }


def _resolve_path(value: str | os.PathLike[str], base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def load_harness_config(path: str | os.PathLike[str]) -> HarnessConfig:
    config_path = Path(path).resolve()
    return HarnessConfig.from_dict(json.loads(config_path.read_text(encoding="utf-8")), base_dir=config_path.parent)


def set_dot_path(data: dict[str, Any], dot_path: str, value: Any) -> None:
    parts = dot_path.split(".")
    cursor: Any = data
    for part in parts[:-1]:
        if not isinstance(cursor, dict) or part not in cursor:
            raise KeyError(dot_path)
        cursor = cursor[part]
    if not isinstance(cursor, dict):
        raise KeyError(dot_path)
    cursor[parts[-1]] = value


def get_dot_path(data: dict[str, Any], dot_path: str) -> Any:
    cursor: Any = data
    for part in dot_path.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            raise KeyError(dot_path)
        cursor = cursor[part]
    return cursor


def apply_workflow_overrides(workflow: dict[str, Any], cfg: HarnessConfig, shot: ShotConfig, *, uploaded_image: str) -> dict[str, Any]:
    patched = copy.deepcopy(workflow)
    for dot_path, value in cfg.workflow_overrides.items():
        set_dot_path(patched, dot_path, value)
    settings = cfg.render_settings
    conventional = {
        "62.inputs.image": uploaded_image,
        "63.inputs.width": int(settings.get("wan_width", 432)),
        "63.inputs.height": int(settings.get("wan_height", 768)),
        "63.inputs.length": int(settings.get("wan_length_frames", 25)),
        "6.inputs.text": shot.prompt,
        "7.inputs.text": cfg.negative_prompt,
        "57.inputs.noise_seed": shot.seed,
        "58.inputs.noise_seed": shot.seed + 1000,
        "61.inputs.filename_prefix": f"{cfg.slug}/{shot.id}_{shot.seed}",
    }
    for dot_path, value in conventional.items():
        try:
            set_dot_path(patched, dot_path, value)
        except KeyError:
            continue
    return patched


def build_output_paths(cfg: HarnessConfig) -> dict[str, Path]:
    out = cfg.output_dir
    return {
        "outdir": out,
        "clips_dir": out / "clips",
        "frames_dir": out / "frames",
        "manifest": out / "manifest.json",
        "manifest_partial": out / "manifest_partial.json",
        "silent": out / f"{cfg.slug}_wan22_silent_1080.mp4",
        "master": out / f"{cfg.slug}_wan22_master_1080.mp4",
        "preview": out / f"{cfg.slug}_wan22_preview_720.mp4",
        "contact_sheet": out / f"contact_sheet_{cfg.slug}.jpg",
        "ffprobe_master": out / "ffprobe_master.json",
        "readme_qa": out / "README_QA_FINAL.md",
    }


def write_readme_qa(cfg: HarnessConfig, paths: dict[str, Path], ffprobe: dict[str, Any], *, frames: int) -> None:
    streams = ffprobe.get("streams", []) if isinstance(ffprobe, dict) else []
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    duration = ffprobe.get("format", {}).get("duration", "unknown") if isinstance(ffprobe, dict) else "unknown"
    lines = [
        f"# {cfg.slug} Wan render QA",
        "",
        f"Master: `{paths['master'].name}`",
        f"Preview: `{paths['preview'].name}`",
        f"Contact sheet: `{paths['contact_sheet'].name}`",
        f"Frames: {frames}",
        f"Duration: {duration}",
        f"Video: {video.get('width', '?')}x{video.get('height', '?')}",
        "AAC/audio stream present" if audio else "NO AUDIO STREAM FOUND",
        "",
        "## QA gate",
    ]
    lines.extend(f"- [ ] {item}" for item in cfg.qa_gate)
    paths["readme_qa"].write_text("\n".join(lines) + "\n", encoding="utf-8")


class ComfyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _json(self, path: str, timeout: int = 30) -> Any:
        with urllib.request.urlopen(self.base_url + path, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def system_stats(self) -> Any:
        return self._json("/system_stats", timeout=10)

    def object_info(self) -> Any:
        return self._json("/object_info", timeout=30)

    def models(self, folder: str) -> list[str]:
        try:
            data = self._json(f"/models/{folder}", timeout=30)
        except urllib.error.HTTPError:
            data = self._json(f"/api/experiment/models/{folder}", timeout=30)
        if isinstance(data, dict):
            vals = data.get("models") or data.get(folder) or data.get("data") or []
            return [str(item.get("name", item)) if isinstance(item, dict) else str(item) for item in vals]
        return [str(item.get("name", item)) if isinstance(item, dict) else str(item) for item in data]


def _normalize_model_name(name: str) -> str:
    return name.replace("\\", "/").strip().lower()


def _model_folder_for_key(key: str) -> str | None:
    if key == "vae_name":
        return "vae"
    if key == "unet_name":
        return "unet"
    if key == "lora_name":
        return "loras"
    if key == "clip_name":
        return "clip"
    if key == "ckpt_name":
        return "checkpoints"
    if key == "control_net_name":
        return "controlnet"
    return None


def _model_refs(workflow: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    refs: list[tuple[str, str, str, str]] = []
    for node in workflow.values():
        if not isinstance(node, dict):
            continue
        class_type = str(node.get("class_type", ""))
        inputs = node.get("inputs", {})
        if not isinstance(inputs, dict):
            continue
        for key, value in inputs.items():
            key = str(key)
            folder = _model_folder_for_key(key)
            if folder and isinstance(value, str) and value and not value.startswith("__"):
                refs.append((folder, value, class_type, key))
    seen: set[tuple[str, str, str, str]] = set()
    unique: list[tuple[str, str, str, str]] = []
    for item in refs:
        normalized = (item[0], _normalize_model_name(item[1]), item[2], item[3])
        if normalized not in seen:
            seen.add(normalized)
            unique.append(item)
    return unique


def _choices_from_object_info(object_info: Any, class_type: str, input_key: str) -> list[str]:
    if not isinstance(object_info, dict):
        return []
    node_info = object_info.get(class_type, {})
    if not isinstance(node_info, dict):
        return []
    input_info = node_info.get("input", {})
    if not isinstance(input_info, dict):
        return []
    for section in ("required", "optional"):
        section_info = input_info.get(section, {})
        if not isinstance(section_info, dict) or input_key not in section_info:
            continue
        spec = section_info[input_key]
        if isinstance(spec, list) and spec and isinstance(spec[0], list):
            return [str(item) for item in spec[0]]
    return []


def _matches_model(required: str, available: list[str]) -> bool:
    req = _normalize_model_name(required)
    req_name = req.rsplit("/", 1)[-1]
    for item in available:
        got = _normalize_model_name(item)
        if got == req or got.endswith("/" + req) or got.rsplit("/", 1)[-1] == req_name:
            return True
    return False


def _effective_workflow_for_preflight(cfg: HarnessConfig, workflow: dict[str, Any]) -> dict[str, Any]:
    patched = copy.deepcopy(workflow)
    for dot_path, value in cfg.workflow_overrides.items():
        try:
            set_dot_path(patched, dot_path, value)
        except KeyError:
            raise PreflightError(f"missing workflow override target: {dot_path}")
    return patched


def run_preflight(cfg: HarnessConfig, *, client: Any | None = None) -> dict[str, Any]:
    if not cfg.workflow.exists():
        raise PreflightError(f"missing workflow: {cfg.workflow}")
    if not cfg.voiceover.exists():
        raise PreflightError(f"missing voiceover: {cfg.voiceover}")
    for shot in cfg.shots:
        if not shot.image.exists():
            raise PreflightError(f"missing source still for shot {shot.id}: {shot.image}")

    for outdir in [cfg.output_dir, *cfg.writable_dirs]:
        try:
            outdir.mkdir(parents=True, exist_ok=True)
            probe = outdir / f".preflight_write_test_{int(time.time() * 1000)}"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
        except Exception as exc:
            raise PreflightError(f"output dir not writable: {outdir} ({exc})")

    try:
        workflow = json.loads(cfg.workflow.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PreflightError(f"invalid workflow JSON: {cfg.workflow} ({exc})")
    if not isinstance(workflow, dict) or "nodes" in workflow:
        raise PreflightError(f"workflow is not Comfy API-format JSON: {cfg.workflow}")

    for node_id in cfg.required_nodes:
        if node_id not in workflow:
            raise PreflightError(f"missing workflow node: {node_id}")

    vae_path = "39.inputs.vae_name"
    expected_vae = cfg.required_vae
    override_vae = cfg.workflow_overrides.get(vae_path)
    if override_vae != expected_vae:
        actual = override_vae if override_vae is not None else get_dot_path(workflow, vae_path)
        raise PreflightError(f"wrong VAE override: {vae_path} is {actual!r}, expected {expected_vae!r}")
    effective_workflow = _effective_workflow_for_preflight(cfg, workflow)

    client = client or ComfyClient(cfg.comfy_url)
    try:
        stats = client.system_stats()
    except Exception as exc:
        raise PreflightError(f"Comfy not reachable at {cfg.comfy_url}: {exc}")
    try:
        object_info = client.object_info()
    except Exception as exc:
        raise PreflightError(f"Comfy object_info unavailable at {cfg.comfy_url}: {exc}")
    available_classes = set(object_info.keys()) if isinstance(object_info, dict) else set()
    for class_name in cfg.required_node_classes:
        if class_name not in available_classes:
            raise PreflightError(f"missing Comfy node class: {class_name}")

    for folder, name, class_type, input_key in _model_refs(effective_workflow):
        try:
            available = client.models(folder)
        except Exception:
            available = _choices_from_object_info(object_info, class_type, input_key)
            if not available:
                raise PreflightError(f"Comfy model list unavailable: {folder}")
        if not _matches_model(name, available):
            display_name = name.replace("\\\\", "/")
            raise PreflightError(f"missing Comfy model: {folder}/{display_name}")

    return {
        "ok": True,
        "comfy_url": cfg.comfy_url,
        "system": stats,
        "workflow": str(cfg.workflow),
        "output_dir": str(cfg.output_dir),
        "shots": len(cfg.shots),
    }


def _local_preflight(cfg: HarnessConfig, *, require_clips: bool = False) -> None:
    missing: list[str] = []
    if not cfg.workflow.exists():
        missing.append(f"workflow: {cfg.workflow}")
    if not cfg.voiceover.exists():
        missing.append(f"voiceover: {cfg.voiceover}")
    for shot in cfg.shots:
        if not shot.image.exists():
            missing.append(f"shot {shot.id} image: {shot.image}")
        if require_clips and (shot.clip is None or not shot.clip.exists()):
            missing.append(f"shot {shot.id} clip: {shot.clip or '<missing clip key>'}")
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))


def _manifest(cfg: HarnessConfig, manifest_shots: list[dict[str, Any]], paths: dict[str, Path]) -> dict[str, Any]:
    data = cfg.to_manifest_dict()
    data["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    data["shots"] = manifest_shots
    data["outputs"] = {key: str(path) for key, path in paths.items() if key not in {"outdir", "clips_dir", "frames_dir"}}
    return data


def _output_items(entry: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for node_id, node_out in entry.get("outputs", {}).items():
        for key in ("videos", "gifs", "images"):
            for item in node_out.get(key, []) or []:
                if isinstance(item, dict) and "filename" in item:
                    out.append({**item, "_node_id": node_id, "_kind": key})
    return out


def _requests_generate_wan_clips(cfg: HarnessConfig, paths: dict[str, Path], *, dry_run: bool = False) -> list[dict[str, Any]]:
    _local_preflight(cfg, require_clips=False)
    paths["clips_dir"].mkdir(parents=True, exist_ok=True)
    workflow_base = json.loads(cfg.workflow.read_text(encoding="utf-8"))
    if dry_run:
        return [{**shot.to_manifest_dict(cfg.project_root), "dry_run": True} for shot in cfg.shots]

    import requests

    def post_json(path: str, payload: dict[str, Any], timeout: int = 30) -> dict[str, Any]:
        response = requests.post(cfg.comfy_url + path, json=payload, timeout=timeout)
        if response.status_code >= 400:
            raise RuntimeError(f"{path} {response.status_code}: {response.text[:4000]}")
        return response.json()

    def upload_image(path: Path) -> str:
        with path.open("rb") as f:
            response = requests.post(
                f"{cfg.comfy_url}/upload/image",
                files={"image": (path.name, f, "image/png")},
                data={"type": "input", "overwrite": "true"},
                timeout=180,
            )
        if response.status_code >= 400:
            raise RuntimeError(response.text[:4000])
        return response.json().get("name") or path.name

    def queue_workflow(workflow: dict[str, Any]) -> str:
        data = post_json("/prompt", {"prompt": workflow, "client_id": str(uuid.uuid4())}, timeout=60)
        if data.get("node_errors"):
            raise RuntimeError(json.dumps(data["node_errors"], indent=2)[:8000])
        return data["prompt_id"]

    def wait_for(prompt_id: str, timeout: int = 7200) -> dict[str, Any]:
        start = time.time()
        while time.time() - start < timeout:
            history = requests.get(f"{cfg.comfy_url}/history/{prompt_id}", timeout=30).json()
            if prompt_id in history:
                status = history[prompt_id].get("status", {})
                if status.get("status_str") == "error":
                    raise RuntimeError(json.dumps(status.get("messages", []), indent=2)[:12000])
                return history[prompt_id]
            print(json.dumps({"waiting_s": round(time.time() - start, 1), "prompt_id": prompt_id}), flush=True)
            time.sleep(10)
        raise TimeoutError(prompt_id)

    try:
        post_json("/free", {"unload_models": True, "free_memory": True}, timeout=30)
    except Exception as exc:
        print(json.dumps({"free_warning": repr(exc)}), flush=True)

    manifest_shots: list[dict[str, Any]] = []
    width = int(cfg.render_settings.get("wan_width", 432))
    height = int(cfg.render_settings.get("wan_height", 768))
    length = int(cfg.render_settings.get("wan_length_frames", 25))
    for shot in cfg.shots:
        dest = paths["clips_dir"] / f"shot{shot.id}_wan22_{width}x{height}_{length}f_seed{shot.seed}.mp4"
        if dest.exists() and dest.stat().st_size > 0:
            shot.clip = dest
            meta = {**shot.to_manifest_dict(cfg.project_root), "reused_existing_clip": True}
            manifest_shots.append(meta)
            paths["manifest_partial"].write_text(json.dumps(_manifest(cfg, manifest_shots, paths), indent=2), encoding="utf-8")
            print(json.dumps({"reused": str(dest), "bytes": dest.stat().st_size}), flush=True)
            continue

        image_name = upload_image(shot.image)
        workflow = apply_workflow_overrides(workflow_base, cfg, shot, uploaded_image=image_name)
        prompt_id = queue_workflow(workflow)
        print(json.dumps({"queued": prompt_id, "shot": shot.id, "seed": shot.seed, "image_name": image_name}), flush=True)
        entry = wait_for(prompt_id)
        outs = _output_items(entry)
        if not outs:
            raise RuntimeError(f"no Comfy output for shot {shot.id}")
        response = requests.get(
            f"{cfg.comfy_url}/view",
            params={"filename": outs[0]["filename"], "subfolder": outs[0].get("subfolder", ""), "type": outs[0].get("type", "output")},
            timeout=600,
        )
        response.raise_for_status()
        dest.write_bytes(response.content)
        shot.clip = dest
        meta = {**shot.to_manifest_dict(cfg.project_root), "prompt_id": prompt_id, "uploaded_image": image_name, "comfy_output": outs[0]}
        manifest_shots.append(meta)
        paths["manifest_partial"].write_text(json.dumps(_manifest(cfg, manifest_shots, paths), indent=2), encoding="utf-8")
        print(json.dumps({"saved": str(dest), "bytes": dest.stat().st_size}), flush=True)
    return manifest_shots


def _assemble_outputs(cfg: HarnessConfig, paths: dict[str, Path]) -> tuple[int, dict[str, Any]]:
    _local_preflight(cfg, require_clips=True)
    fps = int(cfg.render_settings.get("fps", 24))
    master_width = int(cfg.render_settings.get("master_width", 1080))
    master_height = int(cfg.render_settings.get("master_height", 1920))
    wan_length = int(cfg.render_settings.get("wan_length_frames", 25))
    if paths["frames_dir"].exists():
        shutil.rmtree(paths["frames_dir"])
    paths["frames_dir"].mkdir(parents=True)
    frame_idx = 0
    for shot in cfg.shots:
        assert shot.clip is not None
        nframes = int(round(shot.duration * fps))
        tmp = paths["outdir"] / f"tmp_shot{shot.id}_%05d.jpg"
        source_duration = wan_length / fps
        speed_factor = shot.duration / source_duration
        vf = f"setpts={speed_factor:.6f}*PTS,fps={fps},scale={master_width}:{master_height}:flags=lanczos:force_original_aspect_ratio=increase,crop={master_width}:{master_height}"
        subprocess.run(["ffmpeg", "-y", "-i", str(shot.clip), "-vf", vf, "-frames:v", str(nframes), str(tmp)], check=True)
        for frame in sorted(paths["outdir"].glob(f"tmp_shot{shot.id}_*.jpg")):
            frame.rename(paths["frames_dir"] / f"frame_{frame_idx:05d}.jpg")
            frame_idx += 1

    subprocess.run(["ffmpeg", "-y", "-framerate", str(fps), "-i", str(paths["frames_dir"] / "frame_%05d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(fps), "-movflags", "+faststart", "-crf", str(cfg.render_settings.get("master_crf", 18)), "-preset", "medium", str(paths["silent"])], check=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(paths["silent"]), "-i", str(cfg.voiceover), "-c:v", "copy", "-c:a", "aac", "-b:a", str(cfg.render_settings.get("audio_bitrate", "160k")), "-ar", str(cfg.render_settings.get("audio_sample_rate", 48000)), "-shortest", "-movflags", "+faststart", str(paths["master"])], check=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(paths["master"]), "-vf", f"scale={cfg.render_settings.get('preview_width', 720)}:{cfg.render_settings.get('preview_height', 1280)}:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", str(cfg.render_settings.get("preview_crf", 24)), "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "3.1", "-c:a", "aac", "-b:a", str(cfg.render_settings.get("preview_audio_bitrate", "96k")), "-ar", str(cfg.render_settings.get("audio_sample_rate", 48000)), "-movflags", "+faststart", str(paths["preview"])], check=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(paths["master"]), "-vf", "fps=1,scale=270:480,tile=6x4", "-frames:v", "1", "-update", "1", str(paths["contact_sheet"])], check=True)
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-show_entries", "stream=index,codec_type,codec_name,width,height,sample_rate", "-of", "json", str(paths["master"])], text=True)
    paths["ffprobe_master"].write_text(probe, encoding="utf-8")
    return frame_idx, json.loads(probe)


def run_harness(config_path: str | os.PathLike[str], *, dry_run: bool = False, skip_wan: bool = False, assemble: bool = True) -> dict[str, Any]:
    cfg = load_harness_config(config_path)
    paths = build_output_paths(cfg)
    paths["outdir"].mkdir(parents=True, exist_ok=True)
    paths["clips_dir"].mkdir(parents=True, exist_ok=True)

    if skip_wan:
        _local_preflight(cfg, require_clips=not dry_run and assemble)
        manifest_shots = [shot.to_manifest_dict(cfg.project_root) for shot in cfg.shots]
    else:
        manifest_shots = _requests_generate_wan_clips(cfg, paths, dry_run=dry_run)

    frames = 0
    ffprobe_data: dict[str, Any] = {"format": {}, "streams": []}
    if assemble and not dry_run:
        frames, ffprobe_data = _assemble_outputs(cfg, paths)
    write_readme_qa(cfg, paths, ffprobe_data, frames=frames)
    manifest = _manifest(cfg, manifest_shots, paths)
    paths["manifest"].write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"done": True, "dry_run": dry_run, "manifest": str(paths["manifest"]), "readme_qa": str(paths["readme_qa"]), "outputs": {k: str(v) for k, v in paths.items()}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reusable Wan2.2 I2V short render harness")
    parser.add_argument("config", help="JSON manifest/config with project_root, VO, workflow settings, and shots")
    parser.add_argument("--dry-run", action="store_true", help="Validate local inputs and write manifest/README_QA without Comfy or ffmpeg")
    parser.add_argument("--skip-wan", action="store_true", help="Use shot clip paths already present in config instead of generating Wan clips")
    parser.add_argument("--no-assemble", action="store_true", help="Do not assemble master/preview/contact sheet")
    args = parser.parse_args(argv)
    result = run_harness(args.config, dry_run=args.dry_run, skip_wan=args.skip_wan, assemble=not args.no_assemble)
    print(json.dumps(result, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
