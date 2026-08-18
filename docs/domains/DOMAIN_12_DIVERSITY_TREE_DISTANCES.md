# Domain 12: Population Diversity & Tree Edit Distances

> **Domain Index:** `DOMAIN-12`  
> **Engineering Scope:** `DIM-111` .. `DIM-120`  
> **Mathematical Equations:** `EQ-111` .. `EQ-120`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 12 กำหนดการคำนวณระยะห่างและความหลากหลายของประชากร (Population Diversity Preservation) โดยผสาน **Zhang-Shasha Tree Edit Distance ($d_{\text{AST}}$)**, **Normalized Levenshtein Token Distance ($d_{\text{Token}}$)**, **Behavioral Output Distance ($d_{\text{Behavior}}$)**, และ **Shannon Entropy of Diversity ($H$)**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-111  │ EQ-111   │ Normalized Diversity Score Formulation    │ Div(c, P) = (d_AST + d_Token + d_Behavior) / 3 in [0, 1]    │
│ DIM-112  │ EQ-112   │ Zhang-Shasha AST Tree Edit Distance       │ d_AST(T_1, T_2) = TED(T_1, T_2) / max(|T_1|, |T_2|)         │
│ DIM-113  │ EQ-113   │ Normalized Levenshtein Token Metric       │ d_Token(S_1, S_2) = Lev(tok_1, tok_2) / max(|tok_1|,|tok_2|)│
│ DIM-114  │ EQ-114   │ Behavioral Output Vector Distance         │ d_Behavior(y_1, y_2) = (1 / K) * sum I(y_{1,k} != y_{2,k})  │
│ DIM-115  │ EQ-115   │ Shannon Entropy of Genetic Diversity      │ H(P) = - sum_{i=1}^K p_i log_2(p_i)                         │
│ DIM-116  │ EQ-116   │ Diversity Preservation Floor Threshold    │ Div(P) >= epsilon_diversity = 0.10                          │
│ DIM-117  │ EQ-117   │ Genotypic vs Phenotypic Distance Match    │ r_{GP} = Cov(d_G, d_P) / (sigma_G * sigma_P)                │
│ DIM-118  │ EQ-118   │ Subpopulation Clustering Distance Metric  │ J_cluster = sum sum ||x - mu_k||^2                          │
│ DIM-119  │ EQ-119   │ Redundant Candidate Hash Deduplication    │ x === y <=> SHA-256(x) = SHA-256(y)                         │
│ DIM-120  │ EQ-120   │ Diversity Component Weights Convex Sum    │ w_AST + w_Token + w_Behavior = 1.0                          │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-111` / `EQ-111`: Normalized Total Diversity Score
- **Composite Distance:** คะแนนความหลากหลายรวมของ Candidate $c$ เทียบกับประชากร $P$:
  $$\text{Div}(c, P) = \frac{d_{\text{AST}}(c, P) + d_{\text{Token}}(c, P) + d_{\text{Behavior}}(c, P)}{3} \in [0, 1]$$

### `DIM-112` / `EQ-112`: Zhang-Shasha AST Tree Edit Distance
- คำนวณจำนวนการ Insert, Delete, และ Relabel Nodes ใน Abstract Syntax Tree:
  $$d_{\text{AST}}(T_1, T_2) = \frac{\text{TreeEditDistance}(T_1, T_2)}{\max(|T_1|, |T_2|)}$$

### `DIM-113` / `EQ-113`: Normalized Levenshtein Token Metric
- ระยะห่างระดับ Token Stream หลังตัด Whitespace:
  $$d_{\text{Token}}(S_1, S_2) = \frac{\text{Lev}(\text{tok}(S_1), \text{tok}(S_2))}{\max(|\text{tok}_1|, |\text{tok}_2|)}$$

### `DIM-114` / `EQ-114`: Behavioral Output Vector Distance
- สัดส่วนความแตกต่างของ Output จากการรันชุด Test Suite:
  $$d_{\text{Behavior}}(y_1, y_2) = \frac{1}{K} \sum_{k=1}^K \mathbb{I}(y_{1,k} \ne y_{2,k})$$

### `DIM-115` / `EQ-115`: Shannon Entropy of Genetic Diversity
- วัดความไม่แน่นอนและการกระจายตัวของยีนในประชากร:
  $$H(P) = -\sum_{i=1}^K p_i \log_2(p_i)$$

### `DIM-116` / `EQ-116`: Diversity Preservation Floor Threshold
- รักษาระดับความหลากหลายของประชากรไม่ให้ต่ำกว่า 10% เพื่อป้องกัน Inbreeding:
  $$\text{Div}(P) \ge \epsilon_{\text{diversity}} = 0.10$$

### `DIM-117` / `EQ-117`: Genotypic vs Phenotypic Distance Match
- สัมประสิทธิ์ความสัมพันธ์ระหว่างระยะห่างเชิงโค้ดและระยะห่างเชิงพฤติกรรม:
  $$r_{GP} = \frac{\text{Cov}(d_G, d_P)}{\sigma_G \sigma_P}$$

### `DIM-118` / `EQ-118`: Subpopulation Clustering Distance Metric
- การจัดกลุ่ม Cluster ประชากรย่อยเพื่อแยกสายพันธุ์:
  $$J_{\text{cluster}} = \sum_{k=1}^K \sum_{x \in S_k} \|x - \mu_k\|^2$$

### `DIM-119` / `EQ-119`: Redundant Candidate Hash Deduplication
- ตัด Candidate ที่มีไวยากรณ์ซ้ำซ้อนกันทิ้งทันทีในขั้นตอนคัดกรอง:
  $$x \equiv y \iff \text{SHA-256}(x) = \text{SHA-256}(y)$$

### `DIM-120` / `EQ-120`: Diversity Component Weights Convex Sum
- ค่าน้ำหนักทั้ง 3 ด้านต้องรวมกันได้ 1.0:
  $$w_{\text{AST}} + w_{\text{Token}} + w_{\text{Behavior}} = 1.0$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D12-01` [Identical AST Zero Distance]:** ตรวจสอบว่า AST 2 ตัวที่เหมือนกันทุกประการ ให้ค่า $d_{\text{AST}} = 0.000000$
2. **Test `TC-D12-02` [Diversity Triangle Inequality]:** สุ่ม AST 3 ตัว ยืนยันว่าเป็นไปตามอสมการสามเหลี่ยม: $d(A, C) \le d(A, B) + d(B, C)$
3. **Test `TC-D12-03` [Deduplication Filter]:** สร้าง Candidate ที่มี Digest ซ้ำกัน 10 ตัว ตรวจสอบว่าถูกกรองเหลือเพียง 1 ตัว
4. **Test `TC-D12-04` [Entropy Computation Accuracy]:** คำนวณ Shannon Entropy บนการกระจายตัวแบบ Uniform ยืนยันว่าได้ค่าสูงสุด $\log_2(K)$
