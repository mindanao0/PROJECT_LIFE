# 13 — Operations, SRE & Troubleshooting Playbook

> **Dimension:** SRE, Reliability Engineering & Incident Response  
> **Target Audience:** DevOps Engineers, System Administrators, and SREs

เอกสารฉบับนี้เป็นคู่มือการปฏิบัติการและการแก้ไขปัญหาหน้างาน (Troubleshooting & Operations Playbook) สำหรับดูแลรักษา Evolution Engine ในสภาพแวดล้อมจริง

---

## 1. Canonical Reason Codes Dictionary

เมื่อ Candidate ถูกปฏิเสธ (`REJECTED`) หรือถูกกักกัน (`QUARANTINED`) ระบบจะบันทึก `reason_code` มาตรฐาน:

| Reason Code | ความหมาย | สถานะผลลัพธ์ | แนวทางแก้ไขเบื้องต้น |
|---|---|:---:|---|
| `ERR_SYNTAX_INVALID` | โค้ดที่กลายพันธุ์มีข้อผิดพลาดทางไวยากรณ์ (Syntax Error) | `REJECTED` | ปรับจูน Mutation Operator หรือเพิ่ม Safety Filter |
| `ERR_CAPABILITY_REGRESSION` | Candidate ไม่ผ่านชุดทดสอบ Unit/Capability Test | `REJECTED` | ปกติในกระบวนการค้นหา (Evolution Loop จะลองสายพันธุ์อื่น) |
| `ERR_METRIC_INVALID_VALUE` | มาตรวัดได้ค่า `NaN`, `Infinity` หรือเกิน `valid_range` | `REJECTED` | ตรวจสอบ Script วัดผลใน `benchmark/` |
| `ERR_SANDBOX_TIMEOUT` | Candidate รันนานเกิน `timeout_seconds` ที่กำหนด | `REJECTED` | เพิ่ม Timeout ในคอนฟิก หรือ Candidate เกิด Infinite Loop |
| `ERR_SANDBOX_OOM` | Candidate ใช้หน่วยความจำเกิน cgroup memory limit | `REJECTED` | ตรวจสอบ Memory Leak ในโค้ด Candidate |
| `ERR_SANDBOX_SYSCALL_BLOCKED` | Candidate พยายามเรียก Syscall ที่ Seccomp บล็อก | `QUARANTINED` | ตรวจสอบว่าโค้ดมีความพยายามเจาะระบบหรือไม่ |
| `ERR_SANDBOX_FS_DENIED` | Candidate พยายามเขียนไฟล์นอก `/tmp` หรืออ่านไฟล์ความลับ | `QUARANTINED` | ตรวจสอบ Path การเขียนไฟล์ใน Candidate |
| `ERR_SANDBOX_NET_DENIED` | Candidate พยายามเชื่อมต่อเครือข่ายภายนอก | `QUARANTINED` | ปิดคำสั่ง Socket Call ในโปรเจกต์เป้าหมาย |
| `ERR_TEST_FLAKY_DETECTED` | ผลการรันชุดทดสอบบน Candidate เดิมให้ผลไม่แน่นอน | `REJECTED` | กักกัน Flaky Test ในโปรเจกต์เป้าหมาย |
| `ERR_RECOVERY_AUDIT_GAP` | ข้อมูล Audit Hash Chain ขาดช่วง ไม่สามารถต่อโซ่ได้ | `QUARANTINED` | รัน `evolve doctor --verify-audit` เพื่อซ่อมแซม State |

---

## 2. Troubleshooting Scenarios & Solutions

### สถานการณ์ที่ 1: Candidate ติด `TIMEOUT` หรือ `OOM` ถี่ผิดปกติ
- **อาการ:** Candidate จำนวนมากถูก Reject ด้วย `ERR_SANDBOX_TIMEOUT` หรือ `ERR_SANDBOX_OOM`
- **การวินิจฉัย:**
  1. ตรวจสอบว่า Benchmark Script รันบน Input ขนาดใหญ่เกินไปหรือไม่
  2. ตรวจสอบว่า cgroup limit บน Host ต่ำเกินไปหรือไม่
- **วิธีแก้:**
  - เพิ่ม `timeout_seconds` ใน `evolution.yaml`
  - ปรับขนาด `writable_tmp_bytes` ในบล็อก `sandbox` (เช่น เพิ่มจาก 64MB เป็น 128MB)

---

### สถานการณ์ที่ 2: Engine ติดสถานะ `RECOVERING` หรือขัดข้องหลังเครื่องดับ
- **อาการ:** หลังเซิร์ฟเวอร์ดับ (Unclean Shutdown) เมื่อรัน Engine ใหม่ ระบบค้างที่สถานะ `RECOVERING`
- **การวินิจฉัยและขั้นตอนกู้คืน:**
  1. ตรวจสอบสถานะการกู้คืน:
     ```bash
     evolve status --json
     ```
  2. รันคำสั่งกู้คืนแบบ Step-by-Step:
     ```bash
     evolve doctor --reconcile-db
     ```
  3. หาก Audit Chain สมบูรณ์ ระบบจะคืนสถานะ `PAUSED` จากนั้นสั่งทำงานต่อได้ทันที:
     ```bash
     evolve resume --run-id <RUN_ID>
     ```

---

### สถานการณ์ที่ 3: ตรวจพบ Flaky Test ในโปรเจกต์เป้าหมาย
- **อาการ:** Candidate มีผลทดสอบสลับไปมาระหว่าง `PASS` และ `FAIL`
- **การจัดการตามสเปก:**
  - ระบบจะมาร์ก Test นั้นเป็น `FLAKY` และ Candidate จะได้สถานะ `INCONCLUSIVE`
  - ห้ามสั่ง Retry เพื่อหวังให้ผ่าน (ตามกฎ `[REQ-S17-001]`)
  - ให้ผู้ดูแลโปรเจกต์เป้าหมายย้าย Test นั้นไปไว้ใน Quarantine Test Suite จนกว่าจะถูกแก้บั๊ก Race Condition

---

## 3. Routine SRE Maintenance Playbook

### 3.1 การตรวจสอบความสมบูรณ์ของระบบ (Engine Health Check)
```bash
# ตรวจสอบ Linux Kernel Capabilities, cgroups v2, และ Seccomp
evolve doctor --sandbox-probes

# ตรวจสอบความถูกต้องของ Database Foreign Keys และ Invariants
evolve doctor --verify-integrity
```

### 3.2 การทำ Garbage Collection สำหรับ CAS Storage อย่างปลอดภัย
ตามกฎ `[REQ-S01-009]` ห้ามลบ Artifact ที่มีผลต่อ Lineage และ Evidence:
```bash
# ลบเฉพาะ Temp Blobs ที่ไม่ได้ถูก Commit และไม่อยู่ใน Lineage Graph
evolve db gc --dry-run
evolve db gc --apply
```
