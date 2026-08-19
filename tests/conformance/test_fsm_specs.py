"""FSM conformance tests (REQ-S08-012, REQ-S19-003).

REQ-S08-012 requires spec/fsm/{run,recovery,governance}.yaml to encode the
state, transition and terminal sets of their Active Contract sections and to
pass reachability, illegal-transition and terminal-state tests. REQ-S19-003 adds
a rollback-path test for spec/fsm/deployment.yaml.

candidate.yaml is held to the same standard even though no requirement names it,
because the Candidate FSM is section 8.1 of the same contract.
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

from tests.conftest import ROOT

FSM_DIR = ROOT / "spec/fsm"
FSM_NAMES = ["candidate", "run", "recovery", "governance", "deployment"]


def load(name: str) -> dict:
    return yaml.safe_load((FSM_DIR / f"{name}.yaml").read_text(encoding="utf-8"))


def edges(spec: dict) -> dict[str, list[str]]:
    return {t["from"]: t["to"] for t in spec["transitions"]}


@pytest.fixture(scope="module")
def registry() -> dict:
    return yaml.safe_load((ROOT / "spec/fsm_states_57.yaml").read_text(encoding="utf-8"))["fsms"]


@pytest.mark.parametrize("name", FSM_NAMES)
def test_file_exists(name):
    assert (FSM_DIR / f"{name}.yaml").is_file()


@pytest.mark.parametrize("name", FSM_NAMES)
def test_matches_state_registry(name, registry):
    """The FSM file and spec/fsm_states_57.yaml must not drift apart."""
    key = {
        "candidate": "candidate_lifecycle_fsm", "run": "run_lifecycle_fsm",
        "recovery": "recovery_fsm", "governance": "governance_fsm",
        "deployment": "deployment_fsm",
    }[name]
    spec, declared = load(name), registry[key]
    assert set(spec["states"]) == set(declared["states"])
    assert spec["initial_state"] == declared["initial_state"]
    assert set(spec["terminal_states"]) == set(declared["terminal_states"])
    assert spec["states_count"] == len(spec["states"])


@pytest.mark.parametrize("name", FSM_NAMES)
def test_every_transition_target_is_a_declared_state(name):
    spec = load(name)
    states = set(spec["states"])
    for transition in spec["transitions"]:
        assert transition["from"] in states, f"{name}: unknown source {transition['from']}"
        for target in transition["to"]:
            assert target in states, f"{name}: {transition['from']} -> undeclared {target}"


@pytest.mark.parametrize("name", FSM_NAMES)
def test_every_state_is_reachable_from_the_initial_state(name):
    """Reachability (REQ-S08-012, REQ-S19-003)."""
    spec = load(name)
    graph = edges(spec)
    seen, queue = {spec["initial_state"]}, [spec["initial_state"]]
    while queue:
        for target in graph.get(queue.pop(), []):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    unreachable = sorted(set(spec["states"]) - seen)
    assert not unreachable, f"{name}: unreachable states {unreachable}"


@pytest.mark.parametrize("name", FSM_NAMES)
def test_terminal_states_have_no_outgoing_transition(name):
    """Terminal-state test (REQ-S08-012, REQ-S19-003)."""
    spec = load(name)
    graph = edges(spec)
    for terminal in spec["terminal_states"]:
        assert not graph.get(terminal), (
            f"{name}: terminal {terminal} still has outgoing edges {graph[terminal]}")


@pytest.mark.parametrize("name", FSM_NAMES)
def test_every_non_terminal_state_can_exit(name):
    """A non-terminal state with no way out is a deadlock."""
    spec = load(name)
    graph = edges(spec)
    stuck = [s for s in spec["states"] if s not in spec["terminal_states"] and not graph.get(s)]
    assert not stuck, f"{name}: non-terminal states with no exit {stuck}"


@pytest.mark.parametrize("name", FSM_NAMES)
def test_illegal_transitions_are_not_encoded(name):
    """Illegal-transition test: only declared edges exist, and none is a self-loop
    that the contract did not state."""
    spec = load(name)
    graph = edges(spec)
    legal = {(s, t) for s, targets in graph.items() for t in targets}
    for source, target in legal:
        assert source != target, f"{name}: undeclared self-loop {source} -> {source}"
    # a transition the contract never declared must be absent
    for source in spec["states"]:
        for target in spec["states"]:
            if (source, target) not in legal:
                assert target not in graph.get(source, []), (
                    f"{name}: {source} -> {target} is not a declared transition")


def test_deployment_has_a_rollback_path_from_every_non_terminal_state():
    """Rollback-path test (REQ-S19-003)."""
    spec = load("deployment")
    graph = edges(spec)
    for state in spec["states"]:
        if state in spec["terminal_states"]:
            continue
        assert "ROLLED_BACK" in graph.get(state, []), (
            f"{state} cannot roll back; REQ-S19-002 requires deployment to fail closed")


def test_deployment_safe_export_only_reaches_a_terminal_state():
    """Mode SAFE_EXPORT_ONLY must finish without touching live traffic."""
    spec = load("deployment")
    graph = edges(spec)
    assert "ARCHIVED_PRODUCTION" in graph["PACKAGE_BUNDLED"], (
        "SAFE_EXPORT_ONLY would have to pass through CANARY to terminate")


def test_run_fsm_recovers_from_every_non_terminal_state():
    """REQ-S08-006: an unclean non-terminal run must be able to enter RECOVERING."""
    spec = load("run")
    graph = edges(spec)
    for state in spec["states"]:
        if state in spec["terminal_states"] or state == "RECOVERING":
            continue
        assert "RECOVERING" in graph.get(state, []), f"{state} cannot enter RECOVERING"
