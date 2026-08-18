# Flaky Test Detection, Isolation Boundary & Anti-Gaming Protocols

> **Subsystem:** Test Reliability & Non-Gaming Protocols  
> **Authority Level:** NORMATIVE (`REQ-S17-001` .. `REQ-S17-003`)

---

## 1. Flaky Test Detection Algorithm

เมื่อมีการรันชุดทดสอบซ้ำ $K$ ครั้งบน Candidate เดียวกัน:
- หากผลลัพธ์มีทั้ง `PASS` และ `FAIL` $\implies$ Test Case นั้นจะถูกประเมินเป็น **`FLAKY`**
- Candidate ที่เกี่ยวข้องจะได้รับ Verdict เป็น **`INCONCLUSIVE`** และถูกส่งเข้าสู่สถานะ **`REJECTED`** ทันที

---

## 2. Inviolable Anti-Gaming Rules

1. **No-Retry Rule [REQ-S17-001]:** **ห้ามสั่ง Retry การทดสอบซ้ำๆ เพื่อหวังผลให้ผ่านโดยเด็ดขาด** (Anti-Flaky Gaming)
2. **Quarantine Test Suite Isolation [REQ-S17-003]:** Test Case ที่ติดสถานะ Flaky จะถูกย้ายเข้าสู่ Quarantine Test Suite และจะไม่ถูกนำมาใช้เป็น Capability Gate จนกว่าผู้ดูแลโปรเจกต์จะแก้ไขปัญหา Race Condition
3. **Audit Event Logging:** ทุกครั้งที่มีการตรวจพบ Flaky Test ระบบจะบันทึกรหัส Test ID และสถิติการ Flake ลงในตาราง `audit_events`
