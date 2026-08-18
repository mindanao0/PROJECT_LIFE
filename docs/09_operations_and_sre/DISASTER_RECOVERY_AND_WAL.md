# Disaster Recovery, Crash Semantics & SQLite WAL Architecture

> **Subsystem:** Reliability, Disaster Recovery & Storage Durability  
> **Authority Level:** NORMATIVE (`REQ-S13-008`, `REQ-S14-002`)

---

## 1. Disaster Recovery Service Level Objectives (SLOs)

- **Recovery Time Objective (RTO):** $\le 60\text{ seconds}$ สำหรับการกู้คืนฐานข้อมูล SQLite และ CAS ให้พร้อมเริ่มรันต่อ
- **Recovery Point Objective (RPO):** $\le 1\text{ Generation}$ (ไม่สูญเสียข้อมูลของ Generation ที่ได้รับการ Commit แล้ว)

---

## 2. SQLite WAL (Write-Ahead Logging) Configuration

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA wal_autocheckpoint = 1000;
PRAGMA busy_timeout = 5000;
```

### Invariants:
- WAL Mode ช่วยให้ Readers (เช่น CLI `evolve status` หรือ Monitoring Probes) สามารถอ่านข้อมูลได้พร้อมกันโดยไม่บล็อก Single-Writer Coordinator
- หากเกิดเหตุไฟฟ้าดับ SQLite Engine จะทำ Automatic Recovery จากไฟล์ `.evolution/db.sqlite-wal` อัตโนมัติเมื่อเปิดไฟล์ใหม่
