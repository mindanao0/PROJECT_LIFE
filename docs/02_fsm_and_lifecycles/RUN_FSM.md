# Run Lifecycle FSM Specification (11 States)

> **Authority Level:** NORMATIVE FSM SPECIFICATION (L2 Authority)  
> **Target Subsystem:** Run Coordinator & Engine Orchestrator  
> **Governing Equations:** `EQ-023` (Stochastic Operator Matrix), `EQ-009` (Logical Determinism R1), `EQ-030` (Audit Transition Chain)

---

## 1. Complete 11-State Topology & Enums

วงจรสถานะของ Run การวิวัฒนาการถูกควบคุมด้วย 11 สถานะอย่างเป็นทางการ:

```text
       [INITIATED]
           │
           ▼
     [CONFIG_LOADED]
           │
           ▼
    [PREFLIGHT_PASSED] ──────────┐ (Preflight Error)
           │                     │
           ▼                     ▼
       [RUNNING] ───────────► [FAILED]
       ▲   │  ▲                  ▲
 (Resume)  │  │                  │
       │   │  └────────┐         │
       │   ▼           │         │
    [PAUSED]    [GENERATION_COMMITTED]
       │               │         │
       │ (User Abort)  ▼         │
       └──────────► [ABORTED]    │
                       │         │
                       ▼         │
                 [CHECKPOINTING] ┘
                       │
                       ▼
                  [COMPLETED]
                       ▲
                       │ (Recovered)
                 [RECOVERING]
```

### 1.1 Formal State Enum Definitions
1. `INITIATED`: สร้าง Run Record ในฐานข้อมูล กำหนด `run_id` และ Master Seed
2. `CONFIG_LOADED`: อ่านและตรวจสอบ `evolution.yaml` ผ่าน JSON Schema และความถูกต้องของ Preferences
3. `PREFLIGHT_PASSED`: ตรวจสอบสภาพแวดล้อม Linux Kernel Namespaces, cgroups v2, Seccomp BPF และ SQLite WAL
4. `RUNNING`: กำลังประมวลผลการวิวัฒนาการ (Mutation -> Sandbox Execution -> Evaluation -> Selection)
5. `PAUSED`: พักการทำงานชั่วคราวตามคำสั่ง SDK/CLI โดย Worker หยุดรับงานใหม่
6. `GENERATION_COMMITTED`: เสร็จสิ้นการประมวลผลหนึ่งรุ่นและผ่าน Two-Phase Commit เรียบร้อย
7. `CHECKPOINTING`: กำลังบันทึก Run Manifest และ Database Snapshot ลง CAS Storage
8. `COMPLETED`: วิวัฒนาการครบจำนวนรุ่นที่กำหนด ($G_{\max}$) หรือบรรลุเป้าหมาย Pareto
9. `FAILED`: เกิดข้อผิดพลาดร้ายแรงที่ไม่สามารถกู้คืนได้ (Fatal Unrecoverable Exception)
10. `ABORTED`: ผู้ใช้ส่งคำสั่งยกเลิกการทำงานกลางคัน
11. `RECOVERING`: กำลังกู้คืน State หลังเกิด Crash หรือระบบดับกะทันหัน

---

## 2. Transition Rules Matrix & Allowed Events

```text
┌──────────────────────┬──────────────────────┬─────────────────────────┬───────────────────────────────┐
│ Current State        │ Event / Trigger      │ Next State              │ Guard Condition & Actions     │
├──────────────────────┼──────────────────────┼─────────────────────────┼───────────────────────────────┤
│ INITIATED            │ LoadConfig           │ CONFIG_LOADED           │ Config schema valid           │
│ CONFIG_LOADED        │ RunPreflight         │ PREFLIGHT_PASSED        │ Kernel & DB check PASS        │
│ CONFIG_LOADED        │ PreflightFailed      │ FAILED                  │ Kernel / Toolchain MISSING    │
│ PREFLIGHT_PASSED     │ StartEvolution       │ RUNNING                 │ Workers spawned & healthy     │
│ RUNNING              │ PauseCommand         │ PAUSED                  │ Drain in-flight worker tasks  │
│ RUNNING              │ CompleteGeneration   │ GENERATION_COMMITTED    │ 2PC generation commit OK      │
│ RUNNING              │ FatalEngineError     │ FAILED                  │ Write error reason code to DB │
│ RUNNING              │ AbortSignal          │ ABORTED                 │ SIGINT / SIGTERM received     │
│ PAUSED               │ ResumeCommand        │ RUNNING                 │ Resume worker task dispatch   │
│ PAUSED               │ AbortSignal          │ ABORTED                 │ Abort while paused            │
│ GENERATION_COMMITTED │ ContinueGeneration   │ RUNNING                 │ current_gen < max_gen         │
│ GENERATION_COMMITTED │ MaxGenReached        │ CHECKPOINTING           │ current_gen == max_gen        │
│ CHECKPOINTING        │ CheckpointDurable    │ COMPLETED               │ Final run manifest in CAS     │
│ ANY ACTIVE STATE     │ CrashDetected        │ RECOVERING              │ On coordinator restart        │
│ RECOVERING           │ ReplaySucceeded      │ RUNNING / COMPLETED     │ DB & CAS reconciled           │
│ RECOVERING           │ ReconcileFailed      │ FAILED                  │ Corrupted unrecoverable data  │
└──────────────────────┴──────────────────────┴─────────────────────────┴───────────────────────────────┘
```

---

## 3. Transition Invariants & Guard Proofs

1. **No Skip Invariant:** ห้ามเปลี่ยนสถานะจาก `INITIATED` ข้ามไป `RUNNING` โดยไม่ผ่าน `CONFIG_LOADED` และ `PREFLIGHT_PASSED`
2. **Crash-Resilience Invariant:** หากเกิดการ Crash ในสถานะ `RUNNING` หรือ `CHECKPOINTING` เมื่อระบบบูตขึ้นมาใหม่ต้องเข้าสู่ `RECOVERING` ก่อนเสมอ
3. **Audit Trail Invariant:** ทุกการเปลี่ยนสถานะต้องบันทึกลงตาราง `audit_events` พร้อมคำนวณ Merkle Hash Chain:
   $$H_{\text{transition}} = \text{SHA-256}(S_{\text{from}} \parallel \text{Event} \parallel S_{\text{to}} \parallel H_{\text{prev}})$$
