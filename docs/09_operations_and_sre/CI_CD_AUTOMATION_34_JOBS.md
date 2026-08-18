# Continuous Integration Matrix: Complete 34 Jobs Specification

> **Subsystem:** CI/CD Automation & Quality Gate Enforcement  
> **Authority Level:** NORMATIVE (`REQ-S02-009`, `REQ-S21-001`)

---

## 1. Complete 34 CI Jobs Architecture Matrix

```text
┌────┬──────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ No │ CI Job Name                              │ Target Subsystem & Verification Assertions                  │
├────┼──────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 01 │ spec_utf8_control_char_lint              │ ตรวจจับ UTF-8 Encoding และ Control Chars ในสเปก            │
│ 02 │ spec_heading_classification_lint         │ ตรวจสอบแท็กสิทธิ์ [NORMATIVE]/[INFORMATIVE] ทุก Heading    │
│ 03 │ spec_single_active_version_lint          │ บังคับใช้เฉพาะเวอร์ชัน 10.2.2 ชุดเดียวใน Active Section    │
│ 04 │ spec_no_historical_normative_freeze_lint │ ป้องกันการดึง Freeze เก่าใน Archive มามีผลบังคับใช้         │
│ 05 │ spec_active_view_byte_match              │ ตรวจสอบว่า Active View ตรงกับ Canonical Spec บิตต่อบิต     │
│ 06 │ spec_archive_checksum_match              │ ตรวจสอบ SHA-256 ของ Historical Archive ไม่สูญหาย           │
│ 07 │ spec_requirement_id_unique_and_complete  │ ตรวจสอบว่ามี Requirement IDs ครบ 178 ข้อ และเรียงลำดับถูก   │
│ 08 │ spec_requirement_digest_change_guard     │ ตรวจสอบ Digest ป้องกันการแอบแก้ไขข้อความใน Requirement     │
│ 09 │ schema_registry_exact_26                 │ ตรวจสอบว่ามีไฟล์ JSON Schema ครบ 26 ตัวพอดี                 │
│ 10 │ schema_meta_validation                   │ ตรวจสอบ Schemas ทั้ง 26 ตัวกับ Meta-schema Draft 2020-12    │
│ 11 │ schema_valid_invalid_vectors             │ รัน Fixtures valid/invalid ครบทุก Schema 100%               │
│ 12 │ protocol_type_check                      │ Type check Protocols ทั้ง 22 ตัวด้วย MyPy / Pyright Strict  │
│ 13 │ fsm_reachability_and_terminal_tests      │ รัน State Machine Reachability และ Deadlock Tests ครบ 5 FSMs│
│ 14 │ config_argv_only_validation              │ ยืนยันว่าทุก Command ใน evolution.yaml เป็น Argv Array      │
│ 15 │ config_resolution_precedence_validation  │ ตรวจสอบลำดับการ Override Configuration                     │
│ 16 │ config_decimal_and_weight_semantics      │ ยืนยันว่าผลรวม Preference Weights เท่ากับ 1.0 เสมอ         │
│ 17 │ vertical_slice_deterministic_replay      │ รัน MVP-01 Vertical Slice และยืนยันความสามารถในการ Replay   │
│ 18 │ unit_tests                               │ รัน Unit Tests ทั้งหมด ต้องได้ Coverage >= 90%              │
│ 19 │ integration_tests                        │ รัน Integration Tests ข้ามโมดูลภายใน Coordinator            │
│ 20 │ sandbox_profile_a_capability_probes      │ ตรวจสอบ Linux Namespaces, cgroups v2, Seccomp บน Host      │
│ 21 │ sandbox_profile_a_kernel_backend_matrix  │ รัน Conformance Tests บน Linux LTS Kernel Matrix (A1-A4)    │
│ 22 │ sandbox_negative_security_corpus         │ รันชุดทดสอบเจาะระบบ (MVP-08..10) ต้องได้ QUARANTINED ทั้งหมด│
│ 23 │ crypto_profile_test_vectors              │ ตรวจสอบอัลกอริทึม Ed25519 และ Multisig Quorum 2-of-3       │
│ 24 │ golden_core                              │ รัน Golden Corpus ชุด Core (MVP-01 .. MVP-07) ผ่าน 100%     │
│ 25 │ golden_security                          │ รัน Golden Corpus ชุด Security (MVP-08 .. MVP-10) ผ่าน 100% │
│ 26 │ golden_reliability                       │ รัน Golden Corpus ชุด Reliability (MVP-11 .. MVP-13) ผ่าน   │
│ 27 │ replay_tests                             │ รัน Replay Tests ยืนยันผลลัพธ์ R4 Bit-Identical             │
│ 28 │ db_migration_tests                       │ ติดตั้งและอัปเกรดฐานข้อมูล SQLite 29 ตารางจากศูนย์           │
│ 29 │ db_foreign_key_and_state_constraints     │ ทดสอบ Foreign Key Cascades และ Check Constraints ใน SQLite  │
│ 30 │ db_index_query_plan_assertions           │ ตรวจสอบ Query Plans ของ 33 Indices ไม่ให้เกิด Full Scan     │
│ 31 │ db_cas_crash_injection                   │ ทดสอบ Chaos ตัดไฟ 4 จังหวะระหว่าง Commit 2PC               │
│ 32 │ audit_chain_verification                 │ ตรวจสอบความสมบูรณ์ต่อเนื่องของ Audit Hash Chain             │
│ 33 │ traceability_completeness                │ ตรวจสอบว่า Requirement ครบ 178 ข้อมี Test & Evidence รองรับ│
│ 34 │ release_evidence_bundle_validation       │ ตรวจสอบความถูกต้องและลายเซ็นของ Release Evidence Envelope   │
└────┴──────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```
