# CLI Command Surface Specification (`evolve`)

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Canonical verbs:** `spec/ACTIVE_CONTRACT.md` §6.1 — 14 คำสั่ง ห้ามเพิ่ม/ลดที่นี่  
> **Scope:** PUBLIC CLI SPECIFICATION (L4 Authority)
> **Target Subsystem:** Command Line Interface Surface  
> **Governing Equations:** `EQ-047` (CLI Exit Codes), `EQ-048` (JSON stdout Envelope)

---

## 1. Catalog of CLI Subcommands

```text
┌──────────────────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Command Syntax       │ Description & Actions                     │ Key Flags & Arguments                                       │
├──────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ evolve init          │ สร้างโครงร่าง evolution.yaml ในโปรเจกต์   │ --language [python|polyglot], --preset [speed|memory|pareto]│
│ evolve validate      │ ตรวจสอบความถูกต้องของ config และ schemas  │ --config <path>, --strict, --json                           │
│ evolve preflight     │ ตรวจสอบ Kernel Namespaces, cgroups, BPF   │ --fix-permissions, --verbose, --json                        │
│ evolve run           │ เริ่มต้นกระบวนการวิวัฒนาการ               │ --generations <N>, --workers <W>, --seed <S>, --tui, --json │
│ evolve step          │ รันวิวัฒนาการเพียง 1 Generation           │ --run-id <UUID>, --json                                     │
│ evolve status        │ แสดงสถานะของ Run ปัจจุบัน                 │ --run-id <UUID>, --watch, --json                            │
│ evolve pause         │ พักการรันชั่วคราว                         │ --run-id <UUID>, --timeout 10s                              │
│ evolve resume        │ ดำเนินการรันต่อ                           │ --run-id <UUID>, --json                                     │
│ evolve abort         │ ยกเลิกการรันและทำความสะอาด sandbox        │ --run-id <UUID>, --force                                    │
│ evolve export        │ ส่งออก Candidate ที่ผ่านการคัดเลือก       │ --candidate-id <UUID>, --out <dir>, --with-evidence          │
│ evolve replay        │ รันซ้ำเพื่อตรวจสอบ Bit-Identical (R4)     │ --run-id <UUID>, --seed <S>, --verify-digest                │
│ evolve doctor        │ ตรวจสอบและกู้คืนฐานข้อมูล SQLite          │ --reconcile-db, --rebuild-cas, --check-hashes               │
└──────────────────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 2. Standard Structured JSON Output Envelope (`--json`)

เมื่อส่งแฟล็ก `--json` ทุกคำสั่งต้องส่งผลลัพธ์ผ่าน stdout ด้วยโครงสร้าง:
```json
{
  "status": "success",
  "data": {
    "run_id": "018e1234-5678-7abc-8def-0123456789ab",
    "generation": 10,
    "hypervolume": "0.854321",
    "pareto_front_size": 5
  },
  "error": null,
  "timestamp": "2026-08-18T15:00:00.000000Z"
}
```

---

## 3. Exit Codes Mapping Table

```text
  0: SUCCESS (Command completed without errors)
  1: ERR_INVALID_ARGUMENTS (Bad flags or parameters)
  2: ERR_CONFIG_SCHEMA_VIOLATION (evolution.yaml invalid)
  3: ERR_PREFLIGHT_ENVIRONMENT_FAILURE (Missing Linux cgroup/namespaces)
  4: ERR_RUNTIME_EXECUTION_FAILURE (Sandbox or evaluation failure)
  5: ERR_QUARANTINE_SECURITY_VIOLATION (Security breach trapped)
  6: ERR_DATABASE_CORRUPTION (SQLite DB reconciliation needed)
```
