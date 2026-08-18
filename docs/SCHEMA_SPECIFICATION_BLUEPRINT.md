# 12 — Schema Specification Blueprint (26 Schemas Matrix)

> **Dimension:** Data Contracts & Schema Engineering  
> **Milestone Deliverable:** M3 (`schemas/*.schema.json`)  
> **Schema Standard:** JSON Schema Draft 2020-12

เอกสารฉบับนี้เป็นพิมพ์เขียวรายละเอียดฟิลด์ (Field-by-Field Blueprint) ของไฟล์ JSON Schema ทั้ง **26 ตัว** ในระบบ Evolution Engine เพื่อใช้เป็นข้อกำหนดในการสร้างไฟล์จริงในโฟลเดอร์ `schemas/`

---

## 📋 ดัชนีและโครงสร้าง 26 JSON Schemas

```text
กฎทั่วไปของทุก Schema:
1. $schema: "https://json-schema.org/draft/2020-12/schema"
2. $id: "https://evolution-engine.org/schemas/<schema_name>.json"
3. additionalProperties: false (เคร่งครัด)
```

---

### กลุ่มที่ 1: Engine Configuration & Command Primitives

#### 01. `engine_config.schema.json`
- **Purpose:** กำหนดคอนฟิกหลักของ Evolution Engine
- **Required Fields:** `version`, `evolution`, `metrics`, `selection`, `sandbox`, `deployment`, `stopping`
- **Key Properties:**
  - `version`: string (regex: `^10\.2\.2$`)
  - `evolution.level`: enum (`"function"`, `"module"`, `"project"`)
  - `evolution.population_size`: integer (minimum: 2)
  - `evolution.seed`: integer
  - `metrics`: array of `objective` objects (minItems: 1)
  - `sandbox.profile`: enum (`"PROFILE_A_LINUX"`, `"PROFILE_C_MACOS"`)
  - `sandbox.writable_tmp_bytes`: integer (minimum: 1048576)
  - `deployment.mode`: enum (`"SAFE_EXPORT_ONLY"`, `"GOVERNED_CANARY"`, `"PRODUCTION_ACTIVE"`, `"SELF_EVOLUTION_SANDBOX"`)

#### 02. `project_manifest.schema.json`
- **Purpose:** นิยามโปรเจกต์เป้าหมาย โครงสร้างไฟล์ และ Dependency
- **Required Fields:** `project_id`, `name`, `language`, `project_version`, `source_root`, `entry_points`
- **Key Properties:**
  - `project_id`: string (UUID or deterministic hash)
  - `name`: string (regex: `^[a-zA-Z0-9_\-]+$`)
  - `language`: enum (`"python"`)
  - `source_files`: array of POSIX relative paths

---

### กลุ่มที่ 2: Candidate, Mutation & Population

#### 03. `candidate.schema.json`
- **Purpose:** บันทึกข้อมูลและโครงสร้างของ Candidate 1 ตัว
- **Required Fields:** `candidate_id`, `generation_id`, `source_hash`, `candidate_state`, `created_at_utc`
- **Key Properties:**
  - `candidate_id`: string
  - `generation_id`: string
  - `source_hash`: string (regex: `^[a-f0-9]{64}$`)
  - `candidate_state`: enum (17 Candidate states)
  - `rejection_reason`: string (nullable)

#### 04. `candidate_state.schema.json`
- **Purpose:** Enum นิยามสถานะที่เป็นไปได้ของ Candidate
- **Type:** string / enum (17 States: `CREATED`, `MATERIALIZED`, ..., `SELECTED`, `REJECTED`, `QUARANTINED`)

#### 05. `mutation.schema.json`
- **Purpose:** กำหนดคำสั่งการกลายพันธุ์และ Parameters
- **Required Fields:** `mutation_id`, `strategy_id`, `parent_candidate_id`, `seed`, `parameters`
- **Key Properties:**
  - `strategy_id`: enum (`"M01"`, `"M02"`, `"M03"`, `"M04"`, `"M05"`, `"M06"`, `"M07"`, `"M08"`)
  - `seed`: string (hex string)

