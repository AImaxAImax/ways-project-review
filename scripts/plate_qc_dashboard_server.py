#!/usr/bin/env python3
"""Local Plate QC approval dashboard for WAYS Gate 2.

No third-party dependencies. Serves a human review UI and persists Josh's
approve/deny + lane-confirm decisions to a JSON file.

Run from repo root:
    python3 scripts/plate_qc_dashboard_server.py \
      --queue dashboard/plate_qc_queue.json \
      --decisions dashboard/plate_qc_decisions.json \
      --port 8765
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DECISIONS = {"approved", "denied"}
ALLOWED_LANES = {"wan_i2v", "motion_graphic", "still_motion", "regenerate", "hold"}
RENDERABLE_LANES = {"wan_i2v", "motion_graphic", "still_motion"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def safe_project_path(root: Path, rel_path: str) -> Path | None:
    raw = unquote(rel_path).lstrip("/")
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root.resolve())
        return resolved
    except Exception:
        return None


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>WAYS Plate QC Gate</title>
<style>
:root { color-scheme: dark; --bg:#080b12; --panel:#131926; --line:#293244; --text:#eef2ff; --muted:#9ca3af; --ok:#7ee787; --bad:#ff7b7b; --warn:#ffd166; --accent:#7dd3fc; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text); font-family:Inter, ui-sans-serif, system-ui, Segoe UI, Arial, sans-serif; }
header { position:sticky; top:0; z-index:10; background:rgba(8,11,18,.96); border-bottom:1px solid var(--line); padding:16px 20px; }
h1 { margin:0 0 6px; font-size:22px; }
.sub { color:var(--muted); font-size:13px; }
.controls { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
input, select, textarea, button { background:#0b1020; color:var(--text); border:1px solid var(--line); border-radius:10px; padding:8px 10px; }
button { cursor:pointer; font-weight:700; }
button.approve { border-color:var(--ok); color:var(--ok); }
button.deny { border-color:var(--bad); color:var(--bad); }
main { padding:20px; }
.card { display:grid; grid-template-columns:minmax(280px, 1.2fr) minmax(280px, .8fr); gap:16px; border:1px solid var(--line); background:var(--panel); border-radius:18px; padding:16px; margin-bottom:18px; }
@media(max-width:900px){ .card{grid-template-columns:1fr;} }
.meta { color:var(--muted); font-size:12px; display:flex; gap:8px; flex-wrap:wrap; margin:8px 0; }
.badge { border:1px solid var(--line); border-radius:999px; padding:3px 8px; font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:.04em; }
.badge.ok { color:var(--ok); border-color:var(--ok); } .badge.bad { color:var(--bad); border-color:var(--bad); } .badge.warn { color:var(--warn); border-color:var(--warn); } .badge.info { color:var(--accent); border-color:var(--accent); }
.full { max-width:100%; max-height:72vh; object-fit:contain; background:#05070b; border:1px solid var(--line); border-radius:14px; }
.phoneWrap { display:flex; align-items:flex-start; gap:14px; flex-wrap:wrap; }
.phone { width:270px; aspect-ratio:9/16; position:relative; overflow:hidden; border:10px solid #05070b; border-radius:30px; background:#000; box-shadow:0 18px 45px rgba(0,0,0,.35); }
.phone img { width:100%; height:100%; object-fit:cover; display:block; }
.safe { position:absolute; left:10%; right:10%; top:18%; bottom:22%; border:2px dashed rgba(255,209,102,.95); background:rgba(255,209,102,.08); pointer-events:none; }
.safe::after { content:'caption safe cue'; position:absolute; left:8px; top:8px; font-size:11px; color:#111827; background:rgba(255,209,102,.9); padding:2px 6px; border-radius:999px; }
.panel { border:1px solid var(--line); border-radius:14px; padding:12px; margin:10px 0; background:#0d1322; }
.panel h3 { margin:0 0 8px; font-size:14px; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:8px; }
.score { border:1px solid var(--line); border-radius:10px; padding:8px; }
.score b { display:block; font-size:20px; }
ul { margin:6px 0; padding-left:20px; }
textarea { width:100%; min-height:72px; }
.small { color:var(--muted); font-size:12px; }
.saved { color:var(--ok); font-size:13px; min-height:18px; }
a { color:var(--accent); }
</style>
</head>
<body>
<header>
  <h1>WAYS Plate QC Gate</h1>
  <div class="sub" id="status">Loading…</div>
  <div class="controls">
    <input id="q" placeholder="Search plate, shot, blocker, lane…" size="40" />
    <select id="filter"><option value="all">All</option><option value="pending">Pending</option><option value="blocked">Hard blockers</option><option value="approved">Approved</option><option value="denied">Denied</option></select>
  </div>
</header>
<main id="cards"></main>
<script>
const esc = s => String(s ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const media = p => p ? '/media/' + encodeURI(String(p).replace(/^\/+/, '')) : '';
let data = null;
function blockers(p){ return (((p.vlm||{}).detected_hard_blockers)||[]); }
function decisionFor(id){ return ((data.decisions||{}).decisions||{})[id] || null; }
function textFor(p){ return [p.plate_id,p.slug,p.shot_id,p.beat,p.candidate_lane,JSON.stringify(p.vlm||{})].join(' ').toLowerCase(); }
function scoreGrid(scores){ return Object.entries(scores||{}).map(([k,v]) => `<div class="score"><span class="small">${esc(k)}</span><b>${esc(v)}</b></div>`).join(''); }
function render(){
  if(!data) return;
  const q = document.getElementById('q').value.trim().toLowerCase();
  const f = document.getElementById('filter').value;
  const plates = (data.queue.plates||[]).filter(p => {
    const d = decisionFor(p.plate_id);
    const state = d ? d.decision : (blockers(p).length ? 'blocked' : 'pending');
    return (f==='all' || f===state) && (!q || textFor(p).includes(q));
  });
  document.getElementById('status').textContent = `${plates.length}/${(data.queue.plates||[]).length} plates shown. VLM scores are advisory only; Josh decision controls Gate 2. Decisions persist to ${data.decisions_path}.`;
  document.getElementById('cards').innerHTML = plates.map(p => {
    const v = p.vlm || {}; const a = v.animation || {}; const d = decisionFor(p.plate_id); const hard = blockers(p);
    const hasHard = hard.length > 0;
    const saved = d ? `<span class="badge ${d.decision==='approved'?'ok':'bad'}">${esc(d.decision)}</span><span>${esc(d.confirmed_lane||'')}</span><span>${esc(d.reviewed_at||'')}</span>` : '<span class="badge warn">pending Josh</span>';
    return `<article class="card" id="${esc(p.plate_id)}">
      <section>
        <h2>${esc(p.slug || '')} / ${esc(p.shot_id || '')}</h2>
        <div class="meta"><span>${esc(p.plate_id)}</span><span>${esc(p.generator||'')}</span><span>candidate: ${esc(p.candidate_lane||'')}</span>${saved}</div>
        <a href="${media(p.image_path)}" target="_blank"><img class="full" src="${media(p.image_path)}" alt="full-size plate" loading="lazy"></a>
        <div class="panel"><h3>Beat / claim</h3>${esc(p.beat || 'No beat text supplied.')}</div>
      </section>
      <section>
        <div class="phoneWrap"><div class="phone"><img src="${media(p.image_path)}" alt="phone preview"><div class="safe"></div></div><div class="small">Phone-size preview with caption-safe-zone cue. Click full image for native view.</div></div>
        <div class="panel"><h3>VLM advisory <span class="badge info">${esc(v.model || 'gemma3:12b')}</span></h3><p class="small">VLM advisory only — Josh approval controls Gate 2.</p><div class="grid">${scoreGrid(v.scores)}</div><p>${esc(v.advisory_summary || '')}</p></div>
        <div class="panel"><h3>Hard blockers ${hasHard ? '<span class="badge bad">detected</span>' : '<span class="badge ok">none listed</span>'}</h3>${hasHard ? '<ul>'+hard.map(b=>`<li><b>${esc(b.type)}</b> — ${esc(b.location)}: ${esc(b.evidence)} (${esc(b.confidence)})</li>`).join('')+'</ul>' : '<p class="small">No detected text/logo/UI/watermark blockers in queue data.</p>'}</div>
        <div class="panel"><h3>Animation / lane advisory</h3><div class="grid">${scoreGrid({friendliness:a.friendliness_score,boundary_clarity:a.boundary_clarity,texture_density:a.texture_density,suggested_lane:a.suggested_lane})}</div><p>${esc(a.rationale||'')}</p><p class="small">Failure modes: ${esc((a.expected_failure_modes||[]).join('; '))}</p></div>
        <div class="panel"><h3>Josh decision</h3>
          <select id="lane-${esc(p.plate_id)}"><option value="wan_i2v">wan_i2v</option><option value="motion_graphic">motion_graphic</option><option value="still_motion">still_motion</option><option value="regenerate">regenerate</option><option value="hold">hold</option></select>
          <input id="score-${esc(p.plate_id)}" type="number" min="0" max="10" step="0.1" placeholder="human score" value="${esc(d?.human_score || '')}" />
          <label class="small"><input id="override-${esc(p.plate_id)}" type="checkbox" ${d?.override_hard_blockers?'checked':''}/> override hard blockers</label>
          <textarea id="notes-${esc(p.plate_id)}" placeholder="Notes required for hard-blocker override">${esc(d?.notes || '')}</textarea>
          <div class="controls"><button class="approve" onclick="saveDecision('${esc(p.plate_id)}','approved')">Approve + persist</button><button class="deny" onclick="saveDecision('${esc(p.plate_id)}','denied')">Deny / regenerate</button></div>
          <div class="saved" id="saved-${esc(p.plate_id)}"></div>
        </div>
      </section>
    </article>`;
  }).join('') || '<p>No plates match.</p>';
  for (const p of plates) {
    const d = decisionFor(p.plate_id);
    document.getElementById('lane-'+p.plate_id).value = d?.confirmed_lane || (p.vlm?.animation?.suggested_lane || p.candidate_lane || 'wan_i2v');
  }
}
async function load(){
  const res = await fetch('/api/queue');
  data = await res.json();
  render();
}
async function saveDecision(id, decision){
  const body = {
    plate_id:id, decision, reviewer:'Josh',
    confirmed_lane:document.getElementById('lane-'+id).value,
    human_score:document.getElementById('score-'+id).value ? Number(document.getElementById('score-'+id).value) : null,
    notes:document.getElementById('notes-'+id).value,
    override_hard_blockers:document.getElementById('override-'+id).checked
  };
  const res = await fetch('/api/decision', {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify(body)});
  const out = await res.json();
  const el = document.getElementById('saved-'+id);
  if(!res.ok){ el.style.color='var(--bad)'; el.textContent = out.error || 'Save failed'; return; }
  el.style.color='var(--ok)'; el.textContent = 'Saved ' + out.decision.reviewed_at;
  await load();
}
document.getElementById('q').addEventListener('input', render);
document.getElementById('filter').addEventListener('change', render);
load().catch(e => { document.getElementById('status').textContent = 'Load failed: '+e; });
</script>
</body>
</html>
"""


