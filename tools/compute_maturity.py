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
import re
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _run(script: str) -> bool:
    # LINT-20 asks this module for the level, so the linter must not ask back.
    env = dict(os.environ, EE_SKIP_MATURITY_LINT="1")
    return subprocess.run([sys.executable, str(ROOT / script)],
                          capture_output=True, cwd=ROOT, env=env).returncode == 0


def _suite_passes(pattern: str, minimum_tests: int) -> bool:
    """True only when the matching tests exist, collect at least `minimum_tests`, and pass.

    The first version of every rung below asked whether a file matching a glob existed.
    Eight of the thirteen therefore passed on empty files — `touch` ten paths and the
    ladder reported M13. That is the same defect CR-0009 fixed for M4 while writing
    M10..M13 with it intact. A predicate has to run the thing it claims to check.

    Scoped to directories that contain no conformance test, so this cannot re-enter the
    linter that called it.
    """
    matches = sorted(ROOT.glob(pattern))
    if not matches:
        return False
    env = dict(os.environ, EE_SKIP_MATURITY_LINT="1")
    # No -q here. pytest.ini already sets it, and a second -q collapses to -qq, which
    # suppresses the summary line this function reads — the predicate then reports
    # "not yet" for a suite that passed.
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--no-header", "-p", "no:cacheprovider",
         *[str(p) for p in matches]],
        capture_output=True, text=True, cwd=ROOT, env=env)
    if result.returncode != 0:
        return False
    collected = re.search(r"(\d+) passed", result.stdout)
    if collected is None:
        # Passing but unreadable output is a broken predicate, not a passing rung.
        raise RuntimeError(
            f"pytest for {pattern!r} exited 0 but printed no summary; "
            f"the predicate cannot count tests:\n{result.stdout[-400:]}")
    return int(collected.group(1)) >= minimum_tests


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
    """spec/maturity.yaml: "19 Typed Python Protocols with zero type errors",
    plus section 12's "Python runtime/dependencies pinned" and REQ-S03-004's lock
    artifact.

    The first version of this predicate counted .py files, so nineteen empty files
    passed it — weaker than the gate in two directions at once. It now requires the
    named classes to exist as real typing.Protocol subclasses, mypy --strict to be
    clean, and the lock artifact to be present.
    """
    registry = yaml.safe_load((ROOT / "spec/protocols.yaml").read_text(encoding="utf-8"))
    package = ROOT / "src/evolution_engine/protocols"
    if not package.is_dir():
        return False

    if not (ROOT / "requirements.lock").is_file():
        return False  # REQ-S03-004

    wanted = {entry["protocol"] for entry in registry["core_v1_protocols"]}
    source = "\n".join(p.read_text(encoding="utf-8") for p in package.rglob("*.py"))
    declared = set(re.findall(r"class\s+(\w+)\s*\(\s*Protocol\s*[,)]", source))
    if not wanted <= declared:
        return False

    # every method must be annotated; an unannotated def is not a typed protocol
    if re.search(r"^\s+def\s+\w+\s*\([^)]*\)\s*:", source, re.M):
        return False

    mypy = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", str(package)],
        capture_output=True, cwd=ROOT,
        env=dict(os.environ, EE_SKIP_MATURITY_LINT="1"))
    return mypy.returncode == 0


def m5_fsm_and_config() -> bool:
    """FSM tests pass and the trusted-fixture vertical slice replays deterministically."""
    return (ROOT / "src/evolution_engine").is_dir() and _suite_passes("tests/replay/test_*.py", 1)


def m6_security() -> bool:
    """PROFILE_A executes on a real kernel and the negative security corpus is defeated.
    Three cases (MVP-08..10) means at least three assertions."""
    return _suite_passes("tests/security/test_profile_a_on_kernel*.py", 3)


def m7_persistence() -> bool:
    return _suite_passes("tests/integration/test_migration*.py", 1)


def m8_recovery() -> bool:
    """The DB and CAS crash matrix, so more than one crash point."""
    return _suite_passes("tests/recovery/test_*.py", 2)


def m9_core_golden() -> bool:
    """The CORE bucket is MVP-01..MVP-05 after CR-0003, so at least five cases."""
    return _suite_passes("tests/golden/test_corpus_core*.py", 5)


def m10_security_reliability_golden() -> bool:
    """SECURITY is MVP-08..10 and RELIABILITY is MVP-11..12."""
    return _suite_passes("tests/golden/test_corpus_security*.py", 3) and \
        _suite_passes("tests/golden/test_corpus_reliability*.py", 2)


def m11_execution_ready() -> bool:
    """GATE_CORE passed, complete traceability, signed evidence bundle."""
    register = yaml.safe_load((ROOT / "spec/requirements.yaml").read_text(encoding="utf-8"))
    every_requirement_verified = all(
        r["verification_method"] != "PENDING" for r in register["requirements"])
    bundle = ROOT / "build/evidence/evidence_bundle.json"
    return every_requirement_verified and bundle.is_file() and bundle.stat().st_size > 0


def m12_production() -> bool:
    return _suite_passes("tests/integration/test_canary*.py", 1) and \
        _suite_passes("tests/integration/test_rollback*.py", 1)


def m13_self_evolution() -> bool:
    """MVP-14 plus the root-of-trust and immutable-evaluator proofs."""
    return _suite_passes("tests/golden/test_corpus_self_evolution*.py", 1) and \
        _suite_passes("tests/security/test_root_of_trust*.py", 1)


# Every rung in spec/maturity.yaml needs a predicate. Stopping the ladder at M9 made
# every release gate unreachable: GATE_CORE requires M10, so declaring it would always
# have failed LINT-20. Fixed in CR-0009.
LADDER = [
    ("M0", m0_utf8), ("M1", m1_architecture), ("M2", m2_requirements), ("M3", m3_schemas),
    ("M4", m4_protocols), ("M5", m5_fsm_and_config), ("M6", m6_security),
    ("M7", m7_persistence), ("M8", m8_recovery), ("M9", m9_core_golden),
    ("M10", m10_security_reliability_golden), ("M11", m11_execution_ready),
    ("M12", m12_production), ("M13", m13_self_evolution),
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
