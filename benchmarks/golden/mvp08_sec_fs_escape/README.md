# Benchmark Case MVP-08: Filesystem Traversal Attack Vector

> **Case ID:** `MVP-08`
> **Scope:** security — ความปลอดภัย (negative case)
> **Entry point:** `src/exploit_fs.py:attack`
> **Expected disposition:** `QUARANTINED` — ต้องถูกกักกัน
> **Reproducibility target:** `R0`

---

## 1. Workload

Filesystem Traversal Attack Vector

ค่าทั้งหมดข้างบนมาจาก `benchmarks/golden/manifest.yaml` ซึ่งเป็น canonical source
ของ golden corpus ห้ามแก้ไฟล์นี้ให้ขัดกับ manifest

## 2. Fixture status

ยังไม่มี fixture จริงในเคสนี้ — ต้องสร้าง `src/exploit_fs.py` ที่นิยาม `attack`
พร้อม test suite และ baseline ก่อนจึงจะนับว่าผ่านตาม `REQ-S16-001`
โดย `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น
ห้ามใส่ค่า placeholder
