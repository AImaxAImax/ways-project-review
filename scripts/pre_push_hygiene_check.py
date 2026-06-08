#!/usr/bin/env python3
"""Fail-fast hygiene scan for the public WAYS review bundle.

This is intentionally lightweight and conservative. It blocks known local-user
path leaks and high-signal credential literals before a public push. Each run
also writes the human and machine-readable secret-scan artifacts referenced by
the review docs.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs" / "SECRET_SCAN_REPORT.md"
HITS_PATH = ROOT / "docs" / "SECRET_SCAN_HITS.json"
ALLOWLIST = {
    "docs/SECRET_SCAN_REPORT.md",
    "docs/SECRET_SCAN_HITS.json",
    "scripts/pre_push_hygiene_check.py",
}
DENY_PATTERNS = [
    ("local_username_path", re.compile(r"/home/joshn\b|C:[\\/]+Users[\\/]+joshn\b", re.IGNORECASE)),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("generic_secret_assignment", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{24,}")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----")),
]
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "venv", ".venv"}

KNOWN_BAD_SAMPLES = {
    "local_username_path": [
        "/home/joshn/project/file.txt",
        r"C:\Users\joshn\miniconda3\envs\env_uma\python.exe",
        "C:/Users/joshn/miniconda3/envs/env_uma/python.exe",
    ],
    "github_token": ["ghp_abcdefghijklmnopqrstuvwxyz123456"],
    "generic_secret_assignment": ["api_key = abcdefghijklmnopqrstuvwxyz123456"],
    "private_key": ["-----BEGIN PRIVATE KEY-----"],
}


def validate_patterns() -> list[str]:
    errors: list[str] = []
    by_name = {name: pattern for name, pattern in DENY_PATTERNS}
    for name, samples in KNOWN_BAD_SAMPLES.items():
        pattern = by_name[name]
        for sample in samples:
            if not pattern.search(sample):
                errors.append(f"self-test failed for {name}: {sample}")
    return errors


def tracked_files() -> list[Path]:
    proc = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE)
    return [ROOT / line for line in proc.stdout.splitlines() if line]


def should_scan(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return rel not in ALLOWLIST and not any(part in SKIP_DIRS for part in path.parts)


def generated_timestamp(scanned_files: list[Path]) -> str:
    """Return a stable ISO timestamp for the scanned tree.

    The pre-push hook runs this script. Using wall-clock time would dirty the
    working tree on every push. This timestamp instead reflects the newest mtime
    among scanned tracked files, so repeated clean scans are stable while real
    input changes still refresh the artifacts.
    """
    latest_ns = max((path.stat().st_mtime_ns for path in scanned_files if path.exists()), default=0)
    if latest_ns <= 0:
        return datetime.fromtimestamp(0, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    return datetime.fromtimestamp(latest_ns / 1_000_000_000, tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def redacted_snippet(line_text: str, pattern: re.Pattern[str]) -> str:
    snippet = pattern.sub("[REDACTED]", line_text.strip())
    if len(snippet) > 180:
        snippet = snippet[:177] + "..."
    return snippet


def write_scan_outputs(*, generated: str, scanned: int, hits: list[dict[str, object]]) -> None:
    patterns = [name for name, _ in DENY_PATTERNS]
    payload = {
        "generated": generated,
        "scanned": scanned,
        "patterns_checked": patterns,
        "hits": hits,
    }
    HITS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Secret scan report",
        "",
        f"Generated: `{generated}`",
        f"Tracked files scanned: `{scanned}`",
        f"Patterns checked: `{', '.join(patterns)}`",
        "",
    ]
    if hits:
        lines.append("Result: **failed**")
        lines.append("")
        lines.append("Hits:")
        for hit in hits:
            lines.append(f"- `{hit['file']}:{hit['line']}` `{hit['pattern']}`")
    else:
        lines.append("Result: **clean**")
        lines.append("")
        lines.append("No deny-pattern hits were found in scanned tracked files.")
    lines.extend(["", "See `docs/SECRET_SCAN_HITS.json` for the machine-readable scan output.", ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    pattern_errors = validate_patterns()
    if pattern_errors:
        print("Hygiene scan configuration is broken:", file=sys.stderr)
        print("\n".join(pattern_errors), file=sys.stderr)
        return 2

    scan_files = [path for path in tracked_files() if should_scan(path)]
    hits: list[dict[str, object]] = []
    for path in scan_files:
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in DENY_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                line_text = text.splitlines()[line_no - 1] if line_no - 1 < len(text.splitlines()) else ""
                hits.append(
                    {
                        "file": rel,
                        "line": line_no,
                        "pattern": name,
                        "snippet": redacted_snippet(line_text, pattern),
                    }
                )

    write_scan_outputs(generated=generated_timestamp(scan_files), scanned=len(scan_files), hits=hits)

    if hits:
        print("Hygiene scan failed:", file=sys.stderr)
        print("\n".join(f"{hit['file']}:{hit['line']}: {hit['pattern']}" for hit in hits), file=sys.stderr)
        return 1
    print("Hygiene scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
