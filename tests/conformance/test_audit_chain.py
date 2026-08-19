"""Audit hash chain conformance (REQ-S18-001 .. REQ-S18-005).

Section 18.1 gave the shape `SHA256(previous_event_hash || canonical_event_payload)`
and left three things open, each enough to make two verifiers disagree:

  * what canonical_event_payload contains
  * what `||` concatenates — raw bytes, hex, or a prefixed string
  * whether genesis is null or 64 zeros, which section 18.1 and the evidence bundle
    answered differently

These tests pin all three, and prove the chain detects the tampering it exists for.
"""
from __future__ import annotations

import hashlib
import sys

import pytest

from tests.conftest import ROOT

sys.path.insert(0, str(ROOT / "tools"))
from canonical_bytes import (  # noqa: E402
    GENESIS_DIGEST, audit_event_hash, audit_event_payload, verify_audit_chain,
)

TS = "2026-08-19T12:00:00.000000Z"
ARTIFACT = "a" * 64


def build_chain(run_id, count: int) -> list[dict]:
    events, previous = [], None
    for i in range(count):
        event = {
            "run_id": run_id, "sequence_no": i, "actor": "engine",
            "event_type": "GENESIS" if i == 0 else f"EVENT_{i}",
            "payload_artifact_id": ARTIFACT, "created_at_utc": TS,
        }
        payload = audit_event_payload(**event)
        event["event_hash"] = audit_event_hash(previous, payload)
        previous = bytes.fromhex(event["event_hash"])
        events.append(event)
    return events


def test_genesis_digest_is_32_zero_bytes():
    """Section 18.1 said null, the evidence bundle said 64 zeros. Now one answer."""
    assert GENESIS_DIGEST == bytes(32)
    assert len(GENESIS_DIGEST) == 32


def test_payload_binds_sequence_and_scope():
    """Without sequence_no and run_id in the payload, reordering is undetectable."""
    payload = audit_event_payload(None, 7, "engine", "E", ARTIFACT, TS).decode()
    assert '"sequence_no":7' in payload
    assert '"run_id":null' in payload


def test_payload_keys_are_canonically_ordered():
    payload = audit_event_payload("r", 0, "a", "E", ARTIFACT, TS).decode()
    keys = [seg.split('"')[1] for seg in payload.split(",") if '":' in seg]
    assert keys == sorted(keys)


def test_concatenation_is_raw_bytes_not_hex():
    """Hex or a sha256: prefix would give a different, equally plausible answer."""
    payload = audit_event_payload(None, 0, "a", "E", ARTIFACT, TS)
    raw = audit_event_hash(None, payload)
    hex_style = hashlib.sha256(GENESIS_DIGEST.hex().encode() + payload).hexdigest()
    prefixed = hashlib.sha256(b"sha256:" + GENESIS_DIGEST.hex().encode() + payload).hexdigest()
    assert raw != hex_style and raw != prefixed


def test_a_hex_string_is_rejected_as_previous_digest():
    payload = audit_event_payload(None, 1, "a", "E", ARTIFACT, TS)
    with pytest.raises(ValueError):
        audit_event_hash(b"0" * 64, payload)


@pytest.mark.parametrize("run_id", ["018e1234-5678-7abc-8def-0123456789ab", None])
def test_a_well_formed_chain_verifies(run_id):
    """Three events per scope, as REQ-S18-005 requires."""
    assert verify_audit_chain(build_chain(run_id, 3))


def test_run_scope_and_engine_scope_are_different_chains():
    """run_id IS NULL is its own chain and restarts at sequence 0."""
    run = build_chain("018e1234-5678-7abc-8def-0123456789ab", 3)
    engine = build_chain(None, 3)
    assert run[0]["event_hash"] != engine[0]["event_hash"]
    assert verify_audit_chain(run) and verify_audit_chain(engine)


def test_tampering_with_a_field_breaks_the_chain():
    chain = build_chain("r1", 3)
    chain[1]["actor"] = "attacker"
    assert not verify_audit_chain(chain)


def test_reordering_breaks_the_chain():
    chain = build_chain("r1", 3)
    chain[1], chain[2] = chain[2], chain[1]
    assert not verify_audit_chain(chain)


def test_a_gap_breaks_the_chain():
    """REQ-S18-002: recovery must detect a gap."""
    chain = build_chain("r1", 3)
    assert not verify_audit_chain([chain[0], chain[2]])


def test_a_forged_link_breaks_the_chain():
    chain = build_chain("r1", 3)
    chain[2]["event_hash"] = "f" * 64
    assert not verify_audit_chain(chain)


def test_full_chain_verifies_from_genesis(tmp_path):
    """REQ-S18-003: a verifier must validate genesis to latest with nothing else."""
    chain = build_chain("r1", 10)
    assert verify_audit_chain(chain)
    assert chain[0]["sequence_no"] == 0
