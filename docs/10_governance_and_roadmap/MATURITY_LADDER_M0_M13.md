# Implementation Phase Plan (PHASE-01 to PHASE-14)

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** ROADMAP SPECIFICATION (L8 Authority)
> **Target Subsystem:** Release Governance & Maturity Verification  
> **Governing Equations:** `EQ-300` (14-Level Monotonic Closure), `EQ-299` (Self-Evolution Root-of-Trust)

---

## 1. Capability Delivery Order (PHASE-01 .. PHASE-14)

```text
┌───────┬───────────────────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Level │ Maturity Milestone Name           │ Canonical Release Gate Criteria & Authority Threshold                     │
├───────┼───────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ M0    │ Genesis & Invariant Principles    │ กำหนดหลักการ 7 ข้อ, L0-L8 Authority, Threat Models                        │
│ M1    │ Plan Canonical Release            │ รวมศูนย์เอกสารสเปก Master Single-File Plan 10.2.2                         │
│ M2    │ Modular Specs & Requirements Hub  │ แยกเอกสาร 10 โฟลเดอร์, 30 โดเมน, 300 มิติ, 300 สมการ, 178 ข้อบังคับ       │
│ M3    │ Physical JSON Schemas             │ สร้างไฟล์ Draft 2020-12 schemas ครบ 26 ไฟล์ใน schemas/                     │
│ M4    │ Core AST Engine & Visitors        │ อิมพลีเมนต์ AST Parser, CST, และ 8 Static Safety Invariant Visitors       │
│ M5    │ Atomic Mutations (M01-M04)        │ ตัวดำเนินการ Constants, Operators, Boundaries, Loops                       │
│ M6    │ Single-Writer SQLite Storage & 2PC│ ตาราง SQLite 29 ตาราง, CAS Sharding, 2PC Commit Protocol 7 สถานะ          │
│ M7    │ Hardened Linux Sandbox (PROFILE_A)│ Linux Namespaces 5 ตัว, cgroups v2 Quotas, Seccomp BPF Filter Matrix      │
│ M8    │ Pareto Multi-Objective & UCB1 MAB │ Fast Non-dominated Sorting, Hypervolume, UCB1 Bandit Allocation           │
│ M9    │ Quantum Rotation (M09) & Refactor │ M05-M08 Refactoring, M09 Qubit Superposition Search & Annealing           │
│ M10   │ Polyglot Native Accelerator (M10) │ M10 UAST to Safe Rust/C99 Compilation, AVX-512 SIMD Vectorization         │
│ M11   │ ALife Co-Evolution & P2P Swarm    │ Prey vs Predator Co-evolution, P2P Swarm Gossip, Byzantine Bound N>=3f+1  │
│ M12   │ Cryptographic Release (EE-CRYPTO) │ 2-of-3 Multisig Ed25519 Signed Evidence Bundle Production Rollout         │
│ M13   │ Complete Self-Evolution           │ Engine Self-Optimization ภายใต้ Frozen Root-of-Trust Evaluator (EQ-299)   │
└───────┴───────────────────────────────────┴───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Monotonic Closure & Quality Gates Proof

PHASE ต่อไปนี้เป็นลำดับการ**ส่งมอบความสามารถ** ไม่ใช่ maturity level และไม่ใช่ release gate
$$\text{PHASE-01} \longrightarrow \text{PHASE-02} \longrightarrow \dots \longrightarrow \text{PHASE-14}$$
maturity level M0–M13 ที่ใช้ตัดสิน release gate อยู่ใน `spec/maturity.yaml` เท่านั้น ดูตารางข้อ 3

---

## 3. Canonical Maturity Ladder (M0–M13)

> Derived from [`spec/maturity.yaml`](../../spec/maturity.yaml). แก้ที่ไฟล์นั้นเท่านั้น ห้ามแก้ตารางนี้โดยตรง

| Level | Name | Gate |
|---|---|---|
| **M0** | `DRAFT` | UTF-8 encoding valid, no corrupted control characters |
| **M1** | `ARCHITECTURE` | Architecture interfaces and single-writer concurrency defined |
| **M2** | `REQUIREMENTS_CANONICAL` | All 178 Requirement IDs monotonically checked and compliant |
| **M3** | `SCHEMAS` | 26 JSON Schemas Draft 2020-12 valid with test fixtures |
| **M4** | `PROTOCOLS` | 22 Typed Python Protocols with zero type errors |
| **M5** | `FSM_AND_CONFIG` | FSM transition matrix reachability & Vertical Slice MVP-01 pass |
| **M6** | `SECURITY` | PROFILE_A_LINUX passes capabilities probes on Linux matrix |
| **M7** | `PERSISTENCE` | 29 SQLite tables installable from scratch with zero FK violations |
| **M8** | `RECOVERY` | 2PC Commit crash chaos injection matrix 100% recovered |
| **M9** | `CORE_GOLDEN` | Golden Corpus cases MVP-01 to MVP-07 pass |
| **M10** | `SECURITY_RELIABILITY_GOLDEN` | Negative security (MVP-08..10), reliability (MVP-11..12) and swarm (MVP-13) pass |
| **M11** | `EXECUTION_READY` | GATE_CORE passed, traceability complete, evidence bundle signed |
| **M12** | `PRODUCTION` | Governed canary deployment, 2-of-3 Ed25519 multisig quorum |
| **M13** | `SELF_EVOLUTION` | Immutable evaluator root-of-trust bootstrap verified |

`GATE_CORE`, `GATE_PRODUCTION` และ `GATE_SELF_EVOLUTION` อยู่ใน [`spec/release_gates.yaml`](../../spec/release_gates.yaml)

PHASE-xx ข้างบนกับ M0–M13 เป็นคนละแกน: PHASE บอกว่าสร้างอะไรก่อนหลัง ส่วน M บอกว่าปล่อยของได้เมื่อไหร่
