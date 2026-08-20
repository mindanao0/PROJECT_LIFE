"""Vertical slice acceptance (REQ-S29-001 .. REQ-S29-005, section 29.1).

REQ-S29-004 states the acceptance conditions: an invalid candidate is rejected, a valid
one is measured and selected, the export matches its source hash, and two replays agree
on the CandidateId, selection and lineage digests.

That last condition was unverifiable until CR-0004 and CR-0009 made CandidateId
content-derived and closed MutationId inside its envelope. Before that, two replays
produced different ids by construction, so this file could not have existed.
"""
from __future__ import annotations

import hashlib
import sys

import pytest
import yaml

from tests.conftest import ROOT

sys.path.insert(0, str(ROOT / "src"))
from evolution_engine.slice import run_slice  # noqa: E402
from evolution_engine.types import CandidateState, RunState  # noqa: E402

CASE = ROOT / "benchmarks/golden/mvp01_pure_function"
MANIFEST = yaml.safe_load((CASE / "fixture_manifest.yaml").read_text(encoding="utf-8"))
CONFIG = yaml.safe_load((CASE / "evolution.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def first(tmp_path_factory):
    return run_slice(CASE, tmp_path_factory.mktemp("run1") / "export")


@pytest.fixture(scope="module")
def second(tmp_path_factory):
    return run_slice(CASE, tmp_path_factory.mktemp("run2") / "export")


# --- REQ-S29-004: an invalid candidate is rejected ---------------------------

def test_a_static_invalid_candidate_is_rejected(first):
    """The mutation engine emits an AST the compiler refuses; the static gate must
    catch it rather than let the evaluator crash on it later."""
    minimum = MANIFEST["expected_slice_observations"]["candidates_static_rejected_minimum"]
    assert len(first.static_rejected) >= minimum


def test_a_behaviour_breaking_candidate_is_rejected_by_the_capability_gate(first):
    """M01 and M02 change what the function computes, so the capability gate is what
    stops them — not the static gate, which they pass."""
    minimum = MANIFEST["expected_slice_observations"]["candidates_capability_rejected_minimum"]
    assert len(first.capability_rejected) >= minimum
    assert not set(first.static_rejected) & set(first.capability_rejected)


def test_rejected_candidates_never_receive_a_metric(first):
    """REQ-S08-002: a candidate that failed an earlier stage may not be scored by a
    later one."""
    scored = set(first.metrics)
    assert not scored & set(first.static_rejected)
    assert not scored & set(first.capability_rejected)


# --- REQ-S29-004: a valid candidate is measured and selected -----------------

def test_exactly_one_candidate_is_selected(first):
    assert first.selected_candidate_id
    assert first.selected_candidate_id in first.metrics


def test_the_selected_candidate_meets_the_expected_metric(first):
    expected = MANIFEST["expected_metrics"][0]
    assert first.metrics[first.selected_candidate_id] == expected["expected_decimal"]


def test_the_disposition_matches_the_corpus_manifest():
    corpus = {c["id"]: c for c in yaml.safe_load(
        (ROOT / "benchmarks/golden/manifest.yaml").read_text(encoding="utf-8"))["cases"]}
    assert corpus["MVP-01"]["expected_disposition"] == CandidateState.SELECTED.value
    assert MANIFEST["expected_lifecycle_disposition"] == CandidateState.SELECTED.value


# --- REQ-S29-004: the export matches its source hash -------------------------

def test_the_export_matches_the_selected_source_hash(first):
    exported = hashlib.sha256(open(first.export_path, "rb").read()).hexdigest()
    assert exported == first.exported_source_hash


def test_the_export_is_the_untouched_baseline(first):
    """The baseline wins here, so the export must be byte-identical to the fixture and
    match the manifest's baseline hash, which was computed from real bytes."""
    assert first.exported_source_hash == MANIFEST["canonical_baseline_hash"]


# --- REQ-S29-004: two replays agree ------------------------------------------

def test_two_replays_produce_the_same_candidate_ids(first, second):
    assert first.candidate_ids == second.candidate_ids


def test_two_replays_select_the_same_candidate(first, second):
    assert first.selected_candidate_id == second.selected_candidate_id


def test_two_replays_produce_the_same_selection_digest(first, second):
    assert first.selection_digest == second.selection_digest


def test_two_replays_produce_the_same_lineage_digest(first, second):
    assert first.lineage_digest == second.lineage_digest


def test_two_replays_reject_the_same_candidates(first, second):
    assert first.static_rejected == second.static_rejected
    assert first.capability_rejected == second.capability_rejected


# --- section 29.1 scope is fixed and must not drift --------------------------

def test_population_size_matches_the_section_29_1_scope(first):
    assert len(first.candidate_ids) == CONFIG["evolution"]["population_size"] == 4


def test_seed_matches_the_section_29_1_scope():
    assert CONFIG["evolution"]["seed"] == MANIFEST["seed"] == 12345


def test_one_generation_only():
    assert CONFIG["stopping"]["max_generations"] == 1


def test_deployment_is_safe_export_only():
    """REQ-S01-010 and section 29.1 both fix this."""
    assert CONFIG["deployment"]["mode"] == "SAFE_EXPORT_ONLY"


def test_the_slice_does_not_enter_profile_a():
    """REQ-S29-003 forbids it before M6."""
    project = yaml.safe_load((CASE / "project.yaml").read_text(encoding="utf-8"))
    assert project["sandbox_profile"] == "none"
    assert MANIFEST["environment_manifest"]["sandbox_profile"] == "none"


# --- REQ-S29-001: the slice uses the published vocabulary --------------------

def test_run_states_are_the_real_run_fsm(first):
    declared = {s.value for s in RunState}
    assert set(first.run_states) <= declared
    assert first.run_states[0] == RunState.INITIATED.value
    assert first.run_states[-1] == RunState.COMPLETED.value


def test_run_states_follow_a_legal_path(first):
    """Every consecutive pair must be a transition spec/fsm/run.yaml declares."""
    fsm = yaml.safe_load((ROOT / "spec/fsm/run.yaml").read_text(encoding="utf-8"))
    edges = {t["from"]: set(t["to"]) for t in fsm["transitions"]}
    for source, target in zip(first.run_states, first.run_states[1:]):
        assert target in edges.get(source, set()), f"{source} -> {target} is not declared"


def test_candidate_ids_are_content_derived(first):
    """64 hex characters, not a UUID. This is what makes replay comparable at all."""
    for candidate_id in first.candidate_ids:
        assert len(candidate_id) == 64
        assert all(ch in "0123456789abcdef" for ch in candidate_id)
