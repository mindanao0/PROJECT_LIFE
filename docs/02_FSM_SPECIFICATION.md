# 02 — Finite State Machines (FSM) Specification

> **Authority Level:** POINTER — this file is not normative.
> **Canonical machine-readable source:** [`spec/fsm_states_57.yaml`](../spec/fsm_states_57.yaml)
> **Canonical narrative source:** [`docs/02_fsm_and_lifecycles/`](./02_fsm_and_lifecycles/)
> **Binding requirements:** [`build/spec/Evolution_Engine_Active_Spec_10_2_2.md`](../build/spec/Evolution_Engine_Active_Spec_10_2_2.md) sections 8.1–8.5, 14.1 and 19.2

---

## Why this file no longer holds state definitions

ไฟล์นี้เคยนิยาม state ของทั้ง 5 FSM ซ้ำกับ `docs/02_fsm_and_lifecycles/` และเมื่อฝั่งหนึ่งถูกแก้อีกฝั่งไม่ถูกแก้ตาม
ทั้งสองชุดจึงขัดกัน — Recovery FSM ไม่ตรงกันแม้แต่ชื่อเดียว และ Run FSM ตรงกัน 5 จาก 11

ตามลำดับอำนาจใน [`spec/authority.yaml`](../spec/authority.yaml) ไฟล์ใน `docs/` เป็น L8
จึงห้ามนิยาม state vocabulary เอง ต้องอ้างไปยัง `spec/fsm_states_57.yaml` เท่านั้น

---

## Where each FSM is defined

| FSM | States | Narrative | Binding requirements |
|---|---|---|---|
| Candidate Lifecycle | 17 | [`CANDIDATE_FSM.md`](./02_fsm_and_lifecycles/CANDIDATE_FSM.md) | §8.1, `REQ-S08-001`, `REQ-S08-002` |
| Run Lifecycle | 11 | [`RUN_FSM.md`](./02_fsm_and_lifecycles/RUN_FSM.md) | §8.3, `REQ-S08-003` .. `REQ-S08-006` |
| Recovery | 9 | [`RECOVERY_FSM.md`](./02_fsm_and_lifecycles/RECOVERY_FSM.md) | §8.4, `REQ-S08-007` .. `REQ-S08-009` |
| Governance | 12 | [`GOVERNANCE_FSM.md`](./02_fsm_and_lifecycles/GOVERNANCE_FSM.md) | §8.5, `REQ-S08-010` .. `REQ-S08-012` |
| Deployment | 8 | [`DEPLOYMENT_FSM.md`](./02_fsm_and_lifecycles/DEPLOYMENT_FSM.md) | §19.2, `REQ-S19-001` .. `REQ-S19-003` |

รวม 57 states — ตรวจอัตโนมัติด้วย `LINT-09` ใน [`tools/lint_state_vocabulary.py`](../tools/lint_state_vocabulary.py)
ซึ่ง assert ว่า `spec/fsm_states_57.yaml`, JSON Schema enums, SQLite `CHECK` constraints และ prose ของ Active Spec
ใช้คำเดียวกันทั้งหมด

## Persistence

State ถูกเก็บใน 29-table SQLite schema — ดู [`SQLITE_DDL_29_TABLES.md`](./03_storage_and_database/SQLITE_DDL_29_TABLES.md)
คอลัมน์ `runs.run_state`, `candidates.candidate_state`, `deployments.deployment_state`
และ `recovery_records.recovery_status` มี `CHECK` constraint ที่ต้องตรงกับ `spec/fsm_states_57.yaml` เสมอ
