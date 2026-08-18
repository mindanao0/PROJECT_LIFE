# Python AST Special Cases & Language Edge Handling (CPython 3.12+)

> **Subsystem:** Python Language Semantics & AST Special Cases  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S03-001`, `REQ-S09-001`

---

## 1. Preserved Constructs & Syntax Rules

ในการวิวัฒนาการโค้ดภาษา Python (CPython 3.12+) ตัวดำเนินการกลายพันธุ์ต้องปฏิบัติตามกฎการคุ้มครองไวยากรณ์อย่างเข้มงวด:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      PYTHON 3.12+ SYNTAX INVARIANTS                              │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. Docstring Preservation:                                                       │
│    • คอนฟิก preserve_docstrings: true                                            │
│    • AST Mutator ห้ามลบ ast.Expr(value=ast.Constant(str)) ที่เป็น Docstrings     │
│                                                                                  │
│ 2. Type Hints & Annotations:                                                     │
│    • คอนฟิก preserve_type_hints: true                                            │
│    • ห้ามลบ Type Annotations ใน ast.AnnAssign หรือ ast.arg.annotation            │
│                                                                                  │
│ 3. Built-in Decorators:                                                          │
│    • ห้ามลบหรือแก้ไข @dataclass, @property, @staticmethod, @classmethod         │
│                                                                                  │
│ 4. Async / Await Coroutines:                                                     │
│    • การกลายพันธุ์ใน ast.AsyncFunctionDef ห้ามลบ await จนกลายเป็น Blocking Code  │
│                                                                                  │
│ 5. Structural Pattern Matching (PEP 634):                                        │
│    • ใน ast.Match ห้ามสร้าง Duplicate Wildcard (case _) ซ้ำ                      │
│                                                                                  │
│ 6. PEP 695 Type Parameters (Python 3.12):                                        │
│    • รองรับ syntax def f[T](x: T) -> T: และ type Alias = int | str               │
│                                                                                  │
│ 7. Walrus Operator (:= NamedExpr):                                               │
│    • ห้ามเปลี่ยน Scope ของตัวแปร หรือสร้าง Unbound Identifier ก่อนการใช้งาน      │
└──────────────────────────────────────────────────────────────────────────────────┘
```
