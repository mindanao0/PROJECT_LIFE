# Automated Specification Linters Suite Specification

> **Subsystem:** Static Specification Integrity Checkers  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S02-009`

---

## 1. The 8 Specialized Specification Linters

```text
┌────┬──────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ No │ Linter Script Name                       │ Logic & Assertions Description                              │
├────┼──────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 01 │ spec_utf8_control_char_lint.py           │ สแกนทุกไบต์ใน .md ไฟล์ ปฏิเสธ Control Chars แปลกปลอม        │
│ 02 │ spec_heading_classification_lint.py      │ ยืนยันว่าทุก Header มี [NORMATIVE] หรือ [INFORMATIVE] ชัดเจน │
│ 03 │ spec_single_active_version_lint.py       │ ยืนยันว่ามีเฉพาะเวอร์ชัน 10.2.2 ปรากฏใน Active Specification│
│ 04 │ spec_no_historical_normative_freeze_lint │ ยืนยันว่าไม่มีคำสั่ง Freeze ในอดีตมามีผลบังคับใช้           │
│ 05 │ spec_active_view_byte_match.py           │ ตรวจสอบ SHA-256 ของ Active Spec View ให้ตรงกับ Canonical    │
│ 06 │ spec_archive_checksum_match.py           │ ยืนยันว่า Historical Archive (Appendix C) ไม่ถูกลบหรือแก้    │
│ 07 │ spec_requirement_id_unique_complete.py   │ ยืนยันว่ามี Requirement IDs ครบ 179 ข้อ และเรียง 001..N     │
│ 08 │ spec_requirement_digest_change_guard.py  │ ตรวจสอบ Text Digest ป้องกันการแอบแก้ไขข้อความใน Requirement  │
└────┴──────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

- **[REQ-S02-009]** เครื่องมือ Linters ทั้ง 8 ตัวต้องถูกรันใน Pre-commit Hook และใน CI Pipeline ทุกครั้งก่อนการ Merge PR
