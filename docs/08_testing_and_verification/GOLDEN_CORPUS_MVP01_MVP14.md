# Golden Corpus Benchmark Specification (MVP-01 to MVP-14)

> **Authority Level:** NORMATIVE BENCHMARK SPECIFICATION (L6 Authority)  
> **Target Subsystem:** Benchmark Corpus & Golden Verification Suite  
> **Governing Equations:** `EQ-273` (14 Golden Projects Conformance), `EQ-280` (R4 Replay Identity)

---

## 1. Catalog of All 14 Golden Projects

```text
┌────────┬──────────────────────┬─────────────┬─────────────────────────────────────────────────────────────────┐
│ CaseID │ Project Name         │ Primary Aim │ Baseline Characteristics & Verification Gates                   │
├────────┼──────────────────────┼─────────────┼─────────────────────────────────────────────────────────────────┤
│ MVP-01 │ CLI Tool Utility     │ Speed / Lat │ Single file Python CLI; argparse, regex optimization (M01-M03)   │
│ MVP-02 │ Data Pipeline Engine │ Throughput  │ Multi-file batch pipeline; list -> deque/set, generator (M08)    │
│ MVP-03 │ REST API Microservice│ P99 Latency │ Async FastAPI/Aiohttp app; async/await preservation (PEP 695)   │
│ MVP-04 │ Memory Graph Engine  │ RAM Footpr. │ In-memory graph search; memory bound, cycle avoidance (EQ-194)  │
│ MVP-05 │ Mathematical Solver  │ Speed + PBT │ Numerical algorithm; Welch t-test & TOST equivalence (EQ-121)   │
│ MVP-06 │ SQLite ORM Wrapper   │ DB Overhead │ SQLite query builder; SQL trigger & 2PC persistence (EQ-251)    │
│ MVP-07 │ Crypto Hash Utility  │ Correctness │ Ed25519 & SHA-256 validator; RFC 8032 compliance (EQ-231..236)  │
│ MVP-08 │ Polyglot C/Rust Ext  │ 10x Speedup │ Computational hotspot; M10 Rust compilation & SIMD (EQ-091..100)│
│ MVP-09 │ Image Filter Kernel  │ CPU / Cache │ Matrix pixel manipulator; AVX-512 vectorization speedup (EQ-099)│
│ MVP-10 │ P2P Gossip Node      │ Bandwidth   │ Distributed node; Byzantine bound N >= 3f+1, Gossip (EQ-171..180)│
│ MVP-11 │ Multi-Tenant Worker  │ Security    │ Hardened sandbox; Seccomp BPF & cgroups v2 quotas (EQ-211..230) │
│ MVP-12 │ ALife Simulation     │ Co-evolve   │ Predator-prey simulation; Lotka-Volterra dynamics (EQ-161..170) │
│ MVP-13 │ AST Refactoring Tool │ Clean Code  │ Architectural inliner; AST Structural Delta <= 15% (EQ-081..090)│
│ MVP-14 │ Full Self-Evolution  │ M13 Ladder  │ Engine self-optimization; Root-of-trust frozen evaluator (EQ-299)│
└────────┴──────────────────────┴─────────────┴─────────────────────────────────────────────────────────────────┘
```

---

## 2. Benchmark Conformance Gate Criteria

ทุก Release ก่อนเลื่อนสู่ระดับ `M2_REQUIREMENTS_CANONICAL` ต้องรันผ่านชุดทดสอบทั้ง 14 โปรเจกต์โดยปราศจากข้อผิดพลาด:
$$|\mathcal{C}_{\text{golden}}| \equiv 14, \qquad \text{Pass}(\mathcal{C}) \equiv 14$$
และบันทึกผลลัพธ์ลงใน `benchmarks/golden/manifest.yaml`
