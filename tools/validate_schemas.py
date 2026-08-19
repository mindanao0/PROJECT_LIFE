#!/usr/bin/env python3
"""M3 schema gate — the check REQ-S15-001 defines.

Verifies, in order:

  REQ-S15-006  exactly 26 canonical *.schema.json and nothing else counted
  REQ-S15-001  filenames match the section 15.1 registry exactly
  REQ-S15-002  Draft 2020-12, offline-resolvable $id, explicit required,
               additionalProperties: false on every object by default
  REQ-S15-005  every $ref resolves from the local registry with no network, and
               two independent validator implementations agree on every fixture
  REQ-S15-004  each schema has a minimal valid fixture, a complete valid fixture,
               and invalid fixtures covering its required/type/enum/range/pattern
               invariants
  REQ-S15-001  valid fixtures pass and invalid fixtures fail
  REQ-S15-003  spec/schema_manifest.json matches the real bytes on disk

Exit code 0 means the M3 schema gate passes. Any other value means it does not.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

try:
    import jsonschema_rs
except ImportError:  # pragma: no cover
    jsonschema_rs = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schemas"
FIXTURE_DIR = ROOT / "tests/schema/fixtures"
MANIFEST = ROOT / "spec/schema_manifest.json"

REGISTRY_ORDER = [
    "candidate", "candidate_state", "mutation", "mutation_result", "population",
    "generation", "run", "baseline", "project_manifest", "capability_contract",
    "objective", "metric_result", "oracle_result", "environment", "lineage_node",
    "lineage_edge", "selection_decision", "policy_snapshot", "provenance_certificate",
    "reproducibility_certificate", "checkpoint", "recovery_manifest", "release_gate",
    "quarantine_record", "memory_record", "engine_config",
]
EXPECTED_FILES = [f"{i:02d}_{n}.schema.json" for i, n in enumerate(REGISTRY_ORDER, 1)]
DRAFT = "https://json-schema.org/draft/2020-12/schema"


def object_nodes(node):
    """Yield every subschema that describes a JSON object."""
    if isinstance(node, dict):
        if node.get("type") == "object" or "properties" in node:
            yield node
        for key, value in node.items():
            if key in ("properties", "$defs", "patternProperties"):
                for sub in (value or {}).values():
                    yield from object_nodes(sub)
            elif key not in ("enum", "const", "required"):
                yield from object_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from object_nodes(value)


def refs(node):
    if isinstance(node, dict):
        if "$ref" in node:
            yield node["$ref"]
        for value in node.values():
            yield from refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from refs(value)


def main() -> int:
    problems: list[str] = []

    # -- REQ-S15-006 / REQ-S15-001: exactly the 26 canonical names -------------
    on_disk = sorted(p.name for p in SCHEMA_DIR.glob("*.schema.json"))
    stray = sorted(p.name for p in SCHEMA_DIR.glob("*.json") if not p.name.endswith(".schema.json"))
    if len(on_disk) != 26:
        problems.append(f"REQ-S15-006 expected 26 canonical schemas, found {len(on_disk)}")
    for missing in [f for f in EXPECTED_FILES if f not in on_disk]:
        problems.append(f"REQ-S15-001 missing canonical schema {missing}")
    for extra in [f for f in on_disk if f not in EXPECTED_FILES]:
        problems.append(f"REQ-S15-001 unexpected schema file {extra}")
    for helper in stray:
        problems.append(f"REQ-S15-006 non-canonical json file in schemas/: {helper}")

    schemas: dict[str, dict] = {}
    for name in on_disk:
        schemas[name] = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))

    # -- REQ-S15-002: declaration hygiene --------------------------------------
    for name, schema in schemas.items():
        if schema.get("$schema") != DRAFT:
            problems.append(f"REQ-S15-002 {name}: $schema is {schema.get('$schema')!r}, not Draft 2020-12")
        schema_id = schema.get("$id", "")
        if not schema_id.endswith(name):
            problems.append(f"REQ-S15-002 {name}: $id {schema_id!r} does not end with the filename")
        for node in object_nodes(schema):
            declared = node.get("additionalProperties", "<undeclared>")
            if declared == "<undeclared>":
                title = node.get("title", "<inline object>")
                problems.append(
                    f"REQ-S15-002 {name}: object {title!r} leaves additionalProperties undeclared; "
                    f"it must be false, or an explicit value schema if it is a named map")
            elif declared is True:
                title = node.get("title", "<inline object>")
                problems.append(
                    f"REQ-S15-002 {name}: object {title!r} sets additionalProperties: true, "
                    f"which is an unbounded extension point")
        if schema.get("type") == "object" and not schema.get("required"):
            problems.append(f"REQ-S15-002 {name}: object schema declares no required fields")

    # -- build both registries, offline ----------------------------------------
    py_registry = Registry()
    for name, schema in schemas.items():
        resource = Resource.from_contents(schema)
        py_registry = py_registry.with_resource(schema["$id"], resource)
        py_registry = py_registry.with_resource(name, resource)

    known = set(schemas) | {s["$id"] for s in schemas.values()}
    for name, schema in schemas.items():
        for ref in refs(schema):
            if ref.startswith("#"):
                continue
            if ref.startswith(("http://", "https://")) and ref not in known:
                problems.append(f"REQ-S15-005 {name}: $ref {ref!r} would need the network")
            elif not ref.startswith("http") and ref not in known:
                problems.append(f"REQ-S15-005 {name}: $ref {ref!r} does not resolve locally")

    rs_registry = None
    if jsonschema_rs is not None:
        pairs = [(schema["$id"], schema) for schema in schemas.values()]
        pairs += [(name, schema) for name, schema in schemas.items()]
        rs_registry = jsonschema_rs.Registry(pairs)
    else:
        problems.append(
            "REQ-S15-005 only one validator implementation available; install jsonschema-rs")

    # -- REQ-S15-004 / REQ-S15-001: fixtures -----------------------------------
    checked_valid = checked_invalid = 0
    for name, schema in schemas.items():
        stem = name.replace(".schema.json", "")
        base = FIXTURE_DIR / stem
        valid_dir, invalid_dir = base / "valid", base / "invalid"
        if not valid_dir.is_dir():
            problems.append(f"REQ-S15-004 {stem}: no valid fixture directory")
            continue
        valid_files = sorted(valid_dir.glob("*.json"))
        invalid_files = sorted(invalid_dir.glob("*.json")) if invalid_dir.is_dir() else []
        if not any(f.stem == "minimal" for f in valid_files):
            problems.append(f"REQ-S15-004 {stem}: no minimal valid fixture")
        if not any(f.stem == "complete" for f in valid_files):
            problems.append(f"REQ-S15-004 {stem}: no representative complete valid fixture")
        if not invalid_files:
            problems.append(f"REQ-S15-004 {stem}: no invalid fixtures")

        # A validator built without a format checker treats "format" as a comment.
        # That is why the identifier split-brain survived the M3 gate: eleven schemas
        # declared format: uuid on fields the rank 1 rules make 64-hex, and nothing
        # ever evaluated it (REQ-S15-002).
        py_validator = Draft202012Validator(
            schema, registry=py_registry, format_checker=FormatChecker())
        rs_validator = (
            jsonschema_rs.Draft202012Validator(
                schema, registry=rs_registry, validate_formats=True)
            if rs_registry is not None else None)

        for path in valid_files + invalid_files:
            should_pass = path.parent.name == "valid"
            document = json.loads(path.read_text(encoding="utf-8"))
            py_ok = py_validator.is_valid(document)
            rel = path.relative_to(ROOT)
            if py_ok != should_pass:
                verb = "was rejected" if should_pass else "was accepted"
                problems.append(f"REQ-S15-001 {rel} {verb} by jsonschema")
            if rs_validator is not None:
                rs_ok = rs_validator.is_valid(document)
                if rs_ok != py_ok:
                    problems.append(
                        f"REQ-S15-005 {rel}: jsonschema says {py_ok}, jsonschema-rs says {rs_ok}")
            checked_valid += should_pass
            checked_invalid += not should_pass

    # -- REQ-S15-003: manifest -------------------------------------------------
    if not MANIFEST.exists():
        problems.append("REQ-S15-003 spec/schema_manifest.json is missing")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        entries = {e["filename"]: e for e in manifest.get("schemas", [])}
        if len(entries) != len(on_disk):
            problems.append(
                f"REQ-S15-003 manifest lists {len(entries)} schemas but {len(on_disk)} exist")
        for index, name in enumerate(EXPECTED_FILES, 1):
            entry = entries.get(name)
            if entry is None:
                problems.append(f"REQ-S15-003 manifest is missing {name}")
                continue
            if entry.get("registry_order") != index:
                problems.append(
                    f"REQ-S15-003 {name}: registry_order {entry.get('registry_order')} should be {index}")
            if entry.get("schema_id") != schemas[name]["$id"]:
                problems.append(f"REQ-S15-003 {name}: schema_id does not match the file")
            real = hashlib.sha256((SCHEMA_DIR / name).read_bytes()).hexdigest()
            if entry.get("sha256") != real:
                problems.append(f"REQ-S15-003 {name}: sha256 is stale (file is {real[:16]}...)")

    if problems:
        print(f"M3 SCHEMA GATE: FAIL — {len(problems)} problem(s)\n")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    implementations = "jsonschema + jsonschema-rs" if rs_registry else "jsonschema only"
    print(
        f"M3 SCHEMA GATE: PASS — 26 schemas, {checked_valid} valid and {checked_invalid} invalid "
        f"fixtures, agreed by {implementations}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
