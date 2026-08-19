# CI/CD Pipeline Jobs (39 Required Jobs)

> **Subsystem:** CI/CD Automation & Quality Gate Enforcement  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S02-009`, `REQ-S21-001`


---

> รายชื่อ job เป็น canonical ที่ [`spec/ACTIVE_CONTRACT.md`](../../spec/ACTIVE_CONTRACT.md) section 21
> การจัดกลุ่มเป็น stage อยู่ที่ [`tools/ci_matrix.yaml`](../../tools/ci_matrix.yaml) — ตารางนี้ derive จากสองไฟล์นั้น ห้ามแก้มือ

## Pipeline stages

### `spec_verification` — 8 jobs

| # | Job |
|---|---|
| 1 | `spec_utf8_control_char_lint` |
| 2 | `spec_heading_classification_lint` |
| 3 | `spec_single_active_version_lint` |
| 4 | `spec_no_historical_normative_freeze_lint` |
| 5 | `spec_active_view_byte_match` |
| 6 | `spec_archive_checksum_match` |
| 7 | `spec_requirement_id_unique_and_complete` |
| 8 | `spec_requirement_digest_change_guard` |

### `schema_and_protocol` — 4 jobs

| # | Job |
|---|---|
| 9 | `schema_registry_exact_26` |
| 10 | `schema_meta_validation` |
| 11 | `schema_valid_invalid_vectors` |
| 12 | `protocol_type_check` |

### `fsm_config_and_unit` — 6 jobs

| # | Job |
|---|---|
| 13 | `fsm_reachability_and_terminal_tests` |
| 14 | `config_argv_only_validation` |
| 15 | `config_resolution_precedence_validation` |
| 16 | `config_decimal_and_weight_semantics` |
| 17 | `vertical_slice_deterministic_replay` |
| 18 | `unit_tests` |

### `security_and_persistence` — 10 jobs

| # | Job |
|---|---|
| 19 | `integration_tests` |
| 20 | `sandbox_profile_a_capability_probes` |
| 21 | `sandbox_profile_a_kernel_backend_matrix` |
| 22 | `sandbox_negative_security_corpus` |
| 23 | `crypto_profile_test_vectors` |
| 24 | `golden_core` |
| 25 | `golden_security` |
| 26 | `golden_reliability` |
| 27 | `replay_tests` |
| 28 | `db_migration_tests` |

### `golden_and_release` — 11 jobs

| # | Job |
|---|---|
| 29 | `db_foreign_key_and_state_constraints` |
| 30 | `db_index_query_plan_assertions` |
| 31 | `db_cas_crash_injection` |
| 32 | `audit_chain_verification` |
| 33 | `traceability_completeness` |
| 34 | `release_evidence_bundle_validation` |
| 35 | `golden_self_evolution` |
| 36 | `canary_traffic_validation` |
| 37 | `rollback_demonstration` |
| 38 | `immutable_evaluator_checksum_proof` |
| 39 | `root_of_trust_bootstrap_ceremony` |

---

## Which gate consumes which job

> จาก [`spec/release_gates.yaml`](../../spec/release_gates.yaml) — บังคับด้วย `REQ-S21-002` และ `LINT-13`

| Gate | Minimum maturity | Prerequisites | Mandatory checks |
|---|---|---|---|
| **GATE_CORE** | `M10` | — | `spec_requirement_id_unique_and_complete`<br>`schema_registry_exact_26`<br>`schema_meta_validation`<br>`schema_valid_invalid_vectors`<br>`protocol_type_check`<br>`fsm_reachability_and_terminal_tests`<br>`db_migration_tests`<br>`db_foreign_key_and_state_constraints`<br>`db_index_query_plan_assertions`<br>`db_cas_crash_injection`<br>`sandbox_profile_a_capability_probes`<br>`sandbox_negative_security_corpus`<br>`golden_core`<br>`golden_security`<br>`golden_reliability`<br>`replay_tests`<br>`audit_chain_verification`<br>`traceability_completeness`<br>`release_evidence_bundle_validation` |
| **GATE_PRODUCTION** | `M11` | `GATE_CORE` | `canary_traffic_validation`<br>`rollback_demonstration`<br>`crypto_profile_test_vectors` |
| **GATE_SELF_EVOLUTION** | `M12` | `GATE_CORE`, `GATE_PRODUCTION` | `immutable_evaluator_checksum_proof`<br>`root_of_trust_bootstrap_ceremony`<br>`golden_self_evolution` |
