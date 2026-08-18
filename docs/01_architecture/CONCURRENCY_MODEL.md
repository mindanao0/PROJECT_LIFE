# Concurrency Architecture: Single-Writer Coordinator & Worker Pool

> **Subsystem:** Concurrency, IPC & Data Isolation  
> **Authority Level:** NORMATIVE (`REQ-S07-001`, `REQ-S13-001`, `REQ-S14-001`)

---

## 1. Concurrency Architecture Overview

เพื่อขจัดปัญหา Data Race, Database Lock Contention บน SQLite, และการเขียนไฟล์ชนกันใน Content-Addressed Storage (CAS) ระบบ **Evolution Engine** ใช้รูปแบบสถาปัตยกรรม **Single-Writer Coordinator**:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                               COORDINATOR NODE                                   │
│  • เป็น Single-Writer เพียงผู้เดียวที่ได้รับอนุญาตให้เขียนลง SQLite และ CAS      │
│  • ควบคุม State Machines ทั้ง 5 ตัว และจัดสรร Generation Lifecycle               │
│  • ตัดสินผลการคัดเลือก (Pareto Selection) และจัดเก็บ Lineage Graph               │
│  • ดูแลการสื่อสารข้ามโหนดใน P2P Swarm Network                                    │
└──────────────────────────────┬───────────────────────────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │ Task Dispatch    │ Task Dispatch    │ Task Dispatch
            ▼                  ▼                  ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│     WORKER POOL 1     │ │     WORKER POOL 2     │ │     WORKER POOL N     │
│ (Isolated Sandbox)    │ │ (Isolated Sandbox)    │ │ (Isolated Sandbox)    │
│ • Unprivileged UID    │ │ • Unprivileged UID    │ │ • Unprivileged UID    │
│ • Read-Only Code Mount│ │ • Read-Only Code Mount│ │ • Read-Only Code Mount│
│ • No DB Connection    │ │ • No DB Connection    │ │ • No DB Connection    │
│ • รัน Test & Measure  │ │ • รัน Test & Measure  │ │ • รัน Test & Measure  │
└───────────┬───────────┘ └───────────┬───────────┘ └───────────┬───────────┘
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      │ Non-Blocking IPC Return Envelope
                                      ▼
                      ┌──────────────────────────────┐
                      │    COORDINATOR INBOX QUEUE   │
                      │  (FIFO Result Processing)    │
                      └──────────────────────────────┘
```

---

## 2. Invariants & Isolation Boundaries

1. **Worker Database Isolation:** Worker processes ใน Sandbox **ห้ามเปิด SQLite database connection หรือถือ file descriptor ใดๆ ที่ชี้ไปยัง `.evolution/db.sqlite` โดยเด็ดขาด**
2. **Worker CAS Isolation:** Worker ไม่มีสิทธิ์เขียนไฟล์ลงในไดเรกทอรีถาวรของ CAS (`.evolution/cas/`) โดยตรง ผลลัพธ์ stdout/stderr และ Source Snapshots จะถูกส่งกลับเป็น Memory Buffer หรือ Temp File ที่ Coordinator จะเป็นผู้ตรวจสอบและ Fsync ลง CAS เอง
3. **Non-Blocking IPC Protocol:** การส่งถ่าย Task และ Result ระหว่าง Coordinator และ Workers กระทำผ่าน:
   - Linux Unix Domain Sockets (UDS) ในแบบ Packet Stream
   - Shared-Memory Ring Buffer พร้อม Semaphore Synchronization
4. **Idempotent Worker Task Protocol:** หาก Worker ตายกะทันหัน (OOM หรือ Crash) Coordinator สามารถ Re-dispatch Task เดิมให้ Worker ตัวอื่นทำซ้ำได้ทันทีโดยไม่เกิด Partial State

---

## 3. Worker Lifecycle & Health Monitoring

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             WORKER LIFECYCLE                                     │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. PROVISIONING   : Coordinator เตรียม cgroup v2, Mounts และ Seccomp Filter      │
│ 2. SPAWNED        : Fork unprivileged child process และ Drop Linux Capabilities  │
│ 3. TASK_RECEIVED  : รับ Task Envelope พร้อม Candidate Source Bytes              │
│ 4. EXECUTING      : รัน Code, Benchmark Script, และ Unit Test Suite              │
│ 5. RESULT_EMITTED : ส่ง Measurement Vector และ Stdout/Stderr กลับสู่ Coordinator │
│ 6. DESTROYED      : ล้าง tmpfs, ทำลาย cgroup และคืน Process Slot สู่ Pool        │
└──────────────────────────────────────────────────────────────────────────────────┘
```

- **Heartbeat & Watchdog:** Coordinator มอนิเตอร์สัญญาณชีพของ Worker ทุกๆ $500\text{ ms}$ หาก Worker ไม่ตอบสนองเกิน $T_{\text{worker\_timeout}} = \text{task.timeout} + 5.0\text{ s}$ Coordinator จะส่งสัญญาณ `SIGKILL` ทำลาย Process Tree ทันที
