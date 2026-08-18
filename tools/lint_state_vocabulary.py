#!/usr/bin/env python3
"""LINT-09 / LINT-10 — cross-source consistency checks.

LINT-09 (REQ-S13-004): every FSM state vocabulary must be identical across
  spec/fsm_states_57.yaml, the JSON Schema enums, and the SQLite CHECK constraints.
LINT-10 (REQ-S01-009): audit/evidence/quarantine/recovery rows must never be
  destroyed by a cascading delete.
LINT-11 (REQ-S16-001): benchmarks/golden/manifest.yaml is the canonical corpus
  registry; case directories and every derived table must agree with it.

Exit code 0 = pass, 1 = BLOCKER findings.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

DDL_FILES = [
    "docs/03_DATABASE_AND_STORAGE.md",
    "docs/03_storage_and_database/SQLITE_DDL_29_TABLES.md",
    "build/spec/Evolution_Engine_Active_Spec_10_2_2.md",
]

# DDL CHECK column -> fsm key in spec/fsm_states_57.yaml
STATE_COLUMNS = {
    "run_state": "run_lifecycle_fsm",
    "candidate_state": "candidate_lifecycle_fsm",
    "deployment_state": "deployment_fsm",
    "recovery_status": "recovery_fsm",
}

# tables whose rows are evidence and must outlive whatever they record
PROTECTED_TABLES = [
    "audit_events",
    "evidence_records",
    "quarantine_records",
    "recovery_records",
]


def sql_blocks(path: pathlib.Path) -> str:
    """Concatenate every fenced block in the file that contains DDL."""
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
    return "\n".join(b for b in blocks if "CREATE TABLE" in b or "CREATE INDEX" in b)


def check_values(sql: str, column: str) -> set[str] | None:
    m = re.search(rf"{column} TEXT NOT NULL CHECK\({column} IN \((.*?)\)\)", sql, re.S)
    return set(re.findall(r"'([A-Z_]+)'", m.group(1))) if m else None


def schema_enums(path: pathlib.Path) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}

    def walk(node, key=None):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "enum" and isinstance(v, list):
                    found[key] = set(v)
                else:
                    walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)

    walk(json.loads(path.read_text(encoding="utf-8")))
    return found


def main() -> int:
    findings: list[str] = []
    fsms = yaml.safe_load((ROOT / "spec/fsm_states_57.yaml").read_text(encoding="utf-8"))["fsms"]

    # --- fsm_states_57.yaml internal consistency -------------------------------
    for name, fsm in fsms.items():
        states = set(fsm["states"])
        if fsm["states_count"] != len(states):
            findings.append(f"LINT-09 {name}: states_count={fsm['states_count']} but {len(states)} states listed")
        if fsm["initial_state"] not in states:
            findings.append(f"LINT-09 {name}: initial_state {fsm['initial_state']!r} is not in states")
        for term in fsm["terminal_states"]:
            if term not in states:
                findings.append(f"LINT-09 {name}: terminal_state {term!r} is not in states")

    # --- DDL CHECK constraints vs the canonical vocabulary ---------------------
    for rel in DDL_FILES:
        path = ROOT / rel
        if not path.exists():
            findings.append(f"LINT-09 missing DDL source: {rel}")
            continue
        sql = sql_blocks(path)
        for column, fsm_key in STATE_COLUMNS.items():
            actual = check_values(sql, column)
            if actual is None:
                findings.append(f"LINT-09 {rel}: no CHECK constraint found for {column}")
                continue
            expected = set(fsms[fsm_key]["states"])
            if actual != expected:
                findings.append(
                    f"LINT-09 {rel}: {column} diverges from {fsm_key} — "
                    f"DDL-only={sorted(actual - expected)} FSM-only={sorted(expected - actual)}"
                )

        # --- LINT-10: no cascade into evidence -------------------------------
        for table in PROTECTED_TABLES:
            m = re.search(rf"CREATE TABLE {table} \((.*?)\n\);", sql, re.S)
            if not m:
                findings.append(f"LINT-10 {rel}: table {table} not found")
                continue
            if "ON DELETE CASCADE" in m.group(1):
                findings.append(
                    f"LINT-10 {rel}: {table} has an ON DELETE CASCADE parent — "
                    f"violates REQ-S01-009 (Never Destroy Audit History)"
                )

    # --- JSON Schema enums vs the canonical vocabulary -------------------------
    for rel, column, fsm_key in [
        ("schemas/07_run.schema.json", "run_state", "run_lifecycle_fsm"),
        ("schemas/02_candidate_state.schema.json", None, "candidate_lifecycle_fsm"),
    ]:
        path = ROOT / rel
        if not path.exists():
            findings.append(f"LINT-09 missing schema: {rel}")
            continue
        enums = schema_enums(path)
        actual = enums.get(column) if column else (list(enums.values())[0] if len(enums) == 1 else None)
        if actual is None:
            findings.append(f"LINT-09 {rel}: no state enum found")
            continue
        expected = set(fsms[fsm_key]["states"])
        if actual != expected:
            findings.append(
                f"LINT-09 {rel}: enum diverges from {fsm_key} — "
                f"schema-only={sorted(actual - expected)} FSM-only={sorted(expected - actual)}"
            )

    # --- LINT-11: golden corpus directories must match the canonical manifest ----
    corpus = ROOT / "benchmarks/golden"
    manifest = yaml.safe_load((corpus / "manifest.yaml").read_text(encoding="utf-8"))["cases"]
    readme = (corpus / "README.md").read_text(encoding="utf-8")
    declared = dict(
        (mid, name)
        for name, mid in re.findall(r"[\u251c\u2514]\u2500\u2500 (mvp\d\d_[a-z0-9_]+)/\s*#\s*(MVP-\d\d)", readme)
    )
    on_disk = sorted(d.name for d in corpus.iterdir() if d.is_dir())
    if len(manifest) != 14:
        findings.append(f"LINT-11 manifest.yaml declares {len(manifest)} cases, expected 14")
    if len(on_disk) != 14:
        findings.append(f"LINT-11 {len(on_disk)} case directories on disk, expected 14")
    for case in manifest:
        cid = case["id"]
        want = declared.get(cid)
        if want is None:
            findings.append(f"LINT-11 {cid}: no directory declared in benchmarks/golden/README.md")
            continue
        if want not in on_disk:
            findings.append(f"LINT-11 {cid}: directory {want!r} declared in README but missing on disk")
            continue
        pyaml = yaml.safe_load((corpus / want / "project.yaml").read_text(encoding="utf-8"))
        for field, manifest_key in [("case_id", "id"), ("name", "name"), ("scope", "scope"),
                                    ("entry_point", "entry_point"),
                                    ("expected_disposition", "expected_disposition"),
                                    ("reproducibility_target", "reproducibility_target")]:
            if pyaml.get(field) != case[manifest_key]:
                findings.append(
                    f"LINT-11 {want}/project.yaml: {field}={pyaml.get(field)!r} "
                    f"but manifest says {case[manifest_key]!r}"
                )

    # every expected_disposition must be a declared terminal state somewhere
    terminals = set()
    for fsm in fsms.values():
        terminals |= set(fsm["terminal_states"])
    for case in manifest:
        if case["expected_disposition"] not in terminals:
            findings.append(
                f"LINT-11 {case['id']}: expected_disposition "
                f"{case['expected_disposition']!r} is not a terminal state of any FSM"
            )

    if findings:
        print(f"BLOCKER: {len(findings)} finding(s)\n")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("LINT-09 / LINT-10 / LINT-11: PASS — vocabularies agree, evidence is retention-safe, corpus matches manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
