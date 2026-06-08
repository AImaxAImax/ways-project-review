#!/usr/bin/env python3
"""WAYS video-card factory templates and artifact-contract checker.

This tool implements the card schema and Ready-to-Publish artifact contract from:
ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md

It is intentionally publish-safe: it creates folders/files and validates gate evidence,
but it never uploads, schedules, or publishes anything.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_CATEGORY_ID = 28
DEFAULT_VOICE = "elevenlabs_george"
DEFAULT_PRIVACY = "private"

REQUIRED_TOP_LEVEL_FILES = [
    "idea_card.json",
    "script.md",
    "storyboard_manifest.json",
    "lane_map.json",
]

REQUIRED_OUTPUT_FILES = [
    "outputs/clean_master.mp4",
    "outputs/publish_candidate_captioned.mp4",
    "outputs/discord_preview_captioned.mp4",
    "outputs/captions.ass",
    "outputs/captions.srt",
    "outputs/contact_sheet.jpg",
    "outputs/ffprobe_publish.json",
    "outputs/audio_report.txt",
    "outputs/vlm_plate_scores.json",
    "outputs/PUBLISH_GATE.md",
    "outputs/youtube_draft_pack/youtube_metadata.json",
    "outputs/youtube_draft_pack/description_upload.txt",
    "outputs/youtube_draft_pack/thumbnail_candidate.jpg",
    "outputs/youtube_draft_pack/youtube_upload_result.json",
    "outputs/youtube_draft_pack/youtube_verification.json",
]

REQUIRED_DIRS = [
    "assets/accepted_stills",
    "assets/rejected_stills",
    "outputs/i2v_clips",
    "outputs/motion_graphic_clips",
    "outputs/youtube_draft_pack",
]

# Gate 6 public publish authorization is required before Published, but Ready-to-
# Publish must still record the result as held/pending so the artifact contract is
# explicit and private-by-default.
REQUIRED_GATE_NAMES = [
    "gate_1_script",
    "gate_2_plate_qc_human",
    "gate_3_render_qa",
    "gate_4_assembly_qa",
    "gate_5_human_final_review",
    "gate_6_publish_authorization",
]

READY_GATE_ACCEPTED = {
    "gate_1_script": {"pass"},
    "gate_2_plate_qc_human": {"approved", "pass"},
    "gate_3_render_qa": {"pass"},
    "gate_4_assembly_qa": {"pass"},
    "gate_5_human_final_review": {"approved", "pass"},
    "gate_6_publish_authorization": {"hold", "pending", "private_only", "not_authorized"},
}

SLUG_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def validate_slug(slug: str) -> str:
    if not SLUG_RE.match(slug):
        raise SystemExit("slug must be lowercase snake_case with letters/numbers/underscores")
    return slug


def json_dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_idea_card(args: argparse.Namespace, project_dir: Path) -> dict[str, Any]:
    return {
        "slug": args.slug,
        "hook": args.hook,
        "core_fact": args.core_fact,
        "status_column": args.status_column,
        "cohort_tag": args.cohort_tag,
        "test_variable": args.test_variable,
        "category_id": DEFAULT_CATEGORY_ID,
        "voice": DEFAULT_VOICE,
        "lane_map": {},
        "draft_score": None,
        "publish_score": None,
        "youtube_video_id": None,
        "privacy": DEFAULT_PRIVACY,
        "retention_pct_viewed": None,
        "artifact_folder": f"{project_dir.name}/",
        "blocking_gate": None,
        "created_at": utc_now(),
    }


def build_storyboard(slug: str, hook: str, core_fact: str) -> dict[str, Any]:
    return {
        "slug": slug,
        "version": 1,
        "target_format": "1080x1920 vertical Short, H.264, 24fps, AAC 48kHz",
        "caption_style": "WAYS creator captions: large centered white with yellow active/key word and thick black outline; zero non-caption text",
        "shots": [
            {
                "id": "shot01",
                "beat": "Hook payoff in first 1-2 seconds",
                "voiceover": hook,
                "caption": hook,
                "duration_seconds": None,
                "visual_register": None,
                "plate_path": None,
                "accepted_still_path": None,
                "render_clip_path": None,
                "gate_notes": [],
            },
            {
                "id": "shot02",
                "beat": "Core fact proof beat",
                "voiceover": core_fact,
                "caption": core_fact,
                "duration_seconds": None,
                "visual_register": None,
                "plate_path": None,
                "accepted_still_path": None,
                "render_clip_path": None,
                "gate_notes": [],
            },
        ],
    }


def build_lane_map(slug: str) -> dict[str, Any]:
    return {
        "slug": slug,
        "version": 1,
        "confirmed_by_human_gate_2": False,
        "lanes": {
            "shot01": {
                "lane": None,
                "allowed_values": ["wan_i2v", "motion_graphic"],
                "reason": "Set during Gate 2 plate QC; human confirmation required.",
            },
            "shot02": {
                "lane": None,
                "allowed_values": ["wan_i2v", "motion_graphic"],
                "reason": "Set during Gate 2 plate QC; human confirmation required.",
            },
        },
    }


def build_youtube_metadata(slug: str, hook: str) -> dict[str, Any]:
    return {
        "title": hook or slug.replace("_", " ").title(),
        "description_path": "description_upload.txt",
        "tags": ["Wait Are You Serious", "science", "facts", "shorts"],
        "category_id": DEFAULT_CATEGORY_ID,
        "privacy": DEFAULT_PRIVACY,
        "selfDeclaredMadeForKids": False,
        "voice": DEFAULT_VOICE,
        "public_publish_requires_gate_6_human_authorization": True,
    }


def publish_gate_template(slug: str) -> str:
    # Machine-readable JSON block keeps the checker deterministic; the markdown
    # checklist stays easy for humans to edit in review.
    gate_json = {
        "slug": slug,
        "draft_score": None,
        "publish_score": None,
        "gate_results": {
            "gate_1_script": None,
            "gate_2_plate_qc_human": None,
            "gate_3_render_qa": None,
            "gate_4_assembly_qa": None,
            "gate_5_human_final_review": None,
            "gate_6_publish_authorization": "hold",
        },
        "privacy": DEFAULT_PRIVACY,
        "category_id": DEFAULT_CATEGORY_ID,
        "voice": DEFAULT_VOICE,
    }
    return f"""# PUBLISH GATE — {slug}

