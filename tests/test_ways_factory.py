import json
from pathlib import Path

from tools import ways_factory


def test_create_card_writes_ways_schema_and_skeleton(tmp_path):
    rc = ways_factory.main([
        "create-card",
        "--slug", "wombat_cube_poop",
        "--hook", "Wombats poop cubes.",
        "--core-fact", "Only known animal to produce cube-shaped scat.",
        "--cohort-tag", "batch1-animal",
        "--test-variable", "hook_style_A",
        "--root", str(tmp_path),
    ])

    assert rc == 0
    project = tmp_path / "wombat_cube_poop"
    idea = json.loads((project / "idea_card.json").read_text(encoding="utf-8"))
    assert idea["category_id"] == 28
    assert idea["voice"] == "elevenlabs_george"
    assert idea["privacy"] == "private"
    assert idea["cohort_tag"] == "batch1-animal"
    assert idea["test_variable"] == "hook_style_A"
    assert isinstance(idea["test_variable"], str)
    assert (project / "script.md").exists()
    assert (project / "storyboard_manifest.json").exists()
    assert (project / "lane_map.json").exists()
    assert (project / "outputs" / "PUBLISH_GATE.md").exists()
    assert (project / "outputs" / "youtube_draft_pack" / "youtube_metadata.json").exists()

    youtube = json.loads((project / "outputs" / "youtube_draft_pack" / "youtube_metadata.json").read_text(encoding="utf-8"))
    assert youtube["category_id"] == 28
    assert youtube["privacy"] == "private"
    assert youtube["selfDeclaredMadeForKids"] is False


def test_checker_refuses_ready_to_publish_when_required_artifacts_missing(tmp_path):
    ways_factory.main([
        "create-card",
        "--slug", "moon_is_moving",
        "--hook", "The Moon is drifting away.",
        "--core-fact", "It moves about 3.8 centimeters farther each year.",
        "--cohort-tag", "batch1-space",
        "--test-variable", "subject_family_space",
        "--root", str(tmp_path),
    ])

    project = tmp_path / "moon_is_moving"
    rc = ways_factory.main(["check-artifacts", str(project), "--ready-to-publish"])
    assert rc == 1

    # Contract mode without Ready-to-Publish allows an early skeleton to exist, but
    # Ready-to-Publish must refuse missing media/report artifacts and absent gates.
    rc_contract = ways_factory.main(["check-artifacts", str(project)])
    assert rc_contract == 1  # media artifacts are still missing from the contract


def _write_nonempty(path: Path, content: bytes = b"x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_checker_passes_ready_contract_with_artifacts_and_gate_results(tmp_path):
    ways_factory.main([
        "create-card",
        "--slug", "sharks_before_trees",
        "--hook", "Sharks are older than trees.",
        "--core-fact", "Sharks appear hundreds of millions of years before trees.",
        "--cohort-tag", "animal-strong-prior",
        "--test-variable", "hook_style_A",
        "--root", str(tmp_path),
    ])
    project = tmp_path / "sharks_before_trees"

    for rel in ways_factory.REQUIRED_OUTPUT_FILES:
        path = project / rel
        if path.name == "PUBLISH_GATE.md" or path.name == "youtube_metadata.json":
            continue
        _write_nonempty(path)

    gate = {
        "slug": "sharks_before_trees",
        "draft_score": 8.5,
        "publish_score": None,
        "gate_results": {
            "gate_1_script": "pass",
            "gate_2_plate_qc_human": "approved",
            "gate_3_render_qa": "pass",
            "gate_4_assembly_qa": "pass",
            "gate_5_human_final_review": "approved",
            "gate_6_publish_authorization": "hold",
        },
        "privacy": "private",
        "category_id": 28,
        "voice": "elevenlabs_george",
    }
    (project / "outputs" / "PUBLISH_GATE.md").write_text(
        "# PUBLISH GATE\n\n```json\n" + json.dumps(gate, indent=2) + "\n```\n",
        encoding="utf-8",
    )

    rc = ways_factory.main(["check-artifacts", str(project), "--ready-to-publish"])
    assert rc == 0


def test_checker_rejects_confounded_test_variable_and_nonprivate_defaults(tmp_path):
    ways_factory.main([
        "create-card",
        "--slug", "bad_card",
        "--hook", "Bad defaults.",
        "--core-fact", "This should fail.",
        "--cohort-tag", "batch1",
        "--test-variable", "hook_style_A",
        "--root", str(tmp_path),
    ])
    project = tmp_path / "bad_card"
    idea_path = project / "idea_card.json"
    idea = json.loads(idea_path.read_text(encoding="utf-8"))
    idea["category_id"] = 22
    idea["privacy"] = "public"
    idea["test_variable"] = ["hook_style_A", "caption_style_B"]
    idea_path.write_text(json.dumps(idea), encoding="utf-8")

    rc = ways_factory.main(["check-artifacts", str(project)])
    assert rc == 1
