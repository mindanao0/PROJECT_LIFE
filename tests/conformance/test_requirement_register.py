"""Requirement register tests (REQ-S02-008, REQ-S22-001, REQ-S22-003, REQ-S22-004)."""
from __future__ import annotations

import re

import pytest
import yaml

from tests.conftest import ROOT

CONTRACT = ROOT / "spec/ACTIVE_CONTRACT.md"
REQUIRED_FIELDS = {"id", "section", "status", "text_digest", "owner",
                   "verification_method", "test_refs", "evidence_refs", "release_gates"}
ID_PATTERN = re.compile(r"^REQ-S[0-9]{2}-[0-9]{3}$")


@pytest.fixture(scope="module")
def contract_ids() -> set[str]:
    body = CONTRACT.read_text(encoding="utf-8")
    return set(re.findall(r"\[(?:REQ|IMPL|TEST|EVID)\]\[(REQ-S\d{2}-\d{3})\]", body))


@pytest.fixture(scope="module")
def register() -> dict:
    return yaml.safe_load((ROOT / "spec/requirements.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def chain() -> dict:
    return yaml.safe_load((ROOT / "spec/traceability.yaml").read_text(encoding="utf-8"))


def test_register_covers_the_contract_exactly(register, contract_ids):
    ids = {r["id"] for r in register["requirements"]}
    assert ids == contract_ids
    assert register["total_requirements"] == len(ids)


def test_every_id_matches_the_mandated_regex(register):
    """REQ-S02-007."""
    for record in register["requirements"]:
        assert ID_PATTERN.match(record["id"]), record["id"]


def test_no_duplicate_ids(register):
    ids = [r["id"] for r in register["requirements"]]
    assert len(ids) == len(set(ids))


def test_every_record_has_the_mandated_fields(register):
    """REQ-S02-008."""
    for record in register["requirements"]:
        assert REQUIRED_FIELDS <= set(record), (record["id"], sorted(REQUIRED_FIELDS - set(record)))


def test_id_section_component_matches_the_section(register):
    for record in register["requirements"]:
        assert int(record["id"][5:7]) == record["section"], record["id"]


def test_register_and_chain_agree(register, chain):
    """The two files are generated together and must never diverge."""
    left = {r["id"]: r["text_digest"] for r in register["requirements"]}
    right = {r["id"]: r["text_digest"] for r in chain["requirements"]}
    assert left == right


def test_no_dangling_test_reference(register):
    """REQ-S22-003: a dangling reference is a CI failure."""
    for record in register["requirements"]:
        for ref in record["test_refs"]:
            path = ROOT / ref.split("::")[0]
            assert path.exists(), f"{record['id']} points at missing {ref}"


def test_unverified_requirements_are_not_marked_verified(register):
    """REQ-S22-004: no auto-PASS."""
    for record in register["requirements"]:
        if not record["test_refs"]:
            assert record["verification_method"] == "PENDING", record["id"]
        else:
            assert record["verification_method"] == "AUTOMATED_TEST", record["id"]


def test_no_requirement_claims_evidence_that_does_not_exist(register):
    """Nothing has produced an evidence bundle yet."""
    for record in register["requirements"]:
        assert record["evidence_refs"] == [], record["id"]


def test_declared_release_gates_exist(register):
    gates = {g["name"] for g in yaml.safe_load(
        (ROOT / "spec/release_gates.yaml").read_text(encoding="utf-8"))["release_gates"]}
    for record in register["requirements"]:
        for gate in record["release_gates"]:
            assert gate in gates, f"{record['id']} references unknown gate {gate}"
