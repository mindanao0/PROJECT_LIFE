#!/usr/bin/env python3
"""LINT-09 / LINT-10 — cross-source consistency checks.

LINT-09 (REQ-S13-004): every FSM state vocabulary must be identical across
  spec/fsm_states_57.yaml, the JSON Schema enums, and the SQLite CHECK constraints.
LINT-10 (REQ-S01-009): audit/evidence/quarantine/recovery rows must never be
  destroyed by a cascading delete.
LINT-11 (REQ-S16-001): benchmarks/golden/manifest.yaml is the canonical corpus
  registry; case directories and every derived table must agree with it.
LINT-13 (REQ-S21-002): every mandatory_check in spec/release_gates.yaml and every
  job in tools/ci_matrix.yaml must name a job declared in Active Contract section 21,
  and no release gate may require a maturity level that itself requires that gate.
LINT-14: every count declared in spec/version_manifest.yaml must equal the number
  actually present. Hand-asserted counts drifting from reality is the single most
  common defect class in this repo.
LINT-15: every evolution.yaml example printed in the docs must validate against
  schemas/26_engine_config.schema.json. A quickstart whose config is rejected by
  `evolve validate` is worse than no quickstart.
LINT-12: prose state lists anywhere in the repo must not use a state name that
  spec/fsm_states_57.yaml has retired. Prose drift is what made LINT-09 miss the
  first time: the DDL was fixed while the narrative kept the old vocabulary.

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

    # --- LINT-12: no retired state name may survive anywhere in the repo -------
    live = set()
    for fsm in fsms.values():
        live |= set(fsm["states"])
    retired = {
        # run
        "VALIDATING", "READY", "PAUSING", "STOPPING", "STOPPED",
        # recovery
        "REQUESTED", "VALIDATING_INPUTS", "RECONSTRUCTING_CAS", "RECONCILING_DB",
        "VERIFYING_AUDIT", "REPLAYING_GENERATION", "RECOVERED",
        # governance ("DRAFT" is deliberately excluded: it is also the name of
        # maturity level M0 in spec/maturity.yaml, so the token is ambiguous)
        "AUTHORITY_CHECKED", "SAFETY_REVIEWED", "TRACEABILITY_UPDATED",
        "VERSIONED", "EVIDENCE_INVALIDATED", "GATES_RUNNING", "ACCEPTED", "WITHDRAWN",
        # deployment
        "STAGED", "CANARY", "VALIDATED", "APPROVED", "ACTIVE", "PROMOTED",
    } - live
    scan_globs = ["build/spec/*.md", "docs/**/*.md", "spec/*.yaml", "schemas/*.json"]
    for pattern in scan_globs:
        for path in sorted(ROOT.glob(pattern)):
            if path.name == "lint_state_vocabulary.py":
                continue
            text = path.read_text(encoding="utf-8")
            for state in sorted(retired):
                # only flag it when used as a state token: quoted, backticked or in an arrow
                hits = re.findall(
                    rf"(?:'{state}'|`{state}`|^\s*{state}\s*$"
                    rf"|(?:->|\||,)\s*{state}\b|\b{state}\s*->)",
                    text, re.M)
                if hits:
                    rel = path.relative_to(ROOT)
                    findings.append(
                        f"LINT-12 {rel}: retired state name {state!r} still used "
                        f"({len(hits)} occurrence(s)) — not in spec/fsm_states_57.yaml"
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

    # --- LINT-13: CI job names must resolve, and gates must not cycle ----------
    spec_md = (ROOT / "build/spec/Evolution_Engine_Active_Spec_10_2_2.md").read_text(encoding="utf-8")
    start = spec_md.find("# 21. CI")
    end = spec_md.find("# 22.", start)
    canonical_jobs = set(re.findall(r"^([a-z][a-z0-9_]{6,})$", spec_md[start:end], re.M))
    canonical_req_ids = set(re.findall(r"\[(?:REQ|IMPL|TEST|EVID)\]\[(REQ-S\d{2}-\d{3})\]", spec_md))
    if not canonical_jobs:
        findings.append("LINT-13 could not read the job list from Active Contract section 21")

    ci = yaml.safe_load((ROOT / "tools/ci_matrix.yaml").read_text(encoding="utf-8"))
    ci_jobs = {j for stage in ci["stages"] for j in stage["jobs"]}
    for job in sorted(ci_jobs - canonical_jobs):
        findings.append(f"LINT-13 tools/ci_matrix.yaml: job {job!r} is not declared in section 21")
    for job in sorted(canonical_jobs - ci_jobs):
        findings.append(f"LINT-13 tools/ci_matrix.yaml: job {job!r} from section 21 is in no stage")
    if ci.get("total_pipeline_jobs") != len(ci_jobs):
        findings.append(
            f"LINT-13 tools/ci_matrix.yaml: total_pipeline_jobs={ci.get('total_pipeline_jobs')} "
            f"but {len(ci_jobs)} jobs are listed"
        )

    gates = yaml.safe_load((ROOT / "spec/release_gates.yaml").read_text(encoding="utf-8"))["release_gates"]
    ladder = yaml.safe_load((ROOT / "spec/maturity.yaml").read_text(encoding="utf-8"))["maturity_ladder"]
    level_index = {m["level"]: i for i, m in enumerate(ladder)}
    gate_min = {g["name"]: g["minimum_maturity"] for g in gates}
    for gate in gates:
        for check in gate["mandatory_checks"]:
            if check not in canonical_jobs:
                findings.append(
                    f"LINT-13 spec/release_gates.yaml: {gate['name']} requires check {check!r}, "
                    f"which is not a job in section 21"
                )
        if gate["minimum_maturity"] not in level_index:
            findings.append(
                f"LINT-13 spec/release_gates.yaml: {gate['name']} minimum_maturity "
                f"{gate['minimum_maturity']!r} is not a level in spec/maturity.yaml"
            )
        for pre in gate.get("prerequisites", []):
            if pre not in gate_min:
                findings.append(f"LINT-13 {gate['name']}: unknown prerequisite {pre!r}")
            elif level_index.get(gate_min[pre], -1) > level_index.get(gate["minimum_maturity"], -1):
                findings.append(
                    f"LINT-13 {gate['name']} needs {gate['minimum_maturity']} but its prerequisite "
                    f"{pre} needs {gate_min[pre]} — a gate cannot require a level above its own"
                )
        # the level a gate unlocks must not be the level it demands
        for m in ladder:
            gate_words = gate["name"].replace("GATE_", "").lower().split("_")
            if all(w in m["gate"].lower() or w in m["name"].lower() for w in gate_words):
                if m["level"] == gate["minimum_maturity"]:
                    findings.append(
                        f"LINT-13 circular: {gate['name']} requires {m['level']} while "
                        f"{m['level']} is defined by passing {gate['name']}"
                    )

    # --- LINT-14: declared counts must equal real counts -----------------------
    manifest_counts = yaml.safe_load(
        (ROOT / "spec/version_manifest.yaml").read_text(encoding="utf-8"))["subsystems"]
    protocols_doc = (ROOT / "docs/07_schemas_and_protocols/TYPED_PROTOCOLS_22.md").read_text(encoding="utf-8")
    corpus_cases = yaml.safe_load(
        (ROOT / "benchmarks/golden/manifest.yaml").read_text(encoding="utf-8"))["cases"]
    linters = yaml.safe_load((ROOT / "tools/spec_linters.yaml").read_text(encoding="utf-8"))
    ddl_sql = sql_blocks(ROOT / "docs/03_storage_and_database/SQLITE_DDL_29_TABLES.md")

    actual = {
        "schemas_count": len(list((ROOT / "schemas").glob("*.json"))),
        "protocols_count": len(set(re.findall(r"class ([A-Z]\w+)\(Protocol\)", protocols_doc))),
        "sqlite_tables_count": len(re.findall(r"CREATE TABLE", ddl_sql)),
        "sqlite_indices_count": len(re.findall(r"CREATE (?:UNIQUE )?INDEX", ddl_sql)),
        "fsm_count": len(fsms),
        "total_fsm_states": sum(len(f["states"]) for f in fsms.values()),
        "golden_corpus_cases": len(corpus_cases),
        "requirement_ids_count": len(canonical_req_ids),
        "ci_jobs_count": len(canonical_jobs),
        "spec_linters_count": linters["total_linters"],
    }
    for key, real in actual.items():
        declared = manifest_counts.get(key)
        if declared is None:
            findings.append(f"LINT-14 spec/version_manifest.yaml: missing count {key!r} (actual {real})")
        elif declared != real:
            findings.append(
                f"LINT-14 spec/version_manifest.yaml: {key} declares {declared} but {real} exist"
            )
    if len(linters["linters"]) != linters["total_linters"]:
        findings.append(
            f"LINT-14 tools/spec_linters.yaml: total_linters={linters['total_linters']} "
            f"but {len(linters['linters'])} are defined"
        )
    trace = yaml.safe_load((ROOT / "spec/traceability.yaml").read_text(encoding="utf-8"))
    if trace["total_requirements"] != len(trace["requirements"]):
        findings.append(
            f"LINT-14 spec/traceability.yaml: total_requirements={trace['total_requirements']} "
            f"but {len(trace['requirements'])} entries"
        )
    if len(trace["requirements"]) != len(canonical_req_ids):
        findings.append(
            f"LINT-14 spec/traceability.yaml has {len(trace['requirements'])} entries but the "
            f"Active Contract declares {len(canonical_req_ids)} requirements"
        )

    # --- LINT-15: documented config examples must validate ---------------------
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        findings.append("LINT-15 skipped: jsonschema is not installed")
    else:
        cfg_schema = json.loads((ROOT / "schemas/26_engine_config.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cfg_schema)
        validator = Draft202012Validator(cfg_schema)
        sources = sorted(ROOT.glob("docs/**/*.md")) + sorted(ROOT.glob("*.md"))
        sources.append(ROOT / "build/spec/Evolution_Engine_Active_Spec_10_2_2.md")
        checked = 0
        for path in sources:
            for block in re.findall(r"```yaml\n(.*?)```", path.read_text(encoding="utf-8"), re.S):
                try:
                    doc = yaml.safe_load(block)
                except yaml.YAMLError:
                    continue
                if not isinstance(doc, dict) or "evolution" not in doc or "sandbox" not in doc:
                    continue
                checked += 1
                for err in validator.iter_errors(doc):
                    where = "/" + "/".join(str(x) for x in err.path)
                    findings.append(
                        f"LINT-15 {path.relative_to(ROOT)}: config example fails "
                        f"26_engine_config.schema.json at {where}: {err.message}"
                    )
        if checked == 0:
            findings.append("LINT-15 found no evolution.yaml example to validate")

    if findings:
        print(f"BLOCKER: {len(findings)} finding(s)\n")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("LINT-09..15: PASS — vocabularies agree, evidence is retention-safe, corpus matches manifest, CI job names resolve, declared counts are real, config examples validate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
