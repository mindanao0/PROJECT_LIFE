# Benchmark Case MVP-12: 2PC Crash Recovery Chaos Test

> **Case ID:** `MVP-12`
> **Scope:** reliability — ความน่าเชื่อถือ
> **Entry point:** `src/storage.py:commit`
> **Expected disposition:** `RESTORED_READY` — ต้องกู้คืนสำเร็จจนกลับสู่สถานะพร้อมใช้งาน
> **Reproducibility target:** `R1`

---

## 1. Workload

2PC Crash Recovery Chaos Test

ค่าทั้งหมดข้างบนมาจาก `benchmarks/golden/manifest.yaml` ซึ่งเป็น canonical source
ของ golden corpus ห้ามแก้ไฟล์นี้ให้ขัดกับ manifest

## 2. Fixture status

ยังไม่มี fixture จริงในเคสนี้ — ต้องสร้าง `src/storage.py` ที่นิยาม `commit`
พร้อม test suite และ baseline ก่อนจึงจะนับว่าผ่านตาม `REQ-S16-001`
โดย `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น
ห้ามใส่ค่า placeholder
