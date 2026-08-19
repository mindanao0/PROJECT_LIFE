#!/usr/bin/env python3
"""Make every schema agree with spec/reproducibility.yaml on identifier form.

CR-0004 declared CandidateId, GenerationId and ArtifactId content-derived 64-hex but
only changed schemas/01_candidate.schema.json. Eleven other schemas kept
`format: uuid` for the same fields, so the same property carried two forms in two
valid fixtures at once — and the M3 gate could not see it, because
tools/validate_schemas.py built its validators without a format checker, which makes
`format` a comment rather than a constraint.

This rewrites every identifier property from the rank 1 declaration. Run it after
changing spec/reproducibility.yaml, then regenerate fixtures and the manifest.
"""
from __future__ import annotations

import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schemas"
RULES = yaml.safe_load((ROOT / "spec/reproducibility.yaml").read_text(encoding="utf-8"))["identifier_rules"]

CONTENT = set(RULES["content_derived_properties"])
PATTERN = RULES["content_derived_pattern"]
EVENT_FORMAT = RULES["event_derived_format"]


def rewrite(node, key=None) -> int:
    """Set the right form on every identifier property. Returns the change count."""
    changed = 0
    if isinstance(node, dict):
        is_leaf = "type" in node and not node.get("properties")
        if key in CONTENT and is_leaf:
            before = (node.get("format"), node.get("pattern"))
            node.pop("format", None)
            node["pattern"] = PATTERN
            if before != (None, PATTERN):
                changed += 1
        elif key and key.endswith(("_id", "_ids")) and is_leaf and key not in CONTENT:
            # An enum or const already pins the value; strategy_id is M01..M10, not a
            # UUID, and stamping a format on it makes every valid fixture invalid.
            constrained = "enum" in node or "const" in node or "pattern" in node
            if not constrained and node.get("format") != EVENT_FORMAT:
                node["format"] = EVENT_FORMAT
                changed += 1
        for child_key, value in node.items():
            if child_key in ("properties", "$defs", "patternProperties"):
                for prop, sub in (value or {}).items():
                    changed += rewrite(sub, prop)
            elif child_key == "items":
                changed += rewrite(value, key)  # an array of ids keeps the array's name
            elif child_key not in ("enum", "const", "required"):
                changed += rewrite(value, key)
    elif isinstance(node, list):
        for value in node:
            changed += rewrite(value, key)
    return changed


def main() -> int:
    total, touched = 0, []
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        count = rewrite(schema)
        if count:
            path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            touched.append((path.name, count))
            total += count
    for name, count in touched:
        print(f"  {name}: {count} identifier propert{'y' if count == 1 else 'ies'}")
    print(f"{total} properties aligned across {len(touched)} schemas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
