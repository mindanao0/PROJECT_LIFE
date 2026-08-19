# 09 — Maturity Ladder, Release Gates & Unified v1 Implementation Roadmap

> **Active Requirements Covered:** `REQ-S21-001` .. `REQ-S30-002` (Unified v1 Full Scope)  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Not normative.  
> **Canonical source:** [`spec/maturity.yaml และ spec/release_gates.yaml`](../spec/maturity.yaml) — เมื่อขัดกัน ให้ยึดฝั่งนั้น

---

## 1. Maturity Ladder (M0 – M13)

| ระดับ | ชื่อระดับ (Level Name) | เกณฑ์การผ่าน (Verification Criteria) |
|:---:|---|---|
| **M0** | `DRAFT` | เอกสารผ่านการ Parse เป็น UTF-8 และไม่มี Control Characters ผิดรูป |
| **M1** | `ARCHITECTURE` | นิยามสถาปัตยกรรมและอินเทอร์เฟซครบถ้วน |
| **M2** | `REQUIREMENTS_CANONICAL` | **[สถานะปัจจุบัน]** สเปกบูรณาการสมบูรณ์, 179 IDs ครบ, FSM/DDL ตรวจสอบแล้ว |
| **M3** | `SCHEMAS` | มีไฟล์ physical schemas 26/26 ตัว พร้อม fixtures (valid/invalid) ผ่าน 100% |
| **M4** | `PROTOCOLS` | Typed Python protocol package (22 Protocols) สมบูรณ์, Pinned Dependencies |
| **M5** | `FSM_AND_CONFIG` | FSM conformance tests ผ่าน, Vertical Slice (MVP-01) Replay สำเร็จ |
| **M6** | `SECURITY` | PROFILE_A ผ่าน capability probes บน Linux kernel matrix และ negative corpus |
| **M7** | `PERSISTENCE` | 29-table SQLite migrations ติดตั้งได้จาก DB ว่าง, FK/Unique/Index tests ผ่าน |
| **M8** | `RECOVERY` | DB + CAS Crash injection matrix ผ่าน, Audit recovery สำเร็จ |
| **M9** | `CORE_GOLDEN` | ผ่านการทดสอบกับ CORE golden corpus (MVP-01 .. MVP-07) รวม Quantum/Polyglot Operators |
| **M10** | `SECURITY_RELIABILITY_GOLDEN` | ผ่าน SECURITY (MVP-08..10) และ RELIABILITY (MVP-11..13) รวม P2P Swarm |
| **M11** | `EXECUTION_READY` | GATE_CORE ผ่าน, Traceability ครบถ้วน, Evidence bundle ถูกสร้าง |
| **M12** | `PRODUCTION` | Governed canary, Multisig approval verification (2-of-3 Ed25519) |
| **M13** | `SELF_EVOLUTION` | Root-of-trust bootstrap, Immutable evaluator, Self-evolution corpus |

---

## 2. Release Gates

- **`GATE_CORE`:** Maturity $\ge$ M10, Schemas / Protocols / FSM / Persistence / Security / Replay ผ่านทั้งหมด, Traceability ครบถ้วน, Evidence bundle ถูกสร้าง
- **`GATE_PRODUCTION`:** `GATE_CORE` ผ่าน, Maturity $\ge$ M12, Multisig approval ถูกต้อง, Canary / Rollback tests ผ่าน
- **`GATE_SELF_EVOLUTION`:** `GATE_CORE` ผ่าน, Maturity $\ge$ M13, Root-of-trust verification ผ่าน, Immutable evaluator ไม่ถูกแก้ไข

---

## 3. Mandatory Trusted-Fixture Vertical Slice (Section 29.1)

```yaml
fixture: "MVP-01 trusted pure function only"
evolution_level: "function"
mutation_strategies: ["M01", "M02"]
population_size: 4
generations: 1
seed: 12345
capability_tests: 1
objectives: 1
persistence_adapter: "in_memory_non_evidence"
deployment: "SAFE_EXPORT_ONLY to temporary directory"
```

### เส้นทางการประมวลผลของ Slice:
```text
Load Config -> Parse Fixture -> Create Candidates -> Reject Static-Invalid 
-> Execute Evaluator -> Capability Gate -> Measure Metric -> Pareto Select 
-> Export Selected Source -> Replay (Compare Hash Identity)
```

---

## 4. ลำดับขั้นตอนการพัฒนา (Unified v1 Implementation Order)

```text
1.  M2 Closure: Spec linters + Requirement IDs + Active-Spec View
2.  M3: 26-schema package + manifest + valid/invalid fixtures
3.  M4: Typed protocols (22 Protocols) + Public SDK/CLI + Pinned dependencies
4.  M5: FSMs + Config resolution + Mandatory Vertical Slice (MVP-01)
5.  M6: PROFILE_A capability probes + Linux kernel matrix + Negative security corpus
6.  M7: 29-table SQLite migrations + Invariants + CAS
7.  M8: Atomic generation commit + Checkpoint / Recovery / Audit replay
8.  Expand mutation engine to M01–M10 (รวม Quantum Rotation และ Polyglot Native Accelerator)
9.  Tests / Capability / Oracle / Flaky isolation boundary
10. Multi-objective Pareto / Diversity / ALife Ecosystem / P2P Swarm Migration
11. Lineage graph / Evolution memory / Report / SAFE export
12. M9: CORE golden corpus
13. M10: SECURITY + RELIABILITY golden corpus
14. M11: GATE_CORE -> Execution Ready
15. M12: EE-CRYPTO-1 + Governed Canary Deployment
16. M13: Root-of-trust Self-Evolution
```
