#!/usr/bin/env python3
"""Regenerate requirements.lock (REQ-S03-004).

pyproject.toml declares dependencies with >= ranges. That is a declaration, not a
lock: two machines resolving it can install different versions and reach different
verdicts on the same schema corpus, which would break REQ-S15-005's requirement that
two validator implementations agree. The lock records exactly what is installed and
the digest of the pyproject it was resolved from, so drift is detectable.
"""
from __future__ import annotations

import hashlib
import importlib.metadata as metadata
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGES = ["jsonschema", "jsonschema-rs", "pyyaml", "pytest", "mypy"]


def main() -> int:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    lines = [
        "# Pinned runtime for the specification toolchain (REQ-S03-004).",
        "#",
        "# The M4 gate requires exact package versions in a lock artifact. pyproject.toml",
        "# uses >= ranges, which is a dependency declaration, not a lock: two machines",
        "# resolving it can install different versions and produce different validator",
        "# verdicts on the same schema corpus, which would break REQ-S15-005.",
        "#",
        "# Regenerate with tools/generate_lock.py after changing pyproject.toml.",
        "",
        f"# pyproject.toml sha256: {hashlib.sha256(pyproject.encode()).hexdigest()}",
        "",
    ]
    missing = []
    for name in PACKAGES:
        try:
            lines.append(f"{name}=={metadata.version(name)}")
        except metadata.PackageNotFoundError:
            missing.append(name)
    if missing:
        raise SystemExit(f"not installed, cannot lock: {missing}")
    (ROOT / "requirements.lock").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote requirements.lock with {len(PACKAGES)} pinned packages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
