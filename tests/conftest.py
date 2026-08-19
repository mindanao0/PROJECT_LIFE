"""Shared fixtures for the Evolution Engine test suite."""
from __future__ import annotations

import json
import pathlib

import pytest
from referencing import Registry, Resource

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schemas"
FIXTURE_DIR = ROOT / "tests/schema/fixtures"


@pytest.fixture(scope="session")
def repo_root() -> pathlib.Path:
    return ROOT


@pytest.fixture(scope="session")
def schema_paths() -> list[pathlib.Path]:
    return sorted(SCHEMA_DIR.glob("*.schema.json"))


@pytest.fixture(scope="session")
def schemas(schema_paths) -> dict[str, dict]:
    return {p.name: json.loads(p.read_text(encoding="utf-8")) for p in schema_paths}


@pytest.fixture(scope="session")
def registry(schemas) -> Registry:
    """Offline registry: every schema addressable by $id and by filename (REQ-S15-005)."""
    reg = Registry()
    for name, schema in schemas.items():
        resource = Resource.from_contents(schema)
        reg = reg.with_resource(schema["$id"], resource)
        reg = reg.with_resource(name, resource)
    return reg


def fixture_cases(kind: str):
    """(schema filename, fixture path) for every valid/ or invalid/ fixture."""
    cases = []
    for schema_path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        stem = schema_path.name.replace(".schema.json", "")
        for fixture in sorted((FIXTURE_DIR / stem / kind).glob("*.json")):
            cases.append(pytest.param(schema_path.name, fixture,
                                      id=f"{stem}/{kind}/{fixture.stem}"))
    return cases
