#!/usr/bin/env python3
"""Build a focused Josh-attention dashboard for WAYS human gates.

This is intentionally separate from the broad media/candidate dashboard. It only
surfaces items that need a human decision, grouped by gate type, with the media
or metadata needed to make that decision in-place.
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path("/mnt/c/dev/curious-shorts")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ways_discord_qa import QA_CHANNEL_ID, REVIEW_THREAD_ID, discord_command_for_review

OUT = ROOT / "dashboard" / "review.html"
BOARD = "ways-video-lab"


def rel(path: str | Path | None) -> str:
    if not path:
        return ""
    p = Path(path)
    if p.is_absolute():
        try:
            return str(p.relative_to(ROOT))
        except ValueError:
            return str(p)
    return str(p)


def exists_rel(path: str | Path | None) -> bool:
    if not path:
        return False
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return p.exists()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def kanban_tasks(status: str) -> list[dict[str, Any]]:
    try:
        raw = subprocess.check_output(
            ["hermes", "kanban", "--board", BOARD, "list", "--status", status, "--json"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return json.loads(raw)
    except Exception:
        return []


def e(s: Any) -> str:
    return html.escape(str(s or ""), quote=True)


def load_shark_final() -> dict[str, Any] | None:
    base = ROOT / "test_cases/sharks_older_than_trees/outputs/final_polish_v27_captioned"
    if not base.exists():
        return None
    verification = load_json(base / "youtube_draft_pack_20260606/youtube_verification.json")
    metadata = load_json(base / "youtube_draft_pack_20260606/youtube_metadata.json")
    after = verification.get("after") or verification.get("before") or {}
    gate_text = (base / "PUBLISH_GATE.md").read_text(encoding="utf-8") if (base / "PUBLISH_GATE.md").exists() else ""
    checklist = []
    for line in gate_text.splitlines():
        if line.strip().startswith("- ["):
            checklist.append(line.strip().replace("- [ ]", "").replace("- [x]", ""))
    return {
        "slug": "sharks_older_than_trees",
        "title": metadata.get("title") or after.get("title") or "Sharks Are Older Than Trees #Shorts",
        "topic": "Sharks Are Older Than Trees",
        "candidate_video": rel(base / "publish_candidate_captioned.mp4"),
        "discord_preview": rel(base / "discord_preview_captioned.mp4"),
        "contact_sheet": rel(base / "contact_sheet_final_polish.jpg"),
        "publish_gate": rel(base / "PUBLISH_GATE.md"),
        "metadata": metadata,
        "youtube": after,
        "checklist": checklist,
        "base": rel(base),
    }


def gate_header(gate: str, title: str, count: int, desc: str) -> str:
    status = "empty" if count == 0 else "needs"
    return f"""
    <header class="gate-head {status}">
      <div>
        <div class="eyebrow">{e(gate)}</div>
        <h2>{e(title)}</h2>
        <p>{e(desc)}</p>
      </div>
      <div class="count">{count}</div>
    </header>
    """


def empty_card(text: str) -> str:
    return f'<div class="empty-card">✅ {e(text)}</div>'


def admin_card(tasks: list[dict[str, Any]]) -> str:
    if not tasks:
        return empty_card("No Discord/admin setup items need you right now.")
    cards = []
    for t in tasks:
        cards.append(f"""
        <article class="decision-card admin">
          <div class="badge danger">Needs Discord admin</div>
          <h3>{e(t.get('title'))}</h3>
          <p class="why">I cannot do this from the current Discord gateway. A server admin has to create/pin channels or give me a target that already exists.</p>
          <div class="info-grid">
            <div><b>Task ID</b><span>{e(t.get('id'))}</span></div>
            <div><b>Files to use</b><span><code>ops/ways-video-lab-discord/README.md</code><br><code>ops/ways-video-lab-discord/seed-posts.md</code></span></div>
            <div><b>Decision needed</b><span>Create the WAYS Video Lab Discord hub, or tell me to skip Discord and keep this local.</span></div>
          </div>
          <details><summary>Full task text</summary><pre>{e(t.get('body'))}</pre></details>
        </article>
        """)
    return "".join(cards)


def final_review_card(item: dict[str, Any]) -> str:
    video = item["candidate_video"]
    contact = item["contact_sheet"]
    command_private = discord_command_for_review(item["slug"], "Gate 5")
    command_reject = f"QA {item['slug']} reject notes=\"what failed and exact rework\""
    checklist = "".join(f"<li>{e(x)}</li>" for x in item.get("checklist") or [])
    return f"""
    <article class="decision-card final-review" data-slug="{e(item['slug'])}">
      <div class="badge warn">Phone-size watch required</div>
      <h3>{e(item['title'])}</h3>
      <p class="why">Watch the full captioned candidate like a viewer. This is the 8-9/10 private-draft gate and/or 9/10+ publish-readiness judgment. Contact sheets are not enough.</p>
      <div class="review-layout">
        <section class="phone-frame">
          <video controls playsinline preload="metadata" src="/{e(video)}" poster="/{e(contact)}"></video>
        </section>
        <section class="decision-panel">
          <div class="info-grid compact">
            <div><b>Local candidate</b><span><a href="/{e(video)}" target="_blank">open MP4</a></span></div>
            <div><b>Contact sheet</b><span><a href="/{e(contact)}" target="_blank">open image</a></span></div>
            <div><b>Publish gate file</b><span><a href="/{e(item['publish_gate'])}" target="_blank">open MD</a></span></div>
          </div>
          <h4>What to check</h4>
          <ul class="checklist">{checklist}</ul>
          <label>Score
            <select class="score" data-key="{e(item['slug'])}:score">
              <option value="">choose...</option>
              <option>reject / below 8</option>
              <option>8 private-draft OK</option>
              <option>9 public-eligible</option>
              <option>10 publish now quality</option>
            </select>
          </label>
          <label>Notes / exact rework if rejected
            <textarea data-key="{e(item['slug'])}:notes" placeholder="Example: Shot 4 caption too small, shark teeth look warped, audio ok..."></textarea>
          </label>
          <div class="actions">
            <button onclick="saveDecision(this,'approve-private')">Approve private draft</button>
            <button onclick="saveDecision(this,'approve-public-quality')">9+ quality, ready for publish auth</button>
            <button class="reject" onclick="saveDecision(this,'reject-rework')">Reject / rework</button>
          </div>
          <div class="discord-reply">
            <b>Discord-first path</b>
            <p>Prefer replying in the WAYS thread so the decision lives with the project discussion.</p>
            <code>{e(command_private)}</code>
            <code>{e(command_reject)}</code>
            <button class="copy" onclick="copyCommand(this,'{e(command_private)}')">Copy approve command</button>
          </div>
          <p class="saved" aria-live="polite"></p>
        </section>
      </div>
    </article>
    """


def publish_auth_card(item: dict[str, Any]) -> str:
    yt = item.get("youtube") or {}
    meta = item.get("metadata") or {}
    command_publish = discord_command_for_review(item["slug"], "Gate 6")
    command_hold = f"QA {item['slug']} keep-private notes=\"hold reason\""
    url = yt.get("url") or ""
    studio = yt.get("studio_url") or ""
    rows = [
        ("Video ID", yt.get("video_id")),
        ("Privacy", yt.get("privacyStatus") or meta.get("privacyStatus")),
        ("Category", yt.get("categoryId") or meta.get("categoryId")),
        ("Made for Kids", yt.get("selfDeclaredMadeForKids")),
        ("Processing", yt.get("processingStatus") or yt.get("uploadStatus")),
        ("Captions", yt.get("caption")),
    ]
    grid = "".join(f"<div><b>{e(k)}</b><span>{e(v)}</span></div>" for k, v in rows)
    return f"""
    <article class="decision-card publish" data-slug="{e(item['slug'])}">
      <div class="badge danger">Explicit publish authorization required</div>
      <h3>{e(item['title'])}</h3>
      <p class="why">This appears to be a private YouTube draft. I will not make it public unless you explicitly authorize Gate 6.</p>
      <div class="info-grid">{grid}</div>
      <div class="link-row">
        {f'<a class="primary-link" href="{e(url)}" target="_blank">Open YouTube draft/watch link</a>' if url else ''}
        {f'<a class="primary-link" href="{e(studio)}" target="_blank">Open Studio edit page</a>' if studio else ''}
      </div>
      <label>Publish authorization notes
        <textarea data-key="{e(item['slug'])}:publish_notes" placeholder="Type publish time, hold reason, or changes before public..."></textarea>
      </label>
      <div class="actions">
        <button onclick="saveDecision(this,'authorize-public-publish')">Authorize public publish</button>
        <button class="hold" onclick="saveDecision(this,'keep-private')">Keep private</button>
      </div>
      <div class="discord-reply">
        <b>Discord-first path</b>
        <p>Public publish still needs an explicit Discord or dashboard authorization record.</p>
        <code>{e(command_publish)}</code>
        <code>{e(command_hold)}</code>
        <button class="copy" onclick="copyCommand(this,'{e(command_publish)}')">Copy publish command</button>
      </div>
      <p class="saved" aria-live="polite"></p>
    </article>
    """


def running_card(tasks: list[dict[str, Any]]) -> str:
    if not tasks:
        return empty_card("No agent-running implementation cards right now.")
    return "".join(
        f"""
        <article class="mini-card">
          <span class="badge neutral">Agent running</span>
          <h3>{e(t.get('title'))}</h3>
          <p>{e(t.get('body'))}</p>
          <small>{e(t.get('id'))} · @{e(t.get('assignee'))}</small>
        </article>
        """
        for t in tasks
    )


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    blocked = kanban_tasks("blocked")
    running = kanban_tasks("running")
    discord_blocked = [t for t in blocked if "Discord hub" in (t.get("title") or "")]
    shark = load_shark_final()
    shark_privacy = (shark.get("youtube") or {}).get("privacyStatus") if shark else None
    # Once Gate 6 is complete and YouTube is public, the shark card is monitor-only;
    # do not keep surfacing it as a live human review item.
    final_items = [shark] if shark and exists_rel(shark["candidate_video"]) and shark_privacy != "public" else []
    publish_items = []
    if shark and shark_privacy == "private":
        publish_items.append(shark)

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WAYS Human Attention Dashboard</title>
<style>
:root {{ --bg:#07111f; --panel:#0b1726; --panel2:#10243a; --line:#24384e; --text:#edf7ff; --muted:#9db1c5; --cyan:#5ee7ff; --warn:#ffc857; --danger:#ff6b57; --good:#48d597; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif; background:var(--bg); color:var(--text); }}
a {{ color:var(--cyan); }}
main {{ max-width:1180px; margin:0 auto; padding:18px; }}
.hero {{ position:sticky; top:0; z-index:5; background:linear-gradient(180deg,#07111f 85%,rgba(7,17,31,0)); padding:12px 0 20px; }}
h1 {{ margin:0 0 8px; font-size:clamp(28px,5vw,44px); letter-spacing:-.04em; }}
.sub {{ color:var(--muted); max-width:850px; line-height:1.45; }}
.toplinks {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }}
.discord-banner {{ display:grid; grid-template-columns:2fr 1fr 1fr; gap:10px; margin:14px 0; }}
.discord-banner div,.discord-reply {{ border:1px solid var(--line); background:rgba(94,231,255,.06); border-radius:16px; padding:10px; }}
.discord-banner b,.discord-reply b {{ display:block; color:var(--cyan); margin-bottom:4px; }}
.discord-banner span {{ color:#d9ecff; overflow-wrap:anywhere; }}
code {{ background:#020b14; border:1px solid #1d3148; border-radius:7px; padding:2px 5px; color:#eaf7ff; overflow-wrap:anywhere; }}
.discord-reply {{ margin-top:14px; }}
.discord-reply p {{ margin:6px 0 8px; color:var(--muted); }}
.discord-reply code {{ display:block; margin:6px 0; padding:8px; }}
.toplinks a {{ border:1px solid var(--line); background:var(--panel2); padding:10px 12px; border-radius:999px; text-decoration:none; }}
.gate {{ margin:26px 0; }}
.gate-head {{ display:flex; align-items:center; justify-content:space-between; gap:16px; padding:16px; border:1px solid var(--line); border-radius:18px; background:var(--panel2); margin-bottom:12px; }}
.gate-head.needs {{ border-color:var(--warn); }}
.gate-head.empty {{ opacity:.75; }}
.eyebrow {{ color:var(--cyan); text-transform:uppercase; letter-spacing:.12em; font-weight:800; font-size:12px; }}
h2 {{ margin:3px 0; font-size:24px; }}
.gate-head p {{ color:var(--muted); margin:0; }}
.count {{ width:48px; height:48px; border-radius:999px; display:grid; place-items:center; background:var(--bg); border:1px solid var(--line); font-size:24px; font-weight:900; }}
.decision-card,.mini-card,.empty-card {{ background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:16px; margin:12px 0; box-shadow:0 14px 35px rgba(0,0,0,.22); }}
.empty-card {{ color:var(--muted); }}
.badge {{ display:inline-block; padding:6px 10px; border-radius:999px; font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:.05em; background:#182943; }}
.badge.danger {{ color:#ffe5df; background:rgba(255,107,87,.18); border:1px solid rgba(255,107,87,.35); }}
.badge.warn {{ color:#fff3cf; background:rgba(255,200,87,.16); border:1px solid rgba(255,200,87,.35); }}
.badge.neutral {{ color:#d8e9ff; background:#18304d; }}
h3 {{ margin:10px 0 8px; font-size:22px; }}
.why {{ color:#d7e8f8; line-height:1.45; }}
.review-layout {{ display:grid; grid-template-columns:minmax(270px,380px) 1fr; gap:18px; align-items:start; }}
.phone-frame {{ border:1px solid #29425c; border-radius:28px; padding:10px; max-width:390px; background:#02060b; margin:auto; }}
.phone-frame video {{ width:100%; aspect-ratio:9/16; display:block; border-radius:20px; background:#000; }}
.info-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:10px; margin:12px 0; }}
.info-grid div {{ border:1px solid var(--line); border-radius:14px; padding:10px; background:rgba(255,255,255,.025); }}
.info-grid b {{ display:block; color:var(--muted); font-size:12px; margin-bottom:4px; }}
.info-grid span {{ overflow-wrap:anywhere; }}
.checklist {{ line-height:1.5; padding-left:20px; color:#d9ecff; }}
label {{ display:block; margin:12px 0; color:#dcecff; font-weight:700; }}
select, textarea {{ width:100%; margin-top:6px; border-radius:12px; border:1px solid var(--line); background:#06101d; color:var(--text); padding:10px; font:inherit; }}
textarea {{ min-height:86px; resize:vertical; }}
.actions {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:12px; }}
button,.primary-link {{ cursor:pointer; border:0; border-radius:999px; padding:11px 14px; background:var(--good); color:#03140c; font-weight:900; text-decoration:none; display:inline-block; }}
button.reject {{ background:var(--danger); color:white; }}
button.hold {{ background:var(--warn); }}
.link-row {{ display:flex; gap:10px; flex-wrap:wrap; margin:14px 0; }}
.saved {{ color:var(--good); font-weight:800; }}
pre {{ white-space:pre-wrap; color:#c8d7e8; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px; }}
.mini-card p {{ color:var(--muted); max-height:5.5em; overflow:hidden; }}
@media (max-width:800px) {{ .review-layout {{ grid-template-columns:1fr; }} .discord-banner {{ grid-template-columns:1fr; }} .hero {{ position:relative; }} main {{ padding:12px; }} }}
</style>
</head>
<body>
<main>
  <section class="hero">
    <h1>WAYS Human Attention Dashboard</h1>
    <p class="sub">This page is only for decisions Josh actually needs to make, grouped by gate. Discord is the primary decision surface; this dashboard is the media-heavy companion for watching MP4s, opening contact sheets, and copying exact QA reply commands.</p>
    <div class="discord-banner">
      <div><b>Discord-first QA route</b><span>Reply in the WAYS thread with <code>QA &lt;slug&gt; &lt;action&gt; score=... notes="..."</code>. Those replies are treated as source-of-truth decisions and persisted to <code>dashboard/review_decisions.json</code>.</span></div>
      <div><b>Thread</b><span><code>{e(REVIEW_THREAD_ID)}</code></span></div>
      <div><b>QA channel</b><span><code>{e(QA_CHANNEL_ID)}</code></span></div>
    </div>
    <div class="toplinks">
      <a href="/dashboard/kanban.html">Raw Kanban</a>
      <a href="/dashboard/index.html">All media/candidates</a>
      <a href="/ops/ways-video-lab-discord/WAYS_KANBAN_AND_QC_GATES.md">QC gate spec</a>
    </div>
    <p class="sub">Generated {e(datetime.now().isoformat(timespec='seconds'))}. Decisions typed here save in this browser via localStorage and are for review handoff, not automatic publishing.</p>
  </section>

  <section class="gate" id="gate2">
    {gate_header('Gate 2', 'Plate QC: approve/deny stills + lane', 0, 'Human approval before render. VLM scores are advisory only.')}
    {empty_card('No plate approval cards are currently queued.')}
  </section>

  <section class="gate" id="gate5">
    {gate_header('Gate 5', 'Final phone-size video review', len(final_items), 'Watch the captioned master and decide if it clears the 8-9/10 private draft bar or the 9/10+ public-quality bar.')}
    {''.join(final_review_card(x) for x in final_items) if final_items else empty_card('No final video candidates are waiting for phone-size review.')}
  </section>

  <section class="gate" id="gate6">
    {gate_header('Gate 6', 'Public publish authorization', len(publish_items), 'Explicit human authorization required. Default state remains private.')}
    {''.join(publish_auth_card(x) for x in publish_items) if publish_items else empty_card('No private drafts are currently asking for public publish authorization.')}
  </section>

  <section class="gate" id="admin">
    {gate_header('Admin', 'Discord / external setup', len(discord_blocked), 'Things I cannot do through the current tool permissions.')}
    {admin_card(discord_blocked)}
  </section>

  <section class="gate" id="agent-running">
    {gate_header('Agent', 'Being handled by agent, not you', len(running), 'Visible for context only. These should not require Josh unless they later move to a human gate.')}
    <div class="grid">{running_card(running)}</div>
  </section>
</main>
<script>
function restoreInputs() {{
  document.querySelectorAll('[data-key]').forEach(el => {{
    const v = localStorage.getItem('waysReview:' + el.dataset.key);
    if (v !== null) el.value = v;
    el.addEventListener('input', () => localStorage.setItem('waysReview:' + el.dataset.key, el.value));
  }});
}}
async function saveDecision(btn, action) {{
  const card = btn.closest('[data-slug]');
  const slug = card ? card.dataset.slug : 'unknown';
  const score = card?.querySelector('.score')?.value || '';
  const notes = card?.querySelector('textarea')?.value || '';
  const payload = {{ slug, action, score, notes, at: new Date().toISOString() }};
  const saved = card.querySelector('.saved');
  btn.disabled = true;
  if (saved) saved.textContent = 'Saving to server...';
  try {{
    const res = await fetch('/api/review-decision', {{
      method: 'POST',
      headers: {{'content-type':'application/json'}},
      body: JSON.stringify(payload)
    }});
    const out = await res.json();
    if (!res.ok || !out.ok) throw new Error(out.error || 'Save failed');
    localStorage.setItem('waysReviewDecision:' + slug, JSON.stringify(out.decision));
    if (saved) saved.textContent = 'Saved to server: ' + action + (score ? ' · ' + score : '') + '. Agent follow-up is now queued.';
    navigator.clipboard?.writeText(JSON.stringify(out.decision, null, 2)).catch(()=>{{}});
  }} catch (err) {{
    if (saved) saved.textContent = 'Save failed: ' + err.message + '. Refresh the dashboard and try again.';
  }} finally {{
    btn.disabled = false;
  }}
}}
async function copyCommand(btn, command) {{
  try {{
    await navigator.clipboard.writeText(command);
    btn.textContent = 'Copied Discord command';
  }} catch (err) {{
    btn.textContent = 'Copy failed';
  }}
}}
restoreInputs();
</script>
</body>
</html>"""
    OUT.write_text(html_doc, encoding="utf-8")
    print(OUT)
    print(json.dumps({
        "final_review": len(final_items),
        "publish_auth": len(publish_items),
        "discord_admin": len(discord_blocked),
        "running": len(running),
    }, indent=2))


if __name__ == "__main__":
    main()
