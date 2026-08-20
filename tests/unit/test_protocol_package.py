"""The protocol package is the contract made checkable (M4, REQ-S07-003).

Sections 7.2 and 6.2 named 26 types and only three resolved to anything. Every
signature here would otherwise have been invented and later rewritten. These tests
assert the package matches the contract rather than a convenient reading of it.
"""
from __future__ import annotations

import re
import typing

import pytest
import yaml

from tests.conftest import ROOT

import evolution_engine
from evolution_engine import protocols, types

REGISTRY = yaml.safe_load((ROOT / "spec/protocols.yaml").read_text(encoding="utf-8"))
TYPE_DOC = yaml.safe_load((ROOT / "spec/protocol_types.yaml").read_text(encoding="utf-8"))
CANONICAL = [entry["protocol"] for entry in REGISTRY["core_v1_protocols"]]


def test_package_exports_exactly_the_canonical_roster():
    """19 Core v1, and none of the four research protocols CR-0002 removed."""
    assert sorted(protocols.__all__) == sorted(CANONICAL)
    assert len(CANONICAL) == REGISTRY["core_v1_protocol_count"] == 19


@pytest.mark.parametrize("name", CANONICAL)
def test_each_protocol_is_a_real_protocol(name):
    cls = getattr(protocols, name)
    assert typing.is_typeddict(cls) is False
    assert getattr(cls, "_is_protocol", False), f"{name} is not a typing.Protocol"


@pytest.mark.parametrize("name", CANONICAL)
def test_every_method_is_fully_annotated(name):
    """An unannotated parameter makes "Typed Protocols" false on its face."""
    cls = getattr(protocols, name)
    methods = [m for m in vars(cls) if not m.startswith("_")]
    assert methods, f"{name} declares no method"
    for method in methods:
        hints = typing.get_type_hints(getattr(cls, method))
        function = getattr(cls, method)
        expected = function.__code__.co_varnames[1:function.__code__.co_argcount]
        for param in expected:
            assert param in hints, f"{name}.{method}({param}) has no annotation"
        assert "return" in hints, f"{name}.{method} has no return annotation"


def test_no_protocol_returns_a_bare_dict_alias_by_accident():
    """REQ-S06-002 forbids raw dict on the stable surface. ALIAS types are schema
    documents by design; anything else returning a plain dict is a mistake."""
    alias_names = {
        entry.get("schema_title", entry["name"])
        for entry in TYPE_DOC["protocol_types"] if entry["kind"] == "ALIAS"
    }
    for name in CANONICAL:
        cls = getattr(protocols, name)
        for method in [m for m in vars(cls) if not m.startswith("_")]:
            returned = typing.get_type_hints(getattr(cls, method))["return"]
            if returned is types.SchemaDocument:
                source = (ROOT / "src/evolution_engine/protocols").rglob("*.py")
                text = "\n".join(p.read_text(encoding="utf-8") for p in source)
                declared = re.search(rf"def {method}\(.*?-> (\w+):", text, re.S)
                assert declared and declared.group(1) in alias_names, (
                    f"{name}.{method} returns a bare dict that is not a declared ALIAS")


def test_every_contract_output_type_is_resolved():
    """The blocker this package existed to clear."""
    body = (ROOT / "spec/ACTIVE_CONTRACT.md").read_text(encoding="utf-8")
    block = body[body.index("## 7.2 Required Protocols"):]
    block = block[:block.index("# 8.")]
    outputs = [
        line.split("|")[3].strip()
        for line in block.splitlines()
        if line.startswith("|") and line.count("|") >= 4
    ][2:]
    resolved = {e["name"] for e in TYPE_DOC["protocol_types"]}
    unresolved = [o for o in outputs if o and o not in resolved]
    assert not unresolved, f"section 7.2 outputs with no resolution: {unresolved}"


def test_alias_types_point_at_a_schema_that_exists():
    for entry in TYPE_DOC["protocol_types"] + TYPE_DOC["sdk_return_types"]:
        if entry["kind"] != "ALIAS":
            continue
        assert (ROOT / entry["schema"]).exists(), f"{entry['name']} -> missing {entry['schema']}"


def test_in_process_types_have_a_dataclass():
    for entry in TYPE_DOC["protocol_types"]:
        if entry["kind"] != "IN_PROCESS":
            continue
        assert hasattr(types, entry["name"]), f"{entry['name']} has no dataclass"


def test_state_enums_match_the_fsm_registry():
    """The same drift LINT-09 guards, checked from the Python side this time."""
    fsms = yaml.safe_load((ROOT / "spec/fsm_states_57.yaml").read_text(encoding="utf-8"))["fsms"]
    assert {s.value for s in types.CandidateState} == set(fsms["candidate_lifecycle_fsm"]["states"])
    assert {s.value for s in types.RunState} == set(fsms["run_lifecycle_fsm"]["states"])


def test_execution_status_matches_the_violation_mapping():
    profile = yaml.safe_load(
        (ROOT / "spec/sandbox/profile-a-linux.yaml").read_text(encoding="utf-8"))
    mapped = {e["outcome"] for e in profile["violation_detection"]["mapping"]}
    assert {s.value for s in types.ExecutionStatus} == mapped


def test_version_matches_the_manifest():
    manifest = yaml.safe_load((ROOT / "spec/version_manifest.yaml").read_text(encoding="utf-8"))
    assert evolution_engine.__version__ == manifest["engine_version"]
