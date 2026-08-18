# Domain 30: Governance, Ethics, IP & Self-Evolution (M13)

> **Domain Index:** `DOMAIN-30`  
> **Engineering Scope:** `DIM-291` .. `DIM-300`  
> **Mathematical Equations:** `EQ-291` .. `EQ-300`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 30 กำหนดการกำกับดูแลธรรมาภิบาลและการวิวัฒนาการตัวเองของระบบ (System Self-Evolution & Governance) ผ่าน **179 Canonical Requirement IDs Monotonicity**, **Price's Formal Selection Equation**, การตรวจสอบลิขสิทธิ์ซอฟต์แวร์ (IP Provenance), Green Computing, **Root-of-Trust Invariant**, และ **Maturity Ladder M0 ถึง M13**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-291  │ EQ-291   │ Requirement Lifecycle Formal Transition   │ Status in {REQ, IMP, TEST, EVID}                            │
│ DIM-292  │ EQ-292   │ 179 Unique Requirement IDs Monotonicity   │ |R| === 179, Index(R_k) = k                                 │
│ DIM-293  │ EQ-293   │ Governed Spec Change Multi-Party Quorum   │ |Approvers| >= 2 land Author not in Approvers               │
│ DIM-294  │ EQ-294   │ Machine-Readable Traceability Bijection   │ forall r in R, |Tests(r)| >= 1 land |Evidence(r)| >= 1      │
│ DIM-295  │ EQ-295   │ Open Source License Apache-2.0 Conformance│ License === "Apache-2.0"                                    │
│ DIM-296  │ EQ-296   │ Software IP Provenance Match Distance     │ Match(MutatedCode, GPL_Database) < 0.10                     │
│ DIM-297  │ EQ-297   │ Green Computing Energy Efficiency Bound   │ eta_green = Generations / Joules >= eta_min                 │
│ DIM-298  │ EQ-298   │ Price's Formal Evolutionary Selection Eq  │ Delta bar{z} = (1/w) * Cov(w_i, z_i) + (1/w) * E(w_i * Dz_i)│
│ DIM-299  │ EQ-299   │ Immutable Self-Evaluator Root-of-Trust    │ SHA-256(Evaluator_candidate) === SHA-256(Evaluator_genesis) │
│ DIM-300  │ EQ-300   │ Maturity Ladder 14-Level Monotonic Closure│ M_0 -> M_1 -> ... -> M_{13} (M13 Complete Self-Evolution)  │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-291` / `EQ-291`: Requirement Lifecycle Formal Transition
- วงจรสถานะของ Requirement:
  $$\text{Status} \in \{\text{REQ}, \text{IMP}, \text{TEST}, \text{EVID}\}$$

### `DIM-292` / `EQ-292`: 179 Unique Requirement IDs Monotonicity
- รหัสความต้องการ 179 ข้อมีหมายเลขลำดับที่แน่นอน:
  $$|\mathcal{R}| \equiv 179, \qquad \text{Index}(R_k) = k$$

### `DIM-293` / `EQ-293`: Governed Spec Change Multi-Party Quorum
- การแก้ไขสเปกต้องได้รับความเห็นชอบอย่างน้อย 2 คน และผู้เขียนห้ามอนุมัติสเปกตัวเอง:
  $$|\text{Approvers}| \ge 2 \land \text{Author} \notin \text{Approvers}$$

### `DIM-294` / `EQ-294`: Machine-Readable Traceability Bijection
- ทุก Requirement ต้องมี Test และ Evidence รองรับแบบ 1-ต่อ-1:
  $$\forall r \in \mathcal{R}, \quad |\text{Tests}(r)| \ge 1 \land |\text{Evidence}(r)| \ge 1$$

### `DIM-295` / `EQ-295`: Open Source License Apache-2.0 Conformance
- โครงการอยู่ภายใต้สัญญาอนุญาต Apache-2.0:
  $$\text{License} \equiv \text{"Apache-2.0"}$$

### `DIM-296` / `EQ-296`: Software IP Provenance Match Distance
- โค้ดที่สร้างขึ้นต้องไม่ลอกเลียนโค้ดที่มีลิขสิทธิ์เกิน 10%:
  $$\text{Match}(\text{MutatedCode}, \text{GPL\_Database}) < 0.10$$

### `DIM-297` / `EQ-297`: Green Computing Energy Efficiency Bound
- วัดประสิทธิภาพการใช้พลังงาน (รุ่นต่อจูล):
  $$\eta_{\text{green}} = \frac{\text{Generations}}{\text{Joules}} \ge \eta_{\min}$$

### `DIM-298` / `EQ-298`: Price's Formal Equation of Evolutionary Selection
- สมการรากฐานทางทฤษฎีวิวัฒนาการสำหรับแยกแยะระหว่างแรงคัดเลือกทางธรรมชาติกับการกลายพันธุ์แบบสุ่ม:
  $$\Delta \bar{z} = \frac{1}{\bar{w}} \text{Cov}(w_i, z_i) + \frac{1}{\bar{w}} \mathbb{E}(w_i \Delta z_i)$$

### `DIM-299` / `EQ-299`: Immutable Self-Evaluator Root-of-Trust
- ในระดับการวิวัฒนาการตัวเอง (M13 Self-Evolution) Candidate ห้ามแก้ไขโค้ดของ Evaluator ที่ใช้ตัดสินตัวเองเด็ดขาด:
  $$\text{SHA-256}(\text{Evaluator}_{\text{candidate}}) \equiv \text{SHA-256}(\text{Evaluator}_{\text{genesis}})$$

### `DIM-300` / `EQ-300`: Maturity Ladder 14-Level Monotonic Closure
- บันไดความสมบูรณ์ 14 ขั้นปิดบริบูรณ์ที่ระดับ M13 (Complete Self-Evolution):
  $$M_0 \longrightarrow M_1 \longrightarrow \dots \longrightarrow M_{13}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D30-01` [Traceability Completeness]:** ตรวจสอบว่า Requirement ครบ 179 ข้อ มีไฟล์โค้ดและชุดทดสอบแมปรองรับแบบ 1-ต่อ-1
2. **Test `TC-D30-02` [Self-Evaluator Freeze]:** สั่งให้ Candidate พยายามแก้ไขฟังก์ชัน Fitness Function ระบบต้องกักกัน Candidate และให้ Error Code `ERR_SECURITY_VIOLATION`
3. **Test `TC-D30-03` [IP Provenance Scanner]:** รันการสแกนโค้ด Candidate เทียบกับฐานข้อมูล GPL ยืนยันว่าค่า Similarity $< 10\%$
4. **Test `TC-D30-04` [M13 Self-Evolution Gate]:** ตรวจสอบการเลื่อนระดับสู่ M13 ว่าผ่านเงื่อนไขครบถ้วนทุก Gates
