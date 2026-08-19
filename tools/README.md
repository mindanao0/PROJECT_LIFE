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
7. **`spec_requirement_id_unique_complete.py`** : ยืนยันว่ามี Requirement IDs ครบ 179 ข้อ เรียงลำดับถูกต้อง
8. **`spec_requirement_digest_change_guard.py`** : ตรวจสอบ Text Digest ป้องกันการแอบแก้ไขข้อความ

## Schema package tooling (Section 15.2)

| Script | Purpose | Requirement |
|---|---|---|
| `validate_schemas.py` | M3 schema gate: registry, declarations, offline `$ref`, fixtures, two-implementation agreement, manifest digests | `REQ-S15-001` .. `REQ-S15-006` |
| `generate_schema_fixtures.py` | Regenerates `tests/schema/fixtures/`; verifies each fixture actually passes or fails as named before writing it | `REQ-S15-004` |
| `generate_schema_manifest.py` | Regenerates `spec/schema_manifest.json` from real file bytes | `REQ-S15-003` |
| `generate_fsm_specs.py` | Regenerates `spec/fsm/*.yaml` from the Active Contract FSM sections | `REQ-S08-012`, `REQ-S19-003` |
| `generate_requirements.py` | Regenerates `spec/requirements.yaml` and `spec/traceability.yaml` together | `REQ-S02-008`, `REQ-S22-001` |
| `lint_state_vocabulary.py` | LINT-09 .. LINT-17 cross-source consistency | `REQ-S13-004`, `REQ-S01-009`, `REQ-S16-001`, `REQ-S21-002`, `REQ-S02-008` |

```bash
python3 tools/validate_schemas.py      # M3 gate
python3 tools/lint_state_vocabulary.py # spec consistency
pytest                                 # both, plus per-case detail
```

