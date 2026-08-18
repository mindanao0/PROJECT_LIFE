# Artificial-Life (ALife) Ecosystem Co-Evolution

> **Subsystem:** Adversarial Co-Evolution & Niche Energy Accounting  
> **Authority Level:** NORMATIVE (Integrated Core v1 Architecture)

---

## 1. Prey vs Predator Co-Evolution Mechanics

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             ALIFE ECOSYSTEM DYNAMICS                             │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. Prey Population (Candidate Programs):                                         │
│    • มุ่งเน้นการเพิ่มประสิทธิภาพ (Speed/Memory) และผ่าน Test Suite               │
│    • ได้รับ Energy Credits เมื่อสามารถเอาชนะ Predator Tests ได้                  │
│                                                                                  │
│ 2. Predator Population (Adversarial Test Generators):                            │
│    • มุ่งเน้นการสร้าง Worst-Case Inputs, Edge Cases, และ Fuzzing Payloads        │
│    • ได้รับ Energy Credits เมื่อค้นพบ Input ที่ทำให้ Candidate ทำงานช้าลง        │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Niche Specialization & Energy Credits

- **Energy Accounting:** Candidate ที่ไม่ได้รับ Energy Credit ต่อเนื่องเกิน 3 รุ่น จะถูกคัดทิ้งเนื่องจากขาดพลังงาน (Starvation Pruning)
- **Niche Carrying Capacities:** พื้นที่ค้นหาถูกแบ่งออกเป็น Niches ย่อย (เช่น Memory Niche, Latency Niche, Concurrency Niche) โดยแต่ละ Niche มีโควตาประชากรสูงสุดเพื่อป้องกันการผูกขาด
