# 01 — Vision, Principles, Authority & Unified v1 Architecture

> **Active Requirements Covered:** `REQ-S00-001` .. `REQ-S03-005` (Unified v1 Full Scope)  
> **Authority Level:** NORMATIVE (Integrated Core v1 Architecture)

---

## 1. Core Vision & System Identity

**Evolution Engine v1** เป็นระบบอัตโนมัติแบบ **Next-Generation Autonomous Evolutionary Software System** ที่ผสานการค้นหาเชิงควอนตัม (Quantum-Inspired Search), การประมวลผลแบบกระจายศูนย์ (Distributed P2P Swarm), ระบบนิเวศชีวิตประดิษฐ์ (ALife Co-evolution), และการเร่งความเร็วข้ามภาษา (Cross-Language AST Subtree Bridges) เข้าเป็นหนึ่งเดียวใน Core

```text
Observe -> Understand -> Represent (AST/UAST) -> Quantum/Polyglot Mutate 
-> Generate Swarm/Ecosystem Population -> Sandbox Isolate -> Test & Adversarial Validate 
-> Measure -> Pareto Select -> P2P Elite Migrate -> Adapt Strategy -> Repeat
```

### ขอบเขตการวิวัฒนาการใน Core v1:
```text
Function Evolution -> Module Evolution -> Project Evolution -> Self-Evolution (M13)
```

- **[REQ-S01-003]** เป้าหมายคือระบบวิวัฒนาการซอฟต์แวร์แบบนำกลับมาใช้ใหม่ได้ (Reusable evolutionary software system)
- **[REQ-S01-004]** **LLM ไม่เป็น dependency ของ Core** (ใช้ Pure Program Representation, Quantum-inspired Search และ Evolutionary Algorithms)

---

## 2. Core Principles (หลักการ 7 ประการ)

1. **Offline First & Swarm Autonomous [REQ-S01-005]:** Evolution loop ทำงานได้โดยสมบูรณ์แบบ Offline และสามารถทำงานร่วมกันเป็น P2P Swarm ผ่าน Local Network ได้
2. **Deterministic Where Possible [REQ-S01-006]:** การ parse โค้ด, candidate identity, artifact hashing, ordering, lineage และ seeded randomness ต้อง replay ซ้ำได้ผลลัพธ์ตรงกันตามระดับ reproducibility ที่ประกาศ (R0-R4)
3. **Project Owns Its Objectives [REQ-S01-007]:** โปรเจกต์เป้าหมายเป็นผู้กำหนด metrics, directions, trade-offs, constraints, stopping rules ภายในขอบเขตความปลอดภัย
4. **Preserve Capabilities [REQ-S01-008]:** การ optimize ประสิทธิภาพห้ามทำลาย capability หรือชุดทดสอบที่ถูกประกาศเป็น required
5. **Never Destroy Audit History [REQ-S01-009]:** Metadata ที่จำเป็นต่อ lineage, evidence, recovery และ audit ห้ามถูก Garbage Collect ในลักษณะที่ทำให้ reconstruct ประวัติไม่ได้
6. **Safe by Default [REQ-S01-010]:** Default deployment mode คือ `SAFE_EXPORT_ONLY` เพื่อป้องกันการเปลี่ยนแปลงโค้ดจริงโดยไม่ได้ตั้งใจ
7. **Controlled Self-Evolution [REQ-S01-011]:** ในระดับ self-evolution ตัว candidate engine ห้ามแก้ไข evaluator, policy หรือ root-of-trust ที่ใช้ตัดสินตัวเอง

---

## 3. Concurrency Model: Single-Writer Coordinator & Swarm Topology

```text
┌─────────────────────────────────────────────────────────────┐
│                    SWARM NODE (COORDINATOR)                 │
│  • ผู้ดูแล Local State และเป็น Single Writer บน SQLite       │
│  • เขียน SQLite Database, CAS Storage และ Audit Log         │
│  • แลกเปลี่ยน Pareto Elite Candidates ข้าม P2P Swarm        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Dispatch Immutable Tasks
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 WORKER NODES (SANDBOXES)                    │
│  • Execution-Only / Read-Only สิทธิ์ Unprivileged           │
│  • รัน Candidate ใน Kernel-enforced Sandbox (PROFILE_A)    │
│  • รองรับการคอมไพล์ Native Accelerator (Rust/C) ใน Sandbox │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Unified Exception Hierarchy

```python
class EvolutionEngineError(Exception):
    """Base exception สำหรับข้อผิดพลาดทั้งหมดใน Evolution Engine"""
    pass

class PreflightCheckError(EvolutionEngineError):
    """เกิดเมื่อสภาพแวดล้อม รันไทม์ หรือคอนฟิกไม่ผ่านเกณฑ์เบื้องต้น"""
    pass

class SandboxSecurityViolationError(EvolutionEngineError):
    """เกิดเมื่อ Candidate พยายามละเมิดขอบเขตความปลอดภัยของ Sandbox"""
    pass

class ResourceExhaustionError(EvolutionEngineError):
    """เกิดเมื่อ Candidate ใช้งาน CPU, Memory หรือ Timeout เกินโควตา"""
    pass

class ContractViolationError(EvolutionEngineError):
    """เกิดเมื่อ Candidate ไม่ผ่าน Capability Gate หรือทำให้พฤติกรรมเดิมเสียหาย"""
    pass

class OracleEvaluationError(EvolutionEngineError):
    """เกิดเมื่อชุด Oracle สำหรับเปรียบเทียบผลลัพธ์เสียหายหรือไม่พร้อมใช้งาน"""
    pass

class PersistenceIntegrityError(EvolutionEngineError):
    """เกิดเมื่อโครงสร้างฐานข้อมูล SQLite หรือ CAS Manifest ไม่ผ่าน Integrity Check"""
    pass

class SwarmConsensusError(EvolutionEngineError):
    """เกิดเมื่อ Candidate ที่ได้รับจาก P2P Swarm ไม่ผ่านการ Re-verify"""
    pass

class StagnationThresholdError(EvolutionEngineError):
    """เกิดเมื่อประชากรหยุดการพัฒนาต่อเนื่องเกินเกณฑ์ Max Stagnation"""
    pass
```

---

## 5. Canonical Authority & Versioning

```text
L0  Safety & Root-of-Trust invariants
L1  Security sandbox invariants
L2  Active FSM definitions
L3  Active schema/data invariants
L4  Active protocol/interface contracts
L5  Persistence/recovery invariants
L6  Measurement/selection semantics
L7  Project-owned objectives
L8  Informative examples
```

- **[REQ-S02-001]** กฎระดับล่างห้าม Override กฎระดับบน
- **[REQ-S02-002]** ไม่มี historical freeze ใดมีผลบังคับใช้หลัง version `10.2.2`

---

## 6. Supported Runtime & Dependencies

```yaml
python_runtime:
  implementation: "CPython"
  supported_minor: "3.12"
  version_policy: "latest security patch within 3.12.x"
```

- **Core Runtime:** Python Standard Library, Native Linux Sandboxing
- **Native Extension Tooling (M10 Bridge):** `rustc`, `gcc` (ติดตั้งแบบ offline-cached ภายใน Sandbox Toolchain)
- **Validation Tooling:** `jsonschema`, type checker, spec linters
- **Security Backend:** Linux kernel namespaces, cgroups v2, seccomp BPF filters
- **Crypto Backend:** Ed25519 implementation (EE-CRYPTO-1 Profile)
