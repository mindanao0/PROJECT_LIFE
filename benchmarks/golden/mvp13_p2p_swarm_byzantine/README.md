# Benchmark Case MVP-13: Byzantine Malicious Peer Rejection

> **Case ID:** `MVP-13`
> **Scope:** swarm — เครือข่าย P2P (negative case)
> **Entry point:** `src/peer_node.py:sync`
> **Expected disposition:** `QUARANTINED` — ต้องถูกกักกัน
> **Reproducibility target:** `R0`

---

## 1. Workload

Byzantine Malicious Peer Rejection

ค่าทั้งหมดข้างบนมาจาก `benchmarks/golden/manifest.yaml` ซึ่งเป็น canonical source
ของ golden corpus ห้ามแก้ไฟล์นี้ให้ขัดกับ manifest

## 2. Fixture status

ยังไม่มี fixture จริงในเคสนี้ — ต้องสร้าง `src/peer_node.py` ที่นิยาม `sync`
พร้อม test suite และ baseline ก่อนจึงจะนับว่าผ่านตาม `REQ-S16-001`
โดย `baseline_hash` ต้องคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น
ห้ามใส่ค่า placeholder
