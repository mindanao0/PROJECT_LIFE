# Domain 14: Multi-Armed Bandit Dynamic Strategy (UCB1)

> **Domain Index:** `DOMAIN-14`  
> **Engineering Scope:** `DIM-131` .. `DIM-140`  
> **Mathematical Equations:** `EQ-131` .. `EQ-140`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 14 กำหนดการจัดสรรสัดส่วนตัวดำเนินการกลายพันธุ์ (Mutation Strategies Allocation) แบบอัตโนมัติผ่าน **Upper Confidence Bound (UCB1)**, **Thompson Sampling (Beta-Bernoulli Conjugate)**, **Exponentially Decayed Moving Average (EMA)**, และการรับประกัน **Exploration Floor ($\epsilon = 0.05$)**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-131  │ EQ-131   │ UCB1 Acquisition Score Formula            │ Score_i(t) = bar{X}_i + c * sqrt(ln N(t) / n_i(t))          │
│ DIM-132  │ EQ-132   │ Exploration vs Exploitation Regret Bound  │ lim R(N)/ln N <= sum 2/Delta_i                              │
│ DIM-133  │ EQ-133   │ Minimum Exploration Floor Allocation      │ P_i = (1 - K*eps) * Score_i / sum Score_j + eps, eps=0.05   │
│ DIM-134  │ EQ-134   │ Capability-Gated Reward Computation       │ R(c) = I(PassGates(c)) * ParetoGain(c)                      │
│ DIM-135  │ EQ-135   │ Exponentially Decayed Moving Average EMA  │ bar{R}_i(t) = lambda * R_i(t) + (1 - lambda) * bar{R}_i(t-1)│
│ DIM-136  │ EQ-136   │ Thompson Sampling Beta Posterior          │ theta_i ~ Beta(alpha_i + 1, beta_i + 1), i* = argmax theta_i│
│ DIM-137  │ EQ-137   │ Dynamic Arm Activation Subset             │ A_active(t) subseteq {M_01, ..., M_10}                      │
│ DIM-138  │ EQ-138   │ Multi-Objective Vectorized Reward         │ vec{R}(c) = sum_{m=1}^M w_m * Delta f_m(c)                  │
│ DIM-139  │ EQ-139   │ Cold-Start Uniform Initialization Bound   │ n_i(0) = N_init = 3 forall i                                │
│ DIM-140  │ EQ-140   │ Bandit State Persistence Checksum Digest  │ H_bandit = SHA-256(product n_i || bar{X}_i)                 │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-131` / `EQ-131`: UCB1 Acquisition Score Formula
- **Equation:** คะแนนการเลือก Mutation Operator $i$ ในรุ่น $t$:
  $$\text{Score}_i(t) = \bar{X}_i + c \sqrt{\frac{\ln N(t)}{n_i(t)}}, \qquad c = \sqrt{2} \approx 1.414$$

### `DIM-132` / `EQ-132`: Exploration vs Exploitation Regret Bound
- รับประกันขอบเขต Regret สูงสุดที่เติบโตไม่เกิน $\mathcal{O}(\ln N)$:
  $$\lim_{N \to \infty} \frac{R_{\text{regret}}(N)}{\ln N} \le \sum_{i: \Delta_i > 0} \frac{2}{\Delta_i}$$

### `DIM-133` / `EQ-133`: Minimum Exploration Floor Allocation
- เพื่อป้องกันไม่ให้กลยุทธ์ใดกลยุทธ์หนึ่งถูกตัดความน่าจะเป็นจนเป็น 0 ระบบบังคับใช้ Floor $\epsilon = 0.05$:
  $$P_i = (1 - K\epsilon) \frac{\text{Score}_i}{\sum_j \text{Score}_j} + \epsilon, \quad K = 10$$

### `DIM-134` / `EQ-134`: Capability-Gated Reward Computation
- รางวัลจะถูกจ่ายให้ Operator ก็ต่อเมื่อ Candidate ผ่าน Release Gates พื้นฐาน:
  $$R(c) = \mathbb{I}(\text{PassGates}(c)) \cdot \text{ParetoGain}(c)$$

### `DIM-135` / `EQ-135`: Exponentially Decayed Moving Average EMA
- การปรับคะแนนเฉลี่ยเพื่อให้น้ำหนักกับผลลัพธ์ล่าสุด ($\lambda = 0.2$):
  $$\bar{R}_i(t) = \lambda R_i(t) + (1 - \lambda)\bar{R}_i(t-1)$$

### `DIM-136` / `EQ-136`: Thompson Sampling Beta Posterior
- การสุ่มเลือกแบบเบย์เซียนผ่าน Beta Distribution:
  $$\theta_i \sim \text{Beta}(\alpha_i + 1, \beta_i + 1), \qquad i^* = \arg\max \theta_i$$

### `DIM-137` / `EQ-137`: Dynamic Arm Activation Subset
- สับเปลี่ยนชุด Operator ที่เปิดใช้งานตามบริบทของโปรเจกต์:
  $$\mathcal{A}_{\text{active}}(t) \subseteq \{M_{01}, \dots, M_{10}\}$$

### `DIM-138` / `EQ-138`: Multi-Objective Vectorized Reward
- รวมผลการปรับปรุงในหลายมิติเข้าสู่เวกเตอร์รางวัลเดียว:
  $$\vec{R}(c) = \sum_{m=1}^M w_m \cdot \Delta f_m(c)$$

### `DIM-139` / `EQ-139`: Cold-Start Uniform Initialization Bound
- ทุก Operator ต้องถูกทดลองใช้งานอย่างน้อย 3 ครั้งในช่วงเริ่มต้น:
  $$n_i(0) = N_{\text{init}} = 3 \quad \forall i$$

### `DIM-140` / `EQ-140`: Bandit State Persistence Checksum Digest
- บันทึกสถานะ Bandit ลง Checkpoint พร้อม SHA-256 Checksum:
  $$H_{\text{bandit}} = \text{SHA-256}\left(\prod_{i=1}^K n_i \parallel \bar{X}_i\right)$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D14-01` [Exploration Floor Invariant]:** ทดสอบ Operator ที่ล้มเหลวต่อเนื่อง 100 ครั้ง ตรวจสอบว่าความน่าจะเป็นในการถูกเลือกยังคง $\ge 0.05$ เสมอ
2. **Test `TC-D14-02` [UCB1 Reward Update]:** ทดสอบให้ Operator หมายเลข 3 ทำคะแนนเพิ่มขึ้น ตรวจสอบว่า $\bar{X}_3$ และความน่าจะเป็น $P_3$ เพิ่มขึ้นตามสัดส่วน
3. **Test `TC-D14-03` [Cold-Start Enforcement]:** ตรวจสอบว่าใน 30 ครั้งแรก ทุก Operator ถูกเรียกใช้งานครบเท่ากัน 3 ครั้ง
4. **Test `TC-D14-04` [Thompson Sampling Conjugacy]:** ยืนยันว่าการอัปเดต Posterior เป็นไปตามกฎ Beta Conjugate Prior