#### 06. `mutation_result.schema.json`
- **Purpose:** ผลลัพธ์ของการทำ Mutation
- **Required Fields:** `mutation_attempt_id`, `status`, `source_before_hash`, `source_after_hash`, `structural_delta`
- **Key Properties:**
  - `status`: enum (`"APPLIED"`, `"INVALID"`, `"FAILED"`)
  - `structural_delta`: object (AST nodes changed, added, removed)

#### 07. `population.schema.json`
- **Purpose:** บันทึกรายชื่อสมาชิกในประชากรของ Generation
- **Required Fields:** `generation_id`, `memberships`
- **Key Properties:**
  - `memberships`: array of objects (`candidate_id`, `role`: enum `PARENT`, `OFFSPRING`, `ELITE`, `SURVIVOR`)

#### 08. `generation.schema.json`
- **Purpose:** Manifest สรุปข้อมูลของ 1 Generation
- **Required Fields:** `generation_id`, `run_id`, `generation_index`, `manifest_artifact_id`, `status`
- **Key Properties:**
  - `generation_index`: integer (minimum: 0)
  - `status`: enum (7 Generation Commit states)

#### 09. `run.schema.json`
- **Purpose:** สรุปข้อมูลและสถานะของการรัน Engine
- **Required Fields:** `run_id`, `project_id`, `config_hash`, `policy_hash`, `environment_hash`, `run_state`, `seed_hex`
- **Key Properties:**
  - `run_state`: enum (11 Run states)

---

### กลุ่มที่ 3: Testing, Objectives & Measurements

#### 10. `baseline.schema.json`
- **Purpose:** บันทึกผลการวัดค่าอ้างอิงเดิมของโปรเจกต์ (Baseline Metrics)
- **Required Fields:** `project_id`, `source_hash`, `metric_measurements`, `measured_at_utc`

#### 11. `capability_contract.schema.json`
- **Purpose:** ข้อกำหนดชุดทดสอบความถูกต้องที่ไม่ยอมให้เสื่อมถอย
- **Required Fields:** `capability_id`, `project_id`, `required`, `definition_hash`

#### 12. `objective.schema.json`
- **Purpose:** นิยามเป้าหมายการวัดผล 1 ตัว
- **Required Fields:** `name`, `direction`, `unit`, `valid_range`, `practical_margin_decimal`
- **Key Properties:**
  - `direction`: enum (`"maximize"`, `"minimize"`)
  - `valid_range.minimum_decimal`: string
  - `valid_range.maximum_decimal`: string

#### 13. `metric_result.schema.json`
- **Purpose:** ผลการวัดค่า Metric ของ Candidate
- **Required Fields:** `metric_result_id`, `candidate_id`, `objective_id`, `sample_count`, `estimate_decimal`
- **Key Properties:**
  - `sample_count`: integer (minimum: 1)
  - `estimate_decimal`: string
  - `lower_bound_decimal`: string (nullable)
  - `upper_bound_decimal`: string (nullable)

#### 14. `oracle_result.schema.json`
- **Purpose:** ผลการเปรียบเทียบผลลัพธ์กับ Oracle
- **Required Fields:** `oracle_result_id`, `candidate_id`, `oracle_version`, `verdict`, `oracle_digest`
- **Key Properties:**
  - `verdict`: enum (`"PASS"`, `"FAIL"`, `"INCONCLUSIVE"`, `"NOT_REQUIRED"`)

---

### กลุ่มที่ 4: Lineage, Environment & Selection

#### 15. `environment.schema.json`
- **Purpose:** บันทึกสภาพแวดล้อมฮาร์ดแวร์/OS/Kernel ที่ใช้รัน
- **Required Fields:** `environment_hash`, `os_name`, `os_release`, `kernel_version`, `cpu_arch`, `python_version`

