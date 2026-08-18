# Linux Namespaces & cgroups v2 Enforcement

> **Subsystem:** Process, Memory & CPU Isolation  
> **Authority Level:** NORMATIVE (`REQ-S12-002`, `REQ-S12-004`)

---

## 1. The 5 Mandatory Linux Namespaces

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           MANDATORY LINUX NAMESPACES                             │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. User Namespace   : แมป Process เป็น Unprivileged User (uid != 0, gid != 0)     │
│ 2. Mount Namespace  : Mount ซอร์สโค้ดแบบ Read-Only และ /tmp เป็น tmpfs (64MB)    │
│ 3. PID Namespace    : ซ่อน Process บน Host ทั้งหมด มองเห็นเฉพาะ Process ตัวเอง    │
│ 4. Net Namespace    : Loopback interface down ห้ามสร้าง Socket ต่อภายนอก         │
│ 5. IPC Namespace    : ตัดขาด Shared Memory, Semaphores, Message Queues จาก Host   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. cgroups v2 Resource Controllers

```text
/sys/fs/cgroup/evolution/candidate_<id>/
├── memory.max       : 536870912 (512 MB Hard Limit -> OOM Kill ทันทีเมื่อเกิน)
├── memory.high      : 402653184 (384 MB Soft Warning -> Throttling)
├── cpu.max          : 100000 100000 (จำกัด 1.0 CPU Core)
├── pids.max         : 64 (ป้องกัน Fork Bomb / Thread Exhaustion)
└── cpuset.cpus      : 2-3 (CPU Pinning เพื่อลด Jitter ใน Benchmark)
```
