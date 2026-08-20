"""Maturity predicates must be as strong as the gate they claim to check (REQ-S28-002).

Every rung above M4 originally asked "does a file matching this glob exist". Eight of
the thirteen therefore returned True for empty files: `touch` ten paths and the ladder
reported M13, while LINT-20 — written specifically to stop the maturity claim being
asserted rather than earned — reported no problem.

CR-0009 fixed exactly this for M4 and then introduced M10..M13 with the same weakness.
This module is the guard that makes the mistake impossible to repeat: it builds a
throwaway tree of empty files matching every glob a predicate looks for and asserts
that not one rung is satisfied.
"""
from __future__ import annotations

import importlib
import pathlib
import shutil
import subprocess
import sys

import pytest
import yaml

from tests.conftest import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import compute_maturity  # noqa: E402

# Every path a predicate globs for, and the empty file that would satisfy a
# file-existence check.
DECOY_FILES = [
    "tests/replay/test_slice.py",
    "tests/security/test_profile_a_on_kernel.py",
    "tests/security/test_root_of_trust.py",
    "tests/integration/test_migration.py",
    "tests/integration/test_canary.py",
    "tests/integration/test_rollback.py",
    "tests/recovery/test_crash.py",
    "tests/golden/test_corpus_core.py",
    "tests/golden/test_corpus_security.py",
    "tests/golden/test_corpus_reliability.py",
    "tests/golden/test_corpus_self_evolution.py",
    "build/evidence/evidence_bundle.json",
]
UNEARNED_RUNGS = [
    "m5_fsm_and_config", "m6_security", "m7_persistence", "m8_recovery",
    "m9_core_golden", "m10_security_reliability_golden", "m11_execution_ready",
    "m12_production", "m13_self_evolution",
]


@pytest.fixture(scope="module")
def decoy_repo(tmp_path_factory) -> pathlib.Path:
    """A copy of the repo with an empty file at every path a predicate looks for."""
    target = tmp_path_factory.mktemp("decoy") / "repo"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".pytest_cache", "*.pyc"))
    for rel in DECOY_FILES:
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    (target / "src/evolution_engine").mkdir(parents=True, exist_ok=True)
    return target


@pytest.mark.parametrize("rung", UNEARNED_RUNGS)
def test_empty_files_do_not_satisfy_a_rung(decoy_repo, rung):
    """An empty test file proves nothing, so it must not advance the ladder."""
    script = (
        "import sys, pathlib\n"
        f"sys.path.insert(0, {str(decoy_repo / 'tools')!r})\n"
        "import compute_maturity as cm\n"
        f"cm.ROOT = pathlib.Path({str(decoy_repo)!r})\n"
        f"print(cm.{rung}())\n"
    )
    result = subprocess.run([sys.executable, "-c", script],
                            capture_output=True, text=True, cwd=decoy_repo, timeout=300)
    assert result.stdout.strip() == "False", (
        f"{rung} accepted an empty file:\n{result.stdout}{result.stderr}")


def test_every_ladder_rung_has_a_predicate():
    """A rung with no predicate cannot be reached, which is what capped the ladder at M9."""
    declared = [m["level"] for m in yaml.safe_load(
        (ROOT / "spec/maturity.yaml").read_text(encoding="utf-8"))["maturity_ladder"]]
    implemented = [level for level, _ in compute_maturity.LADDER]
    assert implemented == declared


def test_predicates_that_run_tests_demand_a_minimum_count():
    """`_suite_passes(pattern, 0)` would accept a file that collects nothing."""
    source = (ROOT / "tools/compute_maturity.py").read_text(encoding="utf-8")
    for call in compute_maturity.re.findall(r"_suite_passes\([^)]*\)", source):
        if "minimum_tests" in call:
            continue
        minimum = call.rstrip(")").rsplit(",", 1)[-1].strip()
        assert minimum.isdigit() and int(minimum) >= 1, f"{call} allows an empty suite"


def test_m4_still_requires_more_than_files_existing():
    """The original defect. Kept as a regression test in its own right."""
    source = (ROOT / "tools/compute_maturity.py").read_text(encoding="utf-8")
    body = source[source.index("def m4_protocols"):source.index("def m5_fsm_and_config")]
    assert "mypy" in body, "M4 does not type-check"
    assert "requirements.lock" in body, "M4 does not check the lock artifact (REQ-S03-004)"
    assert "Protocol" in body, "M4 does not require real Protocol classes"
