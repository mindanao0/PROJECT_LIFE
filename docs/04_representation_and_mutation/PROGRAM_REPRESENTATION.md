# Program Representation Authority (AST, CST, UAST & CFG)

> **Subsystem:** Static Code Analysis & Syntax Trees  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S09-001`, `REQ-S09-002`

---

## 1. Syntax Representation Hierarchy

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      PROGRAM REPRESENTATION HIERARCHY                            │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. AST (Abstract Syntax Tree)    : โครงสร้างความหมายหลัก ใช้คำนวณ Hash Identity  │
│ 2. CST (Concrete Syntax Tree)    : ตัวแทนรักษา Formatting, Indents และ Comments  │
│ 3. UAST (Universal Polyglot AST) : ไวยากรณ์กลางสำหรับแปลงข้ามภาษา (Python <-> Native)│
│ 4. CFG (Control Flow Graph)      : วิเคราะห์เส้นทางเงื่อนไข ลูป และ Branch Coverage │
│ 5. Source Bytes                  : ข้อมูลไบนารีสำหรับคำนวณ Content Digest SHA-256│
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Invariants & Parse Authority

1. **Host Isolation Invariant [REQ-S09-001]:** **ห้าม import โปรเจกต์เป้าหมายใน host process** เพื่อวิเคราะห์โครงสร้างโค้ดโดยเด็ดขาด การค้นหา Entry Points และ Functions ต้องใช้วิธี Static Parse ด้วย `ast.parse(source_bytes)` เสมอ
2. **Static Discovery Default [REQ-S09-002]:** การระบุตัวตนของฟังก์ชันเป้าหมาย (`TargetFunctionDef`) จะใช้ `ast.FunctionDef` หรือ `ast.AsyncFunctionDef`
3. **Format-Preserving Rewrites:** เมื่อส่งออกโค้ดจริง (Export) ระบบจะใช้ Concrete Syntax Tree (LibCST) เพื่อรักษา Style ดั้งเดิมของผู้เขียนโค้ดไว้ให้มากที่สุด
