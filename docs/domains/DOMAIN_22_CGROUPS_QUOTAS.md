# Domain 22: cgroups v2 Quotas, CPU Pinning & Memory Ceilings

> **Domain Index:** `DOMAIN-22`  
> **Engineering Scope:** `DIM-211` .. `DIM-220`  
> **Mathematical Equations:** `EQ-211` .. `EQ-220`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 22 กำหนดการควบคุมทรัพยากรฮาร์ดแวร์ผ่าน **cgroups v2 unified hierarchy**, การจำกัดหน่วยความจำแบบ Hard Limit (`memory.max = 512MB`), CPU Quota & Period, Process Count Limit (`pids.max = 64`), และ **CPU Core Pinning & NUMA Node Binding** เพื่อลด Jitter.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-211  │ EQ-211   │ cgroups v2 Unified Hierarchy Invariant    │ Mount(cgroup2) === "/sys/fs/cgroup"                         │
│ DIM-212  │ EQ-212   │ Memory Hard Ceiling Limit (OOM Trigger)   │ RAM(t) > memory.max ==> SIGKILL                             │
│ DIM-213  │ EQ-213   │ Memory High Soft Limit Throttle Action    │ Delay(t) proportional max(0, RAM(t) - memory.high)          │
│ DIM-214  │ EQ-214   │ CPU Bandwidth Quota Period Calculus       │ Time_CPU(T) <= (cpu.max.quota / cpu.max.period) * T         │
│ DIM-215  │ EQ-215   │ Process Count Ceiling (Fork Bomb Defense) │ |PIDs| <= pids.max = 64                                     │
│ DIM-216  │ EQ-216   │ CPU Core Pinning & Affinity Masking       │ SchedAffinity(Process) subseteq {C_2, C_3}                  │
│ DIM-217  │ EQ-217   │ NUMA Node Memory Allocation Binding       │ NUMABind(RAM) = NUMANode(CPUSet)                            │
│ DIM-218  │ EQ-218   │ Disk I/O Read/Write Throttling Ceiling    │ IO_rate <= 10 MB/s                                          │
│ DIM-219  │ EQ-219   │ Kernel OOM Event Listener Socket Bound    │ Event(cgroup.events:oom) ==> HandleOOM()                    │
│ DIM-220  │ EQ-220   │ Ephemeral Cgroup Destruction Latency      │ t_cleanup <= 5 ms                                           │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-211` / `EQ-211`: cgroups v2 Unified Hierarchy Invariant
- ควบคุมผ่าน cgroups v2 mount point มาตรฐาน:
  $$\text{Mount}(\text{cgroup2}) \equiv \text{"/sys/fs/cgroup"}$$

### `DIM-212` / `EQ-212`: Memory Hard Limit (OOM Trigger)
- ควบคุมหน่วยความจำสูงสุดไม่เกิน 512MB หากเกิน Kernel OOM Killer จะส่งสัญญาณ `SIGKILL` ทันที:
  $$\text{RAM}(t) > \text{memory.max} \implies \text{SIGKILL}$$

### `DIM-213` / `EQ-213`: Memory High Soft Limit Throttle Action
- เมื่อการใช้ Memory เกิน `memory.high` เคอร์เนลจะชะลอความเร็ว Process ลง:
  $$\text{Delay}(t) \propto \max(0, \text{RAM}(t) - \text{memory.high})$$

### `DIM-214` / `EQ-214`: CPU Bandwidth Quota Period Calculus
- จำกัดเวลา CPU ของ Candidate ต่อช่วงเวลา:
  $$\text{Time}_{\text{CPU}}(T) \le \frac{\text{cpu.max.quota}}{\text{cpu.max.period}} \cdot T$$

### `DIM-215` / `EQ-215`: Process Count Ceiling (Fork Bomb Defense)
- จำกัดจำนวน Process สูงสุดไม่เกิน 64 ตัว เพื่อป้องกัน Fork Bomb:
  $$|\text{PIDs}| \le \text{pids.max} = 64$$

### `DIM-216` / `EQ-216`: CPU Core Pinning & Affinity Masking
- ตรึง Worker ให้อยู่บน Isolated CPU Cores เพื่อลด Jitter:
  $$\text{SchedAffinity}(\text{Process}) \subseteq \{C_2, C_3\}$$

### `DIM-217` / `EQ-217`: NUMA Node Memory Allocation Binding
- ผูกหน่วยความจำเข้ากับ NUMA Node เดียวกับ CPU Cores:
  $$\text{NUMABind}(\text{RAM}) = \text{NUMANode}(\text{CPUSet})$$

### `DIM-218` / `EQ-218`: Disk I/O Read/Write Throttling Ceiling
- จำกัดความเร็วการอ่านเขียน Disk ไม่เกิน 10MB/s:
  $$\text{IO}_{\text{rate}} \le 10\text{ MB/s}$$

### `DIM-219` / `EQ-219`: Kernel OOM Event Listener Socket Bound
- ติดตั้ง Event Listener ดักจับเหตุการณ์ OOM ผ่าน `cgroup.events`:
  $$\text{Event}(\text{cgroup.events:oom}) \implies \text{HandleOOM}()$$

### `DIM-220` / `EQ-220`: Ephemeral Cgroup Destruction Latency
- ลบ cgroup ทิ้งทันทีหลังรันงานเสร็จภายใน 5ms:
  $$t_{\text{cleanup}} \le 5\text{ ms}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D22-01` [Memory Bomb OOM Trap]:** รันโค้ดจอง RAM 1GB ใน Sandbox ตรวจสอบว่า cgroups v2 สั่ง Kill Process ภายใน 100ms และได้ Exit Code OOM
2. **Test `TC-D22-02` [Fork Bomb Defense]:** รัน `while True: os.fork()` ตรวจสอบว่าไม่กระทบ Host Process
3. **Test `TC-D22-03` [CPU Quota Verification]:** รัน Infinite Loop ยืนยันว่า CPU Usage ถูกจำกัดตาม Quota ที่ตั้งไว้
4. **Test `TC-D22-04` [Ephemeral Cleanup Latency]:** จับเวลาการลบ ephemeral cgroup 100 รอบ ตรวจสอบว่าค่าเฉลี่ย $< 5\text{ms}$