Default decision: HOLD / private draft only until every required artifact exists and Gates 1-5 pass. Public publish requires explicit Gate 6 human authorization.

```json
{json.dumps(gate_json, indent=2)}
```

## Human-readable checklist

- [ ] Gate 1 Script automated check passed; cited/safe wording locked.
- [ ] Gate 2 Plate QC human approval recorded for every accepted plate and lane assignment.
- [ ] Gate 3 Render QA passed: expected clips present; no text/logo/morph blockers.
- [ ] Gate 4 Spec/Assembly QA passed: 1080x1920, H.264, 24fps, AAC 48kHz, contact sheet, ffprobe, audio report.
- [ ] Gate 5 Human Final Review approved private draft at phone size; draft_score recorded.
- [ ] Gate 6 Publish Authorization: HOLD unless Josh explicitly authorizes public publish.
"""


def script_template(slug: str, hook: str, core_fact: str) -> str:
    return f"""# Script — {slug}

## Locked voice

- Voice: {DEFAULT_VOICE}
- Tone: kid-friendly awe, not childish.
- First caption/VO beat must pay off the hook in 1-2 seconds.

## Draft

1. {hook}
2. {core_fact}

## Sources

- TODO: add citation URL/title/date for the core fact before Gate 1 can pass.
"""


def create_card(args: argparse.Namespace) -> int:
    slug = validate_slug(args.slug)
    root = args.root.resolve()
    project_dir = (root / slug).resolve() if args.project_dir is None else args.project_dir.resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    for rel in REQUIRED_DIRS:
        (project_dir / rel).mkdir(parents=True, exist_ok=True)

    idea = build_idea_card(args, project_dir)
    storyboard = build_storyboard(slug, args.hook, args.core_fact)
    lane_map = build_lane_map(slug)

    json_dump(project_dir / "idea_card.json", idea)
    write_text(project_dir / "script.md", script_template(slug, args.hook, args.core_fact))
    json_dump(project_dir / "storyboard_manifest.json", storyboard)
    json_dump(project_dir / "lane_map.json", lane_map)
    write_text(project_dir / "outputs" / "PUBLISH_GATE.md", publish_gate_template(slug))
    json_dump(project_dir / "outputs" / "youtube_draft_pack" / "youtube_metadata.json", build_youtube_metadata(slug, args.hook))
    write_text(project_dir / "outputs" / "youtube_draft_pack" / "description_upload.txt", "TODO: write upload description after script lock.\n")

    # Placeholder result files make the skeleton explicit without pretending the
    # artifact contract has passed. The checker rejects these zero-byte files.
    for rel in [
        "outputs/youtube_draft_pack/thumbnail_candidate.jpg",
        "outputs/youtube_draft_pack/youtube_upload_result.json",
        "outputs/youtube_draft_pack/youtube_verification.json",
    ]:
        (project_dir / rel).touch(exist_ok=True)

    print(json.dumps({"project_dir": str(project_dir), "created": REQUIRED_TOP_LEVEL_FILES + ["outputs/PUBLISH_GATE.md", "outputs/youtube_draft_pack/"]}, indent=2))
    return 0


def load_json(path: Path, problems: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        problems.append(f"missing JSON: {path}")
    except json.JSONDecodeError as exc:
        problems.append(f"invalid JSON {path}: {exc}")
    return None


def extract_publish_gate_json(path: Path, problems: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        problems.append(f"missing publish gate: {path}")
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if not match:
        problems.append("PUBLISH_GATE.md missing machine-readable ```json block")
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        problems.append(f"PUBLISH_GATE.md JSON block invalid: {exc}")
        return None
    return data


def check_card_schema(project_dir: Path, problems: list[str]) -> None:
    idea = load_json(project_dir / "idea_card.json", problems)
    if not isinstance(idea, dict):
        return
    required = [
        "slug", "hook", "core_fact", "status_column", "cohort_tag", "test_variable",
        "category_id", "voice", "lane_map", "draft_score", "publish_score",
        "youtube_video_id", "privacy", "retention_pct_viewed", "artifact_folder", "blocking_gate",
    ]
    for key in required:
        if key not in idea:
            problems.append(f"idea_card.json missing field: {key}")
    if idea.get("category_id") != DEFAULT_CATEGORY_ID:
        problems.append("idea_card.json category_id must remain 28")
    if idea.get("voice") != DEFAULT_VOICE:
        problems.append("idea_card.json voice must remain elevenlabs_george")
    if idea.get("privacy") != DEFAULT_PRIVACY:
        problems.append("idea_card.json privacy must default to private")
    if not idea.get("cohort_tag"):
        problems.append("idea_card.json cohort_tag is required")
    tv = idea.get("test_variable")
    if not tv or isinstance(tv, (list, dict)):
        problems.append("idea_card.json test_variable must be one scalar value")


def check_required_paths(project_dir: Path, problems: list[str], *, require_nonempty: bool) -> None:
    for rel in REQUIRED_DIRS:
        path = project_dir / rel
        if not path.is_dir():
            problems.append(f"missing directory: {rel}")
    for rel in REQUIRED_TOP_LEVEL_FILES + REQUIRED_OUTPUT_FILES:
        path = project_dir / rel
        if not path.exists():
            problems.append(f"missing artifact: {rel}")
        elif path.is_dir():
            problems.append(f"expected file but found directory: {rel}")
        elif require_nonempty and path.stat().st_size == 0:
            problems.append(f"empty artifact is not Ready-to-Publish evidence: {rel}")


def normalize_gate_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("status") or value.get("result") or value.get("decision")
    if value is None:
        return None
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def check_publish_gate(project_dir: Path, problems: list[str], *, ready_to_publish: bool) -> None:
    gate = extract_publish_gate_json(project_dir / "outputs" / "PUBLISH_GATE.md", problems)
    if not isinstance(gate, dict):
        return
    if gate.get("category_id") != DEFAULT_CATEGORY_ID:
        problems.append("PUBLISH_GATE.md category_id must remain 28")
    if gate.get("voice") != DEFAULT_VOICE:
        problems.append("PUBLISH_GATE.md voice must remain elevenlabs_george")
    if gate.get("privacy") != DEFAULT_PRIVACY:
        problems.append("PUBLISH_GATE.md privacy must remain private unless Gate 6 public authorization is being checked")
    if "draft_score" not in gate:
        problems.append("PUBLISH_GATE.md missing draft_score")
    if "publish_score" not in gate:
        problems.append("PUBLISH_GATE.md missing publish_score")
    results = gate.get("gate_results")
    if not isinstance(results, dict):
        problems.append("PUBLISH_GATE.md missing gate_results object")
        return
    for name in REQUIRED_GATE_NAMES:
        if name not in results:
            problems.append(f"PUBLISH_GATE.md missing gate result: {name}")
            continue
        normalized = normalize_gate_value(results.get(name))
        if normalized is None:
            problems.append(f"PUBLISH_GATE.md gate result absent: {name}")
            continue
        if ready_to_publish and normalized not in READY_GATE_ACCEPTED[name]:
            accepted = ", ".join(sorted(READY_GATE_ACCEPTED[name]))
            problems.append(f"PUBLISH_GATE.md gate {name} is {normalized!r}; Ready-to-Publish requires one of: {accepted}")


def check_youtube_metadata(project_dir: Path, problems: list[str]) -> None:
    meta = load_json(project_dir / "outputs" / "youtube_draft_pack" / "youtube_metadata.json", problems)
    if not isinstance(meta, dict):
        return
    if meta.get("category_id") != DEFAULT_CATEGORY_ID:
        problems.append("youtube_metadata.json category_id must remain 28")
    if meta.get("privacy") != DEFAULT_PRIVACY:
        problems.append("youtube_metadata.json privacy must default to private")
    if meta.get("selfDeclaredMadeForKids") is not False:
        problems.append("youtube_metadata.json selfDeclaredMadeForKids must be false")


def check_artifacts(args: argparse.Namespace) -> int:
    project_dir = args.project_dir.resolve()
    problems: list[str] = []
    ready = args.ready_to_publish
    if not project_dir.exists():
        problems.append(f"project directory does not exist: {project_dir}")
    else:
        check_required_paths(project_dir, problems, require_nonempty=ready)
        check_card_schema(project_dir, problems)
        check_publish_gate(project_dir, problems, ready_to_publish=ready)
        check_youtube_metadata(project_dir, problems)

    report = {
        "project_dir": str(project_dir),
        "ready_to_publish_requested": ready,
        "ok": not problems,
        "problems": problems,
    }
    if args.report:
        json_dump(args.report.resolve(), report)
    print(json.dumps(report, indent=2))
    return 0 if not problems else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WAYS video factory card generator and artifact checker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    create = sub.add_parser("create-card", help="Generate a new WAYS video card artifact skeleton")
    create.add_argument("--slug", required=True, help="lowercase snake_case video slug")
    create.add_argument("--hook", required=True)
    create.add_argument("--core-fact", required=True)
    create.add_argument("--cohort-tag", required=True)
    create.add_argument("--test-variable", required=True, help="single scalar variable this card tests")
    create.add_argument("--status-column", default="Idea Pool")
    create.add_argument("--root", type=Path, default=Path("test_cases"), help="root under which slug folder is created")
    create.add_argument("--project-dir", type=Path, default=None, help="explicit output folder; overrides --root/--slug")
    create.set_defaults(func=create_card)

    check = sub.add_parser("check-artifacts", help="Validate WAYS artifact contract")
    check.add_argument("project_dir", type=Path)
    check.add_argument("--ready-to-publish", action="store_true", help="enforce non-empty artifacts and accepted gate results")
    check.add_argument("--report", type=Path, default=None, help="optional JSON report path")
    check.set_defaults(func=check_artifacts)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
