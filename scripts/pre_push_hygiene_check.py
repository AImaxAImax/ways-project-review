#!/usr/bin/env python3
"""Fail-fast hygiene scan for the public WAYS review bundle.

This is intentionally lightweight and conservative. It blocks known local-user
path leaks and high-signal credential literals before a public push.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = {
    "docs/SECRET_SCAN_REPORT.md",
    "docs/SECRET_SCAN_HITS.json",
    "scripts/pre_push_hygiene_check.py",
}
DENY_PATTERNS = [
    ("local_username_path", re.compile(r"/home/joshn\b|C:\\\\Users\\\\joshn\b", re.IGNORECASE)),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("generic_secret_assignment", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{24,}")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----")),
]
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "venv", ".venv"}


def tracked_files() -> list[Path]:
    proc = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE)
    return [ROOT / line for line in proc.stdout.splitlines() if line]


def main() -> int:
    hits: list[str] = []
    for path in tracked_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWLIST or any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in DENY_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                hits.append(f"{rel}:{line}: {name}")
    if hits:
        print("Hygiene scan failed:", file=sys.stderr)
        print("\n".join(hits), file=sys.stderr)
        return 1
    print("Hygiene scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
