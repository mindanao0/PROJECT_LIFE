# Statistical Hypothesis Testing (Welch, TOST & Holm-Bonferroni)

> **Subsystem:** Statistical Rigor & Equivalence Testing  
> **Authority Level:** NORMATIVE (`REQ-S10-002` .. `REQ-S10-004`)

---

## 1. Welch's $t$-test (Difference Testing)

$$t = \frac{\bar{X}_{\text{cand}} - \bar{X}_{\text{base}}}{\sqrt{\frac{s_{\text{cand}}^2}{N_{\text{cand}}} + \frac{s_{\text{base}}^2}{N_{\text{base}}}}}$$

Degrees of Freedom (Welch–Satterthwaite Equation):

$$\nu = \frac{\left(\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}\right)^2}{\frac{(s_1^2/N_1)^2}{N_1 - 1} + \frac{(s_2^2/N_2)^2}{N_2 - 1}}$$

- **Zero-Variance Protection:** หาก $s_1^2 = 0$ และ $s_2^2 = 0$ ให้ตั้งค่า $t = 0$ เมื่อ $\bar{X}_1 = \bar{X}_2$ หรือ $t = \pm\infty$ เมื่อค่าเฉลี่ยต่างกัน

---

## 2. TOST (Two One-Sided Tests for Equivalence)

$$t_1 = \frac{(\bar{X}_1 - \bar{X}_2) - (-\Delta)}{\text{SE}}, \qquad t_2 = \frac{(\bar{X}_1 - \bar{X}_2) - (+\Delta)}{\text{SE}}$$

โดยที่ $\text{SE} = \sqrt{\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}}$

Candidate ถือว่า **Equivalent (ไม่เกิด Regression)** ก็ต่อเมื่อ:

$$t_1 \ge t_{\alpha, \nu} \quad \land \quad t_2 \le -t_{\alpha, \nu}$$

---

## 3. Holm-Bonferroni Multi-Testing Step-Down Procedure

เมื่อทดสอบ $m$ สมมติฐานพร้อมกัน:
1. เรียง $p$-values: $p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$
2. สำหรับ $k = 1, \dots, m$: ตรวจสอบว่า $p_{(k)} \le \frac{\alpha}{m - k + 1}$
