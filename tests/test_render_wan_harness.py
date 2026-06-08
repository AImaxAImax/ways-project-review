import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.render_wan_harness import (
    HarnessConfig,
    apply_workflow_overrides,
    build_output_paths,
    load_harness_config,
    write_readme_qa,
)


def _write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def test_load_harness_config_resolves_topic_paths_without_hardcoded_shark_root():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        topic = tmp_path / "test_cases" / "new_topic"
        (topic / "assets").mkdir(parents=True)
        (topic / "audio").mkdir()
        (topic / "assets" / "shot01.png").write_bytes(b"not-a-real-png")
        (topic / "audio" / "vo.mp3").write_bytes(b"not-a-real-mp3")

        config_path = _write_json(topic / "render_config.json", {
            "project_root": ".",
            "slug": "new_topic",
            "output_dir": "outputs/wan22_generalized",
            "voiceover": "audio/vo.mp3",
            "workflow": "workflow.json",
            "comfy_url": "http://127.0.0.1:8188",
            "negative_prompt": "no text",
            "render_settings": {"fps": 24, "wan_width": 432, "wan_height": 768, "wan_length_frames": 25},
            "workflow_overrides": {"39.inputs.vae_name": "wan_2.1_vae.safetensors"},
            "shots": [
                {
                    "id": "01",
                    "image": "assets/shot01.png",
                    "duration": 1.25,
                    "caption": "NEW TOPIC",
                    "seed": 101,
                    "prompt": "subtle motion",
                }
            ],
        })

        cfg = load_harness_config(config_path)

        assert cfg.project_root == topic
        assert cfg.output_dir == topic / "outputs" / "wan22_generalized"
        assert cfg.voiceover == topic / "audio" / "vo.mp3"
        assert cfg.shots[0].image == topic / "assets" / "shot01.png"
        dumped = json.dumps(cfg.to_manifest_dict(), default=str)
        assert "sharks_older_than_trees" not in dumped
        assert "/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees" not in dumped


def test_apply_workflow_overrides_supports_dot_path_nodes_and_shot_fields():
    workflow = {
        "6": {"inputs": {"text": "old positive"}},
        "7": {"inputs": {"text": "old negative"}},
        "39": {"inputs": {"vae_name": "bad.safetensors"}},
        "57": {"inputs": {"noise_seed": 1}},
        "58": {"inputs": {"noise_seed": 2}},
        "61": {"inputs": {"filename_prefix": "old"}},
        "62": {"inputs": {"image": "old.png"}},
        "63": {"inputs": {"width": 1, "height": 1, "length": 1}},
    }
    cfg = HarnessConfig.from_dict({
        "project_root": ".",
        "slug": "new_topic",
        "output_dir": "outputs/run",
        "voiceover": "vo.mp3",
        "workflow": "workflow.json",
        "negative_prompt": "no text",
        "render_settings": {"wan_width": 432, "wan_height": 768, "wan_length_frames": 25},
        "workflow_overrides": {"39.inputs.vae_name": "wan_2.1_vae.safetensors"},
        "shots": [{"id": "01", "image": "plate.png", "duration": 1.0, "caption": "A", "seed": 123, "prompt": "move"}],
    }, base_dir=Path("/tmp/topic"))

    patched = apply_workflow_overrides(workflow, cfg, cfg.shots[0], uploaded_image="shot01.png")

    assert patched["39"]["inputs"]["vae_name"] == "wan_2.1_vae.safetensors"
    assert patched["62"]["inputs"]["image"] == "shot01.png"
    assert patched["63"]["inputs"] == {"width": 432, "height": 768, "length": 25}
    assert patched["6"]["inputs"]["text"] == "move"
    assert patched["7"]["inputs"]["text"] == "no text"
    assert patched["57"]["inputs"]["noise_seed"] == 123
    assert patched["58"]["inputs"]["noise_seed"] == 1123
    assert patched["61"]["inputs"]["filename_prefix"] == "new_topic/01_123"


def test_build_output_paths_uses_slug_and_configured_output_dir_not_template_names():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        cfg = HarnessConfig.from_dict({
            "project_root": ".",
            "slug": "moon_facts",
            "output_dir": "outputs/custom_run",
            "voiceover": "voice.mp3",
            "workflow": "workflow.json",
            "shots": [{"id": "a", "image": "a.png", "duration": 1, "caption": "A", "seed": 5, "prompt": "move"}],
        }, base_dir=tmp_path)

        paths = build_output_paths(cfg)

        assert paths["master"].name == "moon_facts_wan22_master_1080.mp4"
        assert paths["preview"].name == "moon_facts_wan22_preview_720.mp4"
        assert paths["contact_sheet"].name == "contact_sheet_moon_facts.jpg"
        assert paths["manifest"].parent == tmp_path / "outputs" / "custom_run"
        assert "sharks" not in " ".join(str(p) for p in paths.values()).lower()


def test_write_readme_qa_summarizes_outputs_ffprobe_and_gate():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        cfg = HarnessConfig.from_dict({
            "project_root": ".",
            "slug": "moon_facts",
            "output_dir": "outputs/run",
            "voiceover": "voice.mp3",
            "workflow": "workflow.json",
            "qa_gate": ["audio present", "contact sheet coherent"],
            "shots": [{"id": "01", "image": "a.png", "duration": 1, "caption": "A", "seed": 5, "prompt": "move"}],
        }, base_dir=tmp_path)
        paths = build_output_paths(cfg)
        paths["readme_qa"].parent.mkdir(parents=True, exist_ok=True)

        write_readme_qa(cfg, paths, {"format": {"duration": "1.000", "size": "1234"}, "streams": [{"codec_type": "video", "width": 1080, "height": 1920}, {"codec_type": "audio", "sample_rate": "48000"}]}, frames=24)

        text = paths["readme_qa"].read_text(encoding="utf-8")
        assert "# moon_facts Wan render QA" in text
        assert "moon_facts_wan22_master_1080.mp4" in text
        assert "1080x1920" in text
        assert "AAC/audio stream present" in text
        assert "audio present" in text


if __name__ == "__main__":
    tests = [obj for name, obj in sorted(globals().items()) if name.startswith("test_") and callable(obj)]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} tests passed")