class PlateQCHandler(BaseHTTPRequestHandler):
    server_version = "PlateQC/1.0"

    @property
    def app(self) -> "PlateQCServer":
        return self.server  # type: ignore[return-value]

    def send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text: str, content_type: str = "text/html; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_text(HTML)
            return
        if parsed.path == "/api/queue":
            self.send_json({
                "queue": read_json(self.app.queue_path, {"version": 1, "plates": []}),
                "decisions": read_json(self.app.decisions_path, {"version": 1, "decisions": {}}),
                "queue_path": str(self.app.queue_path),
                "decisions_path": str(self.app.decisions_path),
            })
            return
        if parsed.path.startswith("/media/"):
            media_path = safe_project_path(self.app.root, parsed.path.removeprefix("/media/"))
            if not media_path or not media_path.exists() or not media_path.is_file():
                self.send_error(404, "media not found")
                return
            data = media_path.read_bytes()
            self.send_response(200)
            self.send_header("content-type", mimetypes.guess_type(media_path.name)[0] or "application/octet-stream")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/decision":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("content-length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            decision = self.validate_decision(payload)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, 400)
            return
        decisions = read_json(self.app.decisions_path, {"version": 1, "decisions": {}})
        decisions.setdefault("version", 1)
        decisions.setdefault("decisions", {})[decision["plate_id"]] = decision
        decisions["updated_at"] = decision["reviewed_at"]
        atomic_write_json(self.app.decisions_path, decisions)
        self.send_json({"ok": True, "decision": decision})

    def validate_decision(self, payload: dict[str, Any]) -> dict[str, Any]:
        queue = read_json(self.app.queue_path, {"plates": []})
        plates = {p.get("plate_id"): p for p in queue.get("plates", []) if isinstance(p, dict)}
        plate_id = str(payload.get("plate_id", "")).strip()
        if plate_id not in plates:
            raise ValueError("Unknown plate_id")
        decision = str(payload.get("decision", "")).strip()
        if decision not in ALLOWED_DECISIONS:
            raise ValueError("decision must be approved or denied")
        lane = str(payload.get("confirmed_lane", "")).strip()
        if lane not in ALLOWED_LANES:
            raise ValueError(f"confirmed_lane must be one of {sorted(ALLOWED_LANES)}")
        if decision == "approved" and lane not in RENDERABLE_LANES:
            raise ValueError("approved plates require a renderable lane: wan_i2v, motion_graphic, or still_motion")
        reviewer = str(payload.get("reviewer") or "Josh").strip()
        if reviewer != "Josh":
            raise ValueError("Gate 2 reviewer must be Josh")
        notes = str(payload.get("notes") or "").strip()
        hard_blockers = plates[plate_id].get("vlm", {}).get("detected_hard_blockers") or []
        override = bool(payload.get("override_hard_blockers", False))
        if decision == "approved" and hard_blockers and (not override or not notes):
            raise ValueError("approval over detected hard blockers requires override_hard_blockers=true and notes")
        human_score = payload.get("human_score")
        if human_score in ("", None):
            human_score = None
        else:
            try:
                human_score = float(human_score)
            except Exception as exc:
                raise ValueError("human_score must be numeric") from exc
            if not 0 <= human_score <= 10:
                raise ValueError("human_score must be between 0 and 10")
        return {
            "schema_version": 1,
            "plate_id": plate_id,
            "decision": decision,
            "reviewer": reviewer,
            "reviewed_at": now_iso(),
            "confirmed_lane": lane,
            "human_score": human_score,
            "notes": notes,
            "vlm_was_advisory_only": True,
            "override_hard_blockers": override,
        }

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - {fmt % args}")


