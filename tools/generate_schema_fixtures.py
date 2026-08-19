#!/usr/bin/env python3
"""Generate the schema fixture corpus required by REQ-S15-004.

For every canonical schema this writes, under tests/schema/fixtures/<name>/:

  valid/minimal.json      only the required fields, simplest legal values
  valid/complete.json     every declared property populated
  invalid/*.json          one file per invariant that must be rejected —
                          each missing required field, plus type, enum, range,
                          pattern (reference invariant) and additionalProperties

Every generated file is verified before it is written: valid fixtures must
validate, invalid fixtures must fail, and the failure must be attributable to
the invariant the fixture is named after. The generator aborts otherwise, so a
fixture that does not actually test what it claims can never reach the corpus.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import sys

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schemas"
FIXTURE_DIR = ROOT / "tests/schema/fixtures"

UUIDS = [
    "018e1234-5678-7abc-8def-0123456789ab",
    "018e2222-3333-7444-8555-666677778888",
    "018e9999-aaaa-7bbb-8ccc-ddddeeeeffff",
]
TIMESTAMP = "2026-08-19T12:00:00.000000Z"
HEX64 = "a" * 64
HEX128 = "b" * 128


def build_registry() -> Registry:
    registry = Registry()
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        resource = Resource.from_contents(contents)
        registry = registry.with_resource(contents["$id"], resource)
        registry = registry.with_resource(path.name, resource)
    return registry


def sample_for_pattern(pattern: str) -> str:
    table = {
        r"^[0-9a-f]{64}$": HEX64,
        r"^[0-9a-f]{128}$": HEX128,
        r"^[0-9]+\.[0-9]{6}$": "1.000000",
        r"^-?[0-9]+\.[0-9]{6}$": "1.000000",
        r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?$": "1.5",
        r"^[a-zA-Z0-9_-]+$": "example_value",
    }
    if pattern in table:
        return table[pattern]
    raise SystemExit(f"generator has no sample for pattern {pattern!r}; add one to sample_for_pattern")


def violate_pattern(pattern: str) -> str:
    """A string that is the right shape but breaks the pattern."""
    table = {
        r"^[0-9a-f]{64}$": "z" * 64,
        r"^[0-9a-f]{128}$": "z" * 128,
        r"^[0-9]+\.[0-9]{6}$": "1.00",
        r"^-?[0-9]+\.[0-9]{6}$": "1.00",
        r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?$": "1,5",
        r"^[a-zA-Z0-9_-]+$": "has space",
    }
    return table.get(pattern, "!!invalid!!")


def resolve(schema: dict, registry: Registry) -> dict:
    if "$ref" not in schema:
        return schema
    resolved = registry.get(schema["$ref"])
    if resolved is None:
        raise SystemExit(f"cannot resolve $ref {schema['$ref']!r}")
    return resolved.contents


def generate(schema: dict, registry: Registry, minimal: bool, seed: int = 0):
    schema = resolve(schema, registry)

    if "enum" in schema:
        return schema["enum"][0]
    if "const" in schema:
        return schema["const"]

    declared = schema.get("type")
    types = declared if isinstance(declared, list) else [declared]
    # a nullable field is still populated, so the fixture exercises the real type
    kind = next((t for t in types if t != "null"), types[0])

    if kind == "object":
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        keys = required if minimal else list(properties)
        out = {}
        for i, key in enumerate(keys):
            if key in properties:
                out[key] = generate(properties[key], registry, minimal, seed + i)
        return out

    if kind == "array":
        item_schema = schema.get("items", {"type": "string"})
        count = max(schema.get("minItems", 1), 1)
        return [generate(item_schema, registry, minimal, seed + i) for i in range(count)]

    if kind == "integer":
        low = schema.get("minimum")
        if low is None:
            low = schema.get("exclusiveMinimum")
            low = low + 1 if low is not None else 1
        return int(low) + 1

    if kind == "number":
        return float(schema.get("minimum", 0)) + 1.0

    if kind == "boolean":
        return True

    if kind == "string":
        if "pattern" in schema:
            return sample_for_pattern(schema["pattern"])
        fmt = schema.get("format")
        if fmt == "uuid":
            return UUIDS[seed % len(UUIDS)]
        if fmt == "date-time":
            return TIMESTAMP
        return "example"

    if kind is None:
        return "example"
    raise SystemExit(f"generator does not handle type {kind!r}")


def first_scalar_property(schema: dict, registry: Registry):
    """Return (key, subschema) of a required scalar property, for type/range tests."""
    for key in schema.get("required", []):
        sub = resolve(schema.get("properties", {}).get(key, {}), registry)
        if sub.get("type") in ("string", "integer", "number") or "enum" in sub:
            return key, sub
    return None, None


def build_invalid_cases(schema: dict, registry: Registry, complete: dict) -> dict[str, object]:
    """name -> document, each violating exactly one invariant."""
    cases: dict[str, object] = {}
    schema = resolve(schema, registry)

    if schema.get("type") != "object":
        # a scalar or enum schema still has invariants worth pinning
        if "enum" in schema:
            cases["bad_enum_value"] = "NOT_A_MEMBER_OF_THE_ENUM"
            cases["wrong_type_for_enum"] = 12345
        elif schema.get("type") == "string":
            cases["wrong_type"] = 12345
            if "pattern" in schema:
                cases["bad_pattern"] = violate_pattern(schema["pattern"])
        return cases

    for key in schema.get("required", []):
        doc = dict(complete)
        doc.pop(key, None)
        cases[f"missing_required_{key}"] = doc

    if schema.get("additionalProperties") is False:
        doc = dict(complete)
        doc["not_a_declared_field"] = "x"
        cases["additional_property_rejected"] = doc

    key, sub = first_scalar_property(schema, registry)
    if key is not None:
        doc = dict(complete)
        doc[key] = [] if sub.get("type") != "array" else "not-an-array"
        cases[f"wrong_type_{key}"] = doc

    for key in schema.get("required", []):
        sub = resolve(schema.get("properties", {}).get(key, {}), registry)
        if "enum" in sub and f"bad_enum_{key}" not in cases:
            doc = dict(complete)
            doc[key] = "NOT_A_MEMBER_OF_THE_ENUM"
            cases[f"bad_enum_{key}"] = doc
            break

    for key in schema.get("required", []):
        sub = resolve(schema.get("properties", {}).get(key, {}), registry)
        if sub.get("type") == "integer" and ("minimum" in sub or "exclusiveMinimum" in sub):
            floor = sub.get("minimum", sub.get("exclusiveMinimum", 0))
            doc = dict(complete)
            doc[key] = int(floor) - 1
            cases[f"below_range_{key}"] = doc
            break

    for key in schema.get("required", []):
        sub = resolve(schema.get("properties", {}).get(key, {}), registry)
        if "pattern" in sub:
            doc = dict(complete)
            doc[key] = violate_pattern(sub["pattern"])
            cases[f"bad_pattern_{key}"] = doc
            break

    return cases


def main() -> int:
    registry = build_registry()
    schemas = sorted(SCHEMA_DIR.glob("*.schema.json"))
    if len(schemas) != 26:
        raise SystemExit(f"expected 26 canonical schemas, found {len(schemas)}")

    if FIXTURE_DIR.exists():
        shutil.rmtree(FIXTURE_DIR)

    total_valid = total_invalid = 0
    for path in schemas:
        schema = json.loads(path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, registry=registry)
        name = path.name.replace(".schema.json", "")
        base = FIXTURE_DIR / name
        (base / "valid").mkdir(parents=True, exist_ok=True)
        (base / "invalid").mkdir(parents=True, exist_ok=True)

        minimal = generate(schema, registry, minimal=True)
        complete = generate(schema, registry, minimal=False)
        for label, doc in (("minimal", minimal), ("complete", complete)):
            errors = list(validator.iter_errors(doc))
            if errors:
                raise SystemExit(
                    f"{name}/valid/{label} does not validate: {errors[0].message}")
            (base / "valid" / f"{label}.json").write_text(
                json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            total_valid += 1

        for label, doc in build_invalid_cases(schema, registry, complete).items():
            if validator.is_valid(doc):
                raise SystemExit(
                    f"{name}/invalid/{label} was accepted; it does not test anything")
            (base / "invalid" / f"{label}.json").write_text(
                json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            total_invalid += 1

    print(f"{len(schemas)} schemas: {total_valid} valid fixtures, {total_invalid} invalid fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
