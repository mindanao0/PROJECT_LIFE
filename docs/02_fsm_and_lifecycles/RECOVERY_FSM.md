# Recovery & Crash Resilience FSM Specification (9 States)

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** FSM SPECIFICATION (L2 Authority)
> **Target Subsystem:** Disaster Recovery & Storage Reconciler  
> **Governing Equations:** `EQ-024` (Recovery Idempotency Loop), `EQ-285` (Disaster Recovery SLOs: RTO $\le 60$s, RPO $\le 1$ Gen), `EQ-267` (DB Reconstruction)

---

## 1. Complete 9-State Topology

วงจรสถานะการกู้คืนระบบจากภาวะ Crash, ตัดไฟกะทันหัน หรือข้อมูลขัดข้อง (9 Recovery States):

```text
       [DETECT_CRASH]
             │
             ▼
     [SCAN_WAL_AND_CAS]
             │
             ▼
    [VERIFY_LAST_GEN_HASH] ───────┐ (Integrity Failure)
             │                     │
             ▼                     ▼
    [ROLLBACK_UNCOMMITTED]    [ENTER_EMERGENCY_SAFE_MODE]
             │                     │
             ▼                     ▼
     [REPLAY_COMMITTED]       [RECONSTRUCT_FROM_CAS]
             │                     │
             ▼                     │
    [RECONCILE_DB_STATE] ◄────────┘
             │
             ▼
     [RESTORED_READY]
```

### 1.1 Formal State Definitions
1. `DETECT_CRASH`: ตรวจพบ Lock File ค้าง หรือสถานะ Run ไม่ได้จบแบบ `COMPLETED`/`FAILED`
2. `SCAN_WAL_AND_CAS`: สแกน SQLite WAL File และตรวจนับ Blob ใน Content-Addressed Storage
3. `VERIFY_LAST_GEN_HASH`: คำนวณ SHA-256 Digest ของ Generation Manifest ล่าสุดเทียบกับค่าในฐานข้อมูล
4. `ROLLBACK_UNCOMMITTED`: สั่ง Rollback Transaction ที่ค้างอยู่ก่อนจบรุ่น เพื่อขจัดข้อมูลที่ไม่สมบูรณ์
5. `REPLAY_COMMITTED`: Replay เฉพาะ Event และ State ที่ได้รับการ Commit ใน CAS เรียบร้อยแล้ว
6. `ENTER_EMERGENCY_SAFE_MODE`: เข้าสู่โหมดปลอดภัยเมื่อพบความไม่สอดคล้องของข้อมูลระดับลึก
7. `RECONSTRUCT_FROM_CAS`: สร้างฐานข้อมูล SQLite ขึ้นใหม่ทั้งหมดจาก CAS Generation Manifests
8. `RECONCILE_DB_STATE`: ตรวจสอบความถูกต้องสมบูรณ์ของ Foreign Keys และ Triggers ด้วย `PRAGMA integrity_check`
9. `RESTORED_READY`: การกู้คืนเสร็จสิ้น ระบบพร้อมกลับสู่สถานะ `RUNNING` หรือ `COMPLETED`

---

## 2. Transition Rules Matrix & Recovery Actions

```text
┌───────────────────────────┬──────────────────────┬─────────────────────────────┬─────────────────────────────────┐
│ Current State             │ Event / Trigger      │ Next State                  │ Concrete Action & Recovery Step │
├───────────────────────────┼──────────────────────┼─────────────────────────────┼─────────────────────────────────┤
│ DETECT_CRASH              │ LockFound            │ SCAN_WAL_AND_CAS            │ Acquire recovery lock file      │
│ SCAN_WAL_AND_CAS          │ ScanComplete         │ VERIFY_LAST_GEN_HASH        │ Parse CAS objects & WAL headers │
│ VERIFY_LAST_GEN_HASH      │ HashMatch            │ ROLLBACK_UNCOMMITTED        │ Last generation verified OK     │
│ VERIFY_LAST_GEN_HASH      │ HashMismatch         │ ENTER_EMERGENCY_SAFE_MODE   │ Corrupt generation detected     │
│ ROLLBACK_UNCOMMITTED      │ RollbackDone         │ REPLAY_COMMITTED            │ Revert uncommitted DB rows      │
│ REPLAY_COMMITTED          │ ReplayDone           │ RECONCILE_DB_STATE          │ Restore committed candidates    │
│ ENTER_EMERGENCY_SAFE_MODE │ UserApproveRebuild   │ RECONSTRUCT_FROM_CAS        │ Clean corrupt DB, rebuild       │
│ RECONSTRUCT_FROM_CAS      │ RebuildDone          │ RECONCILE_DB_STATE          │ Full DB rebuilt from CAS        │
│ RECONCILE_DB_STATE        │ IntegrityOK          │ RESTORED_READY              │ PRAGMA integrity_check PASS     │
│ RECONCILE_DB_STATE        │ IntegrityFail        │ ENTER_EMERGENCY_SAFE_MODE   │ Re-trigger repair pipeline      │
└───────────────────────────┴──────────────────────┴─────────────────────────────┴─────────────────────────────────┘
```

---

## 3. Disaster Recovery SLOs & Mathematical Bounds

1. **Recovery Time Objective (RTO):** การกู้คืนระบบต้องเสร็จสิ้นภายในเวลา $\le 60.0$ วินาที:
   $$\text{RTO} \le 60.0\text{ s}$$
2. **Recovery Point Objective (RPO):** สูญเสียข้อมูลได้ไม่เกิน 1 Generation (ข้อมูลที่ Commit แล้วใน CAS จะไม่มีวันสูญหาย):
   $$\text{RPO} \le 1\text{ Generation}$$
3. **Idempotency Guarantee:** การรันกระบวนการ Recovery ซ้ำหลายๆ ครั้ง ต้องให้ผลลัพธ์ของฐานข้อมูลตรงกัน 100%:
   $$\text{Recovery}(\text{Recovery}(\text{DB})) \equiv \text{Recovery}(\text{DB})$$
