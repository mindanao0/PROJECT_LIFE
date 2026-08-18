# Domain 16: Evolutionary Stagnation & Escalation Ladders

> **Domain Index:** `DOMAIN-16`  
> **Engineering Scope:** `DIM-151` .. `DIM-160`  
> **Mathematical Equations:** `EQ-151` .. `EQ-160`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 16 กำหนดกลไกการตรวจจับสภาวะวิวัฒนาการหยุดนิ่ง (Stagnation Detection) และบันไดกู้วิวัฒนาการ 4 ระดับ (4-Tier Escalation Ladder), **Maximal Lyapunov Exponent for Chaos Control**, และการฉีดสายพันธุ์ใหม่ (Cataclysmic Re-seeding).

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-151  │ EQ-151   │ Stagnation Generation Counter Formula     │ G_stag = g - max {k | Delta HV_k > 0}                       │
│ DIM-152  │ EQ-152   │ Escalation Tier 1 Temperature Multiplier  │ T_1 = T_0 * 1.5, mu: 0.05 -> 0.20                           │
│ DIM-153  │ EQ-153   │ Escalation Tier 2 Hyper-Mutation Rate     │ Pr(MacroMutation) = 0.50                                    │
│ DIM-154  │ EQ-154   │ Escalation Tier 3 Hippocampal Injection   │ P_inject = 0.25 * N_pop                                     │
│ DIM-155  │ EQ-155   │ Escalation Tier 4 Cataclysmic Re-Seeding  │ P_cull = 0.50 * N_pop                                       │
│ DIM-156  │ EQ-156   │ Stagnation Reset on Front Expansion       │ Delta HV > eps ==> G_stag = 0                               │
│ DIM-157  │ EQ-157   │ Adaptive Stagnation Threshold Formula     │ G_threshold = ceil(5 + ln(|S_search|))                      │
│ DIM-158  │ EQ-158   │ Premature Convergence Variance Warning    │ Var(P) <= sigma_min^2 ==> TriggerEscalation                 │
│ DIM-159  │ EQ-159   │ Maximal Lyapunov Exponent for Chaos Bound │ lambda_max = lim (1/t) sum ln |f'(x_k)|                     │
│ DIM-160  │ EQ-160   │ Stagnation Escalation Audit Log Hash      │ H_stag = SHA-256(G_stag || Tier || H_prev)                  │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-151` / `EQ-151`: Stagnation Generation Counter Formula
- **Counter Definition:** นับจำนวนรุ่นติดต่อกันที่ไม่พบการขยายตัวของ Hypervolume ($\Delta HV \le 0$):
  $$G_{\text{stag}} = g - \max \{k \mid \Delta HV_k > 0\}$$

### `DIM-152` / `EQ-152`: Escalation Tier 1 Temperature Multiplier
- การเพิ่มอัตราการกลายพันธุ์จาก 5% เป็น 20%:
  $$T_1 = T_0 \times 1.5, \qquad \mu: 0.05 \to 0.20$$

### `DIM-153` / `EQ-153`: Escalation Tier 2 Hyper-Mutation Rate
- การเปิดใช้งาน Macro Mutation ปรับเปลี่ยนโครงสร้าง AST ขนาดใหญ่:
  $$\Pr(\text{MacroMutation}) = 0.50$$

### `DIM-154` / `EQ-154`: Escalation Tier 3 Hippocampal Injection
- การดึงความจำการแก้ปัญหาในอดีตมาฉีดเข้าประชากร 25%:
  $$P_{\text{inject}} = 0.25 \times N_{\text{pop}}$$

### `DIM-155` / `EQ-155`: Escalation Tier 4 Cataclysmic Re-Seeding
- การกวาดล้างและสร้างประชากรใหม่ 50% เพื่อทำลาย Local Optima:
  $$P_{\text{cull}} = 0.50 \times N_{\text{pop}}$$

### `DIM-156` / `EQ-156`: Stagnation Reset on Front Expansion
- เมื่อพบการขยายตัวของ Pareto Front ให้รีเซ็ตตัวนับสภาวะหยุดนิ่ง:
  $$\Delta HV > \epsilon \implies G_{\text{stag}} = 0$$

### `DIM-157` / `EQ-157`: Adaptive Stagnation Threshold Formula
- เกณฑ์จำนวนรุ่นที่จะตัดสินว่าหยุดนิ่ง ปรับตามขนาดของ Search Space:
  $$G_{\text{threshold}} = \lceil 5 + \ln(|S_{\text{search}}|) \rceil$$

### `DIM-158` / `EQ-158`: Premature Convergence Variance Warning
- ตรวจจับการบรรจบกันก่อนเวลาอันควรเมื่อความแปรปรวนของประชากรลดต่ำเกินไป:
  $$\text{Var}(P) \le \sigma_{\min}^2 \implies \text{TriggerEscalation}$$

### `DIM-159` / `EQ-159`: Maximal Lyapunov Exponent for Chaos Control
- ใช้วัดเสถียรภาพของการค้นหาเพื่อป้องกันไม่ให้ระบบตกอยู่ในสภาวะอลวนจนหลุดขอบเขต (Chaotic Divergence):
  $$\lambda_{\max} = \lim_{t \to \infty} \frac{1}{t} \sum_{k=0}^{t-1} \ln |f'(x_k)|$$

### `DIM-160` / `EQ-160`: Stagnation Escalation Audit Log Hash
- บันทึกการกระตุ้นบันได Escalation ทุกขั้นลงใน Hash Chain:
  $$H_{\text{stag}} = \text{SHA-256}(G_{\text{stag}} \parallel \text{Tier} \parallel H_{\text{prev}})$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D16-01` [4-Tier Escalation Trigger]:** จำลองประชากรหยุดนิ่ง 20 Generations ตรวจสอบว่าระบบไต่ระดับจาก Tier 1 ไปจนถึง Tier 4 อย่างถูกต้อง
2. **Test `TC-D16-02` [Stagnation Counter Reset]:** เมื่อฉีด Candidate ที่ทำลายสถิติ Hypervolume ได้สำเร็จ ตรวจสอบว่า $G_{\text{stag}}$ รีเซ็ตกลับเป็น 0 ทันที
3. **Test `TC-D16-03` [Lyapunov Stability Check]:** ตรวจสอบว่าค่า Lyapunov Exponent ไม่เกิด Divergence ไปสู่อนันต์
4. **Test `TC-D16-04` [Cataclysmic Re-seeding Diversity]:** ยืนยันว่าประชากรหลังผ่าน Tier 4 มี Diversity Score เพิ่มขึ้น $\ge 40\%$
