# Exact 26 JSON Schema Registry Blueprint

> **Subsystem:** Data Contracts (JSON Schema Draft 2020-12)  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S06-001`, `REQ-S06-002`

---

## 1. Schema Invariants & Standard Headers

ทุกไฟล์ใน `schemas/*.schema.json` ต้องมี Header และ Invariants ดังนี้:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://evolution-engine.org/schemas/<schema_name>.json",
  "type": "object",
  "additionalProperties": false
}
```

---

## 2. Complete 26 Schemas Specification Matrix

```text
┌────┬──────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ No │ Schema Filename                  │ Required Fields & Invariants                                │
├────┼──────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 01 │ candidate.schema.json            │ candidate_id, generation_id, source_hash, candidate_state   │
│ 02 │ candidate_state.schema.json      │ enum of 17 valid candidate states                           │
│ 03 │ mutation.schema.json             │ mutation_id, strategy_id, parent_candidate_id, seed         │
│ 04 │ mutation_result.schema.json      │ mutation_attempt_id, status, source_before_hash, delta      │
│ 05 │ population.schema.json           │ generation_id, memberships array                            │
│ 06 │ generation.schema.json           │ generation_id, run_id, generation_index, status             │
│ 07 │ run.schema.json                  │ run_id, project_id, config_hash, policy_hash, run_state     │
│ 08 │ baseline.schema.json             │ project_id, source_hash, metric_measurements, measured_at   │
│ 09 │ project_manifest.schema.json     │ project_id, name, language, project_version, source_root   │
│ 10 │ capability_contract.schema.json  │ capability_id, project_id, required, definition_hash        │
│ 11 │ objective.schema.json            │ name, direction, unit, valid_range, practical_margin_decimal│
│ 12 │ metric_result.schema.json        │ metric_result_id, candidate_id, objective_id, estimate_dec │
│ 13 │ oracle_result.schema.json        │ oracle_result_id, candidate_id, oracle_version, verdict     │
│ 14 │ environment.schema.json          │ environment_hash, os_name, kernel_version, cpu_arch, python │
│ 15 │ lineage_node.schema.json         │ candidate_id, generation_index, artifact_hash               │
│ 16 │ lineage_edge.schema.json         │ parent_candidate_id, child_candidate_id, relationship       │
│ 17 │ selection_decision.schema.json   │ generation_id, candidate_id, decision, reason_code          │
│ 18 │ policy_snapshot.schema.json      │ policy_snapshot_id, run_id, policy_version, policy_hash     │
│ 19 │ provenance_certificate.schema.json│ certificate_id, candidate_id, root_source_hash, signature   │
│ 20 │ reproducibility_certificate.json │ reproducibility_level, seed, replay_run_id, hash_matches    │
│ 21 │ checkpoint.schema.json           │ checkpoint_id, run_id, generation_id, manifest_artifact_id  │
│ 22 │ recovery_manifest.schema.json    │ recovery_id, run_id, recovery_status, resumed_state         │
│ 23 │ release_gate.schema.json         │ gate_name, maturity_level_verified, decision, evidence_dig  │
│ 24 │ quarantine_record.schema.json    │ quarantine_record_id, candidate_id, reason_code, evidence   │
│ 25 │ memory_record.schema.json        │ memory_id, ast_pattern_hash, reward_score_decimal           │
│ 26 │ engine_config.schema.json        │ project, evolution, metrics, selection, sandbox, deployment,│
└────┴──────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```
