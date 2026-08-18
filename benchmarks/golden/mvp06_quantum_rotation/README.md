# Benchmark Case MVP-06: Quantum Qubit Rotation Operator

> **Case ID:** `MVP-06`
> **Scope:** function — ฟังก์ชันเดี่ยว
> **Entry point:** `src/combinatorial.py:tsp_solver`
> **Expected disposition:** `SELECTED` — ต้องถูกเลือกเป็น candidate ที่ดีขึ้น
> **Reproducibility target:** `R2`

---

## 1. Workload

Quantum Qubit Rotation Operator

ค่าทั้งหมดข้างบนมาจาก `benchmarks/golden/manifest.yaml` ซึ่งเป็น canonical source
ของ golden corpus ห้ามแก้ไฟล์นี้ให้ขัดกับ manifest

## 2. Fixture status

ยังไม่มี fixture จริงในเคสนี้ — ต้องสร้าง `src/combinatorial.py` ที่นิยาม `tsp_solver`
พร้อม test suite และ baseline ก่อนจึงจะนับว่าผ่านตาม `REQ-S16-001`
โดย `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น
ห้ามใส่ค่า placeholder
