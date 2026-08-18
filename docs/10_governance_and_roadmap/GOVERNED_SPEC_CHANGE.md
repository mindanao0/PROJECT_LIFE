# Governed Specification Change Process (Section 27)

> **Subsystem:** Specification Change Governance & Audit Trail  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S27-001` .. `REQ-S27-002`

---

## 1. Step-by-Step Governance Workflow

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    GOVERNED SPECIFICATION CHANGE WORKFLOW                        │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. Proposal Draft (RFC) : เปิด PR พร้อมระบุ Scope, Rationale และ Affected REQ IDs │
│ 2. Automated Linting    : ผ่าน Spec Linters 8 ตัว และ Schema Validation           │
│ 3. Impact Assessment    : ประเมินผลกระทบต่อ Release Gates และ Golden Corpus       │
│ 4. Multi-Party Review   : ได้รับความเห็นชอบจาก Reviewer อย่างน้อย 2 ฝ่าย          │
│ 5. Security Sign-off    : ได้รับการรับรองว่าไม่กระทบ PROFILE_A_LINUX Sandbox      │
│ 6. Traceability Update  : ปรับปรุงไฟล์ spec/traceability.yaml พร้อม Text Digest   │
│ 7. Atomic Ratification  : Commit ลง Canonical Document และออก Evidence Snapshot    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Invariants
- **[REQ-S27-001]** ห้ามแก้ไข Requirement Text โดยไม่มีการปรับปรุง Text Digest และ Re-run Linters
- **[REQ-S27-002]** ห้ามลบ Requirement ID ในลักษณะที่ทำให้ประวัติการตรวจสอบย้อนหลังสูญหาย