#### 16. `lineage_node.schema.json`
- **Purpose:** โหนด Candidate ใน Lineage Graph
- **Required Fields:** `candidate_id`, `generation_index`, `artifact_hash`

#### 17. `lineage_edge.schema.json`
- **Purpose:** เส้นเชื่อมสายสัมพันธ์ระหว่าง Candidate
- **Required Fields:** `parent_candidate_id`, `child_candidate_id`, `relationship`
- **Key Properties:**
  - `relationship`: enum (`"MUTATION"`, `"CROSSOVER"`, `"CLONE"`, `"ROLLBACK"`)

#### 18. `selection_decision.schema.json`
- **Purpose:** บันทึกเหตุผลการตัดสินใจคัดเลือก Candidate
- **Required Fields:** `generation_id`, `candidate_id`, `decision`, `reason_code`, `rank_index`
- **Key Properties:**
  - `decision`: enum (`"SELECTED"`, `"RETAINED"`, `"REJECTED"`)

#### 19. `policy_snapshot.schema.json`
- **Purpose:** สแนปช็อตของนโยบายความปลอดภัยและ Sandbox
- **Required Fields:** `policy_snapshot_id`, `run_id`, `policy_version`, `policy_hash`, `artifact_id`

---

### กลุ่มที่ 5: Certificates, Recovery & Governance

#### 20. `provenance_certificate.schema.json`
- **Purpose:** ใบรับรองแหล่งกำเนิดและประวัติการกลายพันธุ์
- **Required Fields:** `certificate_id`, `candidate_id`, `root_source_hash`, `mutation_history_hash`, `signed_envelope`

#### 21. `reproducibility_certificate.schema.json`
- **Purpose:** ใบรับรองระดับการ Replay ซ้ำได้ (R0–R4)
- **Required Fields:** `reproducibility_level`, `seed`, `replay_run_id`, `hash_matches`
- **Key Properties:**
  - `reproducibility_level`: enum (`"R0"`, `"R1"`, `"R2"`, `"R3"`, `"R4"`)

#### 22. `checkpoint.schema.json`
- **Purpose:** จุดบันทึกสถานะชั่วคราวเพื่อกู้คืนหลังขัดข้อง
- **Required Fields:** `checkpoint_id`, `run_id`, `generation_id`, `manifest_artifact_id`, `random_state_artifact_id`

#### 23. `recovery_manifest.schema.json`
- **Purpose:** บันทึกผลการกู้คืนระบบ
- **Required Fields:** `recovery_id`, `run_id`, `recovery_status`, `resumed_state`
- **Key Properties:**
  - `recovery_status`: enum (9 Recovery states)

#### 24. `release_gate.schema.json`
- **Purpose:** ผลการตรวจสอบเงื่อนไขก่อนการ Release
- **Required Fields:** `gate_name`, `maturity_level_verified`, `decision`, `evidence_digest`
- **Key Properties:**
  - `gate_name`: enum (`"GATE_CORE"`, `"GATE_PRODUCTION"`, `"GATE_SELF_EVOLUTION"`, `"GATE_RESEARCH"`)
  - `decision`: enum (`"PASS"`, `"FAIL"`, `"INCONCLUSIVE"`)

#### 25. `quarantine_record.schema.json`
- **Purpose:** บันทึกข้อมูล Candidate ที่ถูกกักกันเนื่องจากละเมิดความปลอดภัย
- **Required Fields:** `quarantine_record_id`, `candidate_id`, `reason_code`, `security_profile_version`, `evidence_artifact_id`

#### 26. `memory_record.schema.json`
- **Purpose:** บันทึกองค์ความรู้ใน Evolution Memory สำหรับใช้สืบทอด
- **Required Fields:** `memory_id`, `ast_pattern_hash`, `successful_strategies`, `reward_score_decimal`
