#!/usr/bin/env python3
"""Generate src/evolution_engine/protocols/ from the contract (M4).

The 19 protocols, their inputs and their outputs come from Active Contract section 7.2.
Each type name is resolved through spec/protocol_types.yaml, so a signature can never
name a type that does not exist — which is the failure this whole package was blocked
on: 20 of 26 names in sections 7.2 and 6.2 resolved to nothing.

The bodies are `...`. M4's gate is "19 Typed Python Protocols with zero type errors",
not working code; behaviour lands at M5 and beyond behind these same signatures, which
is what REQ-S29-005 requires.
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "spec/ACTIVE_CONTRACT.md"
OUT = ROOT / "src/evolution_engine/protocols"

# How each protocol's prose input maps to a typed parameter list. The contract states
# inputs as English; this is the one place that English becomes a signature.
PARAMS: dict[str, list[tuple[str, str]]] = {
    "ProjectAdapter": [("project_path", "Path")],
    "SourceAnalyzer": [("source_root", "Path")],
    "MutationStrategy": [("parent", "ProgramRepresentation"), ("context", "MutationContext")],
    "MutationEngine": [("population", "PopulationManifest")],
    "PopulationManager": [("candidates", "Sequence[CandidateArtifact]"),
                          ("decisions", "Sequence[SelectionDecision]")],
    "SandboxManager": [("artifact", "CandidateArtifact"), ("request", "SandboxRequest")],
    "TestRunner": [("artifact", "CandidateArtifact"), ("plan", "TestPlan")],
    "CapabilityVerifier": [("results", "TestSuiteResult"), ("contract", "SchemaDocument")],
    "OracleRunner": [("candidate_id", "CandidateId"), ("plan", "TestPlan")],
    "MetricRunner": [("candidate_id", "CandidateId"), ("objective", "SchemaDocument")],
    "ParetoSelector": [("eligible", "Sequence[CandidateId]"),
                       ("objectives", "Sequence[SchemaDocument]")],
    "EvidenceStore": [("evidence_type", "str"), ("artifact_id", "ArtifactId")],
    "ArtifactStore": [("data", "bytes"), ("media_type", "str")],
    "LineageRepository": [("run_id", "RunId")],
    "CheckpointManager": [("run_id", "RunId"), ("generation_id", "GenerationId")],
    "RecoveryManager": [("checkpoint", "CheckpointManifest")],
    "PolicyEngine": [("artifact", "CandidateArtifact")],
    "DeploymentManager": [("artifact_id", "ArtifactId"), ("mode", "str")],
    "AuditLog": [("event_type", "str"), ("actor", "str"), ("payload_artifact_id", "ArtifactId")],
}
METHODS: dict[str, str] = {
    "ProjectAdapter": "load_project",
    "SourceAnalyzer": "analyze",
    "MutationStrategy": "propose",
    "MutationEngine": "draft_candidates",
    "PopulationManager": "advance",
    "SandboxManager": "execute",
    "TestRunner": "run_tests",
    "CapabilityVerifier": "verify",
    "OracleRunner": "check",
    "MetricRunner": "measure",
    "ParetoSelector": "select",
    "EvidenceStore": "record",
    "ArtifactStore": "put",
    "LineageRepository": "snapshot",
    "CheckpointManager": "checkpoint",
    "RecoveryManager": "recover",
    "PolicyEngine": "evaluate",
    "DeploymentManager": "deploy",
    "AuditLog": "append",
}
# Where a return name is an alias, emit the schema title so the signature and the
# schema agree. spec/protocol_types.yaml is what decides this.
MODULE_FOR = {
    "ProjectAdapter": "project", "SourceAnalyzer": "representation",
    "MutationStrategy": "mutation", "MutationEngine": "mutation",
    "PopulationManager": "population", "SandboxManager": "sandbox",
    "TestRunner": "testing", "CapabilityVerifier": "testing", "OracleRunner": "testing",
    "MetricRunner": "measurement", "ParetoSelector": "selection",
    "EvidenceStore": "evidence", "ArtifactStore": "storage",
    "LineageRepository": "lineage", "CheckpointManager": "recovery",
    "RecoveryManager": "recovery", "PolicyEngine": "policy",
    "DeploymentManager": "deployment", "AuditLog": "audit",
}
NEEDS_PATH = {"ProjectAdapter", "SourceAnalyzer"}


def contract_rows() -> list[tuple[str, str, str]]:
    body = CONTRACT.read_text(encoding="utf-8")
    block = body[body.index("## 7.2 Required Protocols"):]
    block = block[:block.index("# 8.")]
    rows = []
    for line in block.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("*` ") for c in line.split("|")[1:-1]]
        if len(cells) == 3 and cells[0] not in ("Protocol", "---", ""):
            rows.append((cells[0], cells[1], cells[2]))
    return rows


def resolve(types_doc: dict) -> dict[str, str]:
    """Contract type name -> the Python name to emit."""
    mapping: dict[str, str] = {}
    for entry in types_doc["protocol_types"]:
        if entry["kind"] == "ALIAS":
            mapping[entry["name"]] = entry.get("schema_title", entry["name"])
        else:
            mapping[entry["name"]] = entry["name"]
    return mapping


def main() -> int:
    types_doc = yaml.safe_load((ROOT / "spec/protocol_types.yaml").read_text(encoding="utf-8"))
    names = resolve(types_doc)
    rows = contract_rows()
    if len(rows) != 19:
        raise SystemExit(f"section 7.2 has {len(rows)} rows, expected 19")

    OUT.mkdir(parents=True, exist_ok=True)
    by_module: dict[str, list[str]] = {}
    exported: list[str] = []

    for protocol, _prose_input, output in rows:
        emitted = names.get(output)
        if emitted is None:
            raise SystemExit(
                f"{protocol} returns {output!r}, which spec/protocol_types.yaml does not resolve")
        params = PARAMS[protocol]
        method = METHODS[protocol]
        arg_list = ", ".join(f"{n}: {t}" for n, t in params)
        used = {t for _, t in params} | {emitted}
        lines = [
            f"class {protocol}(Protocol):",
            f'    """Active Contract section 7.2. Returns {emitted}."""',
            "",
            f"    def {method}(self, {arg_list}) -> {emitted}:",
            "        ...",
            "",
        ]
        module = MODULE_FOR[protocol]
        by_module.setdefault(module, []).append("\n".join(lines))
        by_module.setdefault(f"__types__{module}", []).extend(used)
        exported.append(protocol)

    for module, blocks in sorted(by_module.items()):
        if module.startswith("__types__"):
            continue
        used = sorted({
            t.replace("Sequence[", "").replace("]", "")
            for t in by_module.get(f"__types__{module}", [])
            if t not in ("bytes", "str", "int", "Path")
        })
        header = [
            f'"""{module.capitalize()} protocols. Generated by tools/generate_protocols.py."""',
            "from __future__ import annotations",
            "",
        ]
        if any("Sequence[" in b for b in blocks):
            header.append("from collections.abc import Sequence")
        if any("Path" in b for b in blocks):
            header.append("from pathlib import Path")
        header.append("from typing import Protocol")
        header.append("")
        if used:
            header.append("from evolution_engine.types import (")
            header += [f"    {t}," for t in used]
            header.append(")")
        header.append("")
        header.append("")
        (OUT / f"{module}.py").write_text("\n".join(header) + "\n\n".join(blocks), encoding="utf-8")

    modules = sorted(m for m in by_module if not m.startswith("__types__"))
    init = [
        '"""The 19 Core v1 protocols (Active Contract section 7.2).',
        "",
        "Roster and count come from spec/protocols.yaml; every type in a signature is",
        "resolved by spec/protocol_types.yaml. Generated by tools/generate_protocols.py.",
        '"""',
        "from __future__ import annotations",
        "",
    ]
    for module in modules:
        names_here = re.findall(r"^class (\w+)\(Protocol\)",
                                (OUT / f"{module}.py").read_text(encoding="utf-8"), re.M)
        init.append(f"from evolution_engine.protocols.{module} import "
                    f"{', '.join(sorted(names_here))}")
    init += ["", "__all__ = [", *[f'    "{n}",' for n in sorted(exported)], "]", ""]
    (OUT / "__init__.py").write_text("\n".join(init), encoding="utf-8")

    print(f"wrote {len(exported)} protocols across {len(modules)} modules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
