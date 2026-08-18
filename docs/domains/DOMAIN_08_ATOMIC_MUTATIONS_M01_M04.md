# Domain 08: Atomic Syntax & Control Flow Mutations (M01-M04)

> **Domain Index:** `DOMAIN-08`  
> **Engineering Scope:** `DIM-071` .. `DIM-080`  
> **Mathematical Equations:** `EQ-071` .. `EQ-080`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 08 กำหนดตัวดำเนินการกลายพันธุ์ระดับอะตอม (Atomic AST Mutation Operators) 4 ตัวแรก ได้แก่ **M01 (Constant Mutation)**, **M02 (Operator Mutation)**, **M03 (Condition Boundary Mutation)**, และ **M04 (Loop Control Flow Mutation)** ซึ่งทำหน้าที่สำรวจพื้นที่คำตอบในระดับ Local Optimization.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-071  │ EQ-071   │ M01 Numeric Constant Mutation Step        │ x' = x + (-1)^s * delta, delta in {1, 2, x/2}               │
│ DIM-072  │ EQ-072   │ M01 String Literal Levenshtein Bound      │ d_Lev(S, S') <= 3                                           │
│ DIM-073  │ EQ-073   │ M01 Boolean Inversion Operation           │ b' = not b                                                  │
│ DIM-074  │ EQ-074   │ M02 Arithmetic Operator Swap Matrix       │ P_swap in {0, 1}^{7x7}, Tr(P_swap) = 0                      │
│ DIM-075  │ EQ-075   │ M02 Comparison Operator Dual Inversion    │ Op' in {<, <=, >, >=, ==, !=} \ {Op}                        │
│ DIM-076  │ EQ-076   │ M02 Logical Operator De Morgan Equiv      │ not(A and B) === (not A or not B)                           │
│ DIM-077  │ EQ-077   │ M03 Condition Boundary Shift Inequality   │ Cond' = (x <= theta + epsilon)                              │
│ DIM-078  │ EQ-078   │ M04 Loop Step Size Discrete Mutation      │ Step' = Step +- 1, Step' != 0                               │
│ DIM-079  │ EQ-079   │ M04 For-While Control Equivalence         │ for x in L <=> while i < len(L)                             │
│ DIM-080  │ EQ-080   │ M04 Control Flow Jump Preservation        │ ValidExitPaths(Mutated) >= 1                                │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-071` / `EQ-071`: M01 Numeric Constant Mutation Step
- **Transformation Form:** ตัวเลขคงที่ $x \in \mathbb{R}$ จะถูกปรับเปลี่ยนตามสเต็ปที่สุ่มเลือก:
  $$x' = x + (-1)^s \cdot \delta, \quad s \in \{0, 1\}, \quad \delta \in \{1, 2, \lfloor x/2 \rfloor, 0.1 \times x\}$$

### `DIM-072` / `EQ-072`: M01 String Literal Levenshtein Bound
- การกลายพันธุ์สตริงคงที่ถูกจำกัดระยะห่าง Levenshtein ไม่เกิน 3 ตัวอักษร:
  $$d_{\text{Lev}}(S, S') \le 3$$

### `DIM-073` / `EQ-073`: M01 Boolean Inversion Operation
- การกลับค่าตรรกะแบบตรงไปตรงมา:
  $$b' = \neg b$$

### `DIM-074` / `EQ-074`: M02 Arithmetic Operator Swap Matrix
- การสลับ Operator เลขคณิตผ่าน Permutation Matrix $\mathbf{P} \in \{0, 1\}^{7 \times 7}$ โดย $\text{Tr}(\mathbf{P}) = 0$:
  $$\text{Op} \in \{+, -, *, /, //, \%, **\} \longrightarrow \text{Op}' \ne \text{Op}$$

### `DIM-075` / `EQ-075`: M02 Comparison Operator Dual Inversion
- การเปลี่ยนตัวเปรียบเทียบในเงื่อนไข:
  $$\text{Op}' \in \{<, \le, >, \ge, ==, \ne\} \setminus \{\text{Op}\}$$

### `DIM-076` / `EQ-076`: M02 Logical Operator De Morgan Equiv
- การแปลงนิพจน์ตรรกะตามกฎ De Morgan:
  $$\neg(A \land B) \equiv (\neg A \lor \neg B)$$

### `DIM-077` / `EQ-077`: M03 Condition Boundary Shift Inequality
- การปรับค่าขอบเขตการตัดสินใจในคำสั่ง `if`:
  $$\text{Cond}' = (x \le \theta + \epsilon)$$

### `DIM-078` / `EQ-078`: M04 Loop Step Size Discrete Mutation
- การปรับขนาด Step ใน `range()`:
  $$\text{Step}' = \text{Step} \pm 1, \quad \text{Step}' \ne 0$$

### `DIM-079` / `EQ-079`: M04 For-While Control Equivalence
- การแปลงลูป `for` สู่ลูป `while` เพื่อเปิดโอกาสให้เกิดการ Optimize ในระดับตัวนับ:
  $$\text{for } x \text{ in } L \iff \text{while } i < \text{len}(L)$$

### `DIM-080` / `EQ-080`: M04 Control Flow Jump Preservation
- การรักษารูปแบบคำสั่ง `break` และ `continue` ให้มีทางออกจากลูปที่ถูกต้องเสมอ:
  $$\text{ValidExitPaths}(\text{Mutated}) \ge 1$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D08-01` [Constant Step Validity]:** รัน M01 บนฟังก์ชันทางคณิตศาสตร์ ตรวจสอบว่าค่าคงที่ถูกปรับตามช่วงที่กำหนดและไม่เกิด Zero Division
2. **Test `TC-D08-02` [Comparison Swap Invariant]:** รัน M02 บน Branch Comparison ยืนยันว่า Node ชนิด `ast.Compare` ได้รับการแปลงอย่างถูกต้อง
3. **Test `TC-D08-03` [De Morgan Equivalence Check]:** ตรวจสอบว่าตารางค่าความจริงของนิพจน์ก่อนและหลังแปลง De Morgan ให้ผลลัพธ์ตรงกัน 100%
4. **Test `TC-D08-04` [Loop Exit Invariant]:** แปลงลูป `for` เป็น `while` ตรวจสอบว่ามีตัวเพิ่มค่าตัวแปรดัชนีและไม่ติด Infinite Loop
