# Domain 11: Multi-Objective Pareto Dominance & Fast Sorting

> **Domain Index:** `DOMAIN-11`  
> **Engineering Scope:** `DIM-101` .. `DIM-110`  
> **Mathematical Equations:** `EQ-101` .. `EQ-110`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 11 กำหนดคณิตศาสตร์การคัดเลือกหลายเป้าหมาย (Multi-Objective Optimization) โดยใช้ **Strict Pareto Dominance**, **Fast Non-dominated Sorting Algorithm ($\mathcal{O}(MN^2)$)**, **Hypervolume Indicator (Lebesgue Measure)**, **Crowding Distance (NSGA-II)**, และ **Inverted Generational Distance Plus ($IGD^+$)**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-101  │ EQ-101   │ Strict Pareto Dominance Definition        │ x >- y <=> (forall i, f_i(x) >= f_i(y)) and (exists j, f_j(x) > f_j(y))│
│ DIM-102  │ EQ-102   │ Fast Non-Dominated Sorting Complexity     │ Complexity = O(M * N^2)                                     │
│ DIM-103  │ EQ-103   │ Pareto Front Rank Allocation Function     │ Rank(x) = 1 + |{y | y >- x}|                                │
│ DIM-104  │ EQ-104   │ Direction-Aware Sign Inversion Operator   │ bar{f}_i(x) = -f_i(x) <=> Direction(i) = MIN                │
│ DIM-105  │ EQ-105   │ Multi-Objective Convex Hull Preservation  │ H(S) = Conv({f(x) | x in S})                                │
│ DIM-106  │ EQ-106   │ Hypervolume Indicator Lebesgue Measure    │ HV(S, r) = Lambda(Union_{x in S} product [f_i(x), r_i])     │
│ DIM-107  │ EQ-107   │ Crowding Distance Density Estimator       │ I[i]_dist = I[i]_dist + (f_m(i+1) - f_m(i-1))/(f_m^max - f_m^min)│
│ DIM-108  │ EQ-108   │ Inverted Generational Distance Plus       │ IGD+(P, P*) = (1 / |P*|) * sum min d+(u, v)                 │
│ DIM-109  │ EQ-109   │ Zero-Weight Dominance Isolation Property  │ Pr(Dominated(x, y) | vec{w}) === Pr(Dominated(x, y))        │
│ DIM-110  │ EQ-110   │ Canonical Reversible Tie-Breaking Sort    │ TieBreak(x, y) = strcmp(Hash(x), Hash(y))                   │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-101` / `EQ-101`: Strict Pareto Dominance Definition
- **Formal Definition:** กำหนดให้ $x, y \in \mathcal{P}$ เป็น Candidate 2 ตัว และมี $M$ วัตถุประสงค์ $f_1, \dots, f_M$:
  $$x \succ y \iff \left(\forall i \in \{1, \dots, M\}, \quad f_i(x) \succeq f_i(y)\right) \land \left(\exists j \in \{1, \dots, M\}, \quad f_j(x) \succ f_j(y)\right)$$
- ห้ามนำค่าน้ำหนักมารวมคะแนนเป็นตัวเลขเดี่ยว (Single Weighted Sum) ในการจัดอันดับ Front

### `DIM-102` / `EQ-102`: Fast Non-Dominated Sorting Complexity
- ใช้อัลกอริทึม NSGA-II Fast Non-dominated Sort ในการจัดอันดับ Fronts ด้วย Big-O Bound:
  $$\text{Complexity} = \mathcal{O}(M \cdot N^2)$$

### `DIM-103` / `EQ-103`: Pareto Front Rank Allocation Function
- การจัดอันดับ Front ของ Candidate $x$:
  $$\text{Rank}(x) = 1 + |\{y \in P \mid y \succ x\}|$$

### `DIM-104` / `EQ-104`: Direction-Aware Sign Inversion Operator
- การกลับเครื่องหมายสำหรับ Objective ที่ต้องการ Minimum:
  $$\bar{f}_i(x) = -f_i(x) \iff \text{Direction}(i) = \text{MIN}$$

### `DIM-105` / `EQ-105`: Multi-Objective Convex Hull Preservation
- การคำนวณ Convex Hull เพื่อรักษาพื้นที่ครอบคลุมของ Trade-off:
  $$\mathcal{H}(S) = \text{Conv}(\{f(x) \mid x \in S\})$$

### `DIM-106` / `EQ-106`: Hypervolume Indicator (Lebesgue Measure)
- **Convergence Proof:** ปริมาตรของ Objective Space ที่ถูกครอบคลุมโดย Front $S$ เทียบกับ Reference Point $r$:
  $$HV(S, r) = \Lambda\left(\bigcup_{x \in S} [f_1(x), r_1] \times [f_2(x), r_2] \times \dots \times [f_M(x), r_M]\right)$$
- การขยายตัวของค่า $HV$ อย่างต่อเนื่องเป็นหลักฐานรับรองว่าประชากรพัฒนาไปข้างหน้า

### `DIM-107` / `EQ-107`: Crowding Distance Density Estimator
- การคำนวณความหนาแน่นเพื่อกระจายตัวของ Candidates ใน Front เดียวกัน:
  $$I[i]_{\text{dist}} = I[i]_{\text{dist}} + \frac{f_m(i+1) - f_m(i-1)}{f_m^{\max} - f_m^{\min}}$$

### `DIM-108` / `EQ-108`: Inverted Generational Distance Plus ($IGD^+$)
- การวัดระยะห่างระหว่างประชากรกับ True Pareto Frontier ในอุดมคติ:
  $$IGD^+(P, P^*) = \frac{1}{|P^*|} \sum_{v \in P^*} \min_{u \in P} d^+(u, v)$$

### `DIM-109` / `EQ-109`: Zero-Weight Dominance Isolation Property
- รับประกันว่าการตัดสินความเหนือกว่า (Dominance) ไม่ถูกแทรกแซงด้วยน้ำหนัก Preferences:
  $$\Pr(\text{Dominated}(x, y) \mid \vec{w}) \equiv \Pr(\text{Dominated}(x, y))$$

### `DIM-110` / `EQ-110`: Canonical Reversible Tie-Breaking Sort
- เมื่อ Candidates มีคะแนนเท่ากันทุกด้าน ให้ตัดสินด้วย SHA-256 Hash Digest แบบ Lexicographical:
  $$\text{TieBreak}(x, y) = \text{strcmp}(\text{Hash}(x), \text{Hash}(y))$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D11-01` [Pareto Dominance Asymmetry PBT]:** รันการสุ่มทดสอบด้วย Hypothesis ตรวจสอบว่า $\forall a, b: \neg(a \succ b \land b \succ a)$
2. **Test `TC-D11-02` [Fast Non-dominated Sort Benchmark]:** รันการจัดอันดับบนประชากร 100 Candidates (3 Objectives) ต้องประมวลผลเสร็จในเวลา $< 5.0\text{ ms}$
3. **Test `TC-D11-03` [Hypervolume Monotonicity]:** เมื่อเพิ่ม Candidate ที่ดีขึ้นใน Front ตรวจสอบว่าค่า $HV$ ต้องเพิ่มขึ้นหรือเท่าเดิมเสมอ
4. **Test `TC-D11-04` [Deterministic Tie-Breaking]:** ทดสอบ Candidate 5 ตัวที่มีคะแนนเท่ากันเป๊ะ ตรวจสอบว่าจัดอันดับได้ลำดับเดิม 100%
