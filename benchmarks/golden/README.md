# Golden Test Corpus Directory

> **Subsystem:** Golden Conformance Benchmarks (MVP-01 .. MVP-14)  
> **Authority Level:** NORMATIVE (`REQ-S16-001`)

โฟลเดอร์นี้บรรจุชุดโครงการทดสอบมาตรฐานทั้ง 14 ตัวของ **Evolution Engine** เพื่อใช้ในการทดสอบความถูกต้องแบบ End-to-End และการันตีความสามารถในการ Replay ผลลัพธ์ซ้ำแบบ Bit-Identical (`R4`):

---

## 📁 โครงสร้างโปรเจกต์ทดสอบ

```text
benchmarks/golden/
├── manifest.yaml                  # รายการสรุปและเกณฑ์ Disposition ของทั้ง 14 เคส
├── mvp01_pure_function/           # MVP-01: Pure Function Optimization
├── mvp02_stateful_cache/          # MVP-02: Stateful Class & Cache Mutation
├── mvp03_multi_objective/         # MVP-03: Multi-Objective Latency vs Memory
├── mvp04_async_io/                # MVP-04: Asyncio Coroutines & Non-blocking
├── mvp05_multi_file_dag/          # MVP-05: Multi-file Project DAG
├── mvp06_quantum_rotation/        # MVP-06: Quantum Qubit Rotation Operator
├── mvp07_polyglot_rust/           # MVP-07: Python -> Rust Native Compilation
├── mvp08_sec_fs_escape/           # MVP-08: Filesystem Traversal Attack Vector
├── mvp09_sec_net_socket/          # MVP-09: Network Egress Attack Vector
├── mvp10_sec_forkbomb/            # MVP-10: Fork Bomb PID Exhaustion Attack
├── mvp11_flaky_isolation/         # MVP-11: Flaky Test Non-Gaming Verification
├── mvp12_crash_commit/            # MVP-12: 2PC Crash Recovery Chaos Test
├── mvp13_p2p_swarm_byzantine/     # MVP-13: Byzantine Malicious Peer Rejection
└── mvp14_self_evaluator_freeze/   # MVP-14: Engine Self-Evolution Protection
```
