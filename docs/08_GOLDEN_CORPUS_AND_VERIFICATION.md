# 08 — Golden Corpus & Verification Architecture

> **Active Requirements Covered:** `REQ-S16-001` .. `REQ-S18-003`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Not normative.  
> **Canonical source:** [`benchmarks/golden/manifest.yaml และ docs/08_testing_and_verification/`](../benchmarks/golden/manifest.yaml) — เมื่อขัดกัน ให้ยึดฝั่งนั้น

การยืนยันความถูกต้องและคุณภาพของ Evolution Engine ต้องใช้ **Golden Test Corpus** ที่มี Test Cases ครอบคลุมพฤติกรรมทุกด้าน พร้อมระบบตรวจสอบความน่าเชื่อถือผ่าน **Audit Hash Chain** และ **Evidence Bundle**

---

## 1. Golden Corpus Registry (14 Cases)

ชุดทดสอบมาตรฐาน MVP-01 ถึง MVP-14 โดยมี `benchmarks/golden/manifest.yaml` เป็น canonical source:

| ID | Case Name | Scope | Expected Disposition | Repro |
|---|---|---|---|---|
| **MVP-01** | Pure Function Optimization (`pure-function-opt`) | function | `SELECTED` | `R4` |
| **MVP-02** | Stateful Class & Cache Mutation (`stateful-cache-mod`) | module | `SELECTED` | `R4` |
| **MVP-03** | Multi-Objective Latency vs Memory (`multi-objective-pareto`) | module | `SELECTED` | `R2` |
| **MVP-04** | Asyncio Coroutines & Non-blocking (`async-io-pipeline`) | module | `SELECTED` | `R2` |
| **MVP-05** | Multi-file Project DAG (`multi-file-dag-project`) | project | `SELECTED` | `R1` |
| **MVP-06** | Quantum Qubit Rotation Operator (`quantum-rotation-suite`) | function | `SELECTED` | `R2` |
| **MVP-07** | Python -> Rust Native Compilation (`polyglot-rust-kernel`) | function | `SELECTED` | `R1` |
| **MVP-08** | Filesystem Traversal Attack Vector (`sec-fs-escape-probe`) | security | `QUARANTINED` | `R0` |
| **MVP-09** | Network Egress Attack Vector (`sec-net-socket-probe`) | security | `QUARANTINED` | `R0` |
| **MVP-10** | Fork Bomb PID Exhaustion Attack (`sec-forkbomb-cgroup`) | security | `REJECTED` | `R0` |
| **MVP-11** | Flaky Test Non-Gaming Verification (`flaky-test-isolation`) | reliability | `REJECTED` | `R0` |
| **MVP-12** | 2PC Crash Recovery Chaos Test (`crash-during-commit`) | reliability | `RESTORED_READY` | `R1` |
| **MVP-13** | Byzantine Malicious Peer Rejection (`p2p-swarm-byzantine`) | swarm | `QUARANTINED` | `R0` |
| **MVP-14** | Engine Self-Evolution Protection (`self-evaluator-freeze`) | self_evolution | `QUARANTINED` | `R0` |

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
