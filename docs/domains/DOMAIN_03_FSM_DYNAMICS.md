# Domain 03: Finite State Machine Dynamics (5 FSMs)

> **Domain Index:** `DOMAIN-03`  
> **Engineering Scope:** `DIM-021` .. `DIM-030`  
> **Mathematical Equations:** `EQ-021` .. `EQ-030`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 03 กำหนดโครงสร้างและพลวัตของ **Finite State Machines (5 FSMs)** ครอบคลุม 57 สถานะของระบบ (Candidate 17 States, Run 11 States, Recovery 9 States, Governance 12 States, Deployment 8 States) โดยใช้ทฤษฎี Matrix Algebra, Absorbing Markov Chains, และ Quorum Threshold Functions.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-021  │ EQ-021   │ Candidate 17-State Transition Matrix      │ x_{t+1} = T_{17x17} . x_t, sum x_i = 1                      │
│ DIM-022  │ EQ-022   │ Terminal Absorbing State Invariant        │ T_{ii} = 1 forall i in {SELECTED, REJECTED, QUARANTINED}    │
│ DIM-023  │ EQ-023   │ Run 11-State Stochastic Operator Matrix   │ sum_{j=1}^{11} T_{ij} = 1 forall i in {1..11}               │
│ DIM-024  │ EQ-024   │ Recovery 9-State Idempotency Loop         │ T_recovery^k -> T_terminal                                  │
│ DIM-025  │ EQ-025   │ Governance 12-State Quorum Function       │ Q = sum_{k=1}^K w_k * Vote_k >= Theta_ratify                │
│ DIM-026  │ EQ-026   │ Canary Deployment Traffic Proportion      │ T_canary(t) = min(1.0, alpha * t)                           │
│ DIM-027  │ EQ-027   │ Automated Canary Rollback Hazard Trigger  │ lambda_rollback(t) = I(ErrorRate(t) > 0.01)                 │
│ DIM-028  │ EQ-028   │ Illegal Transition Trap Hadamard Product  │ A_valid (hadamard) T_actual = T_actual                      │
│ DIM-029  │ EQ-029   │ Markov Chain State Reachability Theorem   │ forall j, exists k >= 1 s.t. (T^k)_{1j} > 0                 │
│ DIM-030  │ EQ-030   │ Audit Transition State Vector Hash Chain  │ H_trans = SHA-256(S_from || Event || S_to || H_prev)        │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-021` / `EQ-021`: Candidate 17-State Transition Matrix
- **Matrix Dynamics:** เวกเตอร์สถานะ $\vec{x}_t \in \{0, 1\}^{17}$ จะถูกอัปเดตผ่าน Transition Matrix $\mathbf{T} \in \{0, 1\}^{17 \times 17}$:
  $$\vec{x}_{t+1} = \mathbf{T} \cdot \vec{x}_t, \qquad \sum_{i=1}^{17} x_i = 1$$
- **17 States:** `CREATED`, `MATERIALIZED`, `STATIC_VALIDATED`, `POLICY_VALIDATED`, `SECURITY_VALIDATED`, `SANDBOX_READY`, `EXECUTING`, `EXECUTED`, `TESTING`, `ORACLE_VERIFIED`, `CAPABILITY_VERIFIED`, `METRIC_EVALUATED`, `EVIDENCE_VERIFIED`, `ELIGIBLE`, `SELECTED`, `REJECTED`, `QUARANTINED`.

### `DIM-022` / `EQ-022`: Terminal Absorbing State Invariant
- Candidate ที่เข้าสู่ Terminal States ทั้ง 3 ตัว ห้ามเปลี่ยนสถานะออกไปเป็นสถานะอื่นโดยเด็ดขาด:
  $$T_{ii} = 1 \quad \forall i \in \{\text{SELECTED}, \text{REJECTED}, \text{QUARANTINED}\}, \qquad T_{ij} = 0 \quad \forall j \ne i$$

### `DIM-023` / `EQ-023`: Run 11-State Stochastic Operator Matrix
- การควบคุมวงจรชีวิตของ Run ผ่าน 11 สถานะ: `INITIATED`, `CONFIG_LOADED`, `PREFLIGHT_PASSED`, `RUNNING`, `PAUSED`, `GENERATION_COMMITTED`, `CHECKPOINTING`, `COMPLETED`, `FAILED`, `ABORTED`, `RECOVERING`:
  $$\sum_{j=1}^{11} T_{ij} = 1 \quad \forall i \in \{1, \dots, 11\}$$

### `DIM-024` / `EQ-024`: Recovery 9-State Idempotency Loop
- วงจรการกู้คืนระบบเมื่อเกิด Crash หรือ Power Failure จะหมุนวนจนเข้าสู่ Terminal State ที่ปลอดภัยเสมอ:
  $$\mathbf{T}_{\text{recovery}}^k \to \mathbf{T}_{\text{terminal}}$$

### `DIM-025` / `EQ-025`: Governance 12-State Quorum Function
- การขอแก้ไขสเปกต้องผ่าน Quorum คะแนนเสียงที่ถ่วงน้ำหนัก:
  $$Q = \sum_{k=1}^K w_k \cdot \text{Vote}_k \ge \Theta_{\text{ratify}}$$

### `DIM-026` / `EQ-026`: Canary Deployment Traffic Proportion
- สัดส่วน Traffic ที่ส่งไปยัง Canary Release จะค่อยๆ เพิ่มขึ้นตามเวลา:
  $$T_{\text{canary}}(t) = \min(1.0, \alpha \cdot t)$$

### `DIM-027` / `EQ-027`: Automated Canary Rollback Trigger
- ในช่วงทดสอบ Canary Deployment ระบบจะมอนิเตอร์ Hazard Function:
  $$\lambda_{\text{rollback}}(t) = \mathbb{I}(\text{ErrorRate}(t) > 0.01 \lor \text{LatencyRegression}(t) > 0.15)$$
- หากเงื่อนไขเป็นจริง ระบบต้องสั่ง Rollback สู่สถานะ `ROLLED_BACK` ภายในเวลา $< 1.0\text{ วินาที}$

### `DIM-028` / `EQ-028`: Illegal Transition Trap Hadamard Product
- ทุกการเปลี่ยนสถานะจะถูกตรวจสอบด้วย Allowed Adjacency Matrix $\mathbf{A}_{\text{valid}}$:
  $$\mathbf{A}_{\text{valid}} \odot \mathbf{T}_{\text{actual}} = \mathbf{T}_{\text{actual}}$$

### `DIM-029` / `EQ-029`: Markov Chain State Reachability Theorem
- ทุกสถานะใน FSM ต้องสามารถเข้าถึงได้จากสถานะเริ่มต้น (No Orphan States):
  $$\forall j, \quad \exists k \ge 1 \text{ s.t. } (\mathbf{T}^k)_{1j} > 0$$

### `DIM-030` / `EQ-030`: Audit Transition State Vector Hash Chain
- ทุกการเปลี่ยนสถานะต้องถูกบันทึกลง Hash Chain เพื่อการตรวจสอบย้อนกลับ:
  $$H_{\text{transition}} = \text{SHA-256}(S_{\text{from}} \parallel \text{Event} \parallel S_{\text{to}} \parallel H_{\text{prev}})$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D03-01` [Deadlock Exhaustion]:** รันการวิเคราะห์กราฟ FSM ทั้ง 5 ตัว ยืนยันว่าไม่มี Unreachable State หรือ Deadlock Loop
2. **Test `TC-D03-02` [Illegal Transition Trap]:** ยิงคำสั่งเปลี่ยนสถานะ Candidate ข้ามขั้นจาก `CREATED` ไป `EXECUTING` โดยตรง ระบบต้องดักจับและปฏิเสธคำสั่งทันที
3. **Test `TC-D03-03` [Absorbing Terminal Test]:** สั่ง Transition บน Candidate ที่อยู่ในสถานะ `REJECTED` ตรวจสอบว่า FSM โยน `IllegalStateTransitionError`
4. **Test `TC-D03-04` [Canary Auto-Rollback Latency]:** จำลอง Error Rate 2% ในช่วง Canary Deployment ตรวจสอบว่าระบบ Rollback ภายในเวลา 500ms
