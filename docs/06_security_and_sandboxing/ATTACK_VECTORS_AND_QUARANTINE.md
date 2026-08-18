# Threat Vectors, Defense & Automated Quarantine Specification

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** SECURITY SPECIFICATION (L0 Authority)
> **Target Subsystem:** Threat Detection & Quarantine Subsystem  
> **Governing Equations:** `EQ-241` .. `EQ-250` (Threat Modeling & Quarantine Probability)

---

## 1. Catalog of Prohibited Attack Vectors

```text
┌────────────┬─────────────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Vector ID  │ Attack Description          │ Defense Mechanism & Enforcement Level                                     │
├────────────┼─────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ ATK-01     │ Path Traversal (/etc/shadow)│ Mount Namespace Read-Only + Rootless UID mapping (EQ-201..202)            │
│ ATK-02     │ Container Socket Hijacking  │ Hide /var/run/docker.sock with ENOENT (EQ-242)                            │
│ ATK-03     │ Side-Channel Flush+Reload   │ Buffer MemZero after sandbox run (EQ-243)                                 │
│ ATK-04     │ Stack Exhaustion / Bomb     │ sys.setrecursionlimit(1000) bound (EQ-244)                                │
│ ATK-05     │ Environment Variable Leak   │ Sandbox Env Whitelist: {PATH, PYTHONPATH, LANG} (EQ-245)                  │
│ ATK-06     │ Tmpfs Disk Overflow Attack  │ Tmpfs hard ceiling 64MB (EQ-246)                                          │
│ ATK-07     │ Fork Bomb / PID Exhaustion  │ cgroups v2 pids.max = 64 (EQ-215)                                         │
│ ATK-08     │ OOM RAM Exhaustion Attack   │ cgroups v2 memory.max = 512MB + SIGKILL (EQ-212)                          │
└────────────┴─────────────────────────────┴───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Automated Quarantine Subsystem Workflow

เมื่อเกิดการละเมิดความปลอดภัย ระบบจะตัดการทำงานและบันทึกลงตาราง `quarantine_records` ทันที:
1. **Transition:** ย้าย Candidate สู่สถานะ `QUARANTINED`
2. **Snapshot Evidence:** บันทึก Memory Dump, Stdout, Stderr และ Syscall Traces ลง CAS
3. **Disqualify Lineage:** ตัดสิทธิ์ลูกหลานทั้งหมดของสายพันธุ์นั้น (`Eligible = False`)
4. **Emit Alert:** ส่งสัญญาณเตือนความปลอดภัยภายในเวลา $\le 100\text{ms}$
