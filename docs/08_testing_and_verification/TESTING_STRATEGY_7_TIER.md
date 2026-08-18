# 7-Tier Quality Assurance Testing Strategy

> **Subsystem:** Test Architecture & Quality Assurance  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S16-001` .. `REQ-S16-002`, `REQ-S17-001` .. `REQ-S17-003`, `REQ-S18-001` .. `REQ-S18-003`

---

## 1. The 7-Tier Test Matrix

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             7-TIER QA TEST MATRIX                                │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Tier 7: Golden Test Corpus Conformance (MVP-01 .. MVP-14)                        │
│ Tier 6: Crash Recovery & CAS Reconciliation Chaos Tests                          │
│ Tier 5: Negative Security & Sandbox Attack Vectors                               │
│ Tier 4: FSM Reachability & Deadlock Exhaustion Proofs                            │
│ Tier 3: Property-Based Testing (Hypothesis PBT)                                  │
│ Tier 2: Schema & Fixture Meta-Validation (Draft 2020-12)                         │
│ Tier 1: Unit Tests & AST Visitor Determinism                                     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tier Details & Pass Criteria

1. **Tier 1 (Unit Tests):** ทดสอบฟังก์ชันและโมดูลย่อยทั้งหมด ต้องมี Test Coverage $\ge 90\%$
2. **Tier 2 (Schema Validation):** ตรวจสอบไฟล์ `schemas/*.schema.json` ทั้ง 26 ตัวกับ Meta-schema Draft 2020-12 พร้อม Fixtures valid/invalid
3. **Tier 3 (PBT):** สุ่มตัวเลขทศนิยมและ Invariants ทางคณิตศาสตร์อย่างน้อย 1,000 ตัวอย่างต่อรอบ
4. **Tier 4 (FSM Testing):** ทดสอบ Transition ทุกเส้นทางทั้ง 5 State Machines ยืนยันว่าไม่มี Deadlock
5. **Tier 5 (Negative Security):** รันโค้ดโจมตี (File Escape, Socket, Fork Bomb) ต้องถูก `QUARANTINED` ทั้งหมด
6. **Tier 6 (Crash Chaos):** จำลองตัดไฟ 4 จุดระหว่างการ Commit ต้องกู้คืน State กลับมาได้ 100%
7. **Tier 7 (Golden Corpus):** รันโปรเจกต์มาตรฐาน MVP-01 ถึง MVP-14 ต้อง Replay ได้ผลลัพธ์แบบ Bit-Identical (`R4`)
