# Benchmark Case MVP-14: Engine Self-Evolution Protection

> **Case ID:** `MVP-14`
> **Scope:** self_evolution — การวิวัฒนาการตัวเอง
> **Entry point:** `src/evaluator.py:evaluate`
> **Expected disposition:** `QUARANTINED` — ต้องถูกกักกัน
> **Reproducibility target:** `R0`

---

## 1. Workload

Engine Self-Evolution Protection

ค่าทั้งหมดข้างบนมาจาก `benchmarks/golden/manifest.yaml` ซึ่งเป็น canonical source
ของ golden corpus ห้ามแก้ไฟล์นี้ให้ขัดกับ manifest

## 2. Fixture status

ยังไม่มี fixture จริงในเคสนี้ — ต้องสร้าง `src/evaluator.py` ที่นิยาม `evaluate`
พร้อม test suite และ baseline ก่อนจึงจะนับว่าผ่านตาม `REQ-S16-001`
โดย `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น
ห้ามใส่ค่า placeholder
