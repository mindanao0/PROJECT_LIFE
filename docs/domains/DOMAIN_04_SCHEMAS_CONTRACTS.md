# Domain 04: Data Schemas & Exact JSON Contracts

> **Domain Index:** `DOMAIN-04`  
> **Engineering Scope:** `DIM-031` .. `DIM-040`  
> **Mathematical Equations:** `EQ-031` .. `EQ-040`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 04 กำหนดสัญญาข้อมูล (Data Contracts) ภายใต้มาตรฐาน **JSON Schema Draft 2020-12** ครอบคลุมไฟล์ Schema ทั้ง 26 ตัว, Closed World Assumption (`additionalProperties: false`), การรักษาความถูกต้องของทศนิยม, และการจำกัดขอบเขตข้อมูลแบบไม่สูญหาย.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-031  │ EQ-031   │ JSON Schema Draft 2020-12 Completeness    │ forall x in Payload, Validate(x, S) in {True, False}        │
│ DIM-032  │ EQ-032   │ Strict Closed World Assumption            │ Keys(Instance) \ Properties(Schema) = empty                 │
│ DIM-033  │ EQ-033   │ Engine Config Preference Sum Constraint   │ sum_{i=1}^M w_i = 1.000000, w_i in D                        │
│ DIM-034  │ EQ-034   │ Candidate Digest Identity Composite Hash  │ H_cand = SHA-256(H_source || H_parent || MutationID)        │
│ DIM-035  │ EQ-035   │ Generation Front Cardinality Upper Bound  │ |F_1| <= N_pop                                              │
│ DIM-036  │ EQ-036   │ Run Manifest Composite Checksum Recurrence│ H_run = SHA-256(product_{g=1}^G H_gen_manifest_g)           │
│ DIM-037  │ EQ-037   │ Metric Decimal Precision Scale Bound      │ Scale(v) <= 6 decimal digits                                │
│ DIM-038  │ EQ-038   │ Lineage Graph Direct Acyclicity Invariant │ det(I - A_lineage) = 1                                      │
│ DIM-039  │ EQ-039   │ Reproducibility Score Metric (R0 to R4)   │ R_score = (1 / K) * sum I(Hash_k = Hash_expected)           │
│ DIM-040  │ EQ-040   │ Exact Schema Package Count Ceiling        │ |S_registry| === 26                                         │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-031` / `EQ-031`: JSON Schema Draft 2020-12 Completeness
- **Requirement:** ทุก Payload และ Manifest ต้องสามารถ Validate กับ Schema Draft 2020-12 โดยให้ผลลัพธ์เป็น Boolean ที่แน่นอน:
  $$\forall x \in \text{Payload}, \quad \text{Validate}(x, \mathcal{S}) \in \{\text{True}, \text{False}\}$$

### `DIM-032` / `EQ-032`: Strict Closed World Assumption
- **Requirement:** ทุก Schema ต้องกำหนด `"additionalProperties": false` เพื่อปฏิเสธฟิลด์แปลกปลอม (Unrecognized Fields) ทันที:
  $$\text{Keys}(\text{Instance}) \setminus \text{Properties}(\text{Schema}) = \emptyset$$

### `DIM-033` / `EQ-033`: Engine Config Preference Sum Constraint
- **Requirement:** ผลรวมของค่าน้ำหนัก Preference Weights ใน `evolution.yaml` ต้องเท่ากับ 1.0 เสมอ:
  $$\sum_{i=1}^M w_i = 1.000000, \quad w_i \in \mathbb{D}, \quad w_i \ge 0$$

### `DIM-034` / `EQ-034`: Candidate Digest Identity Composite Hash
- **Requirement:** Candidate Identifier ต้องคำนวณจาก Composite Hash ของ Source, Parent Digest และ Mutation Operator ID:
  $$H_{\text{cand}} = \text{SHA-256}(H_{\text{source}} \parallel H_{\text{parent}} \parallel \text{MutationID})$$

### `DIM-035` / `EQ-035`: Generation Front Cardinality Upper Bound
- จำนวน Candidate ใน Pareto Front 1 ของแต่ละรุ่น ต้องไม่เกินขนาดประชากรทั้งหมด:
  $$|F_1| \le N_{\text{pop}}$$

### `DIM-036` / `EQ-036`: Run Manifest Composite Checksum Recurrence
- Run Manifest Checksum สรุปยอด Hash ของทุก Generation Manifest:
  $$H_{\text{run}} = \text{SHA-256}\left(\prod_{g=1}^G H_{\text{gen\_manifest\_g}}\right)$$

### `DIM-037` / `EQ-037`: Metric Decimal Precision Scale Bound
- ค่าสถิติและตัวเลขทศนิยมทั้งหมดถูกจำกัด Scale ไม่เกิน 6 ตำแหน่งทศนิยม:
  $$\text{Scale}(v) \le 6 \quad \text{decimal digits}$$

### `DIM-038` / `EQ-038`: Lineage Graph Direct Acyclicity Invariant
- กราฟสายพันธุ์ (Lineage DAG) ต้องไม่มีการสืบทอดแบบวนรอบ (No Cycles):
  $$\det(I - \mathbf{A}_{\text{lineage}}) = 1$$

### `DIM-039` / `EQ-039`: Reproducibility Score Metric (R0 to R4)
- การวัดระดับความสามารถในการ Replay ผลลัพธ์ซ้ำ:
  $$R_{\text{score}} = \frac{1}{K} \sum_{k=1}^K \mathbb{I}(\text{Hash}_k = \text{Hash}_{\text{expected}})$$

### `DIM-040` / `EQ-040`: Exact Schema Package Count Ceiling
- **Requirement:** คลัง Schema Registry ของระบบต้องมีไฟล์สัญญาข้อมูลครบถ้วน **26 ตัวพอดี** ห้ามขาดหรือเกิน:
  $$|\mathcal{S}_{\text{registry}}| \equiv 26$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D04-01` [Schema Meta-validation]:** รัน Schema Validator ตรวจสอบไฟล์ Schema ทั้ง 26 ตัวกับ Meta-schema Draft 2020-12 ต้องผ่าน 100%
2. **Test `TC-D04-02` [Additional Properties Injection]:** ฉีดฟิลด์ `"unknown_field": 123` เข้าไปใน Candidate Manifest ระบบต้องปฏิเสธทันที
3. **Test `TC-D04-03` [Weight Sum Invariant]:** ป้อน config ที่มีผลรวมน้ำหนัก 0.999999 ระบบต้องปฏิเสธด้วยข้อความผลรวมไม่เท่ากับ 1.000000
4. **Test `TC-D04-04` [Lineage Acyclicity Check]:** สร้างประวัติสายพันธุ์จำลองที่มี Loop กราฟ ระบบต้องตรวจพบ Cycle และบล็อกการบันทึก
