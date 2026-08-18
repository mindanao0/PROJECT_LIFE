# Benchmark Case MVP-03: Multi-Objective Latency vs Memory

> **Case ID:** `MVP-03`
> **Scope:** module — โมดูล
> **Entry point:** `src/string_indexer.py:build_index`
> **Expected disposition:** `SELECTED` — ต้องถูกเลือกเป็น candidate ที่ดีขึ้น
> **Reproducibility target:** `R2`

---

## 1. Workload

Multi-Objective Latency vs Memory

ค่าทั้งหมดข้างบนมาจาก `benchmarks/golden/manifest.yaml` ซึ่งเป็น canonical source
ของ golden corpus ห้ามแก้ไฟล์นี้ให้ขัดกับ manifest

## 2. Fixture status

ยังไม่มี fixture จริงในเคสนี้ — ต้องสร้าง `src/string_indexer.py` ที่นิยาม `build_index`
พร้อม test suite และ baseline ก่อนจึงจะนับว่าผ่านตาม `REQ-S16-001`
โดย `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น
ห้ามใส่ค่า placeholder
