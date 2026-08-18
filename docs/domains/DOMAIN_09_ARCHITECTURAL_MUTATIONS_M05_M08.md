# Domain 09: Architectural Refactoring & Inlining (M05-M08)

> **Domain Index:** `DOMAIN-09`  
> **Engineering Scope:** `DIM-081` .. `DIM-090`  
> **Mathematical Equations:** `EQ-081` .. `EQ-090`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 09 กำหนดตัวดำเนินการกลายพันธุ์เชิงสถาปัตยกรรม (Architectural Mutation Operators) 4 ตัว ได้แก่ **M05 (Standard Function Replacement)**, **M06 (Function Extraction)**, **M07 (Function Inlining)**, และ **M08 (Data Structure Optimization)** เพื่อลดความซับซ้อนเชิงบิ๊กโอ (Big-O Complexity Reduction) และลด Call Stack Overhead.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-081  │ EQ-081   │ M05 Standard Library Equivalence Invariant│ forall x in Inputs, f_std(x) === f_custom(x)                │
│ DIM-082  │ EQ-082   │ M06 Pure Function Extraction Invariant    │ SideEffects(f_pure) = empty                                 │
│ DIM-083  │ EQ-083   │ M07 Function Inlining Call Overhead Red   │ Delta t_call = N_calls * t_frame_alloc                      │
│ DIM-084  │ EQ-084   │ M08 Deque AppendLeft O(1) Complexity      │ T_appendleft(deque) = O(1) << O(N)_list                     │
│ DIM-085  │ EQ-085   │ M08 Set Membership Lookup O(1) Complexity │ T_lookup(set) = O(1) << O(N)_list                           │
│ DIM-086  │ EQ-086   │ M08 Dict Default Lookup Invariant         │ dict.get(k, v_0) === v_0 <=> k not in keys                  │
│ DIM-087  │ EQ-087   │ List Comprehension Memory Footprint Bound │ Mem(Comp) <= Mem(For_Append)                                │
│ DIM-088  │ EQ-088   │ Generator Stream Constant Memory Ceiling  │ Mem(Gen) = O(1) << O(N)                                     │
│ DIM-089  │ EQ-089   │ Structural Delta Serialization Ratio      │ Ratio = |Delta_AST| / |S_original| <= 0.15                  │
│ DIM-090  │ EQ-090   │ Mutation Reversibility Snapshot Identity  │ M^{-1}(M(AST)) === AST                                      │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-081` / `EQ-081`: M05 Standard Library Equivalence Invariant
- แทนที่ฟังก์ชันที่เขียนเองด้วย Builtin/Standard Library ที่ได้รับการคอมไพล์ใน C เช่น `math.sqrt`, `sum()`:
  $$\forall x \in \text{Inputs}, \quad f_{\text{std}}(x) \equiv f_{\text{custom}}(x)$$

### `DIM-082` / `EQ-082`: M06 Pure Function Extraction Invariant
- การสกัดฟังก์ชันย่อยที่ไม่มี Side Effect เพื่อเปิดโอกาสให้เกิด Pure Function Optimization:
  $$\text{SideEffects}(f_{\text{pure}}) = \emptyset$$

### `DIM-083` / `EQ-083`: M07 Function Inlining Call Overhead Red
- การ Inlining ฟังก์ชันขนาดเล็กเพื่อขจัด Call Frame Allocation:
  $$\Delta t_{\text{call}} = N_{\text{calls}} \times t_{\text{frame\_alloc}}$$

### `DIM-084` / `EQ-084`: M08 Deque AppendLeft O(1) Complexity
- การเปลี่ยนจาก `list.insert(0, x)` สู่ `collections.deque.appendleft(x)` เพื่อลด Complexity จาก $\mathcal{O}(N)$ สู่ $\mathcal{O}(1)$:
  $$T_{\text{appendleft}}(\text{deque}) = \mathcal{O}(1) \ll \mathcal{O}(N)_{\text{list}}$$

### `DIM-085` / `EQ-085`: M08 Set Membership Lookup O(1) Complexity
- เมื่อตรวจพบการค้นหาสมาชิก `if x in collection:` โดยที่ collection ถูกประกาศเป็น `list` ตัวดำเนินการ M08 จะแปลงให้เป็น `set` เพื่อลดเวลาค้นหาจาก $\mathcal{O}(N)$ สู่ $\mathcal{O}(1)$:
  $$T_{\text{lookup}}(\text{set}) = \mathcal{O}(1) \ll \mathcal{O}(N)_{\text{list}}$$

### `DIM-086` / `EQ-086`: M08 Dict Default Lookup Invariant
- การแปลงบล็อก `if k in d: v = d[k] else: v = v0` ให้กลายเป็น `dict.get(k, v0)`:
  $$\text{dict.get}(k, v_0) \equiv v_0 \iff k \notin \text{keys}$$

### `DIM-087` / `EQ-087`: List Comprehension Memory Footprint Bound
- การแปลงลูป `for ...: list.append(...)` ให้กลายเป็น List Comprehension เพื่อเพิ่มความเร็วในการจัดสรร Memory:
  $$\text{Mem}(\text{Comp}) \le \text{Mem}(\text{For\_Append})$$

### `DIM-088` / `EQ-088`: Generator Stream Constant Memory Ceiling
- การแปลงการสร้างลิสต์ขนาดใหญ่ในหน่วยความจำสู่ Generator Expression ช่วยลด Memory Ceiling จาก $\mathcal{O}(N)$ สู่ $\mathcal{O}(1)$:
  $$\text{Mem}(\text{Generator}) = \mathcal{O}(1) \ll \mathcal{O}(N)$$

### `DIM-089` / `EQ-089`: Structural Delta Serialization Ratio
- บันทึกเฉพาะ Delta การเปลี่ยนแปลงของ AST โดยมีสัดส่วนขนาดไม่เกิน 15% ของไฟล์เดิม:
  $$\text{Ratio} = \frac{|\Delta_{\text{AST}}|}{|S_{\text{original}}|} \le 0.15$$

### `DIM-090` / `EQ-090`: Mutation Reversibility Snapshot Identity
- การันตีว่าการเปลี่ยนแปลงของ M05-M08 สามารถ Rollback กลับสู่โค้ดต้นฉบับได้ 100%:
  $$\mathcal{M}^{-1}(\mathcal{M}(\text{AST})) \equiv \text{AST}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D09-01` [List to Set Transformation]:** รัน M08 บนลูปค้นหาข้อมูล 10,000 รายการ ตรวจสอบว่าความเร็ว Latency ดีขึ้นอย่างน้อย $10\times$
2. **Test `TC-D09-02` [Inlining Call Frame]:** รัน M07 ยุบรวมฟังก์ชัน Helper เล็กๆ ตรวจสอบว่าจำนวน Frame Allocation ลดลงตามสมการ
3. **Test `TC-D09-03` [Deque Append Performance]:** ทดสอบการแทรกข้อมูลด้านหน้า 50,000 ครั้ง ยืนยันว่า deque เร็วกว่า list อย่างมีนัยสำคัญ
4. **Test `TC-D09-04` [Generator Memory Bound]:** ประมวลผลสตรีมข้อมูล 1,000,000 รายการ ตรวจสอบว่า Memory Footprint คงที่ $\mathcal{O}(1)$
