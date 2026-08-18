# 19 — CI/CD Automation, Spec Linters & Traceability Engine

> **Dimension:** CI/CD Automation, Compliance & Automated Governance  
> **Target Audience:** DevOps Engineers, Release Managers, and Quality Assurance

เอกสารฉบับนี้กำหนดรายละเอียดกฎของเครื่องมือตรวจสอบสเปก (Spec Linters), สถาปัตยกรรม Continuous Integration ทั้ง **34 Jobs**, และเครื่องมือตรวจสอบความเชื่อมโยงย้อนกลับ (Traceability Engine)

---

## 1. Specification Linter Suite (`tools/spec_linters/`)

ก่อนที่ PR หรือการแก้ไขโค้ดใดๆ จะถูก Merge สเปกจะต้องผ่านเครื่องมือตรวจความถูกต้องอัตโนมัติ 8 ตัว:

```text
┌─────────────────────────────────────────────────────────────┐
│                  SPECIFICATION LINTER SUITE                 │
├─────────────────────────────────────────────────────────────┤
│ 1. spec_utf8_control_char_lint     : ตรวจ UTF-8 และ Control Chars│
│ 2. spec_heading_classification_lint: ตรวจแท็ก [NORMATIVE]/...   │
│ 3. spec_single_active_version_lint : ตรวจ Version 10.2.2 ชุดเดียว │
│ 4. spec_no_historical_normative    : ตรวจห้ามมี freeze เก่าใน Active│
│ 5. spec_active_view_byte_match     : ตรวจ Byte-match ของ Active View│
│ 6. spec_archive_checksum_match     : ตรวจ SHA-256 ของ Archive ไม่หาย│
│ 7. spec_req_id_unique_complete     : ตรวจ 179 IDs เรียง 001..N ไม่ซ้ำ│
│ 8. spec_req_digest_change_guard    : ตรวจ Text Digest ป้องกันแก้เงียบ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. The 34 Canonical CI Jobs Matrix

| หมวดหมู่ (Category) | รายชื่อ CI Jobs | เงื่อนไขการผ่าน (Pass Criteria) |
|---|---|---|
| **Spec & Linters** | `spec_utf8_control_char_lint`<br>`spec_heading_classification_lint`<br>`spec_single_active_version_lint`<br>`spec_no_historical_normative_freeze_lint`<br>`spec_active_view_byte_match`<br>`spec_archive_checksum_match`<br>`spec_requirement_id_unique_and_complete`<br>`spec_requirement_digest_change_guard` | Exit code 0, ไม่พบ Invariant Violation |
| **Schemas** | `schema_registry_exact_26`<br>`schema_meta_validation`<br>`schema_valid_invalid_vectors` | JSON Schema Draft 2020-12 valid, Fixtures ครบ 100% |
| **Protocols & Types** | `protocol_type_check`<br>`fsm_reachability_and_terminal_tests` | MyPy / Pyright strict type check pass |
| **Configuration** | `config_argv_only_validation`<br>`config_resolution_precedence_validation`<br>`config_decimal_and_weight_semantics` | `shell=false` เสมอ, Exact Decimal weights |
| **Vertical Slice** | `vertical_slice_deterministic_replay` | MVP-01 Replay ซ้ำได้ผลลัพธ์ตรงกัน 100% |
| **Unit & Integration** | `unit_tests`<br>`integration_tests` | Test coverage $\ge 90\%$ |
| **Sandbox & Security** | `sandbox_profile_a_capability_probes`<br>`sandbox_profile_a_kernel_backend_matrix`<br>`sandbox_negative_security_corpus`<br>`crypto_profile_test_vectors` | Linux namespaces / cgroups / seccomp / EE-CRYPTO-1 pass |
| **Golden & Replay** | `golden_core`<br>`golden_security`<br>`golden_reliability`<br>`replay_tests` | 14 Golden projects (MVP-01..14) pass |
| **Persistence** | `db_migration_tests`<br>`db_foreign_key_and_state_constraints`<br>`db_index_query_plan_assertions`<br>`db_cas_crash_injection`<br>`audit_chain_verification` | Foreign key checks pass, WAL crash recovery pass |
| **Release & Trace** | `traceability_completeness`<br>`release_evidence_bundle_validation` | ไม่มี Dangling References ใน traceability matrix |

---

## 3. Automated Traceability Engine (`spec/traceability.yaml`)

ทุก Requirement ID ต้องมี Traceability Record ผูกโยงครบวงจร:

```yaml
requirements:
  - id: "REQ-S05-002"
    section: "5.2"
    status: "IMPL"
    text_digest: "sha256:8f4c2e..."
    owner: "security_core"
    verification_method: "automated_test"
    test_refs:
      - "tests/unit/test_command_model.py::test_shell_false_enforced"
      - "tests/security/test_command_injection.py"
    evidence_refs:
      - "artifacts/evidence/m06_command_model_evidence.json"
    release_gates:
      - "GATE_CORE"
```
