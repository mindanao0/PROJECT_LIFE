# Governance & Governed Spec Change FSM Specification (12 States)

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** FSM SPECIFICATION (L2 Authority)
> **Target Subsystem:** Specification Governance & Traceability Engine  
> **Governing Equations:** `EQ-025` (Governance Quorum Function), `EQ-293` (Multi-Party Quorum), `EQ-292` (178 Monotonic Requirements)

---

## 1. Complete 12-State Topology

วงจรสถานะการเสนอและอนุมัติแก้ไขข้อกำหนดแม่บท (12 Governance States):

```text
       [PROPOSAL_SUBMITTED]
               │
               ▼
       [LINTERS_PASSED] ──────────┐ (Lint Failed)
               │                  │
               ▼                  ▼
     [IMPACT_ANALYZED] ─────► [REJECTED]
               │                  ▲
               ▼                  │ (Vetoed)
     [MULTI_PARTY_REVIEW] ────────┤
               │                  │
               ▼                  │
        [VOTING_OPEN] ────────────┘
               │
               ▼
       [QUORUM_REACHED]
               │
               ▼
     [SIGNATURES_COLLECTED] (2-of-3 Multisig)
               │
               ▼
      [RATIFIED_CANONICAL]
               │
               ▼
      [SCHEMA_MIGRATED]
               │
               ▼
      [EVIDENCE_ARCHIVED]
```

### 1.1 Formal State Definitions
1. `PROPOSAL_SUBMITTED`: ยื่นคำขอแก้ไขสเปก (RFC / Spec Change Request)
2. `LINTERS_PASSED`: สเปกผ่านการตรวจสอบรูปแบบจาก Spec Linters ทั้ง 8 ตัว
3. `IMPACT_ANALYZED`: วิเคราะห์ผลกระทบต่อ 176 Requirements และ 300 Dimensions
4. `MULTI_PARTY_REVIEW`: ตรวจสอบโดยคณะกรรมการวิศวกรรม (อย่างน้อย 2 คนที่ไม่ใช่ผู้เขียน)
5. `VOTING_OPEN`: เปิดให้ลงคะแนนเสียง
6. `QUORUM_REACHED`: คะแนนเสียงผ่านเกณฑ์ Quorum $\ge 75\%$
7. `SIGNATURES_COLLECTED`: รวบรวมลายเซ็น Ed25519 ครบ 2 ใน 3 (EE-CRYPTO-1)
8. `RATIFIED_CANONICAL`: สเปกได้รับการรับรองเป็นมาตรฐานสถาปัตยกรรมอย่างเป็นทางการ
9. `SCHEMA_MIGRATED`: อัปเดตไฟล์ JSON Schemas และ Protocol Interfaces ที่เกี่ยวข้อง
10. `EVIDENCE_ARCHIVED`: จัดเก็บหลักฐานการอนุมัติและ Audit Trail ลง CAS
11. `REJECTED`: คำขอถูกปฏิเสธเนื่องจากไม่ผ่านเกณฑ์หรือถูก Veto
12. `SUPERSEDED`: สเปกเดิมถูกแทนที่ด้วยเวอร์ชันใหม่ที่ผ่านกระบวนการสมบูรณ์

---

## 2. Quorum Rules & Invariant Proofs

1. **Independent Approver Invariant:** ผู้เขียน RFC ห้ามเป็นผู้อนุมัติคำขอของตนเอง:
   $$\text{Author}(\text{RFC}) \notin \text{Approvers}(\text{RFC})$$
2. **2-of-3 Cryptographic Multisig:** บันทึกสเปกต้องลงนามด้วยกุญแจ Ed25519 อย่างน้อย 2 ใน 3:
   $$\sum_{i=1}^3 \text{VerifySig}(K_i, M_{\text{spec}}, S_i) \ge 2$$
3. **Monotonic Requirement Traceability:** รหัส Requirement IDs ครบ 176 ข้อ ห้ามถูกลบทิ้งโดยไม่ผ่านขั้นตอน Deprecation Cycle
