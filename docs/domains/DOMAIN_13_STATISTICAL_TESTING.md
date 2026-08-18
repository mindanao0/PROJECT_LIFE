# Domain 13: Statistical Tests (Welch, TOST, Holm, FDR)

> **Domain Index:** `DOMAIN-13`  
> **Engineering Scope:** `DIM-121` .. `DIM-130`  
> **Mathematical Equations:** `EQ-121` .. `EQ-130`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 13 กำหนดการอนุมานทางสถิติที่เข้มงวด (Rigorous Statistical Inference) เพื่อป้องกัน Type I Error และ Regression โดยผสาน **Welch's $t$-test (Difference Testing)**, **TOST (Two One-Sided Tests for Equivalence)**, **Holm-Bonferroni FWER Correction**, **Benjamini-Hochberg FDR**, **Cohen's $d$ Effect Size**, และ **Hodges-Lehmann Non-parametric Estimator**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-121  │ EQ-121   │ Welch's t-test Unequal Variance Statistic │ t = (bar{X}_1 - bar{X}_2) / sqrt(s_1^2/N_1 + s_2^2/N_2)     │
│ DIM-122  │ EQ-122   │ Welch-Satterthwaite Degrees of Freedom    │ nu = (s_1^2/N_1 + s_2^2/N_2)^2 / (frac1 + frac2)            │
│ DIM-123  │ EQ-123   │ TOST Two One-Sided Tests for Equivalence  │ t_1 = (Diff - (-Delta))/SE, t_2 = (Diff - Delta)/SE         │
│ DIM-124  │ EQ-124   │ Holm-Bonferroni FWER Step-Down Correction │ p_{(k)} <= alpha / (m - k + 1)                              │
│ DIM-125  │ EQ-125   │ Zero-Variance Degeneracy Protection       │ s_1^2=0 and s_2^2=0 ==> t = 0 <=> bar{X}_1 = bar{X}_2       │
│ DIM-126  │ EQ-126   │ Minimum Sample Size Enforcement (N >= 5)  │ N >= N_min = 5                                              │
│ DIM-127  │ EQ-127   │ 90% Confidence Interval for TOST Testing  │ CI_90 = (bar{X}_1 - bar{X}_2) +- t_{0.05, nu} * SE          │
│ DIM-128  │ EQ-128   │ Cohen's d Standardized Effect Size        │ d = |bar{X}_1 - bar{X}_2| / s_pooled                        │
│ DIM-129  │ EQ-129   │ Benjamini-Hochberg False Discovery Rate   │ P_{(k)} <= (k / m) * Q                                      │
│ DIM-130  │ EQ-130   │ Hodges-Lehmann Median Shift Estimator     │ Delta_hat = median{X_{1i} - X_{2j}}                         │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-121` / `EQ-121`: Welch's $t$-test Statistic
- **Equation:** การทดสอบความแตกต่างของค่าเฉลี่ยประสิทธิภาพระหว่าง Candidate กับ Baseline:
  $$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}}}$$

### `DIM-122` / `EQ-122`: Welch-Satterthwaite Degrees of Freedom
- การคำนวณ Degrees of Freedom ที่ไม่สมมุติว่าความแปรปรวนเท่ากัน:
  $$\nu = \frac{\left(\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}\right)^2}{\frac{(s_1^2/N_1)^2}{N_1 - 1} + \frac{(s_2^2/N_2)^2}{N_2 - 1}}$$

### `DIM-123` / `EQ-123`: TOST Equivalence Testing
- Candidate ถือว่า **ไม่เกิด Regression** เทียบกับ Baseline ก็ต่อเมื่อผ่านการทดสอบ TOST ทั้งสองด้าน:
  $$t_1 = \frac{(\bar{X}_1 - \bar{X}_2) - (-\Delta)}{\text{SE}} \ge t_{\alpha, \nu} \quad \land \quad t_2 = \frac{(\bar{X}_1 - \bar{X}_2) - (+\Delta)}{\text{SE}} \le -t_{\alpha, \nu}$$

### `DIM-124` / `EQ-124`: Holm-Bonferroni FWER Step-Down Correction
- ควบคุม Family-Wise Error Rate เมื่อมีการทดสอบสมมติฐานพร้อมกันหลายตัว:
  $$p_{(k)} \le \frac{\alpha}{m - k + 1}$$

### `DIM-125` / `EQ-125`: Zero-Variance Degeneracy Protection
- ป้องกันการหารด้วยศูนย์เมื่อทุกตัวอย่างมีค่า Latency เท่ากันเป๊ะ:
  $$s_1^2 = 0 \land s_2^2 = 0 \implies t = 0 \iff \bar{X}_1 = \bar{X}_2$$

### `DIM-126` / `EQ-126`: Minimum Sample Size Enforcement
- บังคับจำนวนครั้งในการทดสอบ Benchmark ขั้นต่ำ $N \ge 5$ ครั้งต่อ Candidate:
  $$N \ge N_{\min} = 5$$

### `DIM-127` / `EQ-127`: 90% Confidence Interval for TOST Testing
- ช่วงความเชื่อมั่น 90% ของความต่างของค่าเฉลี่ย:
  $$\text{CI}_{90\%} = (\bar{X}_1 - \bar{X}_2) \pm t_{0.05, \nu} \cdot \text{SE}$$

### `DIM-128` / `EQ-128`: Cohen's $d$ Effect Size
- วัดขนาดของความแตกต่างเชิงปฏิบัติ (Practical Significance):
  $$d = \frac{|\bar{X}_1 - \bar{X}_2|}{s_{\text{pooled}}}, \qquad s_{\text{pooled}} = \sqrt{\frac{(N_1 - 1)s_1^2 + (N_2 - 1)s_2^2}{N_1 + N_2 - 2}}$$

### `DIM-129` / `EQ-129`: Benjamini-Hochberg False Discovery Rate
- ควบคุมอัตราการค้นพบที่ผิดพลาดในระดับประชากรขนาดใหญ่:
  $$P_{(k)} \le \frac{k}{m} Q$$

### `DIM-130` / `EQ-130`: Hodges-Lehmann Median Shift Estimator
- ตัวประมาณค่าความต่างมัธยฐานแบบ Non-parametric:
  $$\hat{\Delta} = \text{median}\{X_{1i} - X_{2j}\}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D13-01` [Zero Variance Handler]:** ทดสอบตัวอย่างข้อมูลที่ทุกตัวมีค่าเท่ากันเป๊ะ ($s_1^2 = 0, s_2^2 = 0$) ระบบต้องไม่เกิด `ZeroDivisionError`
2. **Test `TC-D13-02` [Holm-Bonferroni FWER]:** รันการทดสอบ $p$-values 20 ตัว ตรวจสอบว่าเกณฑ์ Step-down ถูกคำนวณอย่างถูกต้อง
3. **Test `TC-D13-03` [TOST Equivalence Validation]:** ทดสอบ Candidate ที่มี Latency ต่างจาก Baseline 1% ตรวจสอบว่าผ่านการทดสอบสมมูล
4. **Test `TC-D13-04` [Cohen's d Magnitude Benchmark]:** ตรวจสอบการจำแนกขนาด Effect Size (Small, Medium, Large) ตามเกณฑ์ $d$
