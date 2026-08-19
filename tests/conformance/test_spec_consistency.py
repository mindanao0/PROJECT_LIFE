"""Conformance tests: the cross-source invariants the spec linters enforce.

tools/lint_state_vocabulary.py is the single command CI runs; this module makes
each linter a separate test so a failure names the rule that broke.
"""
from __future__ import annotations

import subprocess
import sys

import pytest

from tests.conftest import ROOT

LINTER = ROOT / "tools/lint_state_vocabulary.py"
SCHEMA_GATE = ROOT / "tools/validate_schemas.py"


def run(script) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=ROOT)


@pytest.fixture(scope="module")
def linter_result():
    return run(LINTER)


def test_spec_linters_pass(linter_result):
    """LINT-09 .. LINT-16 all green."""
    assert linter_result.returncode == 0, linter_result.stdout + linter_result.stderr


@pytest.mark.parametrize("rule", [
    "LINT-09", "LINT-10", "LINT-11", "LINT-12", "LINT-13", "LINT-14", "LINT-15", "LINT-16",
])
def test_no_finding_for_rule(rule, linter_result):
    """Name the individual rule so a regression is attributable at a glance."""
    hits = [line for line in linter_result.stdout.splitlines() if rule in line and line.strip().startswith("-")]
    assert not hits, "\n".join(hits)


def test_m3_schema_gate_passes():
    """REQ-S15-001: the whole M3 schema gate, as one command."""
    result = run(SCHEMA_GATE)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "M3 SCHEMA GATE: PASS" in result.stdout
