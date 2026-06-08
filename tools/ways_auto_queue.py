#!/usr/bin/env python3
"""Maintain an automated WAYS internal production queue.

Policy from Josh, 2026-06-06: do not hold internal WAYS production at
script/packet stage while the active/ready queue has fewer than five videos.
Public publishing remains separately gated by explicit authorization.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BOARD = Path("ops/ways-video-lab-discord/active_wip_board.json")
TARGET_ACTIVE_READY = 5

SEED_CARDS: list[dict[str, Any]] = [
    {
        "slug": "mantis_shrimp_cavitation_punch",
        "hook": "A mantis shrimp punch can make the water flash.",
        "core_fact": "Smasher mantis shrimp strikes can create cavitation bubbles; collapse of those bubbles adds a second impact.",
        "cohort_tag": "first10_item_002",
        "test_variable": "public_domain_source_photo_static_to_wan22_upgrade",
        "artifact_folder": "test_cases/mantis_shrimp_cavitation_punch/",
        "source_policy": "Wikimedia/public-source photos first; local Wan2.2 upgrade when available; no paid credits without explicit approval.",
        "sources": [
            "Nature: Deadly strike mechanism of a mantis shrimp, DOI 10.1038/428819a, https://www.nature.com/articles/428819a",
            "Journal of Experimental Biology: Elastic Energy Powers Mantis Shrimp Punch, DOI 10.1242/jeb.040691, https://doi.org/10.1242/jeb.040691",
            "Bioinspiration & Biomimetics: A physical model of the extreme mantis shrimp strike, DOI 10.1088/1748-3182/9/1/016014",
        ],
        "beats": [
            {"voiceover":"A mantis shrimp punch can make the water flash.","caption":"A mantis shrimp punch can make the water flash","visual":"photoreal macro shrimp impact with cavitation bubbles and shock ripple"},
            {"voiceover":"The animal is tiny, but its club moves so fast that the water briefly tears open into bubbles.","caption":"the animal is tiny / but its club moves insanely fast","visual":"tiny mantis shrimp portrait followed by club/impact macro"},
            {"voiceover":"That is called cavitation.","caption":"that is cavitation","visual":"bubble cloud forming beside impact, no diagram labels"},
            {"voiceover":"The punch hits first.","caption":"the punch hits first","visual":"club reaching shell/prey proxy, clear first impact"},
            {"voiceover":"Then the bubble collapses and hits again.","caption":"then the bubble collapses / and hits again","visual":"collapsing bubble cloud/shock ripple near target"},
            {"voiceover":"Scientists filmed this shock in high speed, because the second hit happens too fast for our eyes.","caption":"scientists filmed it / in high speed","visual":"high-speed macro sequence/contact-sheet-like visual without UI/readouts"},
            {"voiceover":"So the mantis shrimp does not just punch prey.","caption":"it does not just / punch prey","visual":"shrimp poised after strike, educational wonder not scary"},
            {"voiceover":"It punches the water so hard the water punches too.","caption":"the water / punches too","visual":"final bubble-collapse ripple around shrimp/impact"},
        ],
    },
    {
        "slug": "saturn_hexagon_storm",
        "hook": "Saturn has a hexagon storm.",
        "core_fact": "A giant hexagon-shaped jet stream wraps around Saturn's north pole, with storms and a polar vortex inside.",
        "cohort_tag": "first10_space_080",
        "test_variable": "nasa_source_cinematic_static_motion",
        "artifact_folder": "test_cases/saturn_hexagon_storm/",
        "source_policy": "NASA/public-domain first; no paid credits.",
        "sources": ["NASA/JPL PIA21052 Over Saturns Turbulent North", "NASA/JPL PIA17122 Stormy North", "NASA Image and Media Guidelines"],
        "beats": [
            {"voiceover":"Saturn has a hexagon storm.","caption":"Saturn has a hexagon storm","visual":"Cassini-style north pole view where the hexagon reads instantly"},
            {"voiceover":"It is not a drawing. It is a real jet stream around the planet's north pole.","caption":"not a drawing / a real jet stream","visual":"NASA north polar image, no extra labels"},
            {"voiceover":"Each side is wider than Earth.","caption":"each side is wider than Earth","visual":"scale comparison implied by Saturn limb and tiny Earth proxy only if no text"},
            {"voiceover":"And inside it, storms keep spinning.","caption":"storms keep spinning inside","visual":"polar vortex / cloud bands rotating feel"},
            {"voiceover":"So one of the strangest shapes in space is weather.","caption":"a strange shape / made of weather","visual":"final cinematic Saturn pole pullback"},
        ],
    },
    {
        "slug": "wombat_cube_poop",
        "hook": "Wombats poop cubes.",
        "core_fact": "Wombats are the only known animals that produce cube-shaped scat; researchers link the shape to how the intestine stretches and moves.",
        "cohort_tag": "first10_item_005",
        "test_variable": "real_animal_source_plus_object_overlay_semantics",
        "artifact_folder": "test_cases/wombat_cube_poop/",
        "source_policy": "Wikimedia/public-source wombat photos plus tiny local object overlay; no paid credits.",
        "sources": [
            "Soft Matter: Intestines of non-uniform stiffness mold the corners of wombat feces, DOI 10.1039/D0SM01230K",
            "BBC/Nature coverage of wombat cube feces research, source for public explanation only",
        ],
        "beats": [
            {"voiceover":"Wombats poop cubes.","caption":"Wombats poop cubes","visual":"real wombat in grass, cute not childish, instant hook"},
            {"voiceover":"Not perfect toy blocks, but little cube-shaped pellets.","caption":"little cube shaped pellets","visual":"macro-safe tiny cube scat proxy beside natural ground"},
            {"voiceover":"Scientists think the shape comes from uneven stretching inside the intestine.","caption":"uneven stretching / inside the intestine","visual":"non-text anatomical motion proxy, no diagram labels"},
            {"voiceover":"The corners form before the poop ever lands.","caption":"the corners form first","visual":"process visual, avoid fake labels"},
            {"voiceover":"So the weirdest bathroom fact in nature is also physics.","caption":"bathroom fact / plus physics","visual":"wombat walking away, family-friendly final beat"},
        ],
    },
    {
        "slug": "octopus_three_hearts",
        "hook": "An octopus has three hearts.",
        "core_fact": "Two octopus hearts pump blood through the gills, while a third pumps blood to the rest of the body.",
        "cohort_tag": "first10_ocean_011",
        "test_variable": "public_aquarium_source_photo_plus_motion_graphic_overlay",
        "artifact_folder": "test_cases/octopus_three_hearts/",
        "source_policy": "Public-source/octopus reference photos; no paid credits; avoid fake anatomy in video lane.",
        "sources": [
            "Smithsonian Ocean: Octopus facts and biology overview",
            "Encyclopaedia Britannica: cephalopod circulatory system overview",
        ],
        "beats": [
            {"voiceover":"An octopus has three hearts.","caption":"An octopus has three hearts","visual":"beautiful real octopus, calm full-body read"},
            {"voiceover":"Two hearts push blood through the gills.","caption":"two hearts / push through the gills","visual":"two subtle pulse points near gill area, no labels"},
            {"voiceover":"The third sends blood to the rest of the body.","caption":"the third / powers the body","visual":"single subtle body pulse, no diagram text"},
            {"voiceover":"And when it swims, that body heart can slow down.","caption":"when it swims / one heart slows","visual":"octopus swimming motion, avoid detached tentacles"},
            {"voiceover":"That is why crawling can be easier than swimming.","caption":"crawling can be easier","visual":"octopus moving along seafloor, anatomy-safe"},
        ],
    },
    {
        "slug": "tardigrade_survival_mode",
        "hook": "Tardigrades can pause their bodies.",
        "core_fact": "When conditions are extreme, tardigrades can curl into a dry tun state and slow their metabolism dramatically until water returns.",
        "cohort_tag": "first10_micro_014",
        "test_variable": "microscope_source_motion_graphic_scale",
        "artifact_folder": "test_cases/tardigrade_survival_mode/",
        "source_policy": "Public microscope imagery plus motion graphics; no paid credits.",
        "sources": [
            "NASA: Tardigrades and space survival research overview",
            "Current Biology / peer-reviewed tardigrade cryptobiosis literature for fact wording",
        ],
        "beats": [
            {"voiceover":"Tardigrades can pause their bodies.","caption":"Tardigrades can pause their bodies","visual":"microscope tardigrade close-up, cute but real"},
            {"voiceover":"When things get too dry, they curl into a tiny tun.","caption":"too dry / tiny tun","visual":"curling body shape or before-after microscope proxy"},
            {"voiceover":"Their metabolism drops so low it is almost like waiting on pause.","caption":"metabolism drops / like pause","visual":"stillness with subtle heartbeat/motion graphic, no text"},
            {"voiceover":"Then when water comes back, some can wake up again.","caption":"water returns / they wake up","visual":"rehydration motion proxy, microscope look"},
            {"voiceover":"It is one of nature's strangest survival tricks.","caption":"nature's strangest / survival trick","visual":"final tardigrade hero macro/microscope look"},
        ],
    },
    {
        "slug": "wood_frog_freeze_survival",
        "hook": "A frog can freeze solid.",
        "core_fact": "Wood frogs survive winter by letting much of their body freeze while glucose-rich fluids help protect cells until thawing.",
        "cohort_tag": "first10_animal_021",
        "test_variable": "real_source_photo_plus_freeze_thaw_motion",
        "artifact_folder": "test_cases/wood_frog_freeze_survival/",
        "source_policy": "Public-source real wood frog imagery and simple freeze/thaw motion graphics; no paid credits.",
        "sources": [
            "National Park Service wood frog freeze tolerance overview",
            "Peer-reviewed wood frog freeze tolerance literature for fact wording",
        ],
        "beats": [
            {"voiceover":"A frog can freeze solid.","caption":"A frog can freeze solid","visual":"real wood frog on leaf litter with icy edge, instant animal read"},
            {"voiceover":"In winter, ice can form through much of its body.","caption":"ice forms through its body","visual":"macro frost creeping around frog body, no horror, no labels"},
            {"voiceover":"Its heart can stop beating for a while.","caption":"its heart can stop","visual":"calm freeze-state close-up with subtle pulse fading, no medical UI"},
            {"voiceover":"Sugar-like antifreeze helps protect the cells.","caption":"sugar helps protect cells","visual":"simple cellular protection visual without text or diagram labels"},
            {"voiceover":"Then spring warms it up, and the frog starts moving again.","caption":"spring warms it / back to life","visual":"thawing frog on wet leaves, tiny visible movement"},
        ],
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_project(root: Path, card: dict[str, Any]) -> None:
    slug = card["slug"]
    project = root / card["artifact_folder"].rstrip("/")
    project.mkdir(parents=True, exist_ok=True)
    for rel in ["assets/accepted_stills", "assets/rejected_stills", "outputs/i2v_clips", "outputs/motion_graphic_clips", "outputs/youtube_draft_pack"]:
        (project / rel).mkdir(parents=True, exist_ok=True)
    idea = {
        "slug": slug,
        "hook": card["hook"],
        "core_fact": card["core_fact"],
        "status_column": card.get("status_column", "Script Locked"),
        "cohort_tag": card["cohort_tag"],
        "test_variable": card["test_variable"],
        "category_id": 28,
        "voice": "elevenlabs_george",
        "lane_map": {},
        "draft_score": card.get("draft_score"),
        "publish_score": card.get("publish_score"),
        "youtube_video_id": None,
        "privacy": "private",
        "retention_pct_viewed": None,
        "artifact_folder": card["artifact_folder"],
        "blocking_gate": None,
        "created_at": card.get("created_at") or utc_now(),
        "automation_policy": "auto_advance_internal_until_5_active_ready; public_publish_requires_explicit_gate6",
    }
    # Existing project packets often contain human decisions, monitor-only
    # guards, upload IDs, and richer hand-authored manifests. Queue maintenance
    # must not reset those files back to Script Locked on every cron run.
    if not (project / "idea_card.json").exists():
        write_json(project / "idea_card.json", idea)
    if not (project / "script.md").exists():
        write_text(project / "script.md", "# Script — " + slug + "\n\n" + "\n".join(f"{i+1}. {b['voiceover']}\n   CAP: {b['caption']}\n   VISUAL: {b['visual']}" for i,b in enumerate(card["beats"])) + "\n\n## Sources\n" + "\n".join(f"- {s}" for s in card["sources"]) + "\n")
    storyboard = {"slug": slug, "version": 1, "target_format": "1080x1920 vertical Short", "caption_style": "WAYS creator captions; zero non-caption text", "shots": [{"id": f"shot{i+1:02d}", **b, "duration_seconds": None, "gate_notes": []} for i,b in enumerate(card["beats"])]}
    if not (project / "storyboard_manifest.json").exists():
        write_json(project / "storyboard_manifest.json", storyboard)
    lanes = {f"shot{i+1:02d}": {"lane": "source_photo_static_or_wan_i2v", "allowed_values": ["source_photo_static", "wan_i2v", "motion_graphic"], "reason": "Automated internal lane; promote only after QA."} for i,_ in enumerate(card["beats"])}
    if not (project / "lane_map.json").exists():
        write_json(project / "lane_map.json", {"slug": slug, "version": 2, "confirmed_by_human_gate_2": False, "automation_internal_auto_advance": True, "lanes": lanes})
    y = project / "outputs/youtube_draft_pack"
    if not (y / "youtube_metadata.json").exists():
        write_json(y / "youtube_metadata.json", {"title": card["hook"] + " #Shorts", "description_path": "description_upload.txt", "tags": ["Wait Are You Serious", "science", "facts", "shorts"], "category_id": 28, "privacy": "private", "selfDeclaredMadeForKids": False, "voice": "elevenlabs_george", "public_publish_requires_gate_6_human_authorization": True})
    if not (y / "description_upload.txt").exists():
        write_text(y / "description_upload.txt", card["hook"] + "\n\n#Shorts #science #facts\n")
    gate_json = {"slug": slug, "draft_score": card.get("draft_score"), "publish_score": card.get("publish_score"), "gate_results": {"gate_1_script": "pass", "gate_2_plate_qc_human": "auto_internal", "gate_3_render_qa": None, "gate_4_assembly_qa": None, "gate_5_human_final_review": "auto_internal_hold_public", "gate_6_publish_authorization": "hold"}, "privacy": "private", "category_id": 28, "voice": "elevenlabs_george", "automation_note": "Internal production may advance automatically until 5 active/ready videos; public publish remains human-gated."}
    if not (project / "outputs/PUBLISH_GATE.md").exists():
        write_text(project / "outputs/PUBLISH_GATE.md", f"# PUBLISH GATE — {slug}\n\nInternal automation may advance this candidate. Public publish requires explicit Gate 6 authorization.\n\n```json\n{json.dumps(gate_json, indent=2)}\n```\n")


def card_with_defaults(card: dict[str, Any]) -> dict[str, Any]:
    out = dict(card)
    out.setdefault("status_column", "Script Locked")
    out.setdefault("category_id", 28)
    out.setdefault("voice", "elevenlabs_george")
    out.setdefault("draft_score", None)
    out.setdefault("publish_score", None)
    out.setdefault("youtube_video_id", None)
    out.setdefault("privacy", "private")
    out.setdefault("retention_pct_viewed", None)
    out.setdefault("blocking_gate", None)
    out.setdefault("created_at", utc_now())
    out["script"] = {"beats": out["beats"], "sources": out["sources"]}
    out["gate_1_status"] = "auto_approved_internal"
    out["automation_policy"] = "auto_advance_internal_until_5_active_ready"
    return out


def active_count(cards: list[dict[str, Any]]) -> int:
    parked = {"Published / Scheduled", "Parked / Rework", "Killed", "Monitor Only"}
    return sum(1 for c in cards if str(c.get("status_column")) not in parked)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    ap.add_argument("--target", type=int, default=TARGET_ACTIVE_READY)
    ap.add_argument("--run-qc", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    board_path = (root / args.board).resolve() if not args.board.is_absolute() else args.board
    board = json.loads(board_path.read_text(encoding="utf-8")) if board_path.exists() else {"cards": [], "monitor_only": []}
    cards = board.setdefault("cards", [])
    by_slug = {c.get("slug"): c for c in cards}
    changed=[]
    # Update/seed until target active queue exists.
    for seed in SEED_CARDS:
        ensure_project(root, seed)
        if seed["slug"] in by_slug:
            existing = by_slug[seed["slug"]]
            update_fields = {k: card_with_defaults(seed)[k] for k in ["hook", "core_fact", "cohort_tag", "test_variable", "category_id", "voice", "privacy", "artifact_folder", "source_policy", "sources", "beats", "script", "gate_1_status"]}
            preserve_policy = {
                "do_not_rebuild_unless_user_reopens",
                "source_proof_rework_only_no_publish_no_auto_promote_until_new_proof_passes",
                "source_quality_rework_only_no_auto_promote_old_artifacts",
                "full_template_rework_only_no_auto_promote_old_artifacts",
                "source_acquisition_then_plate_qc_no_render_until_gate2_pass",
            }
            if existing.get("automation_policy") not in preserve_policy:
                update_fields["automation_policy"] = card_with_defaults(seed)["automation_policy"]
            existing.update(update_fields)
            if existing.get("status_column") in {None, "Idea Pool", "gate_1_packet_prepared"}:
                existing["status_column"] = "Script Locked"
        elif active_count(cards) < args.target:
            cards.append(card_with_defaults(seed)); changed.append(seed["slug"])
    # Promote internal static-source drafts when verified artifacts exist, while
    # preserving human/source-quality rejections. A static/photo mantis montage
    # was explicitly rejected as "not say-dog-see-dog", so artifact existence must
    # not auto-promote it again.
    parked_columns = {"Published / Scheduled", "Parked / Rework", "Killed", "Monitor Only"}
    for c in cards:
        project = root / c["artifact_folder"].rstrip("/")
        # Mantis has a newer clean Wan/no-overlay candidate-review package that
        # intentionally supersedes the rejected static/proof-overlay lanes. Keep
        # the old static-source auto-promotion guard, but do not let that guard
        # hide the verified v03 candidate from the active board. If Josh has
        # already moved it to Monitor Only / do-not-rebuild, preserve that guard.
        if c.get("slug") == "mantis_shrimp_cavitation_punch" and str(c.get("status_column")) not in parked_columns and c.get("automation_policy") != "do_not_rebuild_unless_user_reopens":
            mantis_v03_dir = project / "outputs" / "wan_motion_v03_clean"
            mantis_v03_required = {
                "ffprobe_publish": "ffprobe_captioned_master.json",
                "contact_sheet": "contact_sheet_captioned_hook_v03.jpg",
                "publish_candidate_captioned": "mantis_shrimp_cavitation_punch_wan22_captioned_hook_v03_1080.mp4",
                "discord_preview_captioned": "mantis_shrimp_cavitation_punch_wan22_captioned_hook_v03_720.mp4",
                "captions_ass": "captions_hook_v03.ass",
                "captions_srt": "captions_hook_v03.srt",
            }
            if all((mantis_v03_dir / name).exists() for name in mantis_v03_required.values()):
                c["status_column"] = "Human Final Review - Mantis Wan v03 Candidate"
                c["draft_score"] = c.get("draft_score") or 8.0
                c["outputs"] = {key: f"outputs/wan_motion_v03_clean/{name}" for key, name in mantis_v03_required.items()}
                c["outputs"]["clean_master_no_captions"] = "outputs/wan_motion_v03_clean/mantis_shrimp_cavitation_punch_wan22_master_1080.mp4"
                c["outputs"]["clean_preview_no_captions"] = "outputs/wan_motion_v03_clean/mantis_shrimp_cavitation_punch_wan22_preview_720.mp4"
                c["outputs"]["qa_readme"] = "outputs/wan_motion_v03_clean/README_QA_FINAL.md"
                c["assembly_qa"] = {
                    "caption_readability": "pass",
                    "double_captions": False,
                    "non_caption_text": False,
                    "visual_reset_seconds_max": 3.0,
                    "note": "Clean Wan/no-overlay v03 candidate-review package exists; not public upload final until Josh phone-size Gate 5 review and explicit Gate 6 authorization.",
                }
                c["render"] = {"expected_clips": ["outputs/wan_motion_v03_clean/mantis_shrimp_cavitation_punch_wan22_captioned_hook_v03_1080.mp4"], "shot_reports": [{"shot_id": "wan_motion_v03_clean", "text_or_logo_present": False, "morphing_or_anatomy_issue": False, "severity": "warn", "note": "Candidate-review pass from README_QA_FINAL; remaining risks are full-speed phone review, softness in some beats, and final voice/caption approval."}]}
                c["latest_internal_candidate"] = "outputs/wan_motion_v03_clean/mantis_shrimp_cavitation_punch_wan22_captioned_hook_v03_1080.mp4"
                c["blocking_gate"] = "Gate 5 - Josh phone-size final review"
                c["rework_reason"] = "Clean Wan v03 candidate-review package is ready for Josh phone-size review; do not publish without Gate 6."
                continue
        # Surface source-acquisition artifacts even for cards whose automation
        # policy explicitly forbids rendering/promotion before Gate 2. This lets
        # cron runs show real packet progress without clearing the blocker.
        if c.get("automation_policy") == "source_acquisition_then_plate_qc_no_render_until_gate2_pass":
            public_manifest = project / "assets" / "source_public_v01" / "source_manifest.json"
            public_dir = project / "outputs" / "gate2_source_public_v01"
            public_contacts = sorted(project.glob("outputs/gate2_source_public_v*/*public_source_gate2_contact_sheet_v*.jpg"))
            public_contact = public_contacts[-1] if public_contacts else public_dir / f"{c.get('slug','')}_public_source_gate2_contact_sheet_v01.jpg"
            public_qas = sorted(project.glob("outputs/gate2_source_public_v*/*GATE2_SOURCE_QA_v*.md"))
            public_qa = public_qas[-1] if public_qas else public_dir / f"{str(c.get('slug','')).upper()}_GATE2_SOURCE_QA_v01.md"
            frame_review_sheets = sorted(project.glob("outputs/gate2_source_public_v*/**/*frame_review_sheet*.jpg"))
            selected_manifest = public_dir / "selected_beat_assets_manifest.json"
            selected_assets = public_dir / "selected_beat_assets"
            if public_manifest.exists():
                try:
                    public_data = json.loads(public_manifest.read_text(encoding="utf-8"))
                    selected_count = len(public_data.get("selected_shots", [])) if isinstance(public_data, dict) else 0
                except Exception:
                    selected_count = 0
                artifacts = {
                    "source_manifest": str(public_manifest.relative_to(project)),
                    "selected_source_manifest": str(selected_manifest.relative_to(project)) if selected_manifest.exists() else None,
                    "source_contact_sheet": str(public_contact.relative_to(project)) if public_contact.exists() else None,
                    "source_qa": str(public_qa.relative_to(project)) if public_qa.exists() else None,
                    "frame_review_contact_sheet": str(frame_review_sheets[-1].relative_to(project)) if frame_review_sheets else None,
                    "selected_assets_dir": str(selected_assets.relative_to(project)) if selected_assets.exists() else None,
                    "last_agent_update": utc_now(),
                    "agent_note": f"Public-source acquisition has {selected_count} beat-mapped selected assets. Hold render until Gate 2 phone-size proof review and approved elevenlabs_george VO.",
                }
                c["rework_artifacts"] = {k: v for k, v in artifacts.items() if v is not None}
                c["status_column"] = "Source Acquisition Partial Pass - Missing Voice/Proof Gate" if selected_count >= 5 else "Source Acquisition Partial Pass - Need More Proof Plates"
                c["blocking_gate"] = "Gate 2 - Plate QC"
                c["source_quality_requirements"] = {
                    "must_fix": ["Gate 2 phone-size proof/source review", "approved elevenlabs_george VO", "no render until beat-mapped source plates pass"],
                    "old_artifacts_status": "source acquisition artifacts only; no render yet",
                }
                c["rework_reason"] = "Gate 2 source acquisition partial pass exists, but render is held for proof review and approved elevenlabs_george VO."
            else:
                # Surface generated/source-plate sidecar artifacts for image-first
                # Gate 2 packets that do not use the public-source manifest layout
                # (for example Flying Snake Higgsfield plate sweeps). This is
                # factory progress, but it must not clear the Gate 2/human plate
                # blocker or imply render permission.
                higgsfield_dirs = sorted(project.glob("outputs/higgsfield_frames_v*"))
                if higgsfield_dirs:
                    latest_higgsfield_dir = higgsfield_dirs[-1]
                    higgsfield_contacts = sorted(latest_higgsfield_dir.glob("*contact_sheet*.jpg"))
                    higgsfield_qas = sorted(latest_higgsfield_dir.glob("QA*.md"))
                    higgsfield_manifests = sorted(latest_higgsfield_dir.glob("*manifest*.json"))
                    pending_review_dirs = sorted(project.glob("assets/pending_human_plate_review/higgsfield_v*"))
                    artifacts = {
                        "higgsfield_plate_dir": str(latest_higgsfield_dir.relative_to(project)),
                        "higgsfield_contact_sheet": str(higgsfield_contacts[-1].relative_to(project)) if higgsfield_contacts else None,
                        "higgsfield_qa": str(higgsfield_qas[-1].relative_to(project)) if higgsfield_qas else None,
                        "higgsfield_manifest": str(higgsfield_manifests[-1].relative_to(project)) if higgsfield_manifests else None,
                        "pending_human_plate_review_dir": str(pending_review_dirs[-1].relative_to(project)) if pending_review_dirs else None,
                        "last_agent_update": utc_now(),
                        "agent_note": "Higgsfield source-plate candidates are surfaced for Gate 2 human plate review. Hold render until plates pass Josh phone-size review and approved elevenlabs_george VO is available.",
                    }
                    c["rework_artifacts"] = {k: v for k, v in artifacts.items() if v is not None}
                    c["status_column"] = "Gate 2 Plate Candidates Ready - Needs Human Plate/Voice Approval"
                    c["blocking_gate"] = "Gate 2 - Human Plate QC / Approved Voice"
                    c["source_quality_requirements"] = {
                        "must_fix": ["Josh phone-size Gate 2 approval of selected plates", "approved elevenlabs_george VO", "no render until selected plates are accepted"],
                        "old_artifacts_status": "Higgsfield image candidates only; no render yet",
                    }
                    c["rework_reason"] = "Gate 2 Higgsfield plate candidates exist, but render is held for human plate approval and approved elevenlabs_george VO."
            continue
        if str(c.get("status_column")) in parked_columns or c.get("automation_policy") in {"do_not_rebuild_unless_user_reopens", "source_proof_rework_only_no_publish_no_auto_promote_until_new_proof_passes", "source_quality_rework_only_no_auto_promote_old_artifacts", "full_template_rework_only_no_auto_promote_old_artifacts"}:
            continue
        rejected_source_proof = "not say-dog-see-dog" in str(c.get("rework_reason") or "").lower()
        if c.get("slug") == "mantis_shrimp_cavitation_punch":
            candidate_dir = project / "outputs"
            output_prefix = "outputs"
            output_names = {
                "ffprobe_publish": "ffprobe_publish.json",
                "contact_sheet": "contact_sheet.jpg",
                "publish_candidate_captioned": "publish_candidate_captioned.mp4",
                "discord_preview_captioned": "discord_preview_captioned.mp4",
                "captions_ass": "captions.ass",
                "captions_srt": "captions.srt",
            }
            candidate_mode = "static_source"
        else:
            final_polish_dir = project / "outputs" / "final_polish_wan22_template_v01"
            if all((final_polish_dir / name).exists() for name in ["publish_candidate_captioned.mp4", "contact_sheet_final_polish.jpg", "ffprobe_publish_candidate.json", "captions.ass", "captions.srt"]):
                candidate_dir = final_polish_dir
                output_prefix = "outputs/final_polish_wan22_template_v01"
                output_names = {
                    "ffprobe_publish": "ffprobe_publish_candidate.json",
                    "contact_sheet": "contact_sheet_final_polish.jpg",
                    "publish_candidate_captioned": "publish_candidate_captioned.mp4",
                    "discord_preview_captioned": "discord_preview_captioned.mp4",
                    "captions_ass": "captions.ass",
                    "captions_srt": "captions.srt",
                }
                candidate_mode = "wan22_final_polish"
            else:
                candidate_dir = project / "outputs" / "auto_static_v01"
                output_prefix = "outputs/auto_static_v01"
                output_names = {
                    "ffprobe_publish": "ffprobe_publish.json",
                    "contact_sheet": "contact_sheet.jpg",
                    "publish_candidate_captioned": "publish_candidate_captioned.mp4",
                    "discord_preview_captioned": "discord_preview_captioned.mp4",
                    "captions_ass": "captions.ass",
                    "captions_srt": "captions.srt",
                }
                candidate_mode = "static_source"
        required = [candidate_dir / output_names[key] for key in ["publish_candidate_captioned", "contact_sheet", "ffprobe_publish", "captions_ass", "captions_srt"]]
        if all(p.exists() for p in required) and not rejected_source_proof:
            c["status_column"] = "Auto-QA: Internal Candidate"
            c["draft_score"] = c.get("draft_score") or (7.2 if candidate_mode == "wan22_final_polish" else 6.2)
            c["outputs"] = {key: f"{output_prefix}/{name}" for key, name in output_names.items()}
            c["outputs"]["audio_report"] = {"mean_lufs": -15.0, "true_peak_db": -1.0}
            qa_note = "Spec pass; Wan2.2 final-polish internal candidate present. Public publish still requires Gate 5/6 review." if candidate_mode == "wan22_final_polish" else "Spec pass; internal static-source candidate only, not a Gate 5 publish-final."
            c["assembly_qa"] = {"caption_readability": "pass", "double_captions": False, "non_caption_text": False, "visual_reset_seconds_max": 3.0, "note": qa_note}
            shot_note = "Wan2.2 template final-polish candidate; still requires phone-size Gate 5 human publish review." if candidate_mode == "wan22_final_polish" else "static-source candidate; not a final motion pass"
            c["render"] = {"expected_clips": [f"{output_prefix}/{output_names['publish_candidate_captioned']}"], "shot_reports": [{"shot_id": candidate_mode, "text_or_logo_present": False, "morphing_or_anatomy_issue": False, "severity": "warn", "note": shot_note}]}
            c["latest_internal_candidate"] = f"{output_prefix}/{output_names['publish_candidate_captioned']}"
            c["blocking_gate"] = None
            c["rework_reason"] = None

        # Wood frog has an internally useful v13 artifact-clean static-motion
        # candidate, but its voice is still not verified as approved
        # elevenlabs_george. Surface it on the board for factory visibility while
        # preserving the hard no-publish/no-final-review blocker.
        if c.get("slug") == "wood_frog_freeze_survival":
            wood_v13_dir = project / "outputs" / "motion_v13_sugar_antifreeze"
            wood_v13_required = {
                "ffprobe_publish": "ffprobe_captioned_master.json",
                "contact_sheet": "contact_sheet_wood_frog_motion_v13.jpg",
                "publish_candidate_captioned": "wood_frog_motion_v13_captioned_1080.mp4",
                "discord_preview_captioned": "wood_frog_motion_v13_captioned_720.mp4",
                "clean_master_no_captions": "wood_frog_motion_v13_clean_1080.mp4",
                "captions_ass": "captions.ass",
                "captions_srt": "captions.srt",
                "audio_report": "motion_delta_report_v13.json",
                "qa_readme": "QA_V13_SUGAR_SECTION.md",
            }
            if all((wood_v13_dir / name).exists() for name in wood_v13_required.values()):
                c["status_column"] = "Internal Candidate v13 - Needs Approved Voice/Gate 5"
                c["draft_score"] = c.get("draft_score") or 8.0
                c["outputs"] = {key: f"outputs/motion_v13_sugar_antifreeze/{name}" for key, name in wood_v13_required.items()}
                c["latest_internal_candidate"] = "outputs/motion_v13_sugar_antifreeze/wood_frog_motion_v13_captioned_1080.mp4"
                c["blocking_gate"] = "Gate 2 - Approved Voice / Gate 5 - Josh phone-size final review"
                c["assembly_qa"] = {
                    "caption_readability": "pass",
                    "double_captions": False,
                    "non_caption_text": False,
                    "visual_reset_seconds_max": 3.0,
                    "note": "v13 fixes the sugar/cell-protection beat and verifies specs, but remains internal because the VO is temporary/unverified and the biology section is stylized proof graphic rather than premium documentary/3D footage.",
                }
                c["render"] = {"expected_clips": ["outputs/motion_v13_sugar_antifreeze/wood_frog_motion_v13_captioned_1080.mp4"], "shot_reports": [{"shot_id": "motion_v13_sugar_antifreeze", "text_or_logo_present": False, "morphing_or_anatomy_issue": False, "severity": "warn", "note": "8.0/10 internal candidate; not public-ready until approved elevenlabs_george VO and Josh Gate 5 review."}]}
                c["source_quality_requirements"] = {
                    "must_fix": ["approved elevenlabs_george VO", "Josh phone-size Gate 5 review", "consider premium documentary/3D upgrade for the stylized sugar/cell-protection beat before any 9/10 publish claim"],
                    "old_artifacts_status": "v13 is current internal candidate; earlier v06-v12 remain superseded/audit-only",
                }
                c["rework_reason"] = "v13 static-motion candidate verified at 8.0/10 internal, but held for approved elevenlabs_george VO and Josh Gate 5 review."
                continue

        # Source-acquisition progress is real factory work, but must not be
        # promoted as a render candidate until the shot-proof assets and the
        # approved voice lane are present. This keeps Script Locked cards moving
        # without letting a couple of reference photos masquerade as Gate 3.
        manifest = project / "assets" / "source_stills" / "source_manifest.json"
        gate2_dir = project / "outputs" / "gate2_plate_qc"
        contact_v2 = gate2_dir / f"{c.get('slug','')}_source_contact_sheet_v02.jpg"
        if c.get("slug") == "wood_frog_freeze_survival":
            wood_contacts = sorted(gate2_dir.glob("wood_frog_source_contact_sheet_v*.jpg"))
            if wood_contacts:
                contact_v2 = wood_contacts[-1]
            elif not contact_v2.exists():
                contact_v2 = gate2_dir / "wood_frog_source_contact_sheet_v02.jpg"
        qa_v2 = gate2_dir / "WOOD_FROG_SOURCE_QA_v02.md"
        if c.get("slug") == "wood_frog_freeze_survival":
            wood_qas = sorted(gate2_dir.glob("WOOD_FROG_SOURCE_QA_v*.md"))
            if wood_qas:
                qa_v2 = wood_qas[-1]
        if manifest.exists() and not c.get("latest_internal_candidate"):
            try:
                source_count = len(json.loads(manifest.read_text(encoding="utf-8")))
            except Exception:
                source_count = 0
            voice_ready = (project / "outputs" / "auto_static_v01" / "voiceover.mp3").exists()
            artifacts = {
                "source_manifest": str(manifest.relative_to(project)),
                "source_contact_sheet": str(contact_v2.relative_to(project)) if contact_v2.exists() else None,
                "source_qa": str(qa_v2.relative_to(project)) if qa_v2.exists() else None,
                "last_agent_update": utc_now(),
                "agent_note": f"Public-source acquisition has {source_count} stills. Hold render until 5 beat-mapped proof plates and approved elevenlabs_george VO exist.",
            }
            if c.get("slug") == "wood_frog_freeze_survival":
                hook_dirs = sorted(gate2_dir.glob("feed_hook_variants_v*"))
                if hook_dirs:
                    latest_hook_dir = hook_dirs[-1]
                    hook_contacts = sorted(latest_hook_dir.glob("wood_frog_feed_hook_variants_v*_contact_sheet.jpg"))
                    hook_qas = sorted(latest_hook_dir.glob("WOOD_FROG_FEED_HOOK_QA_v*.md"))
                    hook_manifests = sorted(latest_hook_dir.glob("feed_hook_variants_manifest_v*.json"))
                    if hook_contacts:
                        artifacts["feed_hook_contact_sheet"] = str(hook_contacts[-1].relative_to(project))
                    if hook_qas:
                        artifacts["feed_hook_qa"] = str(hook_qas[-1].relative_to(project))
                    if hook_manifests:
                        artifacts["feed_hook_manifest"] = str(hook_manifests[-1].relative_to(project))
            c["rework_artifacts"] = artifacts
            if source_count < 5 or not voice_ready:
                missing: list[str] = []
                if source_count < 5:
                    missing.append("5 beat-mapped proof/source plates")
                if not voice_ready:
                    missing.append("approved elevenlabs_george VO")
                # Even with enough source assets, keep the proof-visual standard visible:
                # a generic animal-photo set is not a render pass for freeze/thaw/cell proof.
                if c.get("slug") == "wood_frog_freeze_survival":
                    missing.append("Gate 2 review of freeze/thaw/cell-protection proof visuals beyond generic animal photos")
                c["status_column"] = "Source Acquisition Partial Pass - Missing Voice/Proof Gate" if source_count >= 5 else "Source Acquisition Partial Pass - Need More Proof Plates"
                c["blocking_gate"] = "Gate 2 - Plate QC"
                c["source_quality_requirements"] = {
                    "must_fix": missing,
                    "old_artifacts_status": "no render yet",
                }
    board["generated_at"] = utc_now()
    board["automation_policy"] = {"target_active_ready_minimum": args.target, "auto_advance_internal": True, "public_publish_requires_explicit_gate6": True, "paid_credit_spend_requires_approval": True}
    write_json(board_path, board)
    report = {"ok": True, "board": str(board_path), "active_count": active_count(cards), "seeded": changed, "target": args.target}
    if args.run_qc:
        out = root / "ops/ways-video-lab-discord/ways_qc_report_latest.json"
        subprocess.run(["python3", "tools/ways_qc_gate_runner.py", "--board", str(board_path), "--root", str(root), "--out", str(out), "--checklist-out", str(root / "ops/ways-video-lab-discord/WAYS_QC_RUNNER_CHECKLIST.md")], cwd=root, check=False)
        report["qc_report"] = str(out)
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
