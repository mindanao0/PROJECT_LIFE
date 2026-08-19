# SQLite Integrity Triggers & Polymorphic Validation Specification

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.    
> **ตัวจริงอยู่ที่** [`spec/ACTIVE_CONTRACT.md`](../../spec/ACTIVE_CONTRACT.md) section 13.2 ระหว่าง marker `INTEGRITY_TRIGGERS_BEGIN`/`END` generate ด้วย [`tools/generate_integrity_triggers.py`](../../tools/generate_integrity_triggers.py)  
> SQL ที่เคยอยู่ในไฟล์นี้อ้างตาราง `evaluations` และคอลัมน์ `NEW.seq` ซึ่งไม่มีอยู่จริง ทำให้ `INSERT` ลง `artifact_refs` ล้มทุก owner_type จึงถูกถอดออกที่ CR-0002
> **Scope:** STORAGE SPECIFICATION (L5 Authority)
> **Target Subsystem:** Relational Storage Engine (`.evolution/db.sqlite`)  
> **Governing Equations:** `EQ-253` (Polymorphic Trigger Verification), `EQ-254` (Monotonic Audit Sequence Increment)

---

## 1. Executive Summary

เอกสารฉบับนี้กำหนด **SQLite Triggers** ที่ทำงานระดับเคอร์เนลฐานข้อมูลเพื่อคุ้มครองความถูกต้องของข้อมูล (Referential Integrity) สำหรับ Polymorphic References ในตาราง `artifact_refs`, `lineage_edges`, `quarantine_records`, และการบังคับใช้หมายเลข Sequence ต่อเนื่องแบบ Monotonic ในตาราง `audit_events`.

---

## 2. Complete SQL Triggers DDL Implementation


---

## 3. Trigger Invariants & Verification Proofs

1. **Polymorphic Reference Soundness:** ป้องกันการแทรก Orphan Artifact ที่ชี้ไปยัง Entity ที่ไม่มีอยู่จริง
2. **Gapless Sequence Proof:** รับประกันว่า Audit Event Sequence จะไม่มีช่องว่าง (`Seq_N - Seq_{N-1} === 1`) ป้องกันการแอบลบข้อมูลบันทึกย้อนหลัง
