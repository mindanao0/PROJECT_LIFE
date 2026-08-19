# 11 — Architecture Decision Records (ADRs)

> **Dimension:** Architectural Governance & Design Rationale  
> **Status:** Active / Normative Foundations

เอกสารฉบับนี้บันทึกเหตุผลการตัดสินใจทางสถาปัตยกรรม (Architecture Decision Records) ซึ่งอธิบายถึงสาเหตุ ปัจจัยสนับสนุน ผลกระทบ และทางเลือกที่ถูกปฏิเสธในการออกแบบ Evolution Engine

---

## 📋 ดัชนี ADR ทั้งหมด

| รหัส | หัวข้อการตัดสินใจ (Decision Title) | สถานะ |
|:---:|---|:---:|
| **ADR-001** | การใช้ Pure AST/CST Mutation แทน LLM / Generative AI ใน Core Engine | **ACCEPTED** |
| **ADR-002** | การใช้ Multi-Objective Pareto Dominance แทน Single Weighted-Sum Fitness | **ACCEPTED** |
| **ADR-003** | สถาปัตยกรรม Dual-Storage: SQLite Relational + CAS Immutable Blobs | **ACCEPTED** |
| **ADR-004** | การใช้ Native Linux Namespaces, cgroups v2 และ Seccomp แทน Docker Daemon | **ACCEPTED** |
| **ADR-005** | การบังคับใช้ Canonical Decimal Strings แทน IEEE 754 Binary Floating-Point | **ACCEPTED** |

---

## ADR-001: Pure AST/CST Mutation vs LLM / Generative AI in Core

### Context & Problem Statement
ระบบวิวัฒนาการซอฟต์แวร์ต้องการความสามารถในการปรับปรุงโค้ดอย่างต่อเนื่องและเชื่อถือได้ ปัจจุบันมีแนวโน้มการนำ Large Language Model (LLM) มาใช้ในการสร้างโค้ด เราจำเป็นต้องตัดสินใจว่าจะใช้ LLM หรือใช้ Pure Program Representation (AST/CST) ใน Core Engine

### Decision Outcome
**เลือกใช้: Pure AST/CST Mutation**
- Core Engine จะไม่มีการ import, dependency หรือ API call ใดๆ ไปยัง LLM
- การค้นหาคำตอบจะใช้ Population-based Evolutionary Search บนโครงสร้าง Syntax Tree

### Rationale & Positive Consequences
1. **Deterministic & Replayable (R4):** การใช้ Seeded RNG ร่วมกับ AST Mutator ทำให้การรันซ้ำให้ผลลัพธ์บิตต่อบิตตรงกัน 100% ซึ่ง LLM ทำไม่ได้
2. **Offline-First & Zero Cost:** สามารถรันบน Air-gapped server หรือเครื่องทดลองโดยไม่มีค่า Token Cost หรือปัญหา Network Latency
3. **Formal Safety Invariants:** สามารถตรวจสอบกฎไวยากรณ์ด้วย AST Visitor ได้อย่างสมบูรณ์แบบก่อนรันโค้ดจริง

### Negative Consequences / Trade-offs
- การสร้างฟังก์ชันใหม่ทั้งหมดจากศูนย์ (De novo synthesis) ทำได้ช้ากว่าการ Prompt LLM แต่เหมาะสมอย่างยิ่งสำหรับงาน Optimization และ Refactoring โค้ดที่มีอยู่แล้ว

---

## ADR-002: Multi-Objective Pareto Dominance vs Weighted-Sum

### Context & Problem Statement
ในการปรับปรุงซอฟต์แวร์ เป้าหมายมักจะขัดแย้งกันเอง (Conflicting Objectives) เช่น การเพิ่ม Throughput มักกิน Memory สูงขึ้น เราต้องการวิธีตัดสินใจคัดเลือก Candidate ที่ยุติธรรมและครอบคลุม Trade-off Space

### Decision Outcome
**เลือกใช้: Multi-Objective Pareto Dominance**
- ตัดสินอันดับของ Candidate ด้วย Pareto Fronts ($F_1, F_2, \dots$) โดยไม่ใช้น้ำหนักถ่วง
- ใช้น้ำหนัก Preference Weight เฉพาะกรณีที่ Candidate อยู่ใน Front เดียวกันและมี Diversity Score เสมอกัน

