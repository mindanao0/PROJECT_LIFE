# Developer Tooling & Specification Linters

> **Subsystem:** CI/CD Automation & Spec Linters Suite  
> **Authority Level:** NORMATIVE (`REQ-S02-009`)

โฟลเดอร์นี้บรรจุเครื่องมือตรวจสอบสเปกอัตโนมัติ (Spec Linters) 8 ตัว และสคริปต์สนับสนุนการพัฒนา:

---

## 🛠️ รายการเครื่องมือตรวจสอบสเปก (Spec Linters)

1. **`spec_utf8_control_char_lint.py`** : ตรวจจับ Control Characters แปลกปลอมและบังคับใช้ UTF-8
2. **`spec_heading_classification_lint.py`** : ยืนยันว่าทุก Header มีแท็ก [NORMATIVE] หรือ [INFORMATIVE]
3. **`spec_single_active_version_lint.py`** : ยืนยันว่ามีเฉพาะเวอร์ชัน `10.2.2` ปรากฏใน Active Section
4. **`spec_no_historical_normative_freeze_lint.py`** : ป้องกันการดึง Freeze เก่าในอดีตมามีผลบังคับใช้
5. **`spec_active_view_byte_match.py`** : ตรวจสอบ SHA-256 ของ Active Spec View ให้ตรงกับ Canonical
6. **`spec_archive_checksum_match.py`** : ยืนยันว่า Historical Archive (Appendix C) ไม่ถูกลบหรือดัดแปลง
7. **`spec_requirement_id_unique_complete.py`** : ยืนยันว่ามี Requirement IDs ครบ 178 ข้อ เรียงลำดับถูกต้อง
8. **`spec_requirement_digest_change_guard.py`** : ตรวจสอบ Text Digest ป้องกันการแอบแก้ไขข้อความ
