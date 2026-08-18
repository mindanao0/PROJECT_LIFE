# Domain 19: Long-Term Hippocampal Memory Replay

> **Domain Index:** `DOMAIN-19`  
> **Engineering Scope:** `DIM-181` .. `DIM-190`  
> **Mathematical Equations:** `EQ-181` .. `EQ-190`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 19 กำหนดระบบจัดเก็บและดึงความจำการกลายพันธุ์ระยะยาว (Long-Term Hippocampal Memory) โดยใช้ **AST Subtree Fingerprinting**, **Cosine Similarity Vector Retrieval**, **Prioritized Experience Replay Sampling**, และ **Negative Memory Bloom Filters**.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-181  │ EQ-181   │ Memory Record Persistence Invariant Form  │ M = <H_pattern, vec{v}_embed, bar{R}, t_created>            │
│ DIM-182  │ EQ-182   │ AST Subtree Pattern Fingerprinting Hash   │ H_pattern = SHA-256(CanonicalAST(Subtree))                  │
│ DIM-183  │ EQ-183   │ Cross-Run Transfer Learning Weight Decay  │ W_transfer = exp(-alpha * Delta t_runs)                     │
│ DIM-184  │ EQ-184   │ Cosine Similarity Vector Retrieval Metric │ Sim(vec{u}, vec{v}) = (vec{u} . vec{v}) / (||u|| * ||v||)   │
│ DIM-185  │ EQ-185   │ Memory Forgetting Temporal Exponential    │ R(t) = R_0 * exp(-lambda_forget * t)                        │
│ DIM-186  │ EQ-186   │ Replay Buffer Priority Sampling Density   │ P(i) = p_i^alpha / sum p_k^alpha, p_i = |delta_i| + eps     │
│ DIM-187  │ EQ-187   │ Negative Quarantine Bloom Filter Bound    │ Pr(FalsePositive) <= (1 - e^{-kn/m})^k <= 0.001             │
│ DIM-188  │ EQ-188   │ LRU Memory Eviction Policy Boundary Limit │ |M| <= M_max = 10,000                                       │
│ DIM-189  │ EQ-189   │ Immutable Memory Checkpoint Digest Hash   │ H_mem = SHA-256(product_{m in M} H_m)                       │
│ DIM-190  │ EQ-190   │ Cross-Project Jaccard Knowledge Sharing   │ J(A, B) = |A intersect B| / |A union B|                     │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-181` / `EQ-181`: Memory Record Persistence Invariant Form
- โครงสร้าง Tuple ของบันทึกความจำระยะยาว:
  $$M = \langle H_{\text{pattern}}, \vec{v}_{\text{embedding}}, \bar{R}, t_{\text{created}} \rangle$$

### `DIM-182` / `EQ-182`: AST Subtree Pattern Fingerprinting Hash
- การทำ Fingerprint ของโครงสร้าง AST Subtree:
  $$H_{\text{pattern}} = \text{SHA-256}(\text{CanonicalAST}(\text{Subtree}))$$

### `DIM-183` / `EQ-183`: Cross-Run Transfer Learning Weight Decay
- น้ำหนักความรู้ข้าม Run ลดลงตามเวลา:
  $$W_{\text{transfer}} = \exp(-\alpha \cdot \Delta t_{\text{runs}})$$

### `DIM-184` / `EQ-184`: Cosine Similarity Vector Retrieval
- การค้นหารูปแบบโครงสร้างโค้ดที่เคยปรับปรุงสำเร็จในอดีต:
  $$\text{Sim}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}$$

### `DIM-185` / `EQ-185`: Memory Forgetting Temporal Exponential
- การลบเลือนความจำที่ไม่ได้ใช้งานนาน:
  $$R(t) = R_0 \cdot \exp(-\lambda_{\text{forget}} t)$$

### `DIM-186` / `EQ-186`: Replay Buffer Priority Sampling Density
- การสุ่มดึงความจำตามขนาดผลตอบแทนที่เคยทำได้:
  $$P(i) = \frac{p_i^\alpha}{\sum_k p_k^\alpha}, \qquad p_i = |\delta_i| + \epsilon$$

### `DIM-187` / `EQ-187`: Negative Memory Bloom Filter
- ใช้กรองโครงสร้างโค้ดที่เคยทำให้เกิด Crash เพื่อหลีกเลี่ยงการสุ่มซ้ำ:
  $$\Pr(\text{FalsePositive}) \le (1 - e^{-kn/m})^k \le 0.001$$

### `DIM-188` / `EQ-188`: LRU Memory Eviction Policy Boundary Limit
- จำกัดจำนวนรายการความจำไม่เกิน 10,000 รายการ:
  $$|M| \le M_{\max} = 10,000$$

### `DIM-189` / `EQ-189`: Immutable Memory Checkpoint Digest Hash
- ตรวจสอบความถูกต้องของ Checkpoint ความจำด้วย SHA-256:
  $$H_{\text{mem}} = \text{SHA-256}\left(\prod_{m \in M} H_m\right)$$

### `DIM-190` / `EQ-190`: Cross-Project Jaccard Knowledge Sharing
- การประเมินความสอดคล้องของโครงสร้างระหว่าง 2 โปรเจกต์:
  $$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D19-01` [Pattern Retrieval Accuracy]:** ค้นหา AST Subtree ที่ใกล้เคียงกัน ยืนยันว่าคืนค่า Top-1 ตรงกับความคาดหมาย
2. **Test `TC-D19-02` [Bloom Filter Rejection]:** ตรวจสอบว่าโครงสร้างใน Negative Memory ถูก Reject ตั้งแต่ขั้นตอน Mutation Strategy
3. **Test `TC-D19-03` [LRU Eviction Limit]:** ใส่ข้อมูล 10,001 รายการ ตรวจสอบว่ารายการที่เก่าสุดถูก Evict ออกไป
4. **Test `TC-D19-04` [Priority Sampling Bias]:** ทดสอบว่า Sample ที่มี Reward สูงถูกสุ่มเลือกบ่อยกว่าอย่างมีนัยสำคัญ
