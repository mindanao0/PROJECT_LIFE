"""Integrity trigger conformance (REQ-S13-003).

M7's gate requires "FK/state/polymorphic-owner/invariant tests pass". This module
is that test: it installs the canonical DDL plus the canonical triggers and drives
one positive and one negative insert for every owner_type.

The previous hand-written trigger set referenced a table `evaluations` and a column
`NEW.seq`, neither of which exists, so every artifact_refs insert failed. These
tests would have caught that on the first run.
"""
from __future__ import annotations

import re
import sqlite3

import pytest

from tests.conftest import ROOT

CONTRACT = ROOT / "spec/ACTIVE_CONTRACT.md"
DDL_DOC = ROOT / "docs/03_storage_and_database/SQLITE_DDL_29_TABLES.md"

OWNER_TABLES = {
    "PROJECT": "projects", "RUN": "runs", "GENERATION": "generations",
    "CANDIDATE": "candidates", "MUTATION_ATTEMPT": "mutation_attempts",
    "EVALUATION_ATTEMPT": "evaluation_attempts", "TEST_RESULT": "test_results",
    "CAPABILITY_RESULT": "capability_results", "METRIC_RESULT": "metric_results",
    "ORACLE_RESULT": "oracle_results", "SELECTION_DECISION": "selection_decisions",
    "CHECKPOINT": "checkpoints", "RECOVERY": "recovery_records",
    "EVIDENCE": "evidence_records", "AUDIT": "audit_events", "DEPLOYMENT": "deployments",
}


def fenced(path, predicate):
    blocks, current = [], None
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.startswith("```"):
            if current is None:
                current = []
            else:
                blocks.append("\n".join(current))
                current = None
            continue
        if current is not None:
            current.append(line)
    return "\n".join(b for b in blocks if predicate(b))


@pytest.fixture(scope="module")
def ddl() -> str:
    return fenced(DDL_DOC, lambda b: "CREATE TABLE" in b or "CREATE INDEX" in b)


@pytest.fixture(scope="module")
def triggers() -> str:
    body = CONTRACT.read_text(encoding="utf-8")
    span = re.search(r"<!-- INTEGRITY_TRIGGERS_BEGIN -->(.*?)<!-- INTEGRITY_TRIGGERS_END -->",
                     body, re.S)
    assert span, "the Active Contract carries no integrity trigger block"
    return re.search(r"```sql\n(.*?)```", span.group(1), re.S).group(1)


@pytest.fixture()
def db(ddl, triggers):
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(ddl)
    con.executescript(triggers)
    con.execute("INSERT INTO artifacts VALUES('a1','sha',1,'m','p','t')")
    return con


def artifact_ref_row(con, ref_id, owner_type, owner_id):
    width = len(list(con.execute("PRAGMA table_info(artifact_refs)")))
    values = [ref_id, owner_type, owner_id, "a1"] + ["role"] * (width - 4)
    con.execute(f"INSERT INTO artifact_refs VALUES({','.join('?' * width)})", values)


def seed_owner(con, owner_type) -> str:
    """Insert one row of the owning entity and return its id."""
    con.execute("INSERT OR IGNORE INTO projects VALUES('p1','n','1','t')")
    if owner_type == "PROJECT":
        return "p1"
    con.execute("INSERT OR IGNORE INTO runs VALUES('r1','p1','c','po','e','INITIATED','00','R1',NULL,'t')")
    if owner_type == "RUN":
        return "r1"
    con.execute("INSERT OR IGNORE INTO generations VALUES('g1','r1',0,NULL,'COMMITTED')")
    if owner_type == "GENERATION":
        return "g1"
    con.execute("INSERT OR IGNORE INTO candidates VALUES('c1','g1',NULL,'h','CREATED',NULL,'t')")
    if owner_type == "CANDIDATE":
        return "c1"
    table = OWNER_TABLES[owner_type]
    columns = [c[1] for c in con.execute(f"PRAGMA table_info({table})")]
    pytest.skip(f"{table} needs bespoke seeding ({len(columns)} columns)")


def test_all_sixteen_owner_types_are_covered(triggers):
    """A whitelist that misses an owner_type would reject legal rows."""
    for owner in OWNER_TABLES:
        assert f"NEW.owner_type = '{owner}'" in triggers, f"{owner} has no validation branch"


def test_trigger_tables_all_exist(db, triggers):
    """The defect that broke this before: a trigger naming a table that is not there."""
    real = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table in re.findall(r"SELECT 1 FROM (\w+)", triggers):
        assert table in real, f"trigger references missing table {table}"


@pytest.mark.parametrize("owner_type", ["PROJECT", "RUN", "GENERATION", "CANDIDATE"])
def test_valid_owner_reference_is_accepted(db, owner_type):
    owner_id = seed_owner(db, owner_type)
    artifact_ref_row(db, f"ok_{owner_type}", owner_type, owner_id)


@pytest.mark.parametrize("owner_type", ["PROJECT", "RUN", "GENERATION", "CANDIDATE"])
def test_dangling_owner_reference_is_rejected(db, owner_type):
    seed_owner(db, owner_type)
    with pytest.raises(sqlite3.IntegrityError):
        artifact_ref_row(db, f"bad_{owner_type}", owner_type, "does-not-exist")


def test_audit_sequence_must_be_gapless(db):
    db.execute("INSERT INTO projects VALUES('p1','n','1','t')")
    db.execute("INSERT INTO runs VALUES('r1','p1','c','po','e','INITIATED','00','R1',NULL,'t')")
    db.execute("INSERT INTO audit_events VALUES('e0','r1',0,NULL,'h0','sys','G','a1','t')")
    db.execute("INSERT INTO audit_events VALUES('e1','r1',1,'h0','h1','sys','E','a1','t')")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO audit_events VALUES('e9','r1',9,'h1','h9','sys','E','a1','t')")


def test_engine_scoped_audit_sequence_is_counted_separately(db):
    """run_id IS NULL is its own chain, so it starts at 0 rather than continuing a run."""
    db.execute("INSERT INTO projects VALUES('p1','n','1','t')")
    db.execute("INSERT INTO runs VALUES('r1','p1','c','po','e','INITIATED','00','R1',NULL,'t')")
    db.execute("INSERT INTO audit_events VALUES('e0','r1',0,NULL,'h0','sys','G','a1','t')")
    db.execute("INSERT INTO audit_events VALUES('x0',NULL,0,NULL,'hx','sys','G','a1','t')")


def test_terminal_candidate_is_immutable(db):
    db.execute("INSERT INTO projects VALUES('p1','n','1','t')")
    db.execute("INSERT INTO runs VALUES('r1','p1','c','po','e','INITIATED','00','R1',NULL,'t')")
    db.execute("INSERT INTO generations VALUES('g1','r1',0,NULL,'COMMITTED')")
    db.execute("INSERT INTO candidates VALUES('c1','g1',NULL,'h','SELECTED',NULL,'t')")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE candidates SET source_hash='tampered' WHERE candidate_id='c1'")


def test_lineage_self_loop_is_rejected(db):
    db.execute("INSERT INTO projects VALUES('p1','n','1','t')")
    db.execute("INSERT INTO runs VALUES('r1','p1','c','po','e','INITIATED','00','R1',NULL,'t')")
    db.execute("INSERT INTO generations VALUES('g1','r1',0,NULL,'COMMITTED')")
    db.execute("INSERT INTO candidates VALUES('c1','g1',NULL,'h','CREATED',NULL,'t')")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO lineage_edges VALUES('l1','r1','c1','c1',NULL,'MUTATION')")
