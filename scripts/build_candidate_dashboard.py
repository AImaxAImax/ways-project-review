#!/usr/bin/env python3
"""Build a local candidate dashboard for Curious Shorts.

Scans test_cases/*/outputs for manifests, review JSON, QA markdown, videos, and
contact sheets, then writes dashboard/data.json and dashboard/index.html.

No third-party dependencies; safe to run from the repo root:
    python3 scripts/build_candidate_dashboard.py
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "dashboard"
DATA_PATH = DASHBOARD_DIR / "data.json"
INDEX_PATH = DASHBOARD_DIR / "index.html"

MEDIA_EXTS = {".mp4", ".mov", ".webm", ".mp3", ".wav", ".jpg", ".jpeg", ".png"}
VIDEO_EXTS = {".mp4", ".mov", ".webm"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def rel(path: Path | str) -> str:
    p = Path(path)
    if p.is_absolute():
        try:
            return p.relative_to(ROOT).as_posix()
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # keep dashboard resilient to half-written manifests
        return {"_parse_error": str(exc)}


def read_text(path: Path, limit: int = 12000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def first_matching_file(folder: Path, patterns: list[str]) -> str:
    for pattern in patterns:
        matches = sorted(folder.glob(pattern))
        if matches:
            return rel(matches[0])
    return ""


def topic_title(case_dir: Path) -> str:
    brief = case_dir / "production_brief.md"
    if brief.exists():
        text = read_text(brief, 4000)
        m = re.search(r"## Working title\s*\n\*\*(.+?)\*\*", text, re.S)
        if m:
            return m.group(1).strip()
        m = re.search(r"^#\s+(.+)$", text, re.M)
        if m:
            return m.group(1).strip()
    return case_dir.name.replace("_", " ").title()


def lane_for(name: str, data: Any = None) -> str:
    n = name.lower()
    if "wan22" in n or "wan2" in n:
        return "C - Local I2V / Wan2.2"
    if "motion_probe" in n or "render_v" in n:
        return "B/C - Edit motion probe"
    if "gpt_image" in n or "manual_v24" in n or "manual_v23" in n:
        return "E - GPT Image 2 still challenger"
    if "comfy" in n or "sdxl" in n or "dreamshaper" in n:
        return "B - Local stills / ComfyUI"
    if "voice" in n:
        return "Audio - voice"
    if "rough" in n:
        return "A - Rough motion graphics"
    return "Unknown / internal"


def compact_text(value: Any, max_len: int = 360) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = "; ".join(str(v) for v in value[:5])
    elif isinstance(value, dict):
        bits = []
        for k, v in list(value.items())[:6]:
            bits.append(f"{k}: {compact_text(v, 90)}")
        value = "; ".join(bits)
    s = re.sub(r"\s+", " ", str(value)).strip()
    return s[: max_len - 1] + "…" if len(s) > max_len else s


def markdown_block(text: str, heading_regex: str) -> str:
    m = re.search(heading_regex, text, re.I)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"\n##\s+", text[start:])
    end = start + nxt.start() if nxt else len(text)
    block = text[start:end]
    lines = [re.sub(r"^[-*]\s*", "", ln.strip(" `")) for ln in block.splitlines() if ln.strip()]
    return compact_text(lines, 500)


def verdict_from_text(text: str) -> str:
    t = text.lower()
    if "review-required" in t:
        return "review required"
    for label in ["strong hold", "hold", "successful", "accepted", "promoted", "pass", "failed", "did not pass"]:
        if label in t:
            return label
    return "needs human verdict"


def status_from(text: str, outputs: list[str], verdict: str) -> str:
    t = text.lower()
    v = verdict.lower()
    has_final_video = any(Path(o).suffix.lower() in VIDEO_EXTS for o in outputs)
    if "do not upload" in t or "not a 9/10" in t or "not yet a final" in t or "remaining blockers" in t or "did not pass" in t or "failed" in t:
        return "blocked" if not has_final_video else "publish-gated"
    if "strong hold" in v or "accepted/promoted" in t or "accepted" in v or "promoted" in v:
        return "promoted"
    if has_final_video and ("captions" in t or "qa" in t or "gate" in t):
        return "publish-gated"
    return "internal"


def resolve_media_path(value: str, folder: Path, case_dir: Path) -> str:
    p = Path(value)
    if p.is_absolute():
        return rel(p)
    if value.startswith(("outputs/", "assets/", "scripts/")):
        return rel(case_dir / value)
    candidate = folder / value
    if candidate.exists():
        return rel(candidate)
    return rel(case_dir / value)


def collect_outputs(folder: Path, data: Any, case_dir: Path) -> list[str]:
    outputs: set[str] = set()
    if isinstance(data, dict):
        for key in ["clip", "contact_sheet", "file", "master", "discord", "latest_contact_sheet"]:
            val = data.get(key)
            if isinstance(val, str) and Path(val).suffix.lower() in MEDIA_EXTS:
                outputs.add(resolve_media_path(val, folder, case_dir))
        for key in ["shots", "generated_after_reassessment"]:
            val = data.get(key)
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        for subkey in ["clip", "contact_sheet", "file", "source_image"]:
                            out = item.get(subkey)
                            if isinstance(out, str) and Path(out).suffix.lower() in MEDIA_EXTS:
                                outputs.add(resolve_media_path(out, folder, case_dir))
        for key in ["current_holds"]:
            val = data.get(key)
            if isinstance(val, dict):
                for item in val.values():
                    if isinstance(item, dict) and isinstance(item.get("file"), str):
                        outputs.add(resolve_media_path(item["file"], folder, case_dir))
    for media in folder.iterdir() if folder.exists() else []:
        if media.is_file() and media.suffix.lower() in MEDIA_EXTS and "frame_" not in media.name:
            outputs.add(rel(media))
    return sorted(outputs)


def candidate_id(case_dir: Path, path: Path, name: str) -> str:
    outputs_dir = case_dir / "outputs"
    try:
        folder_rel = path.parent.relative_to(outputs_dir).as_posix()
    except ValueError:
        folder_rel = ""
    if folder_rel == ".":
        folder_rel = ""
    if folder_rel and folder_rel != name:
        return f"{case_dir.name}/{folder_rel}/{name}"
    return f"{case_dir.name}/{name}"


def candidate_from_manifest(path: Path, case_dir: Path, topic: str) -> dict[str, Any]:
    data = read_json(path)
    folder = path.parent
    name = path.parent.name if path.name == "manifest.json" else path.stem.replace("_manifest", "")
    qa_files = sorted([*folder.glob("README_QA*.md"), *folder.glob("README_STATUS.md")])
    qa_text = "\n\n".join(read_text(p) for p in qa_files)
    outputs = collect_outputs(folder, data, case_dir)
    contact_sheet = first_matching_file(folder, ["*contact*.jpg", "*contact*.png", "contact_sheet*.jpg"])
    if not contact_sheet:
        contact_sheet = next((o for o in outputs if "contact" in o.lower() and Path(o).suffix.lower() in IMAGE_EXTS), "")
    summary = ""
    verdict = "needs human verdict"
    next_action = "Review candidate and set next action."
    blockers = ""
    if isinstance(data, dict):
        summary = compact_text(data.get("decision") or data.get("result") or data.get("overall_visual_state") or data.get("created_at") or "manifest")
        next_action = compact_text(data.get("next_step") or data.get("next_generation_target") or next_action, 280)
        verdict = verdict_from_text(json.dumps(data, ensure_ascii=False) + " " + qa_text)
    if qa_text:
        blockers = markdown_block(qa_text, r"\n##\s+(Remaining blockers|Gate|Harsh gate|Visual QA from contact sheet)\s*\n")
        rec = re.search(r"Recommended next step:\s*(.+)", qa_text, re.I)
        if rec:
            next_action = compact_text(rec.group(1), 280)
        if summary == "manifest":
            summary = compact_text(markdown_block(qa_text, r"\n##\s+(Outputs|Decision|Gate|Harsh gate)\s*\n"), 300)
    text_for_status = json.dumps(data, ensure_ascii=False) + " " + qa_text
    status = status_from(text_for_status, outputs, verdict)
    return {
        "id": candidate_id(case_dir, path, name),
        "topic": topic,
        "model_lane": lane_for(name, data),
        "source": rel(path),
        "status": status,
        "human_verdict": verdict,
        "next_action": next_action,
        "qa_blockers": blockers,
        "summary": summary,
        "contact_sheet": contact_sheet,
        "outputs": outputs[:12],
        "updated": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds"),
    }


def candidate_from_review(path: Path, case_dir: Path, topic: str) -> dict[str, Any]:
    data = read_json(path)
    folder = path.parent
    name = path.stem.replace("_review", "")
    outputs = collect_outputs(folder, data, case_dir)
    contact_sheet = ""
    if "contact_sheet" in path.name:
        contact_sheet = rel(path)
    else:
        stem_prefix = name.replace("_selected", "")
        candidates = sorted(folder.glob(stem_prefix + "*contact*.jpg")) + sorted(folder.glob("*contact*.jpg"))
        if candidates:
            contact_sheet = rel(candidates[0])
    verdict = compact_text(data.get("decision") if isinstance(data, dict) else "needs human verdict", 220)
    next_action = compact_text(data.get("next_step") if isinstance(data, dict) else "Review candidate and set next action.", 260)
    blockers = compact_text((data.get("caveats") or data.get("remaining_blockers") or data.get("result")) if isinstance(data, dict) else "", 420)
    status = status_from(json.dumps(data, ensure_ascii=False), outputs, verdict)
    return {
        "id": candidate_id(case_dir, path, name),
        "topic": topic,
        "model_lane": lane_for(name, data),
        "source": rel(path),
        "status": status,
        "human_verdict": verdict or "needs human verdict",
        "next_action": next_action or "Review candidate and set next action.",
        "qa_blockers": blockers,
        "summary": compact_text((data.get("overall_visual_state") or data.get("source") or data.get("shot")) if isinstance(data, dict) else "review", 260),
        "contact_sheet": contact_sheet,
        "outputs": outputs[:12],
        "updated": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds"),
    }


def build_data() -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for case_dir in sorted((ROOT / "test_cases").glob("*")):
        if not case_dir.is_dir():
            continue
        topic = topic_title(case_dir)
        outputs_dir = case_dir / "outputs"
        if not outputs_dir.exists():
            continue
        seen: set[Path] = set()
        for path in sorted(outputs_dir.rglob("*.json")):
            if any(part in {"frames", "clips", "__pycache__"} for part in path.parts):
                continue
            if path.name.startswith("ffprobe"):
                continue
            if "manifest" in path.stem or path.name == "manifest.json" or "selected" in path.stem or "status" in path.stem:
                candidates.append(candidate_from_manifest(path, case_dir, topic))
                seen.add(path)
            elif "review" in path.stem:
                candidates.append(candidate_from_review(path, case_dir, topic))
                seen.add(path)
        # Directory-level QA/readme without manifest gets its own candidate row.
        for qa in sorted(outputs_dir.rglob("README_QA*.md")):
            if qa.parent / "manifest.json" in seen:
                continue
            text = read_text(qa)
            media = sorted(rel(p) for p in qa.parent.iterdir() if p.is_file() and p.suffix.lower() in MEDIA_EXTS and "frame_" not in p.name)
            verdict = verdict_from_text(text)
            candidates.append({
                "id": f"{case_dir.name}/{qa.parent.name}",
                "topic": topic,
                "model_lane": lane_for(qa.parent.name),
                "source": rel(qa),
                "status": status_from(text, media, verdict),
                "human_verdict": verdict,
                "next_action": compact_text(re.search(r"Recommended next step:\s*(.+)", text, re.I).group(1), 260) if re.search(r"Recommended next step:\s*(.+)", text, re.I) else "Review candidate and set next action.",
                "qa_blockers": markdown_block(text, r"\n##\s+(Remaining blockers|Gate|Harsh gate)\s*\n"),
                "summary": compact_text(markdown_block(text, r"\n##\s+(Outputs verified|Outputs|Verified specs)\s*\n"), 260),
                "contact_sheet": first_matching_file(qa.parent, ["*contact*.jpg", "*contact*.png"]),
                "outputs": media[:12],
                "updated": datetime.fromtimestamp(qa.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds"),
            })
    candidates.sort(key=lambda c: (c["topic"], c["updated"], c["id"]), reverse=True)
    counts = {status: sum(1 for c in candidates if c["status"] == status) for status in ["internal", "publish-gated", "blocked", "promoted"]}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": ROOT.as_posix(),
        "counts": counts,
        "candidates": candidates,
    }


def write_index() -> None:
    INDEX_PATH.write_text("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Curious Shorts Candidate Dashboard</title>
<style>
:root { color-scheme: dark; --bg:#0e1116; --panel:#171b23; --muted:#9ca3af; --text:#eef2ff; --line:#2b3240; --accent:#8bd3ff; --bad:#ff7b7b; --gate:#ffd166; --ok:#7ee787; --int:#a78bfa; }
* { box-sizing: border-box; } body { margin:0; font-family: Inter, ui-sans-serif, system-ui, Segoe UI, Arial, sans-serif; background:var(--bg); color:var(--text); }
header { position:sticky; top:0; z-index:10; background:linear-gradient(180deg,#111827 0%,rgba(17,24,39,.93) 100%); border-bottom:1px solid var(--line); padding:18px 22px; }
h1 { margin:0 0 8px; font-size:22px; } .sub { color:var(--muted); font-size:13px; }
.controls { display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; align-items:center; }
button, input, select, textarea { background:#0b0f17; color:var(--text); border:1px solid var(--line); border-radius:10px; padding:8px 10px; }
button { cursor:pointer; } button.active { border-color:var(--accent); color:var(--accent); }
main { padding:22px; } .grid { display:grid; grid-template-columns: repeat(auto-fill,minmax(360px,1fr)); gap:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:14px; box-shadow:0 10px 30px rgba(0,0,0,.18); }
.card h2 { margin:0 0 8px; font-size:16px; line-height:1.25; } .meta { color:var(--muted); font-size:12px; display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px; }
.badge { display:inline-flex; align-items:center; border-radius:999px; padding:3px 8px; font-size:12px; font-weight:700; border:1px solid var(--line); text-transform:uppercase; letter-spacing:.04em; }
.internal { color:var(--int); border-color:var(--int); } .publish-gated { color:var(--gate); border-color:var(--gate); } .blocked { color:var(--bad); border-color:var(--bad); } .promoted { color:var(--ok); border-color:var(--ok); }
.thumb { width:100%; max-height:240px; object-fit:contain; background:#05070b; border-radius:12px; border:1px solid var(--line); margin:8px 0 12px; }
.row { margin:8px 0; } .label { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.05em; margin-bottom:2px; }
.small { color:var(--muted); font-size:12px; } a { color:var(--accent); text-decoration:none; } a:hover { text-decoration:underline; }
ul { padding-left:20px; margin:6px 0; } textarea { width:100%; min-height:56px; resize:vertical; margin-top:4px; }
.summary { display:grid; grid-template-columns: repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin-bottom:16px; } .stat { background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:12px; }
.stat b { display:block; font-size:22px; }
</style>
</head>
<body>
<header>
  <h1>Curious Shorts Candidate Dashboard</h1>
  <div class="sub" id="generated"></div>
  <div class="controls">
    <input id="search" placeholder="Search topic, lane, verdict, blockers…" size="40" />
    <button data-filter="all" class="active">All</button>
    <button data-filter="internal">Internal</button>
    <button data-filter="publish-gated">Publish-gated</button>
    <button data-filter="blocked">Blocked</button>
    <button data-filter="promoted">Promoted</button>
  </div>
</header>
<main>
  <section class="summary" id="summary"></section>
  <section class="grid" id="cards"></section>
</main>
<script>
const state = { data:null, filter:'all', q:'' };
const esc = s => String(s ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const href = p => p ? '../' + p.replace(/^\\/+/, '') : '';
const noteKey = (id, field) => `candidate-dashboard:${id}:${field}`;
function statusBadge(s){ return `<span class="badge ${esc(s)}">${esc(s)}</span>`; }
function candidateText(c){ return [c.id,c.topic,c.model_lane,c.status,c.human_verdict,c.next_action,c.qa_blockers,c.summary,(c.outputs||[]).join(' ')].join(' ').toLowerCase(); }
function render(){
  const d = state.data; if(!d) return;
  document.getElementById('generated').textContent = `Generated ${d.generated_at} from ${d.root}. Human verdict / next-action notes save in this browser via localStorage.`;
  document.getElementById('summary').innerHTML = ['internal','publish-gated','blocked','promoted'].map(s => `<div class="stat">${statusBadge(s)}<b>${d.counts[s]||0}</b></div>`).join('');
  const q = state.q.trim().toLowerCase();
  const rows = d.candidates.filter(c => (state.filter==='all'||c.status===state.filter) && (!q || candidateText(c).includes(q)));
  document.getElementById('cards').innerHTML = rows.map(c => {
    const hv = localStorage.getItem(noteKey(c.id,'human_verdict')) || c.human_verdict || '';
    const nx = localStorage.getItem(noteKey(c.id,'next_action')) || c.next_action || '';
    const outputs = (c.outputs||[]).slice(0,8).map(o => `<li><a href="${href(o)}">${esc(o.split('/').pop())}</a></li>`).join('');
    return `<article class="card">
      <h2>${esc(c.id)}</h2>
      <div class="meta">${statusBadge(c.status)}<span>${esc(c.topic)}</span><span>${esc(c.model_lane)}</span></div>
      ${c.contact_sheet ? `<a href="${href(c.contact_sheet)}"><img class="thumb" src="${href(c.contact_sheet)}" loading="lazy" alt="contact sheet"></a>` : ''}
      <div class="row"><div class="label">Summary</div>${esc(c.summary || 'No summary')}</div>
      <div class="row"><div class="label">QA blockers / gate notes</div>${esc(c.qa_blockers || 'No blockers found in scanned notes.')}</div>
      <div class="row"><div class="label">Human verdict</div><textarea data-id="${esc(c.id)}" data-field="human_verdict">${esc(hv)}</textarea></div>
      <div class="row"><div class="label">Next action</div><textarea data-id="${esc(c.id)}" data-field="next_action">${esc(nx)}</textarea></div>
      <div class="row"><div class="label">Outputs</div><ul>${outputs || '<li class="small">No media outputs found.</li>'}</ul></div>
      <div class="small">Source: <a href="${href(c.source)}">${esc(c.source)}</a> · Updated ${esc(c.updated)}</div>
    </article>`;
  }).join('') || '<p>No candidates match the current filter.</p>';
  document.querySelectorAll('textarea').forEach(t => t.addEventListener('input', e => localStorage.setItem(noteKey(e.target.dataset.id,e.target.dataset.field), e.target.value)));
}
document.querySelectorAll('button[data-filter]').forEach(b => b.addEventListener('click', () => { document.querySelectorAll('button[data-filter]').forEach(x=>x.classList.remove('active')); b.classList.add('active'); state.filter=b.dataset.filter; render(); }));
document.getElementById('search').addEventListener('input', e => { state.q=e.target.value; render(); });
fetch('data.json').then(r => r.json()).then(d => { state.data=d; render(); }).catch(err => { document.getElementById('cards').textContent = 'Could not load data.json: ' + err; });
</script>
</body>
</html>
""", encoding="utf-8")


def main() -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    data = build_data()
    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    write_index()
    print(f"Wrote {DATA_PATH.relative_to(ROOT)} with {len(data['candidates'])} candidates")
    print(f"Wrote {INDEX_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
