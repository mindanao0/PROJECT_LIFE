# Domain 29: SRE Operations, Latency & Chaos Recovery

> **Domain Index:** `DOMAIN-29`  
> **Engineering Scope:** `DIM-281` .. `DIM-290`  
> **Mathematical Equations:** `EQ-281` .. `EQ-290`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 29 กำหนดมาตรฐานวิศวกรรมความน่าเชื่อถือของระบบ (Site Reliability Engineering - SRE) ผ่านพจนานุกรม Reason Codes, **Subsystem P99 Latency Budgets**, ข้อกำหนด **RTO $\le 60$s และ RPO $\le 1$ Gen**, และระบบทดสอบ **34-Job CI Matrix Automation Pipeline**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-281  │ EQ-281   │ Standard Reason Codes Domain Mapping      │ ReasonCode in {ERR_01, ..., ERR_K}                          │
│ DIM-282  │ EQ-282   │ Automated DB Reconciliation Function      │ DoctorRepair(CorruptState) -> HealthyState                  │
│ DIM-283  │ EQ-283   │ Subsystem P99 Latency Budget Bounds       │ P99(AST_Parse) <= 5.0 ms, P99(Sandbox_Spawn) <= 15.0 ms     │
│ DIM-284  │ EQ-284   │ Coordinator Memory Ceiling Bound          │ RAM_coord <= 256 MB                                         │
│ DIM-285  │ EQ-285   │ Disaster Recovery SLOs (RTO & RPO)        │ RTO <= 60.0 s, RPO <= 1 Generation                          │
│ DIM-286  │ EQ-286   │ 34-Job CI Matrix Pipeline Completeness    │ |J_CI| === 34, Passed(J) === 34                             │
│ DIM-287  │ EQ-287   │ 8-Part Continuous Spec Linters Verification│ bigwedge_{i=1}^8 Linter_i(Spec) === PASS                    │
│ DIM-288  │ EQ-288   │ Interactive TUI Terminal Refresh Rate     │ f_TUI >= 10 Hz                                              │
│ DIM-289  │ EQ-289   │ Standalone Export Self-Containment Bound  │ Deps(ExportedPackage) intersect ExternalEngine = empty      │
│ DIM-290  │ EQ-290   │ Storage Write Amplification Factor (WAF)  │ WAF = BytesWrittenToDisk / BytesWrittenByEngine <= 2.5      │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-281` / `EQ-281`: Standard Reason Codes Domain Mapping
- การแมป Error Code และ Reason Code มาตรฐาน:
  $$\text{ReasonCode} \in \{\text{ERR\_01}, \dots, \text{ERR\_K}\}$$

### `DIM-282` / `EQ-282`: Automated DB Reconciliation Function
- คำสั่ง `evolve doctor` กู้คืนโครงสร้างฐานข้อมูลอัตโนมัติ:
  $$\text{DoctorRepair}(\text{CorruptState}) \longrightarrow \text{HealthyState}$$

### `DIM-283` / `EQ-283`: Subsystem P99 Latency Budget Bounds
- งบประมาณเวลาประมวลผล P99 ของระบบย่อย:
  $$\text{P99}(\text{AST\_Parse}) \le 5.0\text{ ms}, \qquad \text{P99}(\text{Sandbox\_Spawn}) \le 15.0\text{ ms}$$

### `DIM-284` / `EQ-284`: Coordinator Memory Ceiling Bound
- จำกัดขนาด RAM ของ Coordinator ไม่เกิน 256MB:
  $$\text{RAM}_{\text{coord}} \le 256\text{ MB}$$

### `DIM-285` / `EQ-285`: Disaster Recovery SLOs (RTO & RPO)
- เกณฑ์เป้าหมายการกู้คืนระบบจากภัยพิบัติ:
  $$\text{RTO} \le 60.0\text{ seconds}, \qquad \text{RPO} \le 1\text{ Generation}$$

### `DIM-286` / `EQ-286`: 34-Job CI Matrix Pipeline Completeness
- ทุกการ Commit ต้องผ่านการทดสอบ CI 34 Jobs:
  $$|\mathcal{J}_{\text{CI}}| \equiv 34, \qquad \text{Passed}(\mathcal{J}) \equiv 34$$

### `DIM-287` / `EQ-287`: 8-Part Continuous Spec Linters Verification
- สเปกต้องผ่าน Spec Linters ทั้ง 8 ตัว:
  $$\bigwedge_{i=1}^8 \text{Linter}_i(\text{Spec}) \equiv \text{PASS}$$

### `DIM-288` / `EQ-288`: Interactive TUI Terminal Refresh Rate
- อัตราการรีเฟรชหน้าจอ TUI ไม่ต่ำกว่า 10Hz:
  $$f_{\text{TUI}} \ge 10\text{ Hz}$$

### `DIM-289` / `EQ-289`: Standalone Export Self-Containment Bound
- แพ็กเกจที่ส่งออกต้องเป็นอิสระจาก Engine 100%:
  $$\text{Deps}(\text{ExportedPackage}) \cap \text{ExternalEngine} = \emptyset$$

### `DIM-290` / `EQ-290`: Storage Write Amplification Factor (WAF)
- ควบคุมอัตราการเขียน Disk ซ้ำซ้อนไม่เกิน 2.5:
  $$\text{WAF} = \frac{\text{BytesWrittenToDisk}}{\text{BytesWrittenByEngine}} \le 2.5$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D29-01` [Doctor Reconciliation]:** ทำลาย Metadata บางส่วนใน SQLite รันคำสั่ง `evolve doctor --reconcile-db` ตรวจสอบว่าระบบกู้คืนสภาพพร้อมรันได้ภายใน 30 วินาที
2. **Test `TC-D29-02` [Latency Benchmark]:** รันการ Parse AST 1,000 ครั้ง ตรวจสอบว่า P99 Latency ต่ำกว่า 5.0ms
3. **Test `TC-D29-03` [Coordinator RAM Footprint]:** ตรวจสอบหน่วยความจำของ Coordinator ระหว่างรัน 50 Generations ต้องไม่เกิน 256MB
4. **Test `TC-D29-04` [Spec Linter Automation]:** รัน Spec Linter ทั้ง 8 ตัว ตรวจสอบว่าผ่าน 100% ไม่มี Format Error
