# Terminal User Interface (TUI) Dashboard Specification

> **Subsystem:** Interactive Operations & SRE Telemetry  
> **Authority Level:** NORMATIVE SPECIFICATION (`REQ-S07-004`)  
> **Governing Equations:** `EQ-288` (TUI Refresh Rate $\ge 10\text{Hz}$), `EQ-106` (Live Hypervolume), `EQ-018` (Worker Telemetry)

---

## 1. Executive Summary & Refresh SLOs

เมื่อผู้ใช้สั่งรัน `evolve run --tui` ระบบจะเปิดใช้งาน Interactive Terminal Dashboard ในโหมด Raw Terminal Mode (ผ่าน ANSI Escape Codes หรือ Ratatui/Rich Engine) โดยมีอัตราการรีเฟรชหน้าจออย่างน้อย 10Hz ($f_{\text{TUI}} \ge 10\text{Hz}$) โดยไม่กินทรัพยากร CPU เกิน 2% ของโหนด Coordinator.

---

## 2. Terminal Dashboard ASCII Layout

```text
┌─ Evolution Engine v10.2.2 ─────────────────────────────────────────── [RUNNING] ───┐
│ Run ID: 018e1234-5678-7abc-8def-0123456789ab | Seed: 42 | Uptime: 00:04:32        │
├──────────────────────────────────────┬─────────────────────────────────────────────┤
│ 🧬 GENERATION TELEMETRY              │ 🧮 LIVE PARETO FRONTIER                     │
│  Current Gen: 14 / 50                │  Front Size: 6 candidates                   │
│  Population: 32 candidates           │  Hypervolume: 0.894215 (+0.041200)          │
│  Stagnation: 0 (Tier 0 Normal)       │  Top Elite: cand_018e... (Latency: -42.5%)  │
│  Diversity:  0.425000 [██████░░░░]   │  Speedup:   1.74x vs Baseline               │
├──────────────────────────────────────┼─────────────────────────────────────────────┤
│ 🎰 MUTATION STRATEGY ALLOCATION (UCB)│ 🔒 WORKER SANDBOX POOL (cgroups v2)         │
│  M01 Constant:    [███░░░░░░░] 12%   │  W01 [CPU: 98% | RAM: 142MB | State: EXEC]  │
│  M02 Operator:    [████░░░░░░] 16%   │  W02 [CPU: 95% | RAM: 156MB | State: EXEC]  │
│  M07 Inlining:    [██████░░░░] 24%   │  W03 [CPU:  0% | RAM:  84MB | State: IDLE]  │
│  M08 DataStruct:  [████████░░] 32%   │  W04 [CPU: 99% | RAM: 210MB | State: EXEC]  │
│  M10 Native Rust: [████░░░░░░] 16%   │  Isolated Cores: [2, 3, 4, 5] | Jitter: 0.2%│
├──────────────────────────────────────┴─────────────────────────────────────────────┤
│ 📜 AUDIT & LIFECYCLE EVENT STREAM                                                   │
│  15:30:12 [INFO] Candidate cand_a12f materialised via M08 (dict -> set lookup)     │
│  15:30:14 [PASS] Oracle verified: 48/48 unit tests passed in 12.4ms                 │
│  15:30:15 [ELITE] New Pareto Front record! Hypervolume expanded by 0.041200        │
│  15:30:18 [COMMIT] Generation 14 committed to CAS & SQLite via 2PC Protocol         │
└─────────────────────────────────────────────────────────────────────────────────────┘
  [P] Pause   [R] Resume   [E] Export Elites   [D] Doctor Diagnostics   [Q] Safe Abort
```

---

## 3. Key Telemetry Metrics Displayed

1. **Generation Counter & Hypervolume:** แสดงการเติบโตของ Lebesgue Measure $HV(S, r)$
2. **Bandit Arm Weights:** สัดส่วนความน่าจะเป็นแบบ Real-time ของ Mutation Strategies M01 ถึง M10
3. **Worker Pool Health:** CPU Quota, RAM Usage (cgroups v2 `memory.current`), และ Heartbeat Status
4. **Interactive Keybindings:**
   - `P`: ส่งคำสั่ง Pause ชั่วคราว
   - `R`: สั่ง Resume การรัน
   - `E`: สั่ง Export Pareto Front ทันทีสู่โฟลเดอร์ `exports/`
   - `Q`: สั่ง Safe Abort พร้อมบันทึก Checkpoint ลง CAS
