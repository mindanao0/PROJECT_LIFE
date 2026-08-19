"""M3 schema gate as executable tests (REQ-S15-001 .. REQ-S15-006).

tools/validate_schemas.py runs the same checks as one command for CI; these
tests exist so a failure names the exact schema or fixture involved.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import pytest
from jsonschema import Draft202012Validator

from tests.conftest import ROOT, SCHEMA_DIR, fixture_cases

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

try:
    import jsonschema_rs
except ImportError:
    jsonschema_rs = None


def test_registry_holds_exactly_26_schemas(schema_paths):
    """REQ-S15-006: helper files must never be counted as schema 27."""
    assert [p.name for p in schema_paths] == EXPECTED_FILES
    strays = [p.name for p in SCHEMA_DIR.glob("*.json") if not p.name.endswith(".schema.json")]
    assert strays == [], f"non-canonical json files in schemas/: {strays}"


@pytest.mark.parametrize("name", EXPECTED_FILES)
def test_schema_declares_draft_2020_12_and_stable_id(name, schemas):
    """REQ-S15-002."""
    schema = schemas[name]
    assert schema["$schema"] == DRAFT
    assert schema["$id"].endswith(name)


@pytest.mark.parametrize("name", EXPECTED_FILES)
def test_schema_compiles(name, schemas):
    """REQ-S15-002: the schema itself must be a legal Draft 2020-12 document."""
    Draft202012Validator.check_schema(schemas[name])


@pytest.mark.parametrize("name", EXPECTED_FILES)
def test_object_schemas_are_closed(name, schemas):
    """REQ-S15-002: additionalProperties must be false, or an explicit value schema."""
    def walk(node, path="$"):
        if isinstance(node, dict):
            if node.get("type") == "object" or "properties" in node:
                assert "additionalProperties" in node, f"{name} {path} leaves it undeclared"
                assert node["additionalProperties"] is not True, f"{name} {path} is unbounded"
            for key, value in node.items():
                if key in ("properties", "$defs", "patternProperties"):
                    for prop, sub in (value or {}).items():
                        walk(sub, f"{path}.{prop}")
                elif key not in ("enum", "const", "required"):
                    walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")

    walk(schemas[name])


@pytest.mark.parametrize("name", EXPECTED_FILES)
def test_refs_resolve_offline(name, schemas, registry):
    """REQ-S15-005: no $ref may need the network."""
    def collect(node):
        if isinstance(node, dict):
            if "$ref" in node:
                yield node["$ref"]
            for value in node.values():
                yield from collect(value)
        elif isinstance(node, list):
            for value in node:
                yield from collect(value)

    for ref in collect(schemas[name]):
        if ref.startswith("#"):
            continue
        assert registry.get(ref) is not None, f"{name}: {ref} does not resolve locally"


@pytest.mark.parametrize("stem", [f.replace(".schema.json", "") for f in EXPECTED_FILES])
def test_fixture_corpus_is_complete(stem):
    """REQ-S15-004: minimal valid, complete valid, and invalid fixtures."""
    base = ROOT / "tests/schema/fixtures" / stem
    valid = {p.stem for p in (base / "valid").glob("*.json")}
    invalid = list((base / "invalid").glob("*.json"))
    assert "minimal" in valid, f"{stem} has no minimal valid fixture"
    assert "complete" in valid, f"{stem} has no complete valid fixture"
    assert invalid, f"{stem} has no invalid fixtures"


@pytest.mark.parametrize("name,fixture", fixture_cases("valid"))
def test_valid_fixture_is_accepted(name, fixture, schemas, registry):
    """REQ-S15-001."""
    validator = Draft202012Validator(schemas[name], registry=registry)
    document = json.loads(fixture.read_text(encoding="utf-8"))
    errors = sorted(validator.iter_errors(document), key=lambda e: list(e.path))
    assert not errors, f"{fixture.name}: {errors[0].message if errors else ''}"


@pytest.mark.parametrize("name,fixture", fixture_cases("invalid"))
def test_invalid_fixture_is_rejected(name, fixture, schemas, registry):
    """REQ-S15-001: an invalid fixture that passes is testing nothing."""
    validator = Draft202012Validator(schemas[name], registry=registry)
    document = json.loads(fixture.read_text(encoding="utf-8"))
    assert not validator.is_valid(document), f"{fixture.name} was accepted"


@pytest.mark.skipif(jsonschema_rs is None, reason="second validator implementation not installed")
@pytest.mark.parametrize("name,fixture", fixture_cases("valid") + fixture_cases("invalid"))
def test_two_implementations_agree(name, fixture, schemas, registry):
    """REQ-S15-005: two independent validators, same verdict on the same corpus."""
    pairs = [(s["$id"], s) for s in schemas.values()] + list(schemas.items())
    rs = jsonschema_rs.Draft202012Validator(schemas[name], registry=jsonschema_rs.Registry(pairs))
    py = Draft202012Validator(schemas[name], registry=registry)
    document = json.loads(fixture.read_text(encoding="utf-8"))
    assert rs.is_valid(document) == py.is_valid(document), f"{fixture.name}: implementations disagree"


def test_manifest_matches_bytes_on_disk(schema_paths):
    """REQ-S15-003."""
    manifest = json.loads((ROOT / "spec/schema_manifest.json").read_text(encoding="utf-8"))
    entries = {e["filename"]: e for e in manifest["schemas"]}
    assert manifest["total_schemas"] == len(schema_paths) == len(entries)
    for order, path in enumerate(schema_paths, 1):
        entry = entries[path.name]
        assert entry["registry_order"] == order
        assert entry["schema_id"] == json.loads(path.read_text(encoding="utf-8"))["$id"]
        assert entry["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(), (
            f"{path.name}: manifest digest is stale")
