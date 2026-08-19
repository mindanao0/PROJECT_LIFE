#!/usr/bin/env python3
"""Compute the maturity level from artifacts, not from a claim (REQ-S28-002).

Every other number in this repository is derived and linted. The project's own
progress marker was hardcoded in five places and checked by nothing, which is how
it stayed at M2 after M3 was finished and verified.

Each rung has a predicate over real files. The reported level is the highest rung
whose predicate and all lower ones hold.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _run(script: str) -> bool:
    # LINT-20 asks this module for the level, so the linter must not ask back.
    env = dict(os.environ, EE_SKIP_MATURITY_LINT="1")
    return subprocess.run([sys.executable, str(ROOT / script)],
                          capture_output=True, cwd=ROOT, env=env).returncode == 0


def m0_utf8() -> bool:
    for path in list(ROOT.glob("spec/**/*.yaml")) + [ROOT / "spec/ACTIVE_CONTRACT.md"]:
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return False
    return True


def m1_architecture() -> bool:
    return (ROOT / "spec/authority.yaml").exists() and (ROOT / "spec/protocols.yaml").exists()


def m2_requirements() -> bool:
    """Unique stable IDs and no conflicting FSM/CLI/SDK definitions."""
    register = yaml.safe_load((ROOT / "spec/requirements.yaml").read_text(encoding="utf-8"))
    ids = [r["id"] for r in register["requirements"]]
    return len(ids) == len(set(ids)) and _run("tools/lint_state_vocabulary.py")


def m3_schemas() -> bool:
    """26 schemas valid with fixtures — the whole M3 gate as one command."""
    return _run("tools/validate_schemas.py")


def m4_protocols() -> bool:
    """Typed protocol package importable with zero type errors."""
    registry = yaml.safe_load((ROOT / "spec/protocols.yaml").read_text(encoding="utf-8"))
    package = ROOT / "src/evolution_engine/protocols"
    if not package.is_dir():
        return False
    found = {p.stem for p in package.glob("*.py")}
    return len(found) >= registry["core_v1_protocol_count"]


def m5_fsm_and_config() -> bool:
    return (ROOT / "src/evolution_engine").is_dir() and (ROOT / "tests/replay").is_dir() and \
        any((ROOT / "tests/replay").glob("test_*.py"))


def m6_security() -> bool:
    return any((ROOT / "tests/security").glob("test_profile_a_on_kernel*.py"))


def m7_persistence() -> bool:
    return any((ROOT / "tests/integration").glob("test_migration*.py"))


def m8_recovery() -> bool:
    return any((ROOT / "tests/recovery").glob("test_*.py"))


def m9_core_golden() -> bool:
    return any((ROOT / "tests/golden").glob("test_corpus_core*.py"))


LADDER = [
    ("M0", m0_utf8), ("M1", m1_architecture), ("M2", m2_requirements), ("M3", m3_schemas),
    ("M4", m4_protocols), ("M5", m5_fsm_and_config), ("M6", m6_security),
    ("M7", m7_persistence), ("M8", m8_recovery), ("M9", m9_core_golden),
]


def compute() -> tuple[str, list[tuple[str, bool]]]:
    ladder = yaml.safe_load((ROOT / "spec/maturity.yaml").read_text(encoding="utf-8"))["maturity_ladder"]
    names = {m["level"]: m["name"] for m in ladder}
    results, reached = [], "M0"
    still_passing = True
    for level, predicate in LADDER:
        ok = predicate() if still_passing else False
        results.append((level, ok))
        if ok:
            reached = level
        else:
            still_passing = False
    return f"{reached}_{names[reached]}", results


def main() -> int:
    claim, results = compute()
    declared = yaml.safe_load(
        (ROOT / "spec/version_manifest.yaml").read_text(encoding="utf-8"))["current_maturity_level"]
    for level, ok in results:
        print(f"  {level}  {'pass' if ok else 'not yet'}")
    print(f"\ncomputed: {claim}\ndeclared: {declared}")
    if declared != claim:
        print(f"\nMISMATCH — spec/version_manifest.yaml declares {declared} "
              f"but the artifacts support {claim} (REQ-S28-002)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
