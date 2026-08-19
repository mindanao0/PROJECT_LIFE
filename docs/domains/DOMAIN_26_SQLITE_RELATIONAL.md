# Domain 26: Relational SQLite Schema & Triggers

> **Domain Index:** `DOMAIN-26`  
> **Engineering Scope:** `DIM-251` .. `DIM-260`  
> **Mathematical Equations:** `EQ-251` .. `EQ-260`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 26 กำหนดโครงสร้างฐานข้อมูลเชิงสัมพันธ์ **SQLite 31 Tables**, 33 High-Performance Indices, Foreign Key Constraints & Cascades, Polymorphic Validation Triggers, และ **B-Tree Height Search Complexity Bound**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-251  │ EQ-251   │ SQLite 29 Relational Tables Completeness  │ |T_db| === 31                                               │
│ DIM-252  │ EQ-252   │ Foreign Key Referential Integrity Relation│ forall r in R, r.FK in pi_PK(S) or r.FK = NULL              │
│ DIM-253  │ EQ-253   │ Polymorphic Trigger Verification Invariant│ OwnerType = T ==> Exists(T, OwnerID)                        │
│ DIM-254  │ EQ-254   │ Monotonic Audit Sequence Increment Check  │ Seq_{t+1} === Seq_t + 1                                     │
│ DIM-255  │ EQ-255   │ High-Performance Index Count Ceiling      │ |I_db| === 33                                               │
│ DIM-256  │ EQ-256   │ B-Tree Height Search Complexity Bound     │ h <= ceil(log_{ceil(M/2)}((N + 1)/2))                       │
│ DIM-257  │ EQ-257   │ SQLite WAL Autocheckpoint Page Bound      │ N_pages <= 1000 pages                                       │
│ DIM-258  │ EQ-258   │ In-Memory DB Zero Evidence Mode Invariant │ DBPath = ":memory:" ==> EvidenceSaved = False               │
│ DIM-259  │ EQ-259   │ Database Migration Monotonic Versioning   │ V_target >= V_current                                       │
│ DIM-260  │ EQ-260   │ PRAGMA Integrity Check Zero Errors Proof  │ PRAGMA integrity_check === "ok"                             │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-251` / `EQ-251`: SQLite 29 Relational Tables Completeness
- โครงสร้างฐานข้อมูลของระบบประกอบด้วย 31 ตารางพอดี:
  $$|\mathcal{T}_{\text{db}}| \equiv 31$$

### `DIM-252` / `EQ-252`: Foreign Key Referential Integrity Relation
- ทุกแถวที่อ้างอิง Foreign Key ต้องชี้ไปยัง Primary Key ที่มีอยู่จริง:
  $$\forall r \in R, \quad r.\text{FK} \in \pi_{\text{PK}}(S) \lor r.\text{FK} = \text{NULL}$$

### `DIM-253` / `EQ-253`: Polymorphic Trigger Verification
- ทริกเกอร์ตรวจสอบความถูกต้องของ `artifact_refs(owner_type, owner_id)` ป้องกัน Dangling References:
  $$\text{OwnerType} = T \implies \text{Exists}(T, \text{OwnerID})$$

### `DIM-254` / `EQ-254`: Monotonic Audit Sequence Increment Check
- ลำดับหมายเลข Audit Event ต้องเพิ่มขึ้นทีละ 1 อย่างเคร่งครัด:
  $$\text{Seq}_{t+1} \equiv \text{Seq}_t + 1$$

### `DIM-255` / `EQ-255`: High-Performance Index Count Ceiling
- สร้างดัชนีเพื่อเร่งความเร็วการค้นหา 33 ดัชนี:
  $$|\mathcal{I}_{\text{db}}| \equiv 33$$

### `DIM-256` / `EQ-256`: B-Tree Index Search Complexity
- รับประกันว่าคิวรีทั้งหมดที่ค้นหาผ่าน 33 Indices มี Search Complexity ไม่เกิน:
  $$h \le \left\lceil \log_{\lceil M/2 \rceil} \left(\frac{N + 1}{2}\right) \right\rceil$$

### `DIM-257` / `EQ-257`: SQLite WAL Autocheckpoint Page Bound
- สั่ง Checkpoint WAL file เมื่อมีขนาดครบ 1,000 หน้า:
  $$N_{\text{pages}} \le 1000 \quad \text{pages}$$

### `DIM-258` / `EQ-258`: In-Memory DB Zero Evidence Mode Invariant
- เมื่อรันในโหมด `:memory:` จะไม่มีการบันทึกไฟล์ลง Disk:
  $$\text{DBPath} = \text{":memory:"} \implies \text{EvidenceSaved} = \text{False}$$

### `DIM-259` / `EQ-259`: Database Migration Monotonic Versioning
- Version การ Migration ฐานข้อมูลต้องเพิ่มขึ้นทางเดียว:
  $$V_{\text{target}} \ge V_{\text{current}}$$

### `DIM-260` / `EQ-260`: PRAGMA Integrity Check Zero Errors Proof
- ตรวจสอบความสมบูรณ์ของโครงสร้าง B-Tree ฐานข้อมูล:
  $$\text{PRAGMA integrity\_check} \equiv \text{"ok"}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D26-01` [Foreign Key Enforcement]:** ทดสอบใส่ Candidate ID ที่ไม่มีอยู่จริงลงตาราง `metric_results` SQLite ต้องโยน FK Constraint Failure
2. **Test `TC-D26-02` [Query Plan Assertion]:** รัน `EXPLAIN QUERY PLAN` บน 30 คิวรีหลัก ยืนยันว่าใช้ Index Search และไม่มี Full Table Scan
3. **Test `TC-D26-03` [Audit Monotonic Sequence]:** บันทึก 1,000 Events ติดต่อกัน ตรวจสอบว่า `seq` เรียงลำดับ $1, 2, \dots, 1000$ ไม่มีข้ามหรือซ้ำ
4. **Test `TC-D26-04` [PRAGMA Integrity]:** รัน `PRAGMA integrity_check` หลังรัน 100 Generations ต้องคืนค่า `"ok"`