class PlateQCServer(ThreadingHTTPServer):
    def __init__(self, addr: tuple[str, int], handler: type[BaseHTTPRequestHandler], root: Path, queue_path: Path, decisions_path: Path):
        super().__init__(addr, handler)
        self.root = root.resolve()
        self.queue_path = queue_path.resolve()
        self.decisions_path = decisions_path.resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve WAYS Plate QC approval dashboard")
    parser.add_argument("--root", default=str(ROOT), help="project root")
    parser.add_argument("--queue", default="dashboard/plate_qc_queue.json", help="plate queue JSON path")
    parser.add_argument("--decisions", default="dashboard/plate_qc_decisions.json", help="decision persistence JSON path")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    queue_path = Path(args.queue)
    decisions_path = Path(args.decisions)
    if not queue_path.is_absolute():
        queue_path = root / queue_path
    if not decisions_path.is_absolute():
        decisions_path = root / decisions_path
    if not queue_path.exists():
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(queue_path, {"version": 1, "generated_at": now_iso(), "root": str(root), "plates": []})
    server = PlateQCServer((args.host, args.port), PlateQCHandler, root, queue_path, decisions_path)
    print(f"Plate QC dashboard: http://{args.host}:{args.port}/")
    print(f"Queue: {queue_path}")
    print(f"Decisions: {decisions_path}")
    server.serve_forever()


if __name__ == "__main__":
    main()
