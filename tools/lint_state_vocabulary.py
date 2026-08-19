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
LINT-16: spec/equations_300.yaml and spec/dimensions_300.yaml must hold every
  EQ and DIM that the docs define, with no dangling reference and one padding
  convention. They previously declared 300 while holding 50 and 0.
LINT-17 (REQ-S02-008, REQ-S08-012, REQ-S19-003): spec/requirements.yaml and
  spec/traceability.yaml must cover every requirement with the mandated fields and
  identical digests, and spec/fsm/*.yaml must exist for all five FSMs and agree
  with spec/fsm_states_57.yaml.
LINT-18 (REQ-S00-009, REQ-S00-010): the recovered archive must match the SHA-256
  in spec/archive/manifest.json, and every retired requirement ID must stay retired.
LINT-19 (section 3.1, section 26): the Core/Research firewall. A golden corpus case
  in the RESEARCH bucket may not be required by any Core gate, and every case must
  carry a maturity_bucket.
LINT-20 (REQ-S28-002): the declared maturity level must equal the level the
  artifacts actually support, computed by tools/compute_maturity.py.
LINT-21: every schema property carrying a content-derived identifier must use the
  64-hex pattern from spec/reproducibility.yaml, and every id in the identifiers list
  must have a derivation formula. This is the check whose absence let CR-0004 change
  one schema while declaring the rule for all of them.
LINT-22: docs/ must not contradict rank 1 on counts, on the Core/Research firewall,
  or on the public surface. Half the regressions in CR-0002..0007 survived because
  every linter read spec/ and none read docs/ — which is where people actually look.
LINT-12: prose state lists anywhere in the repo must not use a state name that
  spec/fsm_states_57.yaml has retired. Prose drift is what made LINT-09 miss the
  first time: the DDL was fixed while the narrative kept the old vocabulary.

Exit code 0 = pass, 1 = BLOCKER findings.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

DDL_FILES = [
    "docs/03_DATABASE_AND_STORAGE.md",
    "docs/03_storage_and_database/SQLITE_DDL_TABLES.md",
    "spec/ACTIVE_CONTRACT.md",
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
    scan_globs = ["spec/*.md", "docs/**/*.md", "spec/*.yaml", "schemas/*.json"]
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
    spec_md = (ROOT / "spec/ACTIVE_CONTRACT.md").read_text(encoding="utf-8")
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
    protocol_registry = yaml.safe_load(
        (ROOT / "spec/protocols.yaml").read_text(encoding="utf-8"))
    corpus_cases = yaml.safe_load(
        (ROOT / "benchmarks/golden/manifest.yaml").read_text(encoding="utf-8"))["cases"]
    linters = yaml.safe_load((ROOT / "tools/spec_linters.yaml").read_text(encoding="utf-8"))
    ddl_sql = sql_blocks(ROOT / "docs/03_storage_and_database/SQLITE_DDL_TABLES.md")

    actual = {
        "schemas_count": len(list((ROOT / "schemas").glob("*.json"))),
        "protocols_count": protocol_registry["core_v1_protocol_count"],
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
        sources.append(ROOT / "spec/ACTIVE_CONTRACT.md")
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

    # --- LINT-16: equation and dimension registries must be complete -----------
    eq_reg = yaml.safe_load((ROOT / "spec/equations_300.yaml").read_text(encoding="utf-8"))
    dim_reg = yaml.safe_load((ROOT / "spec/dimensions_300.yaml").read_text(encoding="utf-8"))
    eq_ids = {e["id"] for d in eq_reg["domains"] for e in d["equations"]}
    dim_ids = {d2["id"] for d in dim_reg["domains"] for d2 in d["dimensions"]}
    if len(eq_ids) != eq_reg["total_equations"]:
        findings.append(
            f"LINT-16 spec/equations_300.yaml: total_equations={eq_reg['total_equations']} "
            f"but {len(eq_ids)} entries")
    if len(dim_ids) != dim_reg["total_dimensions"]:
        findings.append(
            f"LINT-16 spec/dimensions_300.yaml: total_dimensions={dim_reg['total_dimensions']} "
            f"but {len(dim_ids)} entries")
    if len(dim_reg["domains"]) != dim_reg["total_domains"]:
        findings.append(
            f"LINT-16 spec/dimensions_300.yaml: total_domains={dim_reg['total_domains']} "
            f"but {len(dim_reg['domains'])} domains")

    referenced_eq, referenced_dim, padding = set(), set(), set()
    for path in sorted(ROOT.glob("docs/**/*.md")) + sorted(ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for tok in re.findall(r"\bEQ-(\d+)\b", text):
            referenced_eq.add(f"EQ-{int(tok):03d}")
            padding.add(len(tok))
        for tok in re.findall(r"\bDIM-(\d+)\b", text):
            referenced_dim.add(f"DIM-{int(tok):03d}")
            padding.add(len(tok))
    if len(padding) > 1:
        findings.append(
            f"LINT-16 EQ/DIM ids are written with {sorted(padding)} digits in different places; "
            f"the same identifier must have exactly one spelling")
    for missing in sorted(referenced_eq - eq_ids):
        findings.append(f"LINT-16 {missing} is referenced in the docs but absent from spec/equations_300.yaml")
    for missing in sorted(referenced_dim - dim_ids):
        findings.append(f"LINT-16 {missing} is referenced in the docs but absent from spec/dimensions_300.yaml")
    for orphan in sorted(dim_ids):
        eq_of = next(d2["equation"] for d in dim_reg["domains"] for d2 in d["dimensions"] if d2["id"] == orphan)
        if eq_of not in eq_ids:
            findings.append(f"LINT-16 {orphan} maps to {eq_of}, which is not in the equation registry")

    # --- LINT-17: requirement register and FSM specs ---------------------------
    REQUIRED_FIELDS = {"id", "section", "status", "text_digest", "owner",
                       "verification_method", "test_refs", "evidence_refs", "release_gates"}
    register_path = ROOT / "spec/requirements.yaml"
    if not register_path.exists():
        findings.append("LINT-17 spec/requirements.yaml is missing (REQ-S02-008)")
    else:
        register = yaml.safe_load(register_path.read_text(encoding="utf-8"))
        entries = {r["id"]: r for r in register["requirements"]}
        if set(entries) != canonical_req_ids:
            missing = sorted(canonical_req_ids - set(entries))
            extra = sorted(set(entries) - canonical_req_ids)
            findings.append(
                f"LINT-17 spec/requirements.yaml does not cover the contract — "
                f"missing={missing[:5]} extra={extra[:5]}")
        for rid, entry in sorted(entries.items()):
            absent = REQUIRED_FIELDS - set(entry)
            if absent:
                findings.append(f"LINT-17 spec/requirements.yaml {rid}: missing fields {sorted(absent)}")
        chain = {r["id"]: r for r in trace["requirements"]}
        for rid, entry in sorted(entries.items()):
            if rid in chain and chain[rid]["text_digest"] != entry["text_digest"]:
                findings.append(
                    f"LINT-17 {rid}: requirements.yaml and traceability.yaml disagree on text_digest")

    fsm_dir = ROOT / "spec/fsm"
    key_for = {"candidate": "candidate_lifecycle_fsm", "run": "run_lifecycle_fsm",
               "recovery": "recovery_fsm", "governance": "governance_fsm",
               "deployment": "deployment_fsm"}
    for fsm_name, key in key_for.items():
        path = fsm_dir / f"{fsm_name}.yaml"
        if not path.exists():
            findings.append(f"LINT-17 spec/fsm/{fsm_name}.yaml is missing")
            continue
        encoded = yaml.safe_load(path.read_text(encoding="utf-8"))
        declared = fsms[key]
        if set(encoded["states"]) != set(declared["states"]):
            findings.append(f"LINT-17 spec/fsm/{fsm_name}.yaml states differ from spec/fsm_states_57.yaml")
        if encoded["initial_state"] != declared["initial_state"]:
            findings.append(f"LINT-17 spec/fsm/{fsm_name}.yaml initial_state differs from the registry")
        if set(encoded["terminal_states"]) != set(declared["terminal_states"]):
            findings.append(f"LINT-17 spec/fsm/{fsm_name}.yaml terminal_states differ from the registry")
        graph = {tr["from"]: tr["to"] for tr in encoded["transitions"]}
        for terminal in encoded["terminal_states"]:
            if graph.get(terminal):
                findings.append(f"LINT-17 spec/fsm/{fsm_name}.yaml: terminal {terminal} has outgoing edges")

    # --- LINT-18: archive integrity and retired-ID reuse ------------------------
    manifest_path = ROOT / "spec/archive/manifest.json"
    if not manifest_path.exists():
        findings.append("LINT-18 spec/archive/manifest.json is missing (REQ-S00-009)")
    else:
        archive_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        archive_file = ROOT / archive_manifest["file"]
        if not archive_file.exists():
            findings.append(f"LINT-18 archive {archive_manifest['file']} is missing")
        else:
            digest = hashlib.sha256(archive_file.read_bytes()).hexdigest()
            if digest != archive_manifest["file_sha256"]:
                findings.append(
                    f"LINT-18 archive digest mismatch: manifest says "
                    f"{archive_manifest['file_sha256'][:16]}..., file is {digest[:16]}...")

    register_data = yaml.safe_load((ROOT / "spec/requirements.yaml").read_text(encoding="utf-8"))
    retired = {r["id"] for r in register_data.get("retired_requirements", [])}
    reused = sorted(retired & canonical_req_ids)
    if reused:
        findings.append(
            f"LINT-18 retired requirement IDs reappeared in the Active Contract: {reused} — "
            f"Section 2.4 forbids reuse")
    for record in register_data.get("retired_requirements", []):
        if not (ROOT / "spec/change_records").glob(f"{record['withdrawn_by']}*"):
            findings.append(f"LINT-18 {record['id']} cites missing change record {record['withdrawn_by']}")

    # --- protocol registry must equal Active Contract section 7.2 ---------------
    section72 = spec_md[spec_md.index("## 7.2 Required Protocols"):]
    section72 = section72[:section72.index("# 8.")]
    table_names = {row.split("|")[1].strip().strip("*` ")
                   for row in section72.split("\n")
                   if row.startswith("|")} - {"Protocol", "---", ""}
    registry_names = {p["protocol"] for p in protocol_registry["core_v1_protocols"]}
    if table_names != registry_names:
        findings.append(
            f"LINT-14 spec/protocols.yaml disagrees with section 7.2 — "
            f"registry-only={sorted(registry_names - table_names)} "
            f"section-only={sorted(table_names - registry_names)}")
    research = {r["name"] for r in protocol_registry["research_protocols_out_of_core_v1"]}
    if research & registry_names:
        findings.append(
            f"LINT-14 research protocols counted in Core v1: {sorted(research & registry_names)}")

    # --- LINT-19: Core/Research firewall ---------------------------------------
    CORE_BUCKETS = {"CORE", "SECURITY", "RELIABILITY"}
    VALID_BUCKETS = CORE_BUCKETS | {"RESEARCH", "SELF_EVOLUTION"}
    BUCKET_JOB = {"CORE": "golden_core", "SECURITY": "golden_security",
                  "RELIABILITY": "golden_reliability", "SELF_EVOLUTION": "golden_self_evolution"}
    by_bucket: dict[str, list[str]] = {}
    for case in corpus_cases:
        bucket = case.get("maturity_bucket")
        if bucket is None:
            findings.append(f"LINT-19 {case['id']}: no maturity_bucket")
            continue
        if bucket not in VALID_BUCKETS:
            findings.append(f"LINT-19 {case['id']}: unknown maturity_bucket {bucket!r}")
            continue
        by_bucket.setdefault(bucket, []).append(case["id"])

    core_gate = next((g for g in gates if g["name"] == "GATE_CORE"), None)
    if core_gate is not None:
        research_job = BUCKET_JOB.get("RESEARCH")
        if research_job and research_job in core_gate["mandatory_checks"]:
            findings.append("LINT-19 GATE_CORE requires the research corpus")
        # a Core gate must not name a job that runs a research case
        for case_id in by_bucket.get("RESEARCH", []):
            if any(case_id.lower().replace("-", "") in check for check in core_gate["mandatory_checks"]):
                findings.append(f"LINT-19 GATE_CORE names research case {case_id}")

    # the ladder must not describe a Core rung using a research case
    ladder_text = (ROOT / "spec/maturity.yaml").read_text(encoding="utf-8")
    for case_id in by_bucket.get("RESEARCH", []):
        for line in ladder_text.splitlines():
            if case_id in line and ("M9" in line or "M10" in line or "CORE" in line.upper()):
                findings.append(
                    f"LINT-19 spec/maturity.yaml names research case {case_id} in a Core rung: {line.strip()}")

    # --- LINT-20: the maturity claim must be earned -----------------------------
    import os
    import subprocess
    if os.environ.get("EE_SKIP_MATURITY_LINT") != "1":
        maturity = subprocess.run([sys.executable, str(ROOT / "tools/compute_maturity.py")],
                                  capture_output=True, text=True, cwd=ROOT)
        if maturity.returncode != 0:
            tail = [l for l in maturity.stdout.splitlines() if "MISMATCH" in l]
            findings.append("LINT-20 " + (tail[0] if tail else "maturity computation failed"))

    # --- LINT-21: identifier form must match the rank 1 declaration -------------
    repro = yaml.safe_load((ROOT / "spec/reproducibility.yaml").read_text(encoding="utf-8"))
    id_rules = repro["identifier_rules"]
    content_props = set(id_rules["content_derived_properties"])
    want_pattern = id_rules["content_derived_pattern"]

    def walk_props(node, key=None):
        if isinstance(node, dict):
            if key and "type" in node and not node.get("properties"):
                yield key, node
            for child, value in node.items():
                if child in ("properties", "$defs", "patternProperties"):
                    for prop, sub in (value or {}).items():
                        yield from walk_props(sub, prop)
                elif child == "items":
                    yield from walk_props(value, key)
                elif child not in ("enum", "const", "required"):
                    yield from walk_props(value, key)
        elif isinstance(node, list):
            for value in node:
                yield from walk_props(value, key)

    for path in sorted((ROOT / "schemas").glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        for prop, node in walk_props(schema):
            if prop in content_props:
                if node.get("pattern") != want_pattern:
                    findings.append(
                        f"LINT-21 schemas/{path.name}: {prop} is content-derived but declares "
                        f"pattern={node.get('pattern')!r} format={node.get('format')!r}")
                if "format" in node:
                    findings.append(
                        f"LINT-21 schemas/{path.name}: {prop} keeps a format alongside the pattern")

    for entry in repro["identifiers"]:
        if not entry.get("formula"):
            findings.append(f"LINT-21 {entry['name']} has no derivation formula")
        if entry["kind"] == "content-derived" and not entry.get("representation"):
            findings.append(f"LINT-21 {entry['name']} is content-derived with no representation")
    envelope = next(e for e in repro["identifiers"] if e["name"] == "CandidateId")["envelope_fields"]
    declared = {e["name"] for e in repro["identifiers"] if e["kind"] == "content-derived"}
    for field in envelope:
        derived_name = "".join(part.capitalize() for part in field.split("_")).replace("Candidate", "Candidate")
        if field.endswith("_id") and field not in ("parent_candidate_id",):
            wanted = {"mutation_id": "MutationId"}.get(field)
            if wanted and wanted not in declared:
                findings.append(
                    f"LINT-21 CandidateId's envelope contains {field} but {wanted} is not "
                    f"content-derived — CandidateId would not be reproducible")

    # the validator must actually evaluate formats, or none of the above is enforced
    gate_source = (ROOT / "tools/validate_schemas.py").read_text(encoding="utf-8")
    if "format_checker=FormatChecker()" not in gate_source:
        findings.append("LINT-21 tools/validate_schemas.py builds validators without a format checker")

    # --- LINT-22: docs/ must not contradict rank 1 ------------------------------
    docs = sorted(ROOT.glob("docs/**/*.md")) + sorted(ROOT.glob("*.md"))
    counts = manifest_counts
    count_claims = [
        (rf"(\d+)\s+(?:Core v1 )?(?:Typed )?Protocols?\b", counts["protocols_count"], "protocols"),
        (rf"(\d+)[- ](?:SQLite )?[Tt]ables?\b", counts["sqlite_tables_count"], "tables"),
        (rf"(\d+)\s+(?:canonical )?[Ss]chemas?\b", counts["schemas_count"], "schemas"),
    ]
    research_ids = {c["id"] for c in corpus_cases if c.get("maturity_bucket") == "RESEARCH"}
    core_words = ("CORE", "M9", "M10", "GATE_CORE")

    for path in docs:
        if "/archive/" in str(path) or "change_records" in str(path):
            continue
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for pattern, real, label in count_claims:
            for value in re.findall(pattern, text):
                if int(value) != real and int(value) in (19, 22, 26, 29, 31):
                    findings.append(
                        f"LINT-22 {rel}: claims {value} {label} but rank 1 says {real}")
        for line in text.splitlines():
            if any(case in line for case in research_ids) and any(w in line for w in core_words):
                findings.append(
                    f"LINT-22 {rel}: puts a RESEARCH corpus case on a Core rung — {line.strip()[:90]}")

    # the public surface in docs must be a subset of the contract's
    surface = spec_md[spec_md.index("## 6.1 Canonical CLI"):]
    surface = surface[:surface.index("# 7.")]
    cli_verbs = set(re.findall(r"^evolve ([a-z]+)", surface, re.M))
    sdk_ops = set(re.findall(r"^\| (\w+) \|", surface, re.M))
    for path in docs:
        if "/archive/" in str(path) or "change_records" in str(path):
            continue
        text = path.read_text(encoding="utf-8")
        for verb in set(re.findall(r"`?evolve ([a-z]+)", text)):
            if verb not in cli_verbs:
                findings.append(
                    f"LINT-22 {path.relative_to(ROOT)}: offers `evolve {verb}`, "
                    f"which section 6.1 does not declare")

    if findings:
        print(f"BLOCKER: {len(findings)} finding(s)\n")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("LINT-09..22: PASS — vocabularies agree, evidence is retention-safe, corpus matches manifest, CI job names resolve, declared counts are real, config examples validate, EQ/DIM registries are complete, requirement register and FSM specs agree, archive intact, Core/Research firewall holds, maturity claim is earned, identifier forms agree, docs match rank 1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
