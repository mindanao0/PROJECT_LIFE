# Two-Phase Generation Commit Protocol (2PC) Specification

> **Authority Level:** NORMATIVE STORAGE SPECIFICATION (L5 Authority)  
> **Target Subsystem:** Coordinator Commit Protocol & Persistence Orchestrator  
> **Governing Equations:** `EQ-264` (7-State 2PC Loop), `EQ-265` (Generation Manifest Durability), `EQ-266` (Atomic Rollback)

---

## 1. The 7-State Two-Phase Commit FSM

การบันทึกผลลัพธ์ของ Generation หนึ่งๆ ต้องดำเนินตามกระบวนการ Two-Phase Commit (2PC) ครบ 7 สถานะอย่างเคร่งครัด:

```text
       [1. PREPARING]
             │ (Serialize Artifacts & Compute Hashes)
             ▼
    [2. CAS_OBJECTS_DURABLE]
             │ (fsync all blobs to .evolution/cas/)
             ▼
   [3. DB_TRANSACTION_OPEN]
             │ (BEGIN IMMEDIATE TRANSACTION)
             ▼
     [4. DB_ROWS_WRITTEN]
             │ (INSERT candidates, metrics, lineage)
             ▼
      [5. DB_COMMITTED]
             │ (COMMIT TRANSACTION & WAL Checkpoint)
             ▼
 [6. GENERATION_MANIFEST_DURABLE]
             │ (Write generation_manifest.json to CAS)
             ▼
       [7. COMMITTED]
```

---

## 2. Crash Handling & Rollback Points

```text
┌──────────────────────────────┬───────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Crash Stage Occurrence       │ Database Status at Crash      │ Recovery Action on Reboot                                   │
├──────────────────────────────┼───────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ Crash during Stage 1-2       │ No DB Transaction open        │ Clean tmp CAS files, re-evaluate generation                 │
│ Crash during Stage 3-4       │ DB Transaction still OPEN     │ SQLite auto-rollbacks transaction on startup; CAS intact    │
│ Crash during Stage 5         │ DB committed, manifest missing│ Read DB rows, rebuild and write generation manifest to CAS  │
│ Crash during Stage 6-7       │ Fully committed and durable   │ Fast-forward to COMMITTED state                             │
└──────────────────────────────┴───────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Invariant Guarantees

1. **All-or-Nothing Guarantee:** ไม่มีกรณีที่ Candidate ได้รับการบันทึกใน SQLite แต่ซอร์สโค้ดใน CAS สูญหาย
2. **Deterministic Manifest Verification:** Generation Manifest ที่สร้างขึ้นต้องมี Hash ตรงกับข้อมูลในตาราง `generations(manifest_hash)`
