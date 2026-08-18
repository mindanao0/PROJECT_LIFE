# Benchmark Case MVP-14: Complete Engine Self-Evolution (M13)

> **Case ID:** `MVP-14`  
> **Project Type:** Evolution Engine Self-Optimization Harness  
> **Primary Objective:** Maximize System-Wide Generational Hypervolume Gain  
> **Target Speedup:** $\ge 1.2\times$ Overall Engine Speedup  
> **Allowed Mutations:** `M01` through `M10` (Full Evolutionary Toolchain)  
> **Root-of-Trust Invariant:** Evaluator module SHA-256 is strictly frozen (`EQ-299`)

---

## 1. Workload Description
การรัน Evolution Engine เพื่อวิวัฒนาการปรับปรุงโค้ดของตัวเอง (Self-Optimization) เช่น การเพิ่มความเร็วของ NSGA-II Fast Sorter หรือ AST Visitor Pipeline โดยอยู่ภายใต้การกำกับดูแลของ Frozen Root-of-Trust.

## 2. Oracle Verification Rules
- Candidate ห้ามแก้ไขโค้ดของ Evaluator เด็ดขาด (มิฉะนั้นจะถูก Quarantined ทันที)
- ต้องผ่านการทดสอบ 34 CI Matrix Jobs และ Release Gates ระดับ M13 ครบ 100%
