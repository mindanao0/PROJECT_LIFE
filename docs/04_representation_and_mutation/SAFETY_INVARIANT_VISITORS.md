# Static Safety Invariant Visitors Specification

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** COMPILER SPECIFICATION (L4 Authority)
> **Target Subsystem:** AST Static Security Sanitizer  
> **Governing Equations:** `EQ-061` .. `EQ-070` (Static Visitor Invariants)

---

## 1. Visitor Hierarchy & Fail-Fast Static Filters

`ASTSafetyInvariantsChecker` ดำเนินการวิเคราะห์ Abstract Syntax Tree ผ่าน 8 Visitors ย่อย ก่อนส่ง Candidate เข้าสู่ Sandbox:

```text
┌───────────────────────────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────┐
│ Visitor Class Name            │ Prohibited AST Pattern Checked            │ Action & Reason Code on Violation               │
├───────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ ImportWhitelistVisitor        │ ast.Import / ImportFrom not in whitelist  │ Reject immediately (ERR_UNAUTHORIZED_IMPORT)    │
│ DynamicExecutionBlocker       │ Calls to eval(), exec(), compile()        │ Reject immediately (ERR_DYNAMIC_EXECUTION)      │
│ DunderNamespaceProtection     │ Attribute __subclasses__, __globals__     │ Reject immediately (ERR_DUNDER_ABUSE)           │
│ GlobalScopeDenialVisitor      │ ast.Global / ast.Nonlocal node usage      │ Reject immediately (ERR_GLOBAL_MUTATION)        │
│ LoopRecursionDepthVisitor     │ Nested loops > 8 levels                   │ Reject immediately (ERR_LOOP_DEPTH_EXCEEDED)    │
│ MutableDefaultArgVisitor      │ def f(x=[]), def f(x={})                  │ Reject immediately (ERR_MUTABLE_DEFAULT)        │
│ SocketNetworkBlocker          │ Any reference to socket or urllib         │ Reject immediately (ERR_NETWORK_PRIMITIVE)      │
│ AsyncAwaitIntegrityVisitor    │ Stripping await from async functions      │ Reject immediately (ERR_ASYNC_AWAIT_STRIPPED)   │
└───────────────────────────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

## 2. Invariant Filtering Rules & Formal Proofs

Candidate จะได้รับอนุญาตให้ไปต่อใน Sandbox ก็ต่อเมื่อผ่าน Visitors ทั้งหมด 100%:
$$\text{Safe}(\text{AST}) \iff \bigwedge_{v \in \text{Visitors}} \text{Pass}(v, \text{AST})$$
หากไม่ผ่าน Visitor แม้แต่ตัวเดียว Candidate จะถูกคัดทิ้งทันทีในสถานะ `STATIC_VALIDATION_FAILED` โดยไม่สิ้นเปลืองเวลาเปิด Sandbox Worker
