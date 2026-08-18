# Domain 20: Multi-File Dependency Graph Analyzers

> **Domain Index:** `DOMAIN-20`  
> **Engineering Scope:** `DIM-191` .. `DIM-200`  
> **Mathematical Equations:** `EQ-191` .. `EQ-200`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 20 กำหนดการวิเคราะห์โครงการแบบหลายไฟล์ผ่าน **Direct Acyclic Graphs (DAG)**, Cross-File Symbol Resolution, การกลายพันธุ์ระดับ Snapshot หลายไฟล์แบบ Atomic, การวิเคราะห์ Impact Surface, Selective Unit Test Execution, และ **Topological Sort Compilation**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-191  │ EQ-191   │ Direct Acyclic Graph Representation Form  │ G = (V, E), (u, v) in E <=> u imports v                     │
│ DIM-192  │ EQ-192   │ Cross-File Symbol Resolution Invariant    │ forall s in Used(u), exists v s.t. s in Exports(v)          │
│ DIM-193  │ EQ-193   │ Atomic Multi-File Snapshot Composite Hash │ H_snapshot = SHA-256(product_{i=1}^n H_{f_i})               │
│ DIM-194  │ EQ-194   │ DAG Acyclicity Matrix Exponential Trace   │ Tr(exp(A)) = |V|                                            │
│ DIM-195  │ EQ-195   │ Impact Surface Reachability Propagation   │ Impact(f) = {v in V | Path(v, f) exists}                    │
│ DIM-196  │ EQ-196   │ Selective Test Subgraph Execution Set     │ T_run = {t in T | DependsOn(t) intersect Impact(f) != empty}│
│ DIM-197  │ EQ-197   │ Public Module Boundary Interface Invariant│ Exports(Mutated) superset PublicAPI(Original)               │
│ DIM-198  │ EQ-198   │ Package Init Import Soundness Invariant   │ forall m in __all__, ModuleExists(m) === True               │
│ DIM-199  │ EQ-199   │ Multi-File Graph Edit Distance (GED)      │ GED(G_1, G_2) = min_{vec{e}} sum c(e_i)                     │
│ DIM-200  │ EQ-200   │ Topological Sort Order Compilation Order  │ u prec v <=> (u, v) in E*                                   │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-191` / `EQ-191`: Direct Acyclic Graph Representation Form
- กราฟการนำเข้าโมดูลระหว่างไฟล์ในโปรเจกต์:
  $$G = (V, E), \qquad (u, v) \in E \iff u \text{ imports } v$$

### `DIM-192` / `EQ-192`: Cross-File Symbol Resolution Invariant
- ทุกสัญลักษณ์ที่เรียกใช้ข้ามไฟล์ต้องมีไฟล์ต้นทาง Export ออกมาเสมอ:
  $$\forall s \in \text{UsedSymbols}(u), \quad \exists v \in V \text{ s.t. } s \in \text{Exports}(v)$$

### `DIM-193` / `EQ-193`: Atomic Multi-File Snapshot Composite Hash
- ทุก Candidate หลายไฟล์ถูกระบุตัวตนด้วย Snapshot Hash:
  $$H_{\text{snapshot}} = \text{SHA-256}\left(\prod_{i=1}^n H_{f_i}\right)$$

### `DIM-194` / `EQ-194`: DAG Acyclicity Invariant
- เพื่อป้องกันปัญหา Circular Imports กราฟความสัมพันธ์ต้องเป็น DAG ที่ไม่มี Loop:
  $$\text{Tr}(e^{\mathbf{A}}) = |V| \iff \text{Graph is strictly acyclic}$$

### `DIM-195` / `EQ-195`: Impact Surface Reachability Propagation
- คำนวณเซตของไฟล์ทั้งหมดที่ได้รับผลกระทบจากการแก้ไฟล์ $f$:
  $$\text{Impact}(f) = \{v \in V \mid \text{Path}(v, f) \text{ exists}\}$$

### `DIM-196` / `EQ-196`: Selective Test Subgraph Execution
- เลือกรันเฉพาะ Unit Tests ที่ได้รับผลกระทบจากไฟล์ที่ถูกแก้ไขเพื่อประหยัดเวลา:
  $$T_{\text{run}} = \{t \in T \mid \text{DependsOn}(t) \cap \text{Impact}(f) \ne \emptyset\}$$

### `DIM-197` / `EQ-197`: Public Module Boundary Interface Invariant
- การกลายพันธุ์ห้ามทำลาย Public API ดั้งเดิมของแพ็กเกจ:
  $$\text{Exports}(\text{Mutated}) \supseteq \text{PublicAPI}(\text{Original})$$

### `DIM-198` / `EQ-198`: Package Init Import Soundness Invariant
- โมดูลใน `__all__` ต้องมีอยู่จริงในแพ็กเกจ:
  $$\forall m \in \text{__all__}, \quad \text{ModuleExists}(m) \equiv \text{True}$$

### `DIM-199` / `EQ-199`: Multi-File Graph Edit Distance (GED)
- ระยะห่างการปรับโครงสร้างระบบหลายไฟล์:
  $$\text{GED}(G_1, G_2) = \min_{\vec{e}} \sum c(e_i)$$

### `DIM-200` / `EQ-200`: Topological Sort Compilation Order
- ลำดับการประเมินและคอมไพล์ไฟล์ต้องเป็นไปตาม Topological Order:
  $$u \prec v \iff (u, v) \in E^*$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D20-01` [Multi-file DAG Mutation]:** แก้ไขฟังก์ชันในโมดูล A ที่ถูกเรียกใช้โดยโมดูล B ยืนยันว่า Type Signature สอดคล้องกันทั้งคู่
2. **Test `TC-D20-02` [Circular Import Detection]:** สร้างการ Import วนรอบระหว่าง 3 ไฟล์ ระบบต้องตรวจพบและ Reject ทันที
3. **Test `TC-D20-03` [Selective Test Acceleration]:** แก้ไขไฟล์ที่ไม่กระทบ Unit Test โมดูลอื่น ตรวจสอบว่าระบบข้ามการรัน Test ที่ไม่เกี่ยวข้องได้ถูกต้อง
4. **Test `TC-D20-04` [Topological Sort Invariant]:** ตรวจสอบว่าลำดับการคอมไพล์สอดคล้องกับ Dependency DAG
