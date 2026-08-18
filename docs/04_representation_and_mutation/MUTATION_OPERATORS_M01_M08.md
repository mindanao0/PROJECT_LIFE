# Mutation Operators Specification (M01 to M08)

> **Authority Level:** NORMATIVE COMPILER SPECIFICATION (L4 Authority)  
> **Target Subsystem:** AST Transformation & Mutator Pipeline  
> **Governing Equations:** `EQ-071` .. `EQ-090` (Atomic & Architectural Mutation Models)

---

## 1. Catalog of Operators M01 through M08

```text
┌────────────┬─────────────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Operator   │ Strategy Category           │ Transformation Summary & Big-O Impact                                     │
├────────────┼─────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ M01        │ Constant Mutation           │ ปรับตัวเลขคงที่ สตริงคงที่ และค่า Boolean (EQ-071..073)                   │
│ M02        │ Operator Mutation           │ สลับ Arithmetic, Comparison และ Logical Operators (EQ-074..076)            │
│ M03        │ Condition Boundary Mutation │ ปรับแก้ Boundary Offset ในนิพจน์ if (<, <=, >, >=) (EQ-077)                │
│ M04        │ Loop Flow Mutation          │ ปรับ Step size ใน range(), แปลง for <-> while (EQ-078..080)               │
│ M05        │ Standard Function Replacer  │ แทนที่ฟังก์ชันเขียนเองด้วย CPython Builtin C Extensions (EQ-081)           │
│ M06        │ Pure Function Extractor     │ สกัด Pure Function เพื่อขจัด Side Effect (EQ-082)                         │
│ M07        │ Small Function Inlining     │ ยุบรวมฟังก์ชันขนาดเล็กเพื่อลด Call Frame Allocation (EQ-083)               │
│ M08        │ Data Structure Optimizer    │ แปลง List Lookup สู่ Set O(1) และ Queue สู่ Deque O(1) (EQ-084..086)      │
└────────────┴─────────────────────────────┴───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. AST Transformation Rules & Node Rewriters

### 2.1 M01: Constant Mutation
- **`ast.Constant(value=int|float)`:**
  $$\text{value}' = \text{value} + (-1)^s \cdot \delta, \quad \delta \in \{1, 2, \lfloor \text{value}/2 \rfloor, 0.1 \times \text{value}\}$$
- **`ast.Constant(value=str)`:** สลับหรือแทนที่ตัวอักษรโดยจำกัด $d_{\text{Lev}} \le 3$

### 2.2 M02: Operator Mutation
- **`ast.BinOp(op=ast.Add)` $\to$ `ast.Sub` / `ast.Mult` / `ast.FloorDiv`**
- **`ast.Compare(ops=[ast.Lt])` $\to$ `[ast.LtE]` / `[ast.Gt]` / `[ast.NotEq]`**
- **`ast.BoolOp(op=ast.And)` $\to$ `ast.Or`** พร้อมการกระจายแบบ De Morgan

### 2.3 M08: Data Structure Optimization
- **`ast.List` $\to$ `ast.Set` ในคำสั่ง `if x in collection:`**
  ```python
  # Before Mutation (O(N) search):
  allowed_ids = [1, 2, 3, 4, 5]
  if user_id in allowed_ids: ...

  # After Mutation M08 (O(1) search):
  allowed_ids = {1, 2, 3, 4, 5}
  if user_id in allowed_ids: ...
  ```
- **`ast.Call(func=ast.Attribute(value=list, attr='insert'))` $\to$ `collections.deque.appendleft`** (ลดเวลาจาก $\mathcal{O}(N)$ สู่ $\mathcal{O}(1)$)

---

## 3. Structural Reversibility & Delta Serialization

ทุกการเปลี่ยนแปลงของ M01–M08 ต้องสามารถย้อนกลับ (Reversible) สู่ AST ดั้งเดิมได้:
$$\mathcal{M}^{-1}(\mathcal{M}(\text{AST})) \equiv \text{AST}$$
และจัดเก็บในรูปของ JSON Structural Delta Patch โดยมีขนาดไม่เกิน 15% ของ Source เดิม
