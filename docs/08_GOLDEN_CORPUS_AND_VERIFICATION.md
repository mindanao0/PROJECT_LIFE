# 08 — Golden Corpus & Verification Architecture

> **Active Requirements Covered:** `REQ-S16-001` .. `REQ-S18-003`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Not normative.  
> **Canonical source:** [`benchmarks/golden/manifest.yaml และ docs/08_testing_and_verification/`](../benchmarks/golden/manifest.yaml) — เมื่อขัดกัน ให้ยึดฝั่งนั้น

การยืนยันความถูกต้องและคุณภาพของ Evolution Engine ต้องใช้ **Golden Test Corpus** ที่มี Test Cases ครอบคลุมพฤติกรรมทุกด้าน พร้อมระบบตรวจสอบความน่าเชื่อถือผ่าน **Audit Hash Chain** และ **Evidence Bundle**

---

## 1. Golden Corpus Registry (14 Cases)

ชุดทดสอบมาตรฐาน MVP-01 ถึง MVP-14 โดยมี `benchmarks/golden/manifest.yaml` เป็น canonical source:

| ID | Case Name | Scope | Bucket | Expected Disposition | Repro |
|---|---|---|---|---|---|
| **MVP-01** | `pure-function-opt` | function | **CORE** | `SELECTED` | `R4` |
| **MVP-02** | `stateful-cache-mod` | module | **CORE** | `SELECTED` | `R4` |
| **MVP-03** | `multi-objective-pareto` | module | **CORE** | `SELECTED` | `R2` |
| **MVP-04** | `async-io-pipeline` | module | **CORE** | `SELECTED` | `R2` |
| **MVP-05** | `multi-file-dag-project` | project | **CORE** | `SELECTED` | `R1` |
| **MVP-06** | `quantum-rotation-suite` | function | **RESEARCH** | `SELECTED` | `R2` |
| **MVP-07** | `polyglot-rust-kernel` | function | **RESEARCH** | `SELECTED` | `R1` |
| **MVP-08** | `sec-fs-escape-probe` | security | **SECURITY** | `QUARANTINED` | `R0` |
| **MVP-09** | `sec-net-socket-probe` | security | **SECURITY** | `QUARANTINED` | `R0` |
| **MVP-10** | `sec-forkbomb-cgroup` | security | **SECURITY** | `REJECTED` | `R0` |
| **MVP-11** | `flaky-test-isolation` | reliability | **RELIABILITY** | `REJECTED` | `R0` |
| **MVP-12** | `crash-during-commit` | reliability | **RELIABILITY** | `RESTORED_READY` | `R1` |
| **MVP-13** | `p2p-swarm-byzantine` | swarm | **RESEARCH** | `QUARANTINED` | `R0` |
| **MVP-14** | `self-evaluator-freeze` | self_evolution | **SELF_EVOLUTION** | `QUARANTINED` | `R0` |

- **[REQ-S16-001]** ค่า `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอนสร้าง corpus build เท่านั้น ห้ามใส่ค่า Placeholder

---

## 2. Flaky Tests & Holdout Anti-Gaming Boundary

### 2.1 Flaky Test Handling
- หาก Candidate เดิมบน Environment เดิม ให้ผลการทดสอบไม่สม่ำเสมอ:
  - กำหนดสถานะ Test = `FLAKY`
  - Candidate Verdict = `INCONCLUSIVE` (ห้ามผ่าน Release Gate)
  - **[REQ-S17-001]** การรันซ้ำแล้วผ่าน (Retry-as-pass) ห้ามลบล้างหลักฐานความไม่เสถียรเดิม

### 2.2 Holdout Boundary
```text
Search Workload     : มองเห็นได้โดย Evolution Loop (สำหรับ optimize)
Validation Workload : ควบคุมโดย Evaluator (สำหรับคัดกรองระหว่าง generation)
Hidden Holdout      : ใช้เฉพาะตอน Release Gate เท่านั้น
```
- **[REQ-S17-002]** ข้อมูล Hidden Holdout **ห้ามถูกบันทึกลง Evolution Memory**
- **[REQ-S17-003]** Workspace ของ Candidate ต้องไม่สามารถ Mount หรือเข้าถึง Hidden Holdout ได้

---

## 3. Cryptographic Audit Hash Chain & Evidence Bundle

### 3.1 Audit Hash Chain
การบันทึก Event ทุกขั้นตอนลงในตาราง `audit_events`:

```text
Genesis Event (Seq 0) : previous_event_hash = null
Subsequent Event (i)  : event_hash = SHA256(previous_event_hash || canonical_event_payload)
```

- **[REQ-S18-001]** Sequence Number ต้องเรียงลำดับต่อเนื่องแบบ Serialize ต่อแต่ละ Run
- **[REQ-S18-003]** Audit Verifier ต้องสามารถตรวจสอบความสมบูรณ์ของโซ่แฮชได้ตั้งแต่ Genesis จนถึง Event ล่าสุด

### 3.2 Release Evidence Bundle Components
ก่อนที่โปรเจกต์หรือเวอร์ชันจะผ่านการอนุมัติ ต้องมี Bundle ที่บันทึก:
1. Active Contract Version
2. Schema Bundle Digest
3. Protocol Package Digest
4. FSM State Transition Digests
5. Environment & Policy Digests
6. Test Report & Golden Corpus Results
7. Security Profile Verification Result
8. Reproducibility Certificate (R0–R4)
9. Database Migration Status
10. Head of Audit Hash Chain
11. Cryptographic Signatures (ตาม EE-CRYPTO-1)
