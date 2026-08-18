# Domain 27: Content-Addressed Storage & 2PC Durability

> **Domain Index:** `DOMAIN-27`  
> **Engineering Scope:** `DIM-261` .. `DIM-270`  
> **Mathematical Equations:** `EQ-261` .. `EQ-270`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 27 กำหนดระบบจัดเก็บไฟล์แบบอ้างอิงด้วยเนื้อหา **Content-Addressed Storage (CAS)** ด้วยโครงสร้าง SHA-256 2-Tier Directory Sharding, **Atomic Temp-Fsync-Rename Pipeline**, **Zero Torn Reads Guarantee**, และ **Two-Phase Generation Commit Protocol (2PC - 7 States)**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-261  │ EQ-261   │ CAS 2-Tier Sharding Partition Function    │ Path(H) = "cas/" + H[0:2] + "/" + H                         │
│ DIM-262  │ EQ-262   │ Atomic Write Temp-Fsync-Rename Pipeline   │ Write(tmp) -> Fsync(fd) -> Rename(tmp, target) -> Fsync(dir)│
│ DIM-263  │ EQ-263   │ Zero Torn Reads Concurrency Guarantee     │ Pr(PartialRead(CAS)) === 0.0                                │
│ DIM-264  │ EQ-264   │ 2-Phase Commit 7-State FSM Loop Order     │ CommitState in {S_1, ..., S_7}                              │
│ DIM-265  │ EQ-265   │ Generation Manifest Immutable Durability  │ Exists(CAS(H_gen_manifest)) === True                        │
│ DIM-266  │ EQ-266   │ Atomic SQLite Rollback on Sudden Crash    │ CrashBeforeCommit ==> AutoRollback                          │
│ DIM-267  │ EQ-267   │ Full Database Reconstruction from CAS     │ ReconstructDB(M_CAS) =~= OriginalDB                         │
│ DIM-268  │ EQ-268   │ Audit Cryptographic Hash Chain Closure    │ H_N = SHA-256(H_{N-1} || E_N)                               │
│ DIM-269  │ EQ-269   │ Audit Chain Gap Detection Invariant       │ Seq_N - Seq_{N-1} === 1                                     │
│ DIM-270  │ EQ-270   │ CAS Garbage Collection Reachability Bound │ GC(b) <=> b not in ReferencedBlobs(DB union Lineage)        │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-261` / `EQ-261`: CAS 2-Tier Sharding Partition Function
- โครงสร้างไดเรกทอรีจัดเก็บไฟล์ใน CAS:
  $$\text{Path}(H) = \text{"cas/"} + H[0:2] + \text{"/"} + H$$

### `DIM-262` / `EQ-262`: Atomic Write Temp-Fsync-Rename Pipeline
- กระบวนการเขียนไฟล์ลง CAS ต้องรับประกันว่าไม่มีการสูญหายของข้อมูลแม้ตัดไฟ:
  $$\text{Write}(\text{tmp}) \longrightarrow \text{Fsync}(\text{fd}) \longrightarrow \text{Rename}(\text{tmp}, \text{target}) \longrightarrow \text{Fsync}(\text{dir})$$

### `DIM-263` / `EQ-263`: Zero Torn Reads Concurrency Guarantee
- รับประกันว่าการอ่านไฟล์จาก CAS จะไม่มีวันได้ไฟล์ที่ไม่สมบูรณ์:
  $$\Pr(\text{PartialRead}(\text{CAS})) \equiv 0.0$$

### `DIM-264` / `EQ-264`: 2-Phase Commit 7-State FSM Loop Order
- วงจรการบันทึกรุ่น: `PREPARING` $\to$ `CAS_OBJECTS_DURABLE` $\to$ `DB_TRANSACTION_OPEN` $\to$ `DB_ROWS_WRITTEN` $\to$ `DB_COMMITTED` $\to$ `GENERATION_MANIFEST_DURABLE` $\to$ `COMMITTED`:
  $$\text{CommitState} \in \{S_1, \dots, S_7\}$$

### `DIM-265` / `EQ-265`: Generation Manifest Immutable Durability
- Generation Manifest ต้องถูกเก็บไว้ใน CAS อย่างคงทนถาวร:
  $$\text{Exists}(\text{CAS}(H_{\text{gen\_manifest}})) \equiv \text{True}$$

### `DIM-266` / `EQ-266`: Atomic SQLite Rollback on Sudden Crash
- หากเกิด Crash ก่อนขั้นตอนสุดท้าย SQLite จะ Rollback อัตโนมัติ:
  $$\text{CrashBeforeCommit} \implies \text{AutoRollback}$$

### `DIM-267` / `EQ-267`: Full Database Reconstruction from CAS
- สามารถสร้างฐานข้อมูล SQLite ขึ้นมาใหม่ทั้งหมดจากไฟล์ใน CAS:
  $$\text{ReconstructDB}(\mathcal{M}_{\text{CAS}}) \cong \text{OriginalDB}$$

### `DIM-268` / `EQ-268`: Audit Cryptographic Hash Chain Closure
- การปิด Hash Chain ของ Audit Trail:
  $$H_N = \text{SHA-256}(H_{N-1} \parallel E_N)$$

### `DIM-269` / `EQ-269`: Audit Chain Gap Detection Invariant
- ตรวจสอบว่าไม่มีช่องว่างใน Audit Sequence:
  $$\text{Seq}_N - \text{Seq}_{N-1} \equiv 1$$

### `DIM-270` / `EQ-270`: CAS Garbage Collection Reachability Bound
- ลบเฉพาะไฟล์ใน CAS ที่ไม่มีการอ้างอิงจากฐานข้อมูลหรือ Lineage DAG:
  $$\text{GC}(b) \iff b \notin \text{ReferencedBlobs}(\text{DB} \cup \text{Lineage})$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D27-01` [CAS Hash Match]:** เขียนไบนารี 1MB ลง CAS อ่านกลับมาคำนวณ Digest ต้องตรงกันบิตต่อบิต
2. **Test `TC-D27-02` [Crash Chaos Simulation]:** ตัดไฟจำลองระหว่าง State 3 (DB Transaction Open) เปิดระบบใหม่ตรวจสอบว่า SQLite Rollback สมบูรณ์
3. **Test `TC-D27-03` [DB Reconstruction Benchmark]:** ลบไฟล์ `db.sqlite` ทิ้ง สั่งสร้างใหม่จาก CAS ตรวจสอบว่าข้อมูลตรงกัน 100%
4. **Test `TC-D27-04` [Zero Torn Reads Proof]:** อ่านไฟล์ขณะที่อีก Process กำลังเขียน ตรวจสอบว่าไม่มี partial read
