# Candidate Lifecycle Finite State Machine (17 States)

> **Subsystem:** Candidate State & Verification Lifecycle  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S08-001`

---

## 1. Candidate State Definitions

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             17 CANDIDATE STATES                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 01. CREATED             : Candidate Object ถูกสร้างในหน่วยความจำ (จอง Candidate ID)│
│ 02. MATERIALIZED        : ซอร์สโค้ด Candidate ถูกเขียนลงใน CAS Storage สำเร็จ      │
│ 03. STATIC_VALIDATED    : ผ่านการ Parse AST และผ่านการตรวจ AST Safety Invariant   │
│ 04. POLICY_VALIDATED    : ผ่านการตรวจ Import Whitelist และข้อกำหนดด้านความปลอดภัย  │
│ 05. SECURITY_VALIDATED  : ผ่านการตรวจสอบสิทธิ์และคอนฟิก PROFILE_A_LINUX           │
│ 06. SANDBOX_READY       : โฟลเดอร์ /tmp (tmpfs), Mounts, cgroups v2 ถูกเตรียมพร้อม │
│ 07. EXECUTING           : Process กำลังรัน Benchmark หรือ Test Script ใน Sandbox   │
│ 08. EXECUTED            : รันจบสิ้น รวบรวม stdout/stderr, exit code, resource usage│
│ 09. TESTING             : กำลังประมวลผลการทดสอบ Unit/Behavioral Tests              │
│ 10. ORACLE_VERIFIED     : ตรวจสอบความถูกต้องของผลลัพธ์เทียบกับ Test Oracle        │
│ 11. CAPABILITY_VERIFIED : ผ่านเกณฑ์ Capability Gates (ไม่เกิด Regression ใดๆ)     │
│ 12. METRIC_EVALUATED    : วัดค่า Objectives ครบทุกตัว และผ่านการคำนวณทางสถิติ     │
│ 13. EVIDENCE_VERIFIED   : สร้างและลงนาม Evidence Envelope เรียบร้อย                │
│ 14. ELIGIBLE            : มีคุณสมบัติครบถ้วน พร้อมเข้าสู่กระบวนการคัดเลือก Pareto │
│ 15. SELECTED            : [TERMINAL] ได้รับคัดเลือกเข้าสู่ Generation ถัดไป         │
│ 16. REJECTED            : [TERMINAL] ถูกปฏิเสธ (เช่น Syntax ผิด, Test ตก, Timeout) │
│ 17. QUARANTINED         : [TERMINAL] ถูกกักกันเนื่องจากละเมิดความปลอดภัยของ Sandbox│
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete State Transition Matrix

| ลำดับ | From State | Event / Trigger | Guard Condition | To State |
|:---:|---|---|---|---|
| 1 | `CREATED` | `materialize_source` | Source bytes เขียนลง CAS และได้ SHA-256 | `MATERIALIZED` |
| 2 | `MATERIALIZED` | `run_static_analysis` | `ast.parse()` สำเร็จ และไม่มี Forbidden Nodes | `STATIC_VALIDATED` |
| 3 | `STATIC_VALIDATED`| `verify_policy` | ทุก Import อยู่ใน Whitelist และไม่มี global injection | `POLICY_VALIDATED` |
| 4 | `POLICY_VALIDATED`| `check_security_profile` | Kernel รองรับ Seccomp และ cgroups v2 พร้อม | `SECURITY_VALIDATED` |
| 5 | `SECURITY_VALIDATED`| `provision_sandbox` | Mount read-only สำเร็จ และสร้าง tmpfs 64MB สำเร็จ | `SANDBOX_READY` |
| 6 | `SANDBOX_READY` | `spawn_and_execute` | Process เริ่มรันใน Isolated Namespace | `EXECUTING` |
| 7 | `EXECUTING` | `execution_finished` | Exit code 0 และไม่เกิน Timeout/Memory Quota | `EXECUTED` |
| 8 | `EXECUTED` | `start_test_suite` | เริ่มรัน Unit/Capability Tests | `TESTING` |
| 9 | `TESTING` | `oracle_check` | ผลลัพธ์ตรงกับ Test Oracle | `ORACLE_VERIFIED` |
| 10 | `ORACLE_VERIFIED`| `verify_capabilities` | ผ่าน Required Capabilities 100% | `CAPABILITY_VERIFIED` |
| 11 | `CAPABILITY_VERIFIED`| `evaluate_metrics` | ได้ค่าตัวเลขครบทุก Objective และผ่าน Welch/TOST | `METRIC_EVALUATED` |
| 12 | `METRIC_EVALUATED`| `sign_evidence` | สร้าง Evidence Record และคำนวณ Digest สำเร็จ | `EVIDENCE_VERIFIED` |
| 13 | `EVIDENCE_VERIFIED`| `admit_to_selection` | ตรวจสอบ Invariants ครบทุกด้าน | `ELIGIBLE` |
| 14 | `ELIGIBLE` | `pareto_selection_pass` | ได้รับคัดเลือกตาม Pareto Dominance / Diversity | **`SELECTED`** |
| 15 | `*` (Any State) | `validation_or_test_fail` | Syntax error, Unit test fail, Timeout, OOM | **`REJECTED`** |
| 16 | `*` (Any State) | `security_violation_trap`| Syscall blocked, File escape, Network egress | **`QUARANTINED`** |

---

## 3. Execution Disposition Mapping

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          DISPOSITION TO TERMINAL MAPPING                         │
├──────────────────────────────────────────────────────────────────────────────────┤
│ • SUCCESS             ──► ดำเนินการต่อสู่ TESTING / METRIC_EVALUATED             │
│ • TIMEOUT (Time limit)──► REJECTED (Reason: ERR_SANDBOX_TIMEOUT)                 │
│ • OOM (Memory limit)  ──► REJECTED (Reason: ERR_SANDBOX_OOM)                     │
│ • CRASHED (Exit != 0) ──► REJECTED (Reason: ERR_EXECUTION_CRASHED)               │
│ • RESOURCE_EXCEEDED   ──► REJECTED (Reason: ERR_RESOURCE_EXHAUSTED)              │
│ • SECURITY_VIOLATION  ──► QUARANTINED (Reason: ERR_SANDBOX_SYSCALL_BLOCKED)      │
└──────────────────────────────────────────────────────────────────────────────────┘
```

- **[REQ-S08-001]** ห้ามเปลี่ยนสถานะออกจาก Terminal States (`SELECTED`, `REJECTED`, `QUARANTINED`) โดยเด็ดขาด
