"""Canonical serializer conformance (REQ-S11-001, REQ-S11-002, REQ-S10-010).

The vectors in canonical_bytes_vectors.json are the contract. If tools/canonical_bytes.py
changes behaviour, these fail; if the vectors are regenerated to match a broken
serializer, the adversarial pairs below still fail.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest
import yaml

from tests.conftest import ROOT

sys.path.insert(0, str(ROOT / "tools"))
from canonical_bytes import canonical_bytes, candidate_id, generation_id, sha256_hex  # noqa: E402

VECTORS = json.loads((ROOT / "tests/golden/canonical_bytes_vectors.json").read_text(encoding="utf-8"))
RULES = yaml.safe_load((ROOT / "spec/reproducibility.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("vector", VECTORS["canonical_bytes"], ids=lambda v: v["name"])
def test_vector_reproduces(vector):
    assert canonical_bytes(vector["value"]).decode("utf-8") == vector["canonical_utf8"]
    assert sha256_hex(vector["value"]) == vector["sha256"]


def test_nfc_spellings_collapse():
    """Two spellings of the same character must produce the same bytes."""
    assert canonical_bytes({"k": "é"}) == canonical_bytes({"k": "é"})


def test_null_and_absent_are_different_bytes():
    """spec/reproducibility.yaml canonical_bytes.null_vs_absent."""
    assert canonical_bytes({"a": 1, "b": None}) != canonical_bytes({"a": 1})


def test_keys_are_sorted():
    assert canonical_bytes({"b": 1, "A": 2, "a": 3}) == b'{"A":2,"a":3,"b":1}'


def test_no_insignificant_whitespace():
    assert b" " not in canonical_bytes({"a": [1, 2], "b": {"c": 3}})


def test_no_trailing_newline():
    assert not canonical_bytes({"a": 1}).endswith(b"\n")


def test_binary_float_is_refused():
    """REQ-S11-001."""
    with pytest.raises(TypeError):
        canonical_bytes({"x": 1.5})


def test_integer_out_of_range_is_refused():
    bounds = RULES["canonical_bytes"]["integer_bounds"]
    with pytest.raises(ValueError):
        canonical_bytes({"n": bounds["maximum"] + 1})
    with pytest.raises(ValueError):
        canonical_bytes({"n": bounds["minimum"] - 1})


def test_non_ascii_stays_literal():
    """Escaping non-ASCII would make NFC pointless."""
    assert "สวัสดี" in canonical_bytes({"th": "สวัสดี"}).decode("utf-8")


@pytest.mark.parametrize("vector", VECTORS["identifiers"], ids=lambda v: v["name"])
def test_identifier_vector_reproduces(vector):
    if "candidate_id" in vector:
        assert candidate_id(**vector["args"]) == vector["candidate_id"]
    else:
        assert generation_id(**vector["args"]) == vector["generation_id"]


def test_candidate_id_is_content_derived():
    """REQ-S10-010: the same content must always yield the same id, or the final
    tie-break is not deterministic and REQ-S29-004's replay comparison is untestable."""
    args = dict(generation_index=2, source_hash="f" * 64,
                parent_candidate_id="e" * 64, mutation_id=None)
    assert candidate_id(**args) == candidate_id(**args)
    changed = dict(args, source_hash="0" * 64)
    assert candidate_id(**changed) != candidate_id(**args)


def test_candidate_id_ordering_is_total():
    ids = sorted(candidate_id(i, "a" * 64, None, None) for i in range(20))
    assert len(set(ids)) == 20
    assert ids == sorted(ids)


def test_declared_content_derived_ids_have_a_formula():
    for entry in RULES["identifiers"]:
        assert entry["kind"] in {"content-derived", "event-derived"}
        assert entry["formula"], entry["name"]
        if entry["kind"] == "content-derived":
            assert entry["representation"].startswith("lowercase hex"), entry["name"]


def test_every_reproducibility_level_is_defined_and_verifiable():
    """Section 11.3 listed five labels with no definition and no procedure."""
    levels = RULES["reproducibility_levels"]["levels"]
    assert [x["level"] for x in levels] == ["R0", "R1", "R2", "R3", "R4"]
    for level in levels:
        assert len(level["definition"].split()) >= 10, level["level"]
        assert level["verification"], level["level"]
