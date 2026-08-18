# 04 — Program Representation, AST Safety Invariants & Unified Mutation Engine

> **Active Requirements Covered:** `REQ-S09-001` .. `REQ-S09-005` (Unified v1 Full Scope)  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Not normative.  
> **Canonical source:** [`docs/04_representation_and_mutation/`](./04_representation_and_mutation/) — เมื่อขัดกัน ให้ยึดฝั่งนั้น

Evolution Engine v1 รวมความสามารถในการกลายพันธุ์ทั้งแบบมาตรฐานไวยากรณ์ (Syntax Tree Mutations), การประยุกต์ทฤษฎีควอนตัม (Quantum-Inspired Rotation), และการแปลงข้ามภาษา (Cross-Language AST Subtree Bridges) เข้าเป็นหนึ่งเดียวใน Core

---

## 1. Representation Authority

ลำดับความสำคัญของตัวแทนโค้ด:
```text
AST (Abstract Syntax Tree)   = โครงสร้างความหมายหลัก / Input สำหรับระบุ Identity
CST (Concrete Syntax Tree)   = ตัวเลือกสำหรับ Format-preserving rewrite (คง formatting เดิม)
UAST (Universal Polyglot AST)= ตัวแทนโครงสร้างไวยากรณ์ร่วมข้ามภาษา (Python <-> Rust/C++)
CFG (Control Flow Graph)     = ตัวช่วยสำหรับการวิเคราะห์ Branch/Loop
Source Bytes                 = สิ่งที่ใช้กำหนด Hash Identity ของ Artifact ที่ส่งออก
```

- **[REQ-S09-001]** **ห้าม import โปรเจกต์เป้าหมายใน host process** เพื่อวิเคราะห์ source (ใช้วิธี static AST parse ด้วย `ast.parse(source_bytes)` เสมอ)
- **[REQ-S09-002]** Static parse เป็น Default discovery path

---

## 2. Python AST Special Cases & Language Edge Handling

ในการจัดการกับไวยากรณ์และฟีเจอร์เฉพาะของภาษา Python (CPython 3.12+):

1. **Docstring & Type Annotation Preservation:**
   - คอนฟิก `preserve_docstrings: bool = true` และ `preserve_type_hints: bool = true`
   - AST Mutator จะไม่ลบ `Expr(value=Constant(str))` ที่เป็น module/class/function docstrings และจะไม่ทำลาย Type Annotations ใน `AnnAssign` หรือ `arg.annotation`
2. **Decorator Preservation (`@decorator`):**
   - ห้ามลบหรือเปลี่ยน Built-in Decorators เช่น `@dataclass`, `@property`, `@staticmethod`, `@classmethod`
   - Custom Decorators ให้คงไว้เป็น Immutable Wrapper ล้อมรอบฟังก์ชัน
3. **Async / Await Syntax (`async def` / `await`):**
   - การกลายพันธุ์ใน `AsyncFunctionDef` ห้ามลบ `await` ออกจนทำให้กลายเป็น Synchronous blocking code
   - ต้องรันผ่าน Isolated Asyncio Event Loop
4. **Structural Pattern Matching (`match / case`):**
   - การกลายพันธุ์ใน `Match` และ `match_case` ต้องรักษา `MatchAs` / `MatchClass` structure และห้ามสร้าง duplicate wildcard pattern (`case _`) ซ้ำ
5. **Assignment Expressions (Walrus Operator `:=`):**
   - การกลายพันธุ์ `NamedExpr` ต้องไม่เปลี่ยน Scope หรือสร้าง Unbound Identifier ก่อนการใช้งาน

---

## 3. Pre-execution AST Safety Invariants Visitor

ก่อนส่ง Candidate เข้า Sandbox ระบบจะรัน `ASTSafetyInvariantsChecker` เพื่อตัด Candidate ที่ผิดพลาดตั้งแต่ขั้นตอน Static Validation:

```python
import ast

class ASTSafetyInvariantsChecker(ast.NodeVisitor):
    """ตรวจจับโครงสร้างอันตรายหรือไวยากรณ์ที่ทำให้เกิด Runtime Error แน่นอน"""
    def __init__(self):
        self.violations = []

    def visit_Import(self, node: ast.Import):
        # ตรวจสอบการ import module ที่ไม่อยู่ใน whitelist ของ project
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global):
        # ป้องกันการ inject global mutation ที่ทำลาย isolation
        self.generic_visit(node)

    def visit_Nonlocal(self, node: ast.Nonlocal):
        self.generic_visit(node)
```

---

## 4. Complete Unified Mutation Registry (M01 – M10)

ชุดตัวดำเนินการกลายพันธุ์ฉบับสมบูรณ์สำหรับ Core v1:

