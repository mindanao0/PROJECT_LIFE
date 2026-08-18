# Domain 28: 7-Tier Testing & Property-Based Fuzzing

> **Domain Index:** `DOMAIN-28`  
> **Engineering Scope:** `DIM-271` .. `DIM-280`  
> **Mathematical Equations:** `EQ-271` .. `EQ-280`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 28 กำหนดการประกันคุณภาพระบบผ่าน **7-Tier Testing Strategy Hierarchy**, **Hypothesis Property-Based Testing (PBT)**, **14 Golden Projects Corpus (MVP-01..14)**, การตรวจจับ Flaky Tests และกฎห้าม Retry (`No-Retry Rule`).

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-271  │ EQ-271   │ 7-Tier QA Test Strategy Coverage Bound    │ Coverage_overall >= 0.90                                    │
│ DIM-272  │ EQ-272   │ Hypothesis Property-Based Testing Bound   │ N_samples >= 1,000 per property                             │
│ DIM-273  │ EQ-273   │ 14 Golden Projects Conformance Set Count  │ |C_golden| === 14, Pass(C) === 14                           │
│ DIM-274  │ EQ-274   │ Flaky Test Non-Gaming Variance Detection  │ Var(PassFail(c)) > 0 ==> FLAKY                              │
│ DIM-275  │ EQ-275   │ Hidden Holdout Test Anti-Gaming Split     │ P_train = 0.80, P_holdout = 0.20                            │
│ DIM-276  │ EQ-276   │ Negative Security Attack Vector Proof     │ forall v in V_attack, State(v) === QUARANTINED              │
│ DIM-277  │ EQ-277   │ 4-Stage Crash Injection Recovery Proof    │ forall k in {1, 2, 3, 4}, Recover(Crash_k) === SUCCESS      │
│ DIM-278  │ EQ-278   │ FSM Reachability Deadlock Exhaustion Proof│ |{s in S \ Terminal | sum T_sj = 0}| === 0                  │
│ DIM-279  │ EQ-279   │ Signed Evidence Bundle Verification Bound │ VerifyBundle(Bundle) in {True, False}                       │
│ DIM-280  │ EQ-280   │ Deterministic Replay Output Identity (R4) │ OutputBytes(Replay) === OutputBytes(Baseline)               │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-271` / `EQ-271`: 7-Tier QA Test Strategy Coverage Bound
- ความครอบคลุมการทดสอบรวมของระบบต้องไม่ต่ำกว่า 90%:
  $$\text{Coverage}_{\text{overall}} \ge 0.90$$

### `DIM-272` / `EQ-272`: Hypothesis Property-Based Testing Bound
- แต่ละ Property ต้องถูกทดสอบผ่าน Hypothesis อย่างน้อย 1,000 ตัวอย่าง:
  $$N_{\text{samples}} \ge 1,000 \quad \text{per property}$$

### `DIM-273` / `EQ-273`: 14 Golden Projects Conformance Set Count
- ชุดโครงการทดสอบมาตรฐาน Golden Corpus มี 14 โปรเจกต์ และต้องผ่านทั้งหมด:
  $$|\mathcal{C}_{\text{golden}}| \equiv 14, \qquad \text{Pass}(\mathcal{C}) \equiv 14$$

### `DIM-274` / `EQ-274`: Flaky Test Detection & No-Retry Rule
- เมื่อผลทดสอบสลับ `PASS`/`FAIL` บน Candidate เดียวกันโดยไม่มีการแก้โค้ด:
  $$\text{Var}(\text{PassFail}(c)) > 0 \implies \text{Status} \to \text{FLAKY}$$
- ห้าม Retry การทดสอบซ้ำๆ เพื่อหวังผลให้ผ่านเด็ดขาด

### `DIM-275` / `EQ-275`: Hidden Holdout Test Anti-Gaming Split
- แบ่งชุดทดสอบเป็น Train 80% และ Hidden Holdout 20% เพื่อป้องกัน Overfitting:
  $$P_{\text{train}} = 0.80, \qquad P_{\text{holdout}} = 0.20$$

### `DIM-276` / `EQ-276`: Negative Security Attack Vector Proof
- เวกเตอร์การโจมตีความปลอดภัยทั้งหมดต้องถูกกักกัน 100%:
  $$\forall v \in \mathcal{V}_{\text{attack}}, \quad \text{State}(v) \equiv \text{QUARANTINED}$$

### `DIM-277` / `EQ-277`: 4-Stage Crash Injection Recovery Proof
- ระบบต้องสามารถกู้คืนสถานะได้สำเร็จจากจุดตัดไฟจำลองทั้ง 4 จุด:
  $$\forall k \in \{1, 2, 3, 4\}, \quad \text{Recover}(\text{Crash}_k) \equiv \text{SUCCESS}$$

### `DIM-278` / `EQ-278`: FSM Reachability Deadlock Exhaustion Proof
- พิสูจน์ว่าไม่มี Non-terminal State ใดใน FSM ที่ติด Deadlock:
  $$|\{s \in S \setminus \text{Terminal} \mid \sum_j T_{sj} = 0\}| \equiv 0$$

### `DIM-279` / `EQ-279`: Signed Evidence Bundle Verification Bound
- การตรวจสอบความถูกต้องของ Signed Evidence Bundle:
  $$\text{VerifyBundle}(\text{Bundle}) \in \{\text{True}, \text{False}\}$$

### `DIM-280` / `EQ-280`: Deterministic Replay Output Identity (R4)
- ผลลัพธ์การรัน Replay ต้องเหมือนกับผลลัพธ์ดั้งเดิมแบบบิตต่อบิต:
  $$\text{OutputBytes}(\text{Replay}) \equiv \text{OutputBytes}(\text{Baseline})$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D28-01` [Golden Corpus Conformance]:** รันการทดสอบ Golden Corpus ทั้ง 14 เคส (MVP-01 ถึง MVP-14) ต้องผ่าน 100%
2. **Test `TC-D28-02` [PBT Test Execution]:** รัน Hypothesis Property Tests 1,000 ตัวอย่างต่อรอบ ยืนยันว่าไม่มี Invariant ใดถูกละเมิด
3. **Test `TC-D28-03` [Flaky Test Isolation]:** จำลอง Test ที่มี Random Pass/Fail ตรวจสอบว่าระบบจัดประเภทเป็น FLAKY และบล็อกการ Merge
4. **Test `TC-D28-04` [Crash Recovery Invariant]:** ยิง Crash Injection 4 จุด ตรวจสอบว่าระบบ Recovery สำเร็จทุกครั้ง
