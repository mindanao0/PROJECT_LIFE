# Vision, Principles, Authority Hierarchy & System Identity

> **Subsystem:** Core System Identity  
> **Authority Level:** NORMATIVE (`REQ-S00-001` .. `REQ-S03-005`)  
> **Lineage:** Plan 10.2.2 Unified Core Architecture

---

## 1. System Vision & Core Mission

**Evolution Engine v1** เป็นระบบอัตโนมัติแบบ **Offline-first population-based evolutionary computation** ที่รับ source code ของโปรเจกต์ภาษา Python แล้วสร้างประชากรของ candidate programs จาก source เดิม เพื่อค้นหาและปรับปรุงประสิทธิภาพของโค้ดอย่างเป็นระบบ:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         AUTONOMOUS EVOLUTIONARY CYCLE                            │
└──────────────────────────────────────────────────────────────────────────────────┘
   [1. Observe & Parse]  --> สแกน Static AST/CST/UAST โดยไม่ Import ใน Host
   [2. Mutate]           --> กลายพันธุ์โครงสร้าง (M01-M10, Quantum, Native Bridge)
   [3. Isolate]          --> เตรียม Sandbox (Linux Namespaces, cgroups v2, Seccomp)
   [4. Execute & Test]   --> รัน Unit Test & Capability Gates (ตรวจจับ Flaky)
   [5. Measure]          --> วัดค่า Objectives (Latency, Memory, Throughput)
   [6. Statistical Eval] --> ทดสอบทางสถิติ (Welch's t-test, TOST Equivalence, Holm)
   [7. Pareto Select]    --> จัดอันดับ Pareto Fronts & รักษาความหลากหลาย (Diversity)
   [8. Swarm Migrate]    --> แลกเปลี่ยน Elite ข้าม P2P Islands (Byzantine Verified)
   [9. Commit & Loop]    --> บันทึก 2PC (SQLite 29 Tables + CAS Blobs) สู่รุ่นถัดไป
```

### ขอบเขตการวิวัฒนาการตามระดับความสมบูรณ์ (Evolutionary Scopes):
1. **Function-Level Evolution (M5):** การวิวัฒนาการ Pure Function เดี่ยว
2. **Module-Level Evolution (M7):** การวิวัฒนาการ State, Classes, และ Method Interfaces
3. **Project-Level Evolution (M9):** การวิวัฒนาการ Multi-File DAG Project
4. **Engine Self-Evolution (M13):** การวิวัฒนาการตัว Engine เองภายใต้ Immutable Root-of-Trust

- **[REQ-S01-003]** เป้าหมายคือระบบวิวัฒนาการซอฟต์แวร์แบบนำกลับมาใช้ใหม่ได้ (Reusable evolutionary software system) ไม่ใช่ AI coding assistant หรือ random text mutator
- **[REQ-S01-004]** **LLM ไม่เป็น dependency ของ Core Engine** (ใช้ Pure Program Representation, Quantum-Inspired Search และ Evolutionary Operators)

---

## 2. The 7 Inviolable Principles (หลักการ 7 ข้อที่ละเมิดไม่ได้)

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           THE 7 INVIOLABLE PRINCIPLES                            │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. Offline First & Swarm Autonomous [REQ-S01-005]                                │
│    • Evolution loop ทำงานได้ 100% โดยไม่ต้องเชื่อมต่อ Cloud หรือ Internet        │
│                                                                                  │
│ 2. Deterministic Where Possible [REQ-S01-006]                                    │
│    • การ parse, identity, hashing, ordering, lineage และ seed ต้อง replay       │
│      ได้ผลลัพธ์ตรงกันตามระดับ Reproducibility ที่ประกาศ (R0-R4)                   │
│                                                                                  │
│ 3. Project Owns Its Objectives [REQ-S01-007]                                     │
│    • โปรเจกต์เป้าหมายเป็นผู้กำหนด metrics, directions, trade-offs, constraints   │
│                                                                                  │
│ 4. Preserve Capabilities [REQ-S01-008]                                           │
│    • การ optimize ประสิทธิภาพห้ามทำลาย Required Capability หรือ Test เดิม        │
│                                                                                  │
│ 5. Never Destroy Audit History [REQ-S01-009]                                     │
│    • ข้อมูล Lineage, Evidence, Checkpoint และ Audit ห้ามถูกลบทำลาย               │
│                                                                                  │
│ 6. Safe by Default [REQ-S01-010]                                                 │
│    • Default deployment mode คือ SAFE_EXPORT_ONLY ป้องกันการแก้โค้ดจริง          │
│                                                                                  │
│ 7. Controlled Self-Evolution [REQ-S01-011]                                       │
│    • ในระดับ self-evolution ตัว candidate ห้ามแก้ไข evaluator หรือ root-of-trust │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Authority Hierarchy (ลำดับชั้นสิทธิ์และกฎหมายของระบบ)

ในการตัดสินข้อขัดแย้งทางสถาปัตยกรรม ระบบใช้ลำดับชั้นสิทธิ์ L0 ถึง L8 อย่างเคร่งครัด:

```text
L0  Safety, Sandbox Invariants & Root-of-Trust Invariants (สูงสุด ละเมิดไม่ได้)
L1  Security Sandbox Baseline (PROFILE_A_LINUX, Seccomp BPF)
L2  Active Finite State Machine (FSM) Transition Constraints
L3  Active Schema Registry (26 JSON Schemas Draft 2020-12)
L4  Active Typed Protocol Contracts (22 Architecture Protocols)
L5  Persistence, 2PC Commit & Recovery Invariants
L6  Measurement, Statistical Testing & Pareto Selection Semantics
L7  Project-Owned Target Objectives & Metrics in evolution.yaml
L8  Informative Examples, Guides & Historical Archive Documentation
```

- **[REQ-S02-001]** กฎระดับล่างห้าม Override หรือขัดแย้งกับกฎระดับบนโดยเด็ดขาด
- **[REQ-S02-002]** ไม่มี Historical Freeze ใดมีผลบังคับใช้หลังเวอร์ชัน `10.2.2`

---

## 4. Supported Runtime & System Dependencies

```yaml
python_runtime:
  implementation: "CPython"
  supported_minor: "3.12"
  version_policy: "latest security patch within 3.12.x"

system_dependencies:
  linux_kernel: ">= 6.1 LTS"
  container_runtime: "Rootless runc (Optional reference backend)"
  compiler_toolchain:
    rust: "rustc >= 1.75"
    c: "gcc >= 12.0 or clang >= 16.0"
  crypto_backend: "Ed25519 standard implementation"
```

- **[REQ-S03-001]** Core runtime ต้องพึ่งพาเฉพาะ Python Standard Library และเครื่องมือที่กำหนดในสเปก
- **[REQ-S03-002]** Core runtime ห้าม import ไลบรารีกลุ่มวิจัยภายนอกโดยไม่ผ่าน Governed Spec Change
