import json
from pathlib import Path

from scripts.render_wan_harness import HarnessConfig, PreflightError, run_preflight


class FakeComfyClient:
    def __init__(self, *, reachable=True, nodes=None, models=None):
        self.reachable = reachable
        self.nodes = nodes or {}
        self.model_map = models or {}

    def system_stats(self):
        if not self.reachable:
            raise RuntimeError("connection refused")
        return {"devices": [{"name": "fake-gpu"}]}

    def object_info(self):
        return self.nodes

    def models(self, folder):
        return self.model_map.get(folder, [])


def _write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def _valid_workflow():
    return {
        "39": {"class_type": "VAELoader", "inputs": {"vae_name": "Wan2.1_VAE.safetensors"}},
        "90": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "HighNoise/Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf"}},
        "91": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "LowNoise/Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf"}},
        "80": {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "Wan2.2-Lightning_I2V-A14B-4steps-lora_HIGH_fp16.safetensors"}},
        "82": {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors"}},
        "38": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors"}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "old"}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "bad"}},
        "57": {"class_type": "KSamplerAdvanced", "inputs": {"noise_seed": 1}},
        "58": {"class_type": "KSamplerAdvanced", "inputs": {"noise_seed": 2}},
        "61": {"class_type": "SaveVideo", "inputs": {"filename_prefix": "old"}},
        "62": {"class_type": "LoadImage", "inputs": {"image": "old.png"}},
        "63": {"class_type": "WanImageToVideo", "inputs": {"width": 1, "height": 1, "length": 1}},
    }


def _valid_cfg(tmp_path: Path, workflow=None) -> HarnessConfig:
    (tmp_path / "assets").mkdir()
    (tmp_path / "audio").mkdir()
    (tmp_path / "outputs").mkdir()
    (tmp_path / "assets" / "shot01.png").write_bytes(b"png")
    (tmp_path / "audio" / "vo.mp3").write_bytes(b"mp3")
    _write_json(tmp_path / "workflow.json", workflow or _valid_workflow())
    return HarnessConfig.from_dict({
        "project_root": ".",
        "slug": "topic",
        "output_dir": "outputs/run",
        "voiceover": "audio/vo.mp3",
        "workflow": "workflow.json",
        "comfy_url": "http://127.0.0.1:8188",
        "workflow_overrides": {"39.inputs.vae_name": "wan_2.1_vae.safetensors"},
        "required_nodes": ["6", "7", "39", "57", "58", "61", "62", "63"],
        "required_node_classes": ["VAELoader", "UnetLoaderGGUF", "LoraLoaderModelOnly", "CLIPLoader", "CLIPTextEncode", "KSamplerAdvanced", "LoadImage", "WanImageToVideo", "SaveVideo"],
        "required_vae": "wan_2.1_vae.safetensors",
        "shots": [{"id": "01", "image": "assets/shot01.png", "duration": 1, "caption": "A", "seed": 5, "prompt": "move"}],
    }, base_dir=tmp_path)


def _client():
    return FakeComfyClient(
        nodes={name: {} for name in ["VAELoader", "UnetLoaderGGUF", "LoraLoaderModelOnly", "CLIPLoader", "CLIPTextEncode", "KSamplerAdvanced", "LoadImage", "WanImageToVideo", "SaveVideo"]},
        models={
            "vae": ["wan_2.1_vae.safetensors"],
            "unet": ["HighNoise/Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf", "LowNoise/Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf"],
            "loras": ["Wan2.2-Lightning_I2V-A14B-4steps-lora_HIGH_fp16.safetensors", "Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors"],
            "clip": ["umt5_xxl_fp8_e4m3fn_scaled.safetensors"],
        },
    )


def test_preflight_passes_before_gpu_work_when_all_prereqs_exist(tmp_path):
    report = run_preflight(_valid_cfg(tmp_path), client=_client())

    assert report["ok"] is True
    assert report["workflow"] == str(tmp_path / "workflow.json")
    assert report["shots"] == 1


def test_preflight_fails_fast_with_exact_missing_workflow(tmp_path):
    cfg = _valid_cfg(tmp_path)
    cfg.workflow = tmp_path / "missing.json"

    try:
        run_preflight(cfg, client=_client())
    except PreflightError as exc:
        assert str(exc) == f"missing workflow: {tmp_path / 'missing.json'}"
    else:
        raise AssertionError("expected PreflightError")


def test_preflight_rejects_wrong_vae_override_before_queueing(tmp_path):
    cfg = _valid_cfg(tmp_path)
    cfg.workflow_overrides["39.inputs.vae_name"] = "wan2.2_vae.safetensors"

    try:
        run_preflight(cfg, client=_client())
    except PreflightError as exc:
        assert str(exc) == "wrong VAE override: 39.inputs.vae_name is 'wan2.2_vae.safetensors', expected 'wan_2.1_vae.safetensors'"
    else:
        raise AssertionError("expected PreflightError")


def test_preflight_reports_missing_model_file_with_folder_and_name(tmp_path):
    client = _client()
    client.model_map["unet"] = ["HighNoise/Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf"]

    try:
        run_preflight(_valid_cfg(tmp_path), client=client)
    except PreflightError as exc:
        assert str(exc) == "missing Comfy model: unet/LowNoise/Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf"
    else:
        raise AssertionError("expected PreflightError")


def test_preflight_reports_first_missing_source_still_before_comfy_models(tmp_path):
    cfg = _valid_cfg(tmp_path)
    (tmp_path / "assets" / "shot01.png").unlink()

    try:
        run_preflight(cfg, client=_client())
    except PreflightError as exc:
        assert str(exc) == f"missing source still for shot 01: {tmp_path / 'assets' / 'shot01.png'}"
    else:
        raise AssertionError("expected PreflightError")
