#!/usr/bin/env python3
"""Generate the canonical serializer golden byte vectors (REQ-S11-002).

Each vector pins one rule from spec/reproducibility.yaml canonical_bytes. Two are
adversarial pairs that must not come out wrong:

  nfc_normalization / nfc_precomposed        must hash identically
  null_present_vs_absent_a / ..._b           must hash differently

Both are asserted here, so a serializer that gets either wrong cannot ship vectors.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from canonical_bytes import canonical_bytes, candidate_id, generation_id, sha256_hex

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests/golden/canonical_bytes_vectors.json"

CASES = [
    ("empty_object", {}),
    ("empty_array", []),
    ("null_present_vs_absent_a", {"a": 1, "b": None}),
    ("null_present_vs_absent_b", {"a": 1}),
    ("key_order", {"b": 1, "A": 2, "a": 3}),
    ("nfc_normalization", {"k": "é"}),   # decomposed: e + combining acute
    ("nfc_precomposed", {"k": "é"}),      # precomposed, must match the above
    ("non_ascii_literal", {"th": "สวัสดี"}),
    ("escapes", {"s": "a\"b\\c\nd\te\bf\fg\rh"}),
    ("control_char_u0001", {"s": ""}),
    ("int_bounds_max", {"n": 9223372036854775807}),
    ("int_bounds_min", {"n": -9223372036854775808}),
    ("decimal_string", {"weight_decimal": "0.7", "margin_decimal": "1.0"}),
    ("nested", {"z": [1, {"y": "x"}], "a": {"b": [], "c": {}}}),
]


def main() -> int:
    vectors = []
    for name, value in CASES:
        vectors.append({
            "name": name,
            "value": value,
            "canonical_utf8": canonical_bytes(value).decode("utf-8"),
            "sha256": sha256_hex(value),
        })

    identifiers = [
        {"name": "candidate_baseline",
         "args": {"generation_index": 0, "source_hash": "a" * 64,
                  "parent_candidate_id": None, "mutation_id": None},
         "candidate_id": candidate_id(0, "a" * 64, None, None)},
        {"name": "candidate_child",
         "args": {"generation_index": 1, "source_hash": "b" * 64,
                  "parent_candidate_id": "c" * 64, "mutation_id": "d" * 64},
         "candidate_id": candidate_id(1, "b" * 64, "c" * 64, "d" * 64)},
        {"name": "generation",
         "args": {"run_id": "018e1234-5678-7abc-8def-0123456789ab", "generation_index": 3},
         "generation_id": generation_id("018e1234-5678-7abc-8def-0123456789ab", 3)},
    ]

    by_name = {v["name"]: v for v in vectors}
    if by_name["nfc_normalization"]["sha256"] != by_name["nfc_precomposed"]["sha256"]:
        raise SystemExit("NFC normalization is broken: the two spellings hash differently")
    if by_name["null_present_vs_absent_a"]["sha256"] == by_name["null_present_vs_absent_b"]["sha256"]:
        raise SystemExit("null and absent collided; spec/reproducibility.yaml requires them to differ")

    OUT.write_text(json.dumps({
        "note": "Golden byte vectors required by REQ-S11-002. "
                "Regenerate with tools/generate_golden_vectors.py.",
        "canonical_bytes": vectors,
        "identifiers": identifiers,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(vectors)} byte vectors and {len(identifiers)} identifier vectors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
