# Benchmark Case MVP-02: Stateful Class & Cache Mutation

> **Case ID:** `MVP-02`
> **Scope:** module — โมดูล
> **Entry point:** `src/lru_cache.py:LRUCache`
> **Expected disposition:** `SELECTED` — ต้องถูกเลือกเป็น candidate ที่ดีขึ้น
> **Reproducibility target:** `R4`

---

## 1. Workload

Stateful Class & Cache Mutation

ค่าทั้งหมดข้างบนมาจาก `benchmarks/golden/manifest.yaml` ซึ่งเป็น canonical source
ของ golden corpus ห้ามแก้ไฟล์นี้ให้ขัดกับ manifest

## 2. Fixture status

ยังไม่มี fixture จริงในเคสนี้ — ต้องสร้าง `src/lru_cache.py` ที่นิยาม `LRUCache`
พร้อม test suite และ baseline ก่อนจึงจะนับว่าผ่านตาม `REQ-S16-001`
โดย `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น
ห้ามใส่ค่า placeholder
