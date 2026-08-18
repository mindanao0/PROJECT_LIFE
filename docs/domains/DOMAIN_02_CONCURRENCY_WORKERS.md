# Domain 02: Concurrency & Single-Writer Coordinator

> **Domain Index:** `DOMAIN-02`  
> **Engineering Scope:** `DIM-011` .. `DIM-020`  
> **Mathematical Equations:** `EQ-011` .. `EQ-020`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 02 กำหนดโครงสร้างการประมวลผลคู่ขนานแบบกระจายงาน (Concurrency Architecture) ภายใต้สถาปัตยกรรม **Single-Writer Coordinator & Worker Pool** โดย Coordinator ทำหน้าที่เป็นผู้เขียน SQLite และ CAS เพียงรายเดียว ในขณะที่ Worker Pool ประมวลผลงานใน Linux Sandbox และสื่อสารผลลัพธ์ผ่าน Non-blocking IPC Queues.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-011  │ EQ-011   │ Single-Writer Invariant                   │ |{W in Processes | WritePerm(W, DB) = 1}| === 1             │
│ DIM-012  │ EQ-012   │ Worker Read-Only Database Isolation       │ forall w in Workers, FD(w) intersect FD(SQLite) = empty     │
│ DIM-013  │ EQ-013   │ Immutable Task Manifest Snapshot          │ H_task = SHA-256(SourceBytes || Seed || Params)             │
│ DIM-014  │ EQ-014   │ Non-Blocking IPC Ring Buffer Arithmetic   │ Head_{t+1} = (Head_t + 1) mod N                             │
│ DIM-015  │ EQ-015   │ Idempotent Task Execution Invariant       │ f(f(Task)) === f(Task)                                      │
│ DIM-016  │ EQ-016   │ Multi-Core Amdahl Worker Scaling          │ S(p) = 1 / ((1 - s) + s / p)                                │
│ DIM-017  │ EQ-017   │ Little's Law Task Queue Backpressure      │ L = lambda * W <= Q_max                                     │
│ DIM-018  │ EQ-018   │ Worker Heartbeat Exponential Telemetry    │ P_alive(t) = exp(-lambda_hb * (t - t_last))                 │
│ DIM-019  │ EQ-019   │ Dead Worker Timeout Pruning Bound         │ Kill(w) <=> (t_now - t_last_heartbeat) > 5.0 s              │
│ DIM-020  │ EQ-020   │ Zero-Lock WAL Concurrency Probability     │ Pr(LockContention(Reader, Writer)) = 0.0                    │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-011` / `EQ-011`: Single-Writer Invariant
- **Requirement:** เฉพาะโหนด Coordinator เท่านั้นที่ได้รับอนุญาตให้เปิด SQLite Database Connection ในโหมด Read-Write (`SQLITE_OPEN_READWRITE`)
- **Mathematical Form:** เซตของผู้เขียนฐานข้อมูลต้องมีสมาชิกเพียงตัวเดียวอย่างเคร่งครัด:
  $$|\{W \in \text{Processes} \mid \text{WritePerm}(W, \text{DB}) = 1\}| \equiv 1$$

### `DIM-012` / `EQ-012`: Worker Read-Only Database Isolation
- **Requirement:** กระบวนการ Worker ทุกตัวที่รันใน Sandbox จะไม่มีสิทธิ์เข้าถึงหรือเปิด File Descriptor ไปยัง SQLite Database file:
  $$\forall w \in \text{Workers}, \quad \text{FD}(w) \cap \text{FD}(\text{SQLite}) = \emptyset$$

### `DIM-013` / `EQ-013`: Immutable Task Manifest Snapshot
- **Requirement:** Coordinator จ่ายงานให้ Worker ผ่าน Immutable JSON Task Snapshot ที่มี Hash กำกับ:
  $$H_{\text{task}} = \text{SHA-256}(\text{SourceBytes} \parallel \text{Seed} \parallel \text{Params})$$

### `DIM-014` / `EQ-014`: Non-Blocking IPC Ring Buffer Arithmetic
- **Ring Buffer Invariants:** การส่งข้อมูลผลการประเมินจาก Worker กลับมายัง Coordinator จะกระทำผ่าน Circular Ring Buffer ในหน่วยความจำร่วม (Shared Memory) โดยใช้ Modulo Pointer Arithmetic:
  $$\text{Head}_{t+1} = (\text{Head}_t + 1) \pmod N, \qquad \text{OccupiedSlots} = (\text{Tail} - \text{Head}) \pmod N$$
- หาก `OccupiedSlots == N - 1` ให้ระบบกระตุ้น Backpressure ชะลอการส่งงานใหม่

### `DIM-015` / `EQ-015`: Idempotent Task Execution Invariant
- **Requirement:** การประเมิน Candidate งานเดิมซ้ำกี่ครั้งก็ตาม ต้องได้ผลลัพธ์ของ Metric และ Exit Status ตรงกันเสมอ:
  $$f(f(\text{Task})) \equiv f(\text{Task})$$

### `DIM-016` / `EQ-016`: Multi-Core Amdahl Worker Scaling
- กำหนดสัดส่วนงานที่สามารถกระจายแบบคู่ขนานได้ ($s \approx 0.95$) และคำนวณ Speedup ทางทฤษฎีตามจำนวน Worker Cores ($p$):
  $$S(p) = \frac{1}{(1 - s) + \frac{s}{p}}$$

### `DIM-017` / `EQ-017`: Little's Law Task Queue Backpressure
- **Queue Stability:** ความยาวของ Task Queue ($L$) จะต้องไม่เกินขีดจำกัด $Q_{\max} = 2 \times N_{\text{workers}}$:
  $$L = \lambda W \le Q_{\max}$$

### `DIM-018` / `EQ-018`: Worker Heartbeat Exponential Telemetry
- ความน่าเชื่อถือว่า Worker ยังคงมีชีวิตอยู่จะคำนวณผ่านฟังก์ชัน Exponential Decay:
  $$P_{\text{alive}}(t) = \exp(-\lambda_{\text{hb}} (t - t_{\text{last}}))$$

### `DIM-019` / `EQ-019`: Dead Worker Timeout Pruning Bound
- หาก Worker ใดไม่ส่ง Heartbeat กลับมานานเกิน 5.0 วินาที Coordinator จะส่งคำสั่งตัดไฟ (Kill & Prune):
  $$\text{Kill}(w) \iff (t_{\text{now}} - t_{\text{last\_heartbeat}}) > 5.0\text{ s}$$

### `DIM-020` / `EQ-020`: Zero-Lock WAL Concurrency Probability
- โหมด SQLite WAL (Write-Ahead Logging) รับประกันว่า Reader และ Writer ไม่บล็อกซึ่งกันและกัน:
  $$\Pr(\text{LockContention}(\text{Reader}, \text{Writer})) = 0.0$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D02-01` [Concurrent Worker Stress]:** สั่งรัน 32 Workers พร้อมกันเป็นเวลา 60 วินาที ตรวจสอบว่าไม่มี SQLite Database Locked Error (`SQLITE_BUSY`) เกิดขึ้นแม้แต่ครั้งเดียว
2. **Test `TC-D02-02` [Worker Death Recovery]:** ส่งสัญญาณ `SIGKILL` ยิงทำลาย Worker หมายเลข 3 กลางคัน Coordinator ต้องตรวจพบภายใน 5 วินาที และ Re-dispatch งานเดิมให้ Worker ตัวใหม่ทำซ้ำอย่างถูกต้อง
3. **Test `TC-D02-03` [IPC Ring Buffer Saturation]:** ยัด Task เข้า Ring Buffer จนเต็ม ตรวจสอบว่าระบบส่งสัญญาณ Backpressure และไม่มี Task ใดสูญหาย
4. **Test `TC-D02-04` [Worker DB Isolation]:** สั่ง Worker พยายามเปิดไฟล์ `db.sqlite` ตรวจสอบว่าถูกเคอร์เนลบล็อกและไม่พบ File Descriptor
