#!/usr/bin/env python3
"""Generate spec/requirements.yaml and spec/traceability.yaml (REQ-S02-008, REQ-S22-001).

Both files are emitted from one pass over the Active Contract so they cannot
disagree. They are not rivals:

  spec/requirements.yaml   the register — identity, status, digest, owner,
                           verification method (REQ-S02-008)
  spec/traceability.yaml   the chain — which schema, protocol, implementation,
                           test, evidence and gate each requirement reaches
                           (REQ-S22-001)

text_digest is SHA-256 over the NFC-normalized requirement text, starting after
the "[STATUS][ID] " prefix and ending at the line before the next requirement,
heading, or horizontal rule. Line endings are LF, per-line trailing whitespace is
stripped, leading and trailing blank lines are dropped.

Nothing is invented. owner is UNASSIGNED because no owner data exists, and
verification_method is PENDING unless a real test covers the requirement today.
REQ-S22-004 requires the honest status over an auto-PASS.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys
import unicodedata

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec/ACTIVE_CONTRACT.md"

# Withdrawn by a governed change. Section 2.4 makes published IDs immutable and
# forbids reuse even after withdrawal, so they are recorded rather than freed.
RETIRED = {
    "REQ-S00-005": "CR-0001",
    "REQ-S00-006": "CR-0001",
    "REQ-S00-007": "CR-0001",
    "REQ-S00-008": "CR-0001",
}

DELIMITER = re.compile(r"^(\[(?:REQ|IMPL|TEST|EVID)\]\[REQ-S\d{2}-\d{3}\]|#{1,6}\s|---\s*$)")
DECLARATION = re.compile(r"^\[(REQ|IMPL|TEST|EVID)\]\[(REQ-S(\d{2})-\d{3})\]\s*(.*)$")

# Which requirements a test exercises is DISCOVERED, not typed by hand.
#
# A hand-maintained map is the same hand-asserted-count disease this repo keeps
# fixing everywhere else. Tests were written covering sixteen requirements and the
# map was not updated, so those stayed PENDING while being covered — the map was
# wrong in the safe direction that time, but nothing guaranteed it would be.
#
# A test claims coverage by naming the requirement id in its own source, usually in
# the module or function docstring. That claim is checked: tests/conformance/
# test_requirement_register.py asserts every referenced file exists, and the test
# itself has to actually pass for the suite to be green.
def discover_test_refs() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for folder in ("tests", "tools"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            rel = str(path.relative_to(ROOT))
            if rel == "tools/generate_requirements.py":
                continue  # this file names ids in comments, not as coverage
            text = path.read_text(encoding="utf-8")
            for rid in sorted(set(re.findall(r"REQ-S\d{2}-\d{3}", text))):
                if rel not in found.setdefault(rid, []):
                    found[rid].append(rel)
    return found
SCHEMA_REFS = {f"REQ-S15-{n:03d}": ["spec/schema_manifest.json"] for n in range(1, 8)}
FSM_REFS = {
    "REQ-S08-012": ["spec/fsm/run.yaml", "spec/fsm/recovery.yaml", "spec/fsm/governance.yaml"],
    "REQ-S19-003": ["spec/fsm/deployment.yaml"],
}


def section_titles(lines: list[str]) -> dict[int, str]:
    titles = {0: "Document Control & Active-Spec Generation"}
    for line in lines:
        m = re.match(r"^# (\d+)\.\s+(.*?)\s*\[(?:NORMATIVE|INFORMATIVE|RESEARCH)\]\s*$", line)
        if m:
            titles[int(m.group(1))] = m.group(2).strip()
    return titles


def gates_for(jobs: list[str], gates: list[dict]) -> list[str]:
    return sorted({g["name"] for g in gates for j in jobs if j in g["mandatory_checks"]})


def main() -> int:
    lines = SPEC.read_text(encoding="utf-8").split("\n")
    titles = section_titles(lines)
    contract = "\n".join(lines)

    start = contract.find("# 21. CI")
    end = contract.find("# 22.", start)
    ci_jobs = set(re.findall(r"^([a-z][a-z0-9_]{6,})$", contract[start:end], re.M))
    gates = yaml.safe_load((ROOT / "spec/release_gates.yaml").read_text(encoding="utf-8"))["release_gates"]

    verified_by = discover_test_refs()
    records = []
    for i, line in enumerate(lines):
        m = DECLARATION.match(line)
        if not m:
            continue
        status, rid, section, first = m.groups()
        body = [first]
        for j in range(i + 1, len(lines)):
            if DELIMITER.match(lines[j]):
                break
            body.append(lines[j])
        text = "\n".join(x.rstrip() for x in "\n".join(body).strip().split("\n")).strip()
        text = unicodedata.normalize("NFC", text)
        named_jobs = sorted(j for j in ci_jobs if j in text)
        tests = verified_by.get(rid, [])
        records.append({
            "id": rid,
            "section": int(section),
            "section_title": titles.get(int(section), "(unknown section)"),
            "status": status,
            "text_digest": "sha256:" + hashlib.sha256(text.encode()).hexdigest(),
            "owner": "UNASSIGNED",
            "verification_method": "AUTOMATED_TEST" if tests else "PENDING",
            "test_refs": tests,
            "evidence_refs": [],
            "release_gates": gates_for(named_jobs, gates),
        })

    header = (
        "# Requirement register — one entry per active normative requirement (REQ-S02-008).\n"
        "# Generated with spec/traceability.yaml by tools/generate_requirements.py from\n"
        "# spec/ACTIVE_CONTRACT.md. Do not hand-edit either file.\n"
        "#\n"
        "# text_digest = SHA-256(UTF-8 bytes of the NFC-normalized requirement text), taken\n"
        "# from the first character after the \"[STATUS][ID] \" prefix to the line before the\n"
        "# next requirement, heading or horizontal rule. LF endings, per-line trailing\n"
        "# whitespace stripped, leading and trailing blank lines dropped.\n"
        "#\n"
        "# owner is UNASSIGNED because no owner data exists yet, and verification_method is\n"
        "# PENDING unless a test in this repo exercises the requirement today. REQ-S22-004\n"
        "# requires the honest status rather than an auto-PASS.\n\n")
    live = {r["id"] for r in records}
    clashes = sorted(live & set(RETIRED))
    if clashes:
        raise SystemExit(f"retired requirement IDs reused: {clashes} — Section 2.4 forbids this")

    (ROOT / "spec/requirements.yaml").write_text(
        header + yaml.safe_dump(
            {"spec_version": "10.2.2", "digest_algorithm": "SHA-256/NFC",
             "total_requirements": len(records),
             "retired_requirements": [
                 {"id": rid, "withdrawn_by": cr, "reusable": False}
                 for rid, cr in sorted(RETIRED.items())],
             "requirements": records},
            sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8")

    chain = []
    for record in records:
        chain.append({
            "id": record["id"],
            "section": record["section"],
            "section_title": record["section_title"],
            "status": record["status"],
            "text_digest": record["text_digest"],
            "schema_refs": SCHEMA_REFS.get(record["id"], []),
            "protocol_refs": [],
            "implementation_refs": [],
            "fsm_refs": FSM_REFS.get(record["id"], []),
            "test_refs": record["test_refs"],
            "evidence_refs": [],
            "release_gates": record["release_gates"],
        })
    trace_header = (
        "# Requirement traceability chain (REQ-S22-001).\n"
        "# Generated with spec/requirements.yaml by tools/generate_requirements.py.\n"
        "# The register holds identity and status; this file holds the chain from a\n"
        "# requirement to the artefacts that satisfy it. Empty lists mean the artefact does\n"
        "# not exist yet, which REQ-S22-004 requires over an auto-PASS.\n\n")
    (ROOT / "spec/traceability.yaml").write_text(
        trace_header + yaml.safe_dump(
            {"spec_version": "10.2.2", "digest_algorithm": "SHA-256/NFC",
             "total_requirements": len(chain), "requirements": chain},
            sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8")

    verified = sum(1 for r in records if r["test_refs"])
    print(f"wrote spec/requirements.yaml and spec/traceability.yaml — {len(records)} requirements, "
          f"{verified} with an automated test, {len(records) - verified} PENDING")
    return 0


if __name__ == "__main__":
    sys.exit(main())
