# Benchmark Case MVP-01: Pure Function Optimization

> **Case ID:** `MVP-01`
> **Scope:** function — ฟังก์ชันเดี่ยว
> **Entry point:** `src/math_kernel.py:compute_series`
> **Expected disposition:** `SELECTED` — ต้องถูกเลือกเป็น candidate ที่ดีขึ้น
> **Reproducibility target:** `R4`

---

## 1. Workload

Pure Function Optimization

ค่าทั้งหมดข้างบนมาจาก `benchmarks/golden/manifest.yaml` ซึ่งเป็น canonical source
ของ golden corpus ห้ามแก้ไฟล์นี้ให้ขัดกับ manifest

## 2. Fixture status

ยังไม่มี fixture จริงในเคสนี้ — ต้องสร้าง `src/math_kernel.py` ที่นิยาม `compute_series`
พร้อม test suite และ baseline ก่อนจึงจะนับว่าผ่านตาม `REQ-S16-001`
โดย `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น
ห้ามใส่ค่า placeholder