| รหัส | ชื่อกลยุทธ์ (Strategy) | รายละเอียดการทำงาน | ความเสี่ยง (Risk) |
|---|---|---|---|
| **M01** | `constant_mutation` | ปรับเปลี่ยนค่าคงที่ (Numeric values, String literals, Booleans, Step increments) | LOW |
| **M02** | `operator_mutation` | สลับ Arithmetic, Bitwise, Comparison หรือ Logical Operators (`+` $\leftrightarrow$ `-`, `<` $\leftrightarrow$ `<=`, `and` $\leftrightarrow$ `or`) | LOW |
| **M03** | `condition_boundary` | ปรับเงื่อนไขขอบเขตใน `if`, `while`, Ternary expressions (Off-by-one, boundary checks) | MEDIUM |
| **M04** | `loop_control_flow` | ปรับเปลี่ยนโครงสร้าง Loop (`for` $\leftrightarrow$ `while`, `break`, `continue`, loop bounds, range steps) | MEDIUM |
| **M05** | `function_replacement` | สลับการเรียกใช้ฟังก์ชันใน Standard Library หรือ Helper ภายในโมดูลเดียวกัน | MEDIUM |
| **M06** | `function_extraction` | แตกก้อนโค้ดที่มีความซ้ำซ้อนออกมาเป็น Pure Sub-function | HIGH |
| **M07** | `function_inlining` | ยุบรวมฟังก์ชันขนาดเล็กกลับเข้ามาใน caller เพื่อลด call-stack overhead | HIGH |
| **M08** | `data_structure_swap` | สลับชนิดโครงสร้างข้อมูลภายใน (เช่น `list` $\leftrightarrow$ `deque`, `dict` lookup $\leftrightarrow$ `set` containment) | HIGH |
| **M09** | `quantum_rotation_mutation` | ใช้ **Quantum-Inspired Rotation Gate** ปรับความน่าจะเป็นของยีนแบบต่อเนื่อง (Superposition Exploration) | MEDIUM |
| **M10** | `cross_language_subtree_bridge` | สกัด Algorithmic Hotspot แปลงเป็น **Compiled Native Kernel (Rust/C Extension)** เพื่อความเร็วระดับฮาร์ดแวร์ | HIGH |

---

## 5. Quantum-Inspired Rotation Operator (M09 Specification)

ในกลยุทธ์ **M09 (Quantum-Inspired Mutation)** ยีนแต่ละตำแหน่งจะถูกแทนด้วย Qubit Probability Vector $[\alpha_j, \beta_j]^T$ โดยที่ $|\alpha_j|^2 + |\beta_j|^2 = 1$:

$$\begin{bmatrix} \alpha_j' \\ \beta_j' \end{bmatrix} = \begin{bmatrix} \cos(\Delta \theta_j) & -\sin(\Delta \theta_j) \\ \sin(\Delta \theta_j) & \cos(\Delta \theta_j) \end{bmatrix} \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}$$

- ค่ามุมหมุน $\Delta \theta_j = s(\alpha_j, \beta_j) \times \delta \theta$ จะถูกคำนวณเปรียบเทียบระหว่าง Candidate ปัจจุบันกับ Pareto Best Solution
- ช่วยให้ Engine สามารถกระโดดข้าม Local Optima และสำรวจพื้นที่ค้นหาที่ซับซ้อนได้อย่างรวดเร็ว

---

## 6. Cross-Language AST Subtree Bridge (M10 Specification)

ในกลยุทธ์ **M10**:
1. **Hotspot Profiling:** ตรวจจับ Loop หรือ Math Calculation ที่กินเวลา CPU สูงสุดใน Python
2. **UAST Mapping:** แปลง Python AST Node $\rightarrow$ Universal AST $\rightarrow$ Native Rust / C Foreign Function Code
3. **Sandbox Compilation:** คอมไพล์ใน Sandbox ด้วย `rustc` / `gcc` (ผ่าน cgroups quota) ให้เป็น `.so` / `.pyd` module
4. **Transparent Foreign Import:** เชื่อมต่อผ่าน Python `ctypes` / `cffi` โดยยังคงรักษา Interface เดิมของฟังก์ชันไว้ 100%

---

## 7. Multi-Armed Bandit Adaptive Mutation (UCB1)

ระบบบริหารสัดส่วนการเรียกใช้กลยุทธ์ M01–M10 อัตโนมัติด้วยอัลกอริทึม **UCB1**:

$$\text{Score}_i = \bar{X}_i + c \sqrt{\frac{\ln N}{n_i}}$$

- **[REQ-S09-004]** **Reward คิดจาก Candidate ที่ผ่าน Capability Gates เท่านั้น**
