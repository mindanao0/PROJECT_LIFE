#!/usr/bin/env python3
"""Reference canonical serializer (REQ-S11-001, REQ-S11-002).

Implements spec/reproducibility.yaml canonical_bytes exactly. This is the
executable definition: if the rules and this file ever disagree, the rules win and
this file is the bug.
"""
from __future__ import annotations

import hashlib
import json
import unicodedata

INT_MIN = -9223372036854775808
INT_MAX = 9223372036854775807


def canonical_bytes(value) -> bytes:
    """Serialize to the canonical byte string. No trailing newline."""
    return _emit(value).encode("utf-8")


def _emit(value) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        if not INT_MIN <= value <= INT_MAX:
            raise ValueError(f"integer {value} is outside signed 64-bit range")
        return str(value)
    if isinstance(value, float):
        raise TypeError("binary floating point is forbidden in hash-critical bytes (REQ-S11-001)")
    if isinstance(value, str):
        return _string(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_emit(v) for v in value) + "]"
    if isinstance(value, dict):
        keys = [k for k in value]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate object keys are forbidden")
        for k in keys:
            if not isinstance(k, str):
                raise TypeError("object keys must be strings")
        ordered = sorted(keys, key=lambda k: unicodedata.normalize("NFC", k).encode("utf-8"))
        return "{" + ",".join(f"{_string(k)}:{_emit(value[k])}" for k in ordered) + "}"
    raise TypeError(f"cannot canonicalise {type(value).__name__}")


def _string(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    out = ['"']
    for ch in text:
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\f":
            out.append("\\f")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04x}")
        else:
            out.append(ch)  # non-ASCII stays literal UTF-8
    out.append('"')
    return "".join(out)


def sha256_hex(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def candidate_id(generation_index: int, source_hash: str,
                 parent_candidate_id: str | None, mutation_id: str | None) -> str:
    """CandidateId = SHA-256(canonical bytes of the identity envelope)."""
    envelope = {
        "generation_index": generation_index,
        "source_hash": source_hash,
        "parent_candidate_id": parent_candidate_id,
        "mutation_id": mutation_id,
    }
    return sha256_hex(envelope)


def generation_id(run_id: str, generation_index: int) -> str:
    return sha256_hex({"run_id": run_id, "generation_index": generation_index})


if __name__ == "__main__":
    print(json.dumps({
        "empty_object": sha256_hex({}),
        "candidate_baseline": candidate_id(0, "a" * 64, None, None),
    }, indent=2))


# --- audit hash chain (section 18.1) ----------------------------------------

GENESIS_DIGEST = bytes(32)  # 32 zero bytes; the DB column stores NULL


def audit_event_payload(run_id, sequence_no: int, actor: str, event_type: str,
                        payload_artifact_id: str, created_at_utc: str) -> bytes:
    """The six fields the chain binds, in canonical byte form."""
    return canonical_bytes({
        "run_id": run_id,
        "sequence_no": sequence_no,
        "actor": actor,
        "event_type": event_type,
        "payload_artifact_id": payload_artifact_id,
        "created_at_utc": created_at_utc,
    })


def audit_event_hash(previous_digest: bytes | None, payload: bytes) -> str:
    """SHA-256(previous_digest_bytes || canonical_event_payload), raw byte concat."""
    prev = GENESIS_DIGEST if previous_digest is None else previous_digest
    if len(prev) != 32:
        raise ValueError("previous digest must be 32 raw bytes, not a hex string")
    return hashlib.sha256(prev + payload).hexdigest()


def verify_audit_chain(events: list[dict]) -> bool:
    """Recompute a whole scope from genesis. events must be ordered by sequence_no."""
    previous = None
    for index, event in enumerate(events):
        if event["sequence_no"] != index:
            return False
        payload = audit_event_payload(
            event["run_id"], event["sequence_no"], event["actor"],
            event["event_type"], event["payload_artifact_id"], event["created_at_utc"])
        expected = audit_event_hash(previous, payload)
        if expected != event["event_hash"]:
            return False
        previous = bytes.fromhex(expected)
    return True
