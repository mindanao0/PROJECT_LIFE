# Evolutionary Stagnation & 4-Tier Escalation Ladder

> **Subsystem:** Stagnation Recovery & Diversity Reseeding  
> **Authority Level:** NORMATIVE (`REQ-S10-010`)

---

## 1. Stagnation Detection Metric

ระบบมอนิเตอร์จำนวนรุ่นติดต่อกัน ($g$) ที่ค่า **Hypervolume** หรือขนาดของ **Pareto Front ลำดับที่ 1 ($F_1$)** ไม่มีการขยายตัว:

$$\Delta \text{Front}(g) = 0 \quad \text{for } g \ge G_{\text{stagnant}}$$

---

## 2. The 4 Escalation Tiers

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   STAGNATION ESCALATION LADDER (TIERS 1 - 4)                     │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Tier 1 (หลัง 5 Generations):                                                     │
│   • เพิ่ม Mutation Temperature: ขยาย Mutation Rate μ จาก 0.05 สู่ 0.20           │
│                                                                                  │
│ Tier 2 (หลัง 10 Generations):                                                    │
│   • กระตุ้น Hyper-Mutation Mode: สุ่มเปลี่ยนโครงสร้าง AST ขนาดใหญ่ (M06/M08)     │
│                                                                                  │
│ Tier 3 (หลัง 15 Generations):                                                    │
│   • Hippocampal Memory Injection: ฉีด Candidate จากคลัง Long-term Memory         │
│                                                                                  │
│ Tier 4 (หลัง 20 Generations):                                                    │
│   • Cataclysmic Re-Seeding: ตัดประชากร 50% และสุ่มสายพันธุ์ใหม่เข้ามาแทน         │
└──────────────────────────────────────────────────────────────────────────────────┘
```
