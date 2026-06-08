#!/usr/bin/env python3
"""WAYS human-attention dashboard server.

Serves the project static files and persists Josh's Gate 5/Gate 6 decisions.
This replaces plain `python -m http.server`, which made the UI look clickable but
could not perform any real action.
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
DECISIONS_DEFAULT = ROOT / "dashboard" / "review_decisions.json"
ALLOWED_ACTIONS = {
    "approve-private",
    "approve-public-quality",
    "reject-rework",
    "authorize-public-publish",
    "keep-private",
    "approve-plate",
    "deny-plate",
}
LANES = {"wan_i2v", "motion_graphic", "still_motion", "regenerate", "hold"}


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
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def safe_project_path(root: Path, request_path: str) -> Path | None:
    raw = unquote(request_path).split("?", 1)[0].lstrip("/") or "dashboard/review.html"
    candidate = root / raw
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root.resolve())
        return resolved
    except Exception:
        return None


class ReviewHandler(BaseHTTPRequestHandler):
    server_version = "WAYSReview/1.0"

    @property
    def app(self) -> "ReviewServer":
        return self.server  # type: ignore[return-value]

    def send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("cache-control", "no-store")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, "file not found")
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("content-type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        if path.suffix.lower() in {".html", ".js", ".css", ".json"}:
            self.send_header("cache-control", "no-store")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/review-decisions":
            self.send_json(read_json(self.app.decisions_path, {"version": 1, "decisions": {}}))
            return
        path = safe_project_path(self.app.root, parsed.path)
        if not path:
            self.send_error(403, "outside project root")
            return
        self.serve_file(path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/review-decision":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("content-length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            decision = self.validate_decision(payload)
        except ValueError as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)
            return
        decisions = read_json(self.app.decisions_path, {"version": 1, "decisions": {}})
        decisions.setdefault("version", 1)
        decisions.setdefault("decisions", {})[decision["decision_id"]] = decision
        decisions["updated_at"] = decision["reviewed_at"]
        atomic_write_json(self.app.decisions_path, decisions)
        self.send_json({"ok": True, "decision": decision, "decisions_path": str(self.app.decisions_path)})

    def validate_decision(self, payload: dict[str, Any]) -> dict[str, Any]:
        slug = str(payload.get("slug") or "").strip()
        if not slug:
            raise ValueError("missing slug")
        action = str(payload.get("action") or "").strip()
        if action not in ALLOWED_ACTIONS:
            raise ValueError(f"unknown action: {action}")
        score = str(payload.get("score") or "").strip()
        notes = str(payload.get("notes") or "").strip()
        lane = str(payload.get("confirmed_lane") or payload.get("lane") or "").strip()
        if lane and lane not in LANES:
            raise ValueError(f"unknown lane: {lane}")
        if action == "approve-plate" and lane not in {"wan_i2v", "motion_graphic", "still_motion"}:
            raise ValueError("approve-plate requires a renderable confirmed_lane")
        gate = "Gate 5 final video review"
        if action in {"authorize-public-publish", "keep-private"}:
            gate = "Gate 6 public publish authorization"
        elif action in {"approve-plate", "deny-plate"}:
            gate = "Gate 2 human plate QC"
        reviewed_at = now_iso()
        explicit_authorization = None
        if action == "authorize-public-publish":
            explicit_authorization = f"Josh authorizes public publish for {slug} via WAYS Human Attention Dashboard at {reviewed_at}"
        decision = {
            "schema_version": 2,
            "decision_id": f"{slug}:{action}",
            "slug": slug,
            "gate": gate,
            "action": action,
            "score": score,
            "notes": notes,
            "reviewer": "Josh",
            "reviewed_at": reviewed_at,
            "source": str(payload.get("source") or "dashboard"),
            "explicit_public_publish_authorization": explicit_authorization,
            "requires_agent_followup": action in {"authorize-public-publish", "reject-rework", "approve-public-quality", "approve-plate", "deny-plate"},
        }
        if lane:
            decision["confirmed_lane"] = lane
        if action in {"approve-plate", "deny-plate"}:
            decision["vlm_was_advisory_only"] = True
        return decision

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - {fmt % args}")


class ReviewServer(ThreadingHTTPServer):
    def __init__(self, addr: tuple[str, int], handler: type[BaseHTTPRequestHandler], *, root: Path, decisions_path: Path):
        super().__init__(addr, handler)
        self.root = root.resolve()
        self.decisions_path = decisions_path.resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve WAYS human attention dashboard")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--decisions", default=str(DECISIONS_DEFAULT))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    decisions = Path(args.decisions)
    if not decisions.is_absolute():
        decisions = root / decisions
    server = ReviewServer((args.host, args.port), ReviewHandler, root=root, decisions_path=decisions)
    print(f"WAYS review dashboard: http://{args.host}:{args.port}/dashboard/review.html")
    print(f"Decisions: {decisions}")
    server.serve_forever()


if __name__ == "__main__":
    main()
