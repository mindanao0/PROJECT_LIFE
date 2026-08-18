# Domain 17: ALife Ecosystems & Niche Energy Dynamics

> **Domain Index:** `DOMAIN-17`  
> **Engineering Scope:** `DIM-161` .. `DIM-170`  
> **Mathematical Equations:** `EQ-161` .. `EQ-170`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 17 กำหนดการจำลองระบบนิเวศชีววิทยาประดิษฐ์ (Artificial Life Co-Evolution) ระหว่าง **Prey (Candidate Programs)** กับ **Predator (Adversarial Test Generators)** โดยใช้ **Discretized Lotka-Volterra Equations**, บัญชีพลังงาน (Energy Credits Ledger), Niche Specialization, และ **Gini-Simpson Ecological Diversity Index**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-161  │ EQ-161   │ Discretized Lotka-Volterra Predator-Prey  │ Delta x = alpha * x - beta * x * y, Delta y = delta*x*y - gamma*y│
│ DIM-162  │ EQ-162   │ Adversarial Predator Test Generator Fit   │ f_predator(T) = sum I(Fail(c, T)) * Latency(c)              │
│ DIM-163  │ EQ-163   │ Energy Credit Allocation Accounting Ledger│ E_c(t+1) = E_c(t) + R_pass - C_metabolism                   │
│ DIM-164  │ EQ-164   │ Starvation-Based Population Pruning Rule  │ Prune(c) <=> E_c(t) <= 0                                    │
│ DIM-165  │ EQ-165   │ Niche Specialization Carrying Capacity    │ |P_{niche_k}| <= K_k                                        │
│ DIM-166  │ EQ-166   │ Symbiotic Co-Evolution Dynamics Velocity  │ v_coevol = ||grad f_prey|| + ||grad f_predator||            │
│ DIM-167  │ EQ-167   │ Niche Crowding Factor Sharing Penalty     │ f_shared(c) = f(c) / sum Sh(d(c, j))                        │
│ DIM-168  │ EQ-168   │ Dynamic Resource Landscape Periodic Wave  │ R_env(t) = R_0 * [1 + A * sin(omega * t)]                   │
│ DIM-169  │ EQ-169   │ Adversarial Input Fuzzing Entropy Metric  │ H(I_fuzz) >= H_threshold                                    │
│ DIM-170  │ EQ-170   │ Gini-Simpson Ecological Diversity Index   │ 1 - D = 1 - sum_{i=1}^S p_i^2                               │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-161` / `EQ-161`: Discretized Lotka-Volterra Predator-Prey
- **Population Dynamics:** การเปลี่ยนแปลงของประชากร Candidate ($x$) และ Test Generators ($y$):
  $$\Delta x = \alpha x - \beta x y, \qquad \Delta y = \delta x y - \gamma y$$

### `DIM-162` / `EQ-162`: Adversarial Predator Test Generator Fit
- Fitness ของ Test Case ขึ้นกับความสามารถในการค้นหา Edge Case ที่ทำให้ Candidate ล้มเหลวหรือช้าลง:
  $$f_{\text{predator}}(T) = \sum_{c \in \text{Prey}} \mathbb{I}(\text{Fail}(c, T)) \cdot \text{Latency}(c)$$

### `DIM-163` / `EQ-163`: Energy Credit Allocation
- Candidate ที่สามารถผ่านการทดสอบจะได้รับ Energy Credits เพื่อความอยู่รอด:
  $$E_c(t+1) = E_c(t) + R_{\text{pass}} - C_{\text{metabolism}}$$

### `DIM-164` / `EQ-164`: Starvation-Based Population Pruning Rule
- Candidate ที่พลังงานหมดจะถูกตัดออกจากประชากรทันที:
  $$\text{Prune}(c) \iff E_c(t) \le 0$$

### `DIM-165` / `EQ-165`: Niche Specialization Carrying Capacity
- จำกัดจำนวนประชากรในแต่ละ Niche เฉพาะทางไม่เกินความจุ $K_k$:
  $$|P_{\text{niche}_k}| \le K_k$$

### `DIM-166` / `EQ-166`: Symbiotic Co-Evolution Dynamics Velocity
- อัตราความเร็วในการพัฒนาคู่ขนานระหว่าง Candidate และชุดทดสอบ:
  $$v_{\text{coevol}} = \|\nabla f_{\text{prey}}\| + \|\nabla f_{\text{predator}}\|$$

### `DIM-167` / `EQ-167`: Niche Crowding Factor Sharing Penalty
- การลงโทษประชากรที่รวมกลุ่มหนาแน่นเกินไปเพื่อบังคับให้กระจายตัว:
  $$f_{\text{shared}}(c) = \frac{f(c)}{\sum_{j \in \text{niche}} \text{Sh}(d(c, j))}$$

### `DIM-168` / `EQ-168`: Dynamic Resource Landscape Periodic Wave
- ทรัพยากรสิ่งแวดล้อมจำลองเปลี่ยนแปลงตามคลื่นไซน์เพื่อทดสอบความยืดหยุ่น:
  $$R_{\text{env}}(t) = R_0 [1 + A \sin(\omega t)]$$

### `DIM-169` / `EQ-169`: Adversarial Input Fuzzing Entropy Metric
- ชุดข้อมูลทดสอบที่สร้างโดย Predator ต้องมีความหลากหลายเชิงเอนโทรปี:
  $$H(I_{\text{fuzz}}) \ge H_{\text{threshold}}$$

### `DIM-170` / `EQ-170`: Gini-Simpson Ecological Diversity Index
- ดัชนีความหลากหลายของระบบนิเวศวิวัฒนาการ:
  $$1 - D = 1 - \sum_{i=1}^S p_i^2$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D17-01` [Co-evolution Equilibrium]:** รันการจำลอง Prey vs Predator 50 Generations ยืนยันว่าประชากรทั้งสองฝั่งรักษาสมดุลไม่สูญพันธุ์
2. **Test `TC-D17-02` [Starvation Pruning]:** Candidate ที่ไม่ผ่าน Test ต่อเนื่อง 3 รุ่น ต้องมี Energy เป็น 0 และถูกคัดทิ้งอย่างถูกต้อง
3. **Test `TC-D17-03` [Niche Capacity Limit]:** ตรวจสอบว่าไม่มี Niche ใดมีประชากรเกินค่า $K_k$
4. **Test `TC-D17-04` [Fuzzing Entropy Validation]:** ทดสอบว่า Test Generator สร้าง Input ที่มี Entropy ผ่านเกณฑ์ขั้นต่ำ
