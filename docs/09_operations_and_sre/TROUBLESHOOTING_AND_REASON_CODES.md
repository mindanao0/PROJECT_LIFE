# SRE Troubleshooting & Canonical Reason Codes Specification

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** OPERATIONS SPECIFICATION (L7 Authority)
> **Target Subsystem:** Diagnostics & SRE Incident Response  
> **Governing Equations:** `EQ-281` (Canonical Reason Codes Mapping), `EQ-282` (Doctor DB Reconciliation)

---

## 1. Catalog of Standard Error Reason Codes

```text
┌───────────────────────────────┬──────┬───────────────────────────────────────────┬─────────────────────────────────────────────┐
│ Reason Code ID                │ Exit │ Root Cause Description                    │ Triage & Automated Remedy Action            │
├───────────────────────────────┼──────┼───────────────────────────────────────────┼─────────────────────────────────────────────┤
│ ERR_CONFIG_SCHEMA_VIOLATION   │ 2    │ evolution.yaml fails Draft 2020-12 schema │ Validate YAML syntax; check additionalProps │
│ ERR_PREFLIGHT_CGROUP_MISSING  │ 3    │ cgroups v2 not mounted at /sys/fs/cgroup  │ Mount cgroups v2; enable systemd unified cgr│
│ ERR_PREFLIGHT_SECCOMP_DISABLED│ 3    │ Kernel lacks Seccomp BPF support          │ Enable CONFIG_SECCOMP_FILTER in Linux kernel│
│ ERR_UNAUTHORIZED_IMPORT       │ 5    │ Prohibited module import in candidate AST │ Candidate rejected; no action needed        │
│ ERR_DYNAMIC_EXECUTION         │ 5    │ eval(), exec() detected in AST            │ Candidate rejected; static visitor pass     │
│ ERR_SANDBOX_TIMEOUT_EXCEEDED  │ 4    │ Candidate execution exceeded timeout (10s)│ Kill candidate process; tag as TIMEOUT      │
│ ERR_SANDBOX_OOM_KILLED        │ 4    │ Candidate exceeded memory.max (512MB)     │ cgroups v2 SIGKILL; tag as OOM_KILLED       │
│ ERR_FLAKY_TEST_DETECTED       │ 4    │ Non-deterministic test output variance > 0│ Tag candidate as FLAKY; isolate test suite  │
│ ERR_DATABASE_LOCKED           │ 6    │ SQLite locked (Single-Writer violated)    │ Run evolve doctor --reconcile-db            │
│ ERR_CAS_HASH_MISMATCH         │ 6    │ File digest in CAS corrupted              │ Rebuild blob from source or backup          │
│ ERR_QUARANTINE_SECURITY_TRAP  │ 5    │ Seccomp BPF or path traversal attempt     │ Move to quarantine_records table            │
└───────────────────────────────┴──────┴───────────────────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 2. The `evolve doctor` Automated Reconciliation Subsystem

เมื่อเกิดเหตุฉุกเฉินหรือความขัดข้องของฐานข้อมูล สามารถรัน:
```bash
evolve doctor --reconcile-db --check-hashes --fix-permissions
```
ระบบจะดำเนินการ:
1. ปิดค้าง Lock Files และกู้คืน Transaction ผ่าน WAL Checkpoint
2. สแกน `.evolution/cas/` ตรวจสอบความถูกต้องของ SHA-256 Digest ทุกไฟล์
3. รัน `PRAGMA integrity_check` และ `PRAGMA foreign_key_check`
4. ซิงค์ตาราง `generations(manifest_hash)` เข้ากับไฟล์ใน CAS
