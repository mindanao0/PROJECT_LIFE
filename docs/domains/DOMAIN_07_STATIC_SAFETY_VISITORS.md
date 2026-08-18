# Domain 07: Static Pre-Execution Safety Invariant Visitors

> **Domain Index:** `DOMAIN-07`  
> **Engineering Scope:** `DIM-061` .. `DIM-070`  
> **Mathematical Equations:** `EQ-061` .. `EQ-070`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 07 กำหนดการตรวจสอบความปลอดภัยของ Abstract Syntax Tree ก่อนส่งเข้าสู่กระบวนการคอมไพล์หรือรันใน Sandbox (Fail-Fast Static Sanitization) ผ่านตัวกรอง `ASTSafetyInvariantsChecker` ป้องกันการลักลอบ Import โมดูลต้องห้าม, Dynamic Execution (`eval`/`exec`), Dunder Abuse, และ Infinite Loop Depths.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-061  │ EQ-061   │ Visitor Pre-execution Safety Filter       │ Safe(AST) <=> bigwedge_{v in Visitors} Pass(v, AST)         │
│ DIM-062  │ EQ-062   │ Import Whitelist Intersection Invariant   │ Imports(AST) subseteq W_allowed                             │
│ DIM-063  │ EQ-063   │ Global Scope Injection Denial Invariant   │ |{n in AST | Type(n) = ast.Global}| === 0                   │
│ DIM-064  │ EQ-064   │ Dynamic Execution Function Blocker        │ |{c in Calls(AST) | c in {eval, exec, compile}}| === 0      │
│ DIM-065  │ EQ-065   │ Dunder Namespace Protection Bound         │ forall a in Attr(AST), a not in {__subclasses__, __globals__}│
│ DIM-066  │ EQ-066   │ Recursive Loop Static Depth Bound         │ Depth_loop(AST) <= 8                                        │
│ DIM-067  │ EQ-067   │ Dead Code Branch Pruning Ratio            │ DeadCodeRatio = |UnreachableNodes| / |TotalNodes| <= 0.05   │
│ DIM-068  │ EQ-068   │ Static Off-By-One Boundary Proof          │ forall i in Indices, 0 <= i < Len(Array)                    │
│ DIM-069  │ EQ-069   │ Mutable Default Argument Zero Count       │ |{a in Args | Default(a) in {list, dict, set}}| === 0       │
│ DIM-070  │ EQ-070   │ AST Diagnostic Vector Error Distance      │ Delta_diag = sqrt((Line_1 - Line_2)^2 + (Col_1 - Col_2)^2)  │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-061` / `EQ-061`: Visitor Pre-execution Safety Filter
- **Requirement:** Candidate AST จะผ่านสู่ขั้นตอนรันได้ก็ต่อเมื่อผ่าน Visitors ทุกตัว:
  $$\text{Safe}(\text{AST}) \iff \bigwedge_{v \in \text{Visitors}} \text{Pass}(v, \text{AST})$$

### `DIM-062` / `EQ-062`: Import Whitelist Intersection Invariant
- **Requirement:** ทุกการ Import ใน Candidate AST ต้องอยู่ใน Whitelist ที่อนุญาตเท่านั้น:
  $$\text{Imports}(\text{AST}) \subseteq \mathcal{W}_{\text{allowed}}$$
- โมดูลต้องห้าม เช่น `socket`, `ctypes`, `subprocess`, `os.system` จะถูกปฏิเสธตั้งแต่ขั้นตอน Static Parsing โดยไม่ส่งเข้ารันใน Sandbox

### `DIM-063` / `EQ-063`: Global Scope Injection Denial Invariant
- ห้ามใช้คีย์เวิร์ด `global` หรือแก้ไข Global Scope จากภายในฟังก์ชัน:
  $$|\{n \in \text{AST} \mid \text{Type}(n) = \text{ast.Global}\}| \equiv 0$$

### `DIM-064` / `EQ-064`: Dynamic Execution Function Blocker
- **Requirement:** ห้ามมีการเรียกใช้ `eval()`, `exec()`, `compile()` หรือ `__import__()` ใน Candidate AST เด็ดขาด:
  $$|\{c \in \text{Calls}(\text{AST}) \mid c \in \{\text{eval}, \text{exec}, \text{compile}, \text{__import__}\}\}| \equiv 0$$

### `DIM-065` / `EQ-065`: Dunder Namespace Protection Bound
- ป้องกันการเข้าถึง Attributes อันตราย เช่น `__subclasses__` หรือ `__globals__`:
  $$\forall a \in \text{Attributes}(\text{AST}), \quad a \notin \{\text{__subclasses__}, \text{__globals__}, \text{__code__}\}$$

### `DIM-066` / `EQ-066`: Recursive Loop Static Depth Bound
- ความลึกของ Nested Loops ต้องไม่เกิน 8 ชั้น:
  $$\text{Depth}_{\text{loop}}(\text{AST}) \le 8$$

### `DIM-067` / `EQ-067`: Dead Code Branch Pruning Ratio
- สัดส่วนของโค้ดที่ไม่สามารถเข้าถึงได้ (Dead Code) ต้องไม่เกิน 5%:
  $$\text{DeadCodeRatio} = \frac{|\text{UnreachableNodes}|}{|\text{TotalNodes}|} \le 0.05$$

### `DIM-068` / `EQ-068`: Static Off-By-One Boundary Proof
- การสแกนดัชนี Array เพื่อป้องกัน Off-by-one errors:
  $$\forall i \in \text{Indices}, \quad 0 \le i < \text{Len}(\text{Array})$$

### `DIM-069` / `EQ-069`: Mutable Default Argument Zero Count
- ห้ามประกาศ Default Argument เป็น Mutable Objects (`[]`, `{}`):
  $$|\{a \in \text{Args} \mid \text{Default}(a) \in \{\text{list}, \text{dict}, \text{set}\}\}| \equiv 0$$

### `DIM-070` / `EQ-070`: AST Diagnostic Vector Error Distance
- ระยะห่างของจุดเกิดข้อผิดพลาดสำหรับการรายงานใน Diagnostic Report:
  $$\Delta_{\text{diag}} = \sqrt{(\text{Line}_1 - \text{Line}_2)^2 + (\text{Col}_1 - \text{Col}_2)^2}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D07-01` [Malicious Import Trapping]:** ส่ง Candidate ที่มีคำสั่ง `import socket` เข้า Static Visitor ระบบต้อง Reject และให้ Error Code `ERR_POLICY_VIOLATION`
2. **Test `TC-D07-02` [Eval Trap]:** ส่ง Candidate ที่มีคำสั่ง `eval("1+1")` เข้า Static Visitor ระบบต้องตรวจพบและปฏิเสธทันที
3. **Test `TC-D07-03` [Dunder Access Trap]:** ส่งโค้ด `().__class__.__subclasses__()` ตรวจสอบว่าถูกดักจับและปฏิเสธ
4. **Test `TC-D07-04` [Mutable Default Trap]:** ส่งฟังก์ชัน `def foo(x=[])` ตรวจสอบว่าถูกตรวจพบและแจ้งเตือน
