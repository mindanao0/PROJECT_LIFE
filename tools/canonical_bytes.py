#!/usr/bin/env python3
"""Re-export of the canonical serializer for tooling.

The implementation moved to src/evolution_engine/canonical.py in CR-0012: it is engine
code that the protocols and the slice depend on, not a build tool. This shim keeps the
existing `sys.path.insert(0, "tools")` imports in the tests and generators working.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from evolution_engine.canonical import (  # noqa: F401,E402
    GENESIS_DIGEST,
    audit_event_hash,
    audit_event_payload,
    canonical_bytes,
    candidate_id,
    generation_id,
    sha256_hex,
    verify_audit_chain,
)

if __name__ == "__main__":
    import json

    print(json.dumps({
        "empty_object": sha256_hex({}),
        "candidate_baseline": candidate_id(0, "a" * 64, None, None),
    }, indent=2))
