# Domain 06: Python 3.12 Deep AST/CST Semantic Parsing

> **Domain Index:** `DOMAIN-06`  
> **Engineering Scope:** `DIM-051` .. `DIM-060`  
> **Mathematical Equations:** `EQ-051` .. `EQ-060`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 06 กำหนดการวิเคราะห์เชิงโครงสร้างของภาษา Python (CPython 3.12+) ด้วย **Abstract Syntax Trees (AST)** และ **Concrete Syntax Trees (CST)** โดยไม่ Import โค้ดใน Host Process พร้อมการคุ้มครองไวยากรณ์ขั้นสูง เช่น PEP 695 Type Parameters, PEP 654 Exception Groups, Structural Pattern Matching, Async/Await Coroutines, และ Walrus Scope Rules.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-051  │ EQ-051   │ AST Node Invariant Mapping Authority      │ AST = <V, E, tau>, tau: V -> PythonNodeTypes                │
│ DIM-052  │ EQ-052   │ CST Lossless Formatting Preservation      │ Bytes(CST(S)) === S                                         │
│ DIM-053  │ EQ-053   │ PEP 695 Type Parameter Variance Invariant │ T_param = <Name, Bound, Variance>                           │
│ DIM-054  │ EQ-054   │ PEP 654 Exception Group Tree Recursion    │ D(ExceptionGroup) = 1 + max_{e in G} D(e)                   │
│ DIM-055  │ EQ-055   │ PEP 701 Nested F-String Recursion Limit   │ D_fstring <= 16                                             │
│ DIM-056  │ EQ-056   │ Structural Pattern Exhaustiveness Invar   │ Union_{i=1}^n CasePattern_i superset Domain(X)              │
│ DIM-057  │ EQ-057   │ Async/Await Preservation Non-blocking     │ Count_{await}(Mutated) >= Count_{await}(Parent)             │
│ DIM-058  │ EQ-058   │ Docstring Structural Equality Invariant   │ Docstring(Mutated) === Docstring(Parent)                    │
│ DIM-059  │ EQ-059   │ Type Annotation Preservation Ratio        │ |Ann(Mutated) intersect Ann(Parent)| / |Ann(Parent)| = 1.0  │
│ DIM-060  │ EQ-060   │ Walrus Operator Scope Lifetime Bounds     │ Scope(NamedExpr(x, E)) === CurrentFunctionScope             │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-051` / `EQ-051`: AST Node Invariant Mapping Authority
- **Requirement:** การสแกนโค้ดโปรเจกต์เป้าหมายต้องกระทำผ่าน `ast.parse()` ในแบบ Pure Static Parsing โดยห้ามรันคำสั่ง `import` ภายใน Host Process เด็ดขาด:
  $$\text{AST} = \langle V, E, \tau \rangle, \quad \tau: V \to \text{PythonNodeTypes}$$

### `DIM-052` / `EQ-052`: CST Lossless Formatting Preservation
- **Requirement:** การแก้ไขโค้ดผ่าน CST (LibCST) ต้องคงสภาพ Comments และ Indentation ดั้งเดิม:
  $$\text{Bytes}(\text{CST}(S)) \equiv S$$

### `DIM-053` / `EQ-053`: PEP 695 Type Parameter Variance Invariant
- รองรับ Generic Type Parameter Syntax ของ Python 3.12 (`type Alias[T] = list[T]`):
  $$T_{\text{param}} = \langle \text{Name}, \text{Bound}, \text{Variance} \rangle$$

### `DIM-054` / `EQ-054`: PEP 654 Exception Group Tree Recursion
- การคำนวณความลึกของข้อยกเว้นแบบกลุ่ม (`except*`):
  $$D(\text{ExceptionGroup}) = 1 + \max_{e \in G} D(e)$$

### `DIM-055` / `EQ-055`: PEP 701 Nested F-String Recursion Limit
- จำกัดความลึกของ F-string ซ้อนกันไม่เกิน 16 ชั้น:
  $$D_{\text{fstring}} \le 16$$

### `DIM-056` / `EQ-056`: Structural Pattern Exhaustiveness
- รูปแบบ `match/case` ต้องครอบคลุม Domain ของตัวแปร:
  $$\bigcup_{i=1}^n \text{CasePattern}_i \supseteq \text{Domain}(X)$$

### `DIM-057` / `EQ-057`: Async/Await Preservation
- **Requirement:** การกลายพันธุ์ในฟังก์ชัน `ast.AsyncFunctionDef` ห้ามลบคำสั่ง `await` จนกลายเป็น Blocking Code:
  $$\text{Count}_{\text{await}}(\text{Mutated}) \ge \text{Count}_{\text{await}}(\text{Parent})$$

### `DIM-058` / `EQ-058`: Docstring Structural Equality Invariant
- Docstring ของฟังก์ชันและคลาสต้องถูกเก็บรักษาไว้เหมือนเดิม 100%:
  $$\text{Docstring}(\text{Mutated}) \equiv \text{Docstring}(\text{Parent})$$

### `DIM-059` / `EQ-059`: Type Annotation Preservation Ratio
- สัดส่วน Type Annotations ต้องคงเดิม 100%:
  $$\frac{|\text{Annotations}(\text{Mutated}) \cap \text{Annotations}(\text{Parent})|}{|\text{Annotations}(\text{Parent})|} = 1.0$$

### `DIM-060` / `EQ-060`: Walrus Operator Scope Lifetime Bounds
- ขอบเขตของ Walrus Operator (`:=`) ต้องจำกัดอยู่ภายในฟังก์ชันปัจจุบัน:
  $$\text{Scope}(\text{NamedExpr}(x, E)) \equiv \text{CurrentFunctionScope}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D06-01` [Python 3.12 Syntax Suite]:** สแกนโค้ดทดสอบที่บรรจุ PEP 695 (`def f[T](x: T)`), PEP 701 (Nested F-strings) และ Pattern Matching ต้อง Parse และรักษารูปแบบได้สมบูรณ์
2. **Test `TC-D06-02` [Docstring Protection]:** สั่งกลายพันธุ์ฟังก์ชันที่มี Docstring ตรวจสอบว่า Docstring ไม่สูญหาย
3. **Test `TC-D06-03` [Async Await Invariant]:** สั่งกลายพันธุ์บนฟังก์ชัน async ยืนยันว่าไม่มีการถอดคำสั่ง await ออกจนกลายเป็น synchronous
4. **Test `TC-D06-04` [Type Annotation Retention]:** ตรวจสอบว่าทุก Type Annotation ในฟังก์ชันที่มี Signature ซับซ้อนยังคงอยู่ครบถ้วน
