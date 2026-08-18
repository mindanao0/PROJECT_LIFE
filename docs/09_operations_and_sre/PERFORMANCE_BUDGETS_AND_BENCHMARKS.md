# Engine Performance Budgets & Resource Ceilings

> **Subsystem:** Performance Engineering & Latency Budgets  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.

---

## 1. Engine Subsystem Latency Budgets (P50 & P99)

```text
┌──────────────────────────────────────┬─────────────┬─────────────┬───────────────────────────┐
│ Engine Subsystem Operation           │ Target P50  │ Maximum P99 │ Measurement Baseline      │
├──────────────────────────────────────┼─────────────┼─────────────┼───────────────────────────┤
│ AST Parse & Tree Construction        │ < 2.0 ms    │ < 5.0 ms    │ ต่อไฟล์ Python <= 50 KB   │
│ Static Safety Invariant Scanner      │ < 1.0 ms    │ < 3.0 ms    │ ต่อ Candidate AST         │
│ Mutation Operator Execution (M01-M08)│ < 0.5 ms    │ < 2.0 ms    │ ต่อ Mutation Attempt      │
│ Quantum Rotation Mutation (M09)      │ < 1.5 ms    │ < 4.0 ms    │ ต่อ Qubit State Collapse  │
│ Linux Sandbox Provision & Spawn      │ < 3.0 ms    │ < 15.0 ms   │ Native Namespaces + Mount │
│ SQLite Batch Transaction Commit      │ < 10.0 ms   │ < 50.0 ms   │ ต่อ 20 Candidates Batch   │
│ CAS fsync & Atomic File Materialize  │ < 5.0 ms    │ < 20.0 ms   │ ต่อ Artifact Blob <= 1 MB │
│ Fast Pareto Dominance Sort (N=50,M=3)│ < 1.0 ms    │ < 5.0 ms    │ ต่อ Generation Selection  │
└──────────────────────────────────────┴─────────────┴─────────────┴───────────────────────────┘
```

---

## 2. Resource Footprint & Scalability Ceilings

- **Coordinator RAM Footprint:** จำกัดไม่เกิน **$256\text{ MB}$** สำหรับประชากร 1,000 Candidates Active ในหน่วยความจำ
- **Generation Scalability:** รองรับการรันต่อเนื่องสูงสุด **$10,000\text{ Generations}$** โดยไม่มี Memory Leak
- **Worker Memory Ceilings:** ควบคุมผ่าน cgroups v2 `memory.max = 512MB` ต่อ 1 Worker Instance
