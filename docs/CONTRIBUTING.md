# Contributing Guidelines — Evolution Engine

> **Specification Reference:** Section 2, Section 22, Section 27  
> **Governance Model:** Governed Specification Change Process

ขอบคุณที่สนใจร่วมพัฒนา **Evolution Engine** โปรเจกต์นี้มีมาตรฐานด้านความถูกต้องและสถาปัตยกรรมที่เข้มงวด กรุณาปฏิบัติตามแนวทางด้านล่างเพื่อให้มั่นใจว่าการมีส่วนร่วมของคุณสอดคล้องกับ Active Contract ของระบบ

---

## 1. Core Contribution Rules

1. **Single Source of Truth:**
   - ห้ามเพิ่ม Section ใหม่เพื่อทับ Section เก่า
   - หากต้องการแก้ไขหรือแทนที่ข้อกำหนดเดิม ต้องแก้ที่ Source Definition หรือย้ายของเก่าออกจาก Active Specification ตามขั้นตอนใน Section 27
2. **Requirement Status Lifecycle:**
   - ข้อกำหนดทุกข้อเริ่มต้นด้วยสถานะ `[REQ]`
   - การเลื่อนสถานะเป็น `[IMPL]`, `[TEST]`, หรือ `[EVID]` จะทำได้ก็ต่อเมื่อมี Artifact, Conformance Tests หรือ Signed Evidence ที่ตรวจสอบได้จริงใน Repository
   - **ห้ามข้ามสถานะ**
3. **Requirement ID Immutability:**
   - ทุกข้อกำหนดต้องมี ID รูปแบบ `^REQ-S[0-9]{2}-[0-9]{3}$`
   - เมื่อ Publish แล้ว ห้ามนำ ID เดิมไปใช้ซ้ำ (Immutable ID) แม้ข้อกำหนดนั้นจะถูกถอนออก
4. **No LLM/AI Dependency in Core:**
   - โค้ดใน Core ต้องทำงานได้แบบ Pure Evolutionary Algorithm (AST/CST manipulation, Deterministic evaluation) โดยไม่พึ่งพา External AI API

---

## 2. Governed Specification Change Workflow (Section 27)

หากการเปลี่ยนแปลงของคุณส่งผลต่อ Active Specification หรือ Invariants ของระบบ ต้องผ่านขั้นตอนดังนี้:

```text
1. Change Proposal (เขียนข้อเสนอการเปลี่ยนแปลงและเหตุผล)
   │
   ▼
2. Impact Analysis (วิเคราะห์ผลกระทบต่อ L0-L9 Authority Levels)
   │
   ▼
3. Authority Check (ตรวจสอบว่าไม่ละเมิด Safety & Root-of-Trust Invariants)
   │
   ▼
4. Security & Safety Review (ตรวจสอบความปลอดภัยของ Sandbox และ Isolation)
   │
   ▼
5. Traceability Impact (อัปเดต Requirement IDs และ Traceability Matrix)
   │
   ▼
6. Human / Multisig Approval (ได้รับการอนุมัติจาก Reviewer ที่ไม่ใช่ Author)
   │
   ▼
7. Version Bump & Active Contract Update
   │
   ▼
8. Invalidate Affected Evidence & Re-run Required Gates
```

---

## 3. Pull Request Checklist

ก่อนส่ง Pull Request กรุณาตรวจสอบว่า:
- [ ] เอกสารผ่าน UTF-8 linting และไม่มี Control Characters ผิดรูป
- [ ] Heading ทุกหัวข้อมีแท็กระบุประเภท เช่น `[NORMATIVE]`, `[INFORMATIVE]`, หรือ `[RESEARCH]`
- [ ] ไม่มีข้อความที่ขัดแย้งกับ State Machines (FSMs) ทั้ง 5 ชุด
- [ ] คอนฟิกคำสั่งเป็นรูปแบบ `argv` list (`shell=false` เสมอ)
- [ ] ตัวเลขทศนิยมที่มีผลต่อการคำนวณและ Hash ใช้ Canonical Decimal String
