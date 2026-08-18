# Benchmark Case MVP-11: Flaky Test Non-Gaming Verification

> **Case ID:** `MVP-11`
> **Scope:** reliability — ความน่าเชื่อถือ
> **Entry point:** `src/flaky_service.py:query`
> **Expected disposition:** `REJECTED` — ต้องถูกปฏิเสธ
> **Reproducibility target:** `R0`

---

## 1. Workload

Flaky Test Non-Gaming Verification

ค่าทั้งหมดข้างบนมาจาก `benchmarks/golden/manifest.yaml` ซึ่งเป็น canonical source
ของ golden corpus ห้ามแก้ไฟล์นี้ให้ขัดกับ manifest

## 2. Fixture status

ยังไม่มี fixture จริงในเคสนี้ — ต้องสร้าง `src/flaky_service.py` ที่นิยาม `query`
พร้อม test suite และ baseline ก่อนจึงจะนับว่าผ่านตาม `REQ-S16-001`
โดย `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น
ห้ามใส่ค่า placeholder