### Rationale & Positive Consequences
1. **Eliminate Arbitrary Bias:** การรวมคะแนนด้วย $\sum w_i x_i$ บังคับให้ผู้ใช้ต้องเดาค่าน้ำหนักล่วงหน้า ซึ่งทำให้ระบบพลาดโซลูชันที่เป็น Trade-off ที่ดีเลิศ
2. **Preserve Solution Diversity:** Pareto Frontier รักษาประชากรหลากหลายสายพันธุ์ (เช่น สายพันธุ์ที่เน้นความเร็วสูงสุด กับสายพันธุ์ที่เน้นประหยัดแรมสูงสุด) ไว้ในประชากรเดียวกัน

---

## ADR-003: SQLite Relational Database + CAS Immutable Storage

### Context & Problem Statement
ระบบต้องจัดเก็บทั้งโครงสร้างความสัมพันธ์ (Metadata, FSM State, Lineage Graph) และไฟล์ไบนารีขนาดใหญ่ (Source Snapshots, Output Logs, Checkpoints) การเก็บทุกอย่างในฐานข้อมูลอย่างเดียวทำให้ DB บวม หรือการเก็บในไฟล์อย่างเดียวทำให้ Query ความสัมพันธ์ยาก

### Decision Outcome
**เลือกใช้: สถาปัตยกรรม Dual-Storage**
- **SQLite (31 Tables):** จัดเก็บ Relational Metadata, Invariants, และ Audit Indices พร้อม Foreign Key Cascade
- **Content-Addressed Storage (CAS):** จัดเก็บ Immutable Blobs ในโฟลเดอร์แยกโดยใช้ชื่อไฟล์เป็น SHA-256

### Rationale & Positive Consequences
1. **Lightweight & Embedded:** SQLite ไม่ต้องติดตั้ง Server Daemon แยก สะดวกต่อการพกพา
2. **Crash-Resilience:** เมื่อรวมกับ Generation Commit Protocol หาก SQLite พัง สามารถกู้คืน (Reconstruct) ข้อมูลทั้งหมดได้จาก CAS Manifests

---

## ADR-004: Native Linux Kernel Isolation vs Docker Daemon

### Context & Problem Statement
Candidate Code เป็นโค้ดที่ไม่น่าไว้วางใจและอาจมีคำสั่งอันตราย เราต้องการระบบ Sandbox ที่ปลอดภัยสูงสุดและมี Overhead ในการสร้าง/ทำลาย Process ต่ำที่สุด

### Decision Outcome
**เลือกใช้: Native Linux Namespaces + cgroups v2 + Seccomp BPF (PROFILE_A_LINUX)**
- ควบคุมการแยก Process โดยตรงผ่าน Linux System Calls
- รองรับ Rootless OCI (`runc`) เป็นทางเลือกลำดับถัดไป

### Rationale & Positive Consequences
1. **Sub-Millisecond Spawn Latency:** การสร้าง Linux Namespace ทำได้ในระดับ 1–5 มิลลิวินาที เทียบกับ Docker Daemon ที่ใช้ 200–800 มิลลิวินาที
2. **Rootless & Daemonless:** ไม่ต้องรัน Docker Daemon ที่ต้องการสิทธิ์ Root บน Host ลดความเสี่ยง Privilege Escalation

---

## ADR-005: Exact Canonical Decimal Strings vs Floating-Point

### Context & Problem Statement
ในการคำนวณ Hash Identity ของ Config, Evidence และ Result Manifests การใช้ IEEE 754 Floating-Point มักเจอปัญหา Floating-Point Rounding Error ที่ให้ค่าต่างกันเล็กน้อยเมื่อรันบน CPU ต่างสถาปัตยกรรม (เช่น x86_64 vs ARM64)

### Decision Outcome
**เลือกใช้: Exact Decimal Strings (เช่น `"0.001"`) และ Integer**
- ห้ามใช้ Binary Floating-Point ใน Hash-Critical Serialization ทั้งหมด

### Rationale & Positive Consequences
1. **Cross-Architecture Hash Identity:** ค่า SHA-256 ของ Manifest จะตรงกัน 100% ไม่ว่าจะคำนวณบน Intel, AMD, Apple Silicon หรือ Graviton
2. **Lossless Serialization:** ค่าทศนิยมที่กำหนดโดยผู้ใช้จะไม่สูญเสียความแม่นยำจากการแปลงเป็นฐานสอง
