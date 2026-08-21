# Evolution Engine — Next-Generation Autonomous Software Optimization System

> **Specification Authority:** [spec/ACTIVE_CONTRACT.md](spec/ACTIVE_CONTRACT.md)  
> **Master 300-Dimensional Framework:** 🌐 **[docs/300_DIMENSIONAL_HYPER_SYSTEM_FRAMEWORK.md](docs/300_DIMENSIONAL_HYPER_SYSTEM_FRAMEWORK.md)**  
> **Master 300 Canonical Equations:** 🧮 **[docs/05_math_and_selection/300_CANONICAL_MATHEMATICAL_EQUATIONS.md](docs/05_math_and_selection/300_CANONICAL_MATHEMATICAL_EQUATIONS.md)**  
> **Documentation Hub:** 📚 **[docs/README.md](docs/README.md)**  
> **Version:** `10.2.2` | **Current Maturity:** `M6_SECURITY` | **Default Mode:** `SAFE_EXPORT_ONLY`

---

## 🌟 ภาพรวมระบบ (System Overview)

**Evolution Engine** เป็นระบบอัตโนมัติแบบ **Offline-first population-based evolutionary computation** ที่รับ source code ของโปรเจกต์ภาษา Python แล้วสร้างประชากรของ candidate programs จาก source เดิม เพื่อค้นหาและปรับปรุงประสิทธิภาพของโค้ดอย่างเป็นระบบ โดยไม่พึ่งพา LLM หรือ Cloud API ภายนอก

ระบบได้รับการออกแบบภายใต้ **300 มิติวิศวกรรมเฉพาะทาง (`DIM-001` ถึง `DIM-300`)** ที่ผูกโยงเข้ากับ **300 มหาสมการคณิตศาสตร์แม่บท (`EQ-001` ถึง `EQ-300`)** แบบ 1-to-1 บริบูรณ์

---

## 🏛️ โครงสร้างคลังเอกสารและสเปกโมดูลาร์ (Modular Architecture Hub)

เอกสารข้อกำหนดทั้งหมดถูกแยกหมวดหมู่อย่างเป็นระเบียบในโฟลเดอร์ `docs/`:

- 🌐 **[docs/300_DIMENSIONAL_HYPER_SYSTEM_FRAMEWORK.md](docs/300_DIMENSIONAL_HYPER_SYSTEM_FRAMEWORK.md)** — สารบัญและข้อกำหนดเชิงลึก 300 มิติ
- 🧮 **[docs/05_math_and_selection/300_CANONICAL_MATHEMATICAL_EQUATIONS.md](docs/05_math_and_selection/300_CANONICAL_MATHEMATICAL_EQUATIONS.md)** — คลัง 300 มหาสมการคณิตศาสตร์แม่บท
- 📁 **[docs/01_architecture/](docs/01_architecture)** — วิสัยทัศน์, Concurrency Single-Writer, Exceptions, ADRs
- 📁 **[docs/02_fsm_and_lifecycles/](docs/02_fsm_and_lifecycles)** — 5 Finite State Machines (Candidate, Run, Recovery, Governance, Deployment)
- 📁 **[docs/03_storage_and_database/](docs/03_storage_and_database)** — SQLite DDL 31 ตาราง, Triggers, CAS Engine, 2PC Commit
- 📁 **[docs/04_representation_and_mutation/](docs/04_representation_and_mutation)** — AST/CST, Python 3.12, M01-M08, Quantum M09, Polyglot Rust M10
- 📁 **[docs/05_math_and_selection/](docs/05_math_and_selection)** — Pareto Dominance, Zhang-Shasha, Welch/TOST/Holm, UCB1, Swarm
- 📁 **[docs/06_security_and_sandboxing/](docs/06_security_and_sandboxing)** — PROFILE_A Linux Namespaces, cgroups v2, Seccomp BPF, Ed25519
- 📁 **[docs/07_schemas_and_protocols/](docs/07_schemas_and_protocols)** — 26 JSON Schemas Blueprint, 19 Core v1 Typed Protocols, SDK, CLI
- 📁 **[docs/08_testing_and_verification/](docs/08_testing_and_verification)** — QA 7 Tiers, Hypothesis PBT, 14 Golden Cases, Signed Evidence
- 📁 **[docs/09_operations_and_sre/](docs/09_operations_and_sre)** — Reason Codes, Latency Budgets, WAL Recovery, 34 CI Jobs
- 📁 **[docs/10_governance_and_roadmap/](docs/10_governance_and_roadmap)** — Maturity M0-M13, Governed Change, 176 Requirement Traceability
