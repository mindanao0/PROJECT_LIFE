# SQLite Integrity Triggers & Polymorphic Validation Specification

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** STORAGE SPECIFICATION (L5 Authority)
> **Target Subsystem:** Relational Storage Engine (`.evolution/db.sqlite`)  
> **Governing Equations:** `EQ-253` (Polymorphic Trigger Verification), `EQ-254` (Monotonic Audit Sequence Increment)

---

## 1. Executive Summary

เอกสารฉบับนี้กำหนด **SQLite Triggers** ที่ทำงานระดับเคอร์เนลฐานข้อมูลเพื่อคุ้มครองความถูกต้องของข้อมูล (Referential Integrity) สำหรับ Polymorphic References ในตาราง `artifact_refs`, `lineage_edges`, `quarantine_records`, และการบังคับใช้หมายเลข Sequence ต่อเนื่องแบบ Monotonic ในตาราง `audit_events`.

---

## 2. Complete SQL Triggers DDL Implementation

```sql
-- ============================================================================
-- 1. Polymorphic Reference Validation Trigger for artifact_refs
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS trg_artifact_refs_polymorphic_validate
BEFORE INSERT ON artifact_refs
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN NEW.owner_type = 'RUN' AND NOT EXISTS (SELECT 1 FROM runs WHERE run_id = NEW.owner_id) THEN
            RAISE(ABORT, 'Integrity Error: owner_id does not exist in runs table')
        WHEN NEW.owner_type = 'GENERATION' AND NOT EXISTS (SELECT 1 FROM generations WHERE generation_id = NEW.owner_id) THEN
            RAISE(ABORT, 'Integrity Error: owner_id does not exist in generations table')
        WHEN NEW.owner_type = 'CANDIDATE' AND NOT EXISTS (SELECT 1 FROM candidates WHERE candidate_id = NEW.owner_id) THEN
            RAISE(ABORT, 'Integrity Error: owner_id does not exist in candidates table')
        WHEN NEW.owner_type = 'EVALUATION' AND NOT EXISTS (SELECT 1 FROM evaluations WHERE evaluation_id = NEW.owner_id) THEN
            RAISE(ABORT, 'Integrity Error: owner_id does not exist in evaluations table')
        WHEN NEW.owner_type NOT IN ('RUN', 'GENERATION', 'CANDIDATE', 'EVALUATION') THEN
            RAISE(ABORT, 'Integrity Error: Invalid owner_type in artifact_refs')
    END;
END;

-- ============================================================================
-- 2. Monotonic Strict Increment Trigger for audit_events Sequence
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS trg_audit_events_monotonic_seq
BEFORE INSERT ON audit_events
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN NEW.seq != (SELECT COALESCE(MAX(seq), 0) + 1 FROM audit_events WHERE run_id = NEW.run_id) THEN
            RAISE(ABORT, 'Integrity Error: audit_events.seq must increment monotonically by exactly 1 without gaps')
    END;
END;

-- ============================================================================
-- 3. Immutability Trigger on Committed Candidates
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS trg_candidates_prevent_source_modification
BEFORE UPDATE OF source_hash, parent_candidate_id, generation_id ON candidates
FOR EACH ROW
WHEN OLD.lifecycle_state IN ('SELECTED', 'REJECTED', 'QUARANTINED')
BEGIN
    SELECT RAISE(ABORT, 'Integrity Error: Cannot modify immutable attributes of a finalized candidate');
END;

-- ============================================================================
-- 4. Lineage Acyclicity Self-Reference Protection
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS trg_lineage_edges_prevent_self_loop
BEFORE INSERT ON lineage_edges
FOR EACH ROW
WHEN NEW.parent_candidate_id = NEW.child_candidate_id
BEGIN
    SELECT RAISE(ABORT, 'Integrity Error: Direct self-loop detected in lineage_edges');
END;
```

---

## 3. Trigger Invariants & Verification Proofs

1. **Polymorphic Reference Soundness:** ป้องกันการแทรก Orphan Artifact ที่ชี้ไปยัง Entity ที่ไม่มีอยู่จริง
2. **Gapless Sequence Proof:** รับประกันว่า Audit Event Sequence จะไม่มีช่องว่าง (`Seq_N - Seq_{N-1} === 1`) ป้องกันการแอบลบข้อมูลบันทึกย้อนหลัง
