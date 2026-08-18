# 05 — Metrics, Statistics, Multi-Objective Pareto, P2P Swarm & ALife Ecosystems

> **Active Requirements Covered:** `REQ-S10-001` .. `REQ-S10-010`, `REQ-S11-001` .. `REQ-S11-002` (Unified v1 Full Scope)  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Not normative.  
> **Canonical source:** [`docs/05_math_and_selection/`](./05_math_and_selection/) — เมื่อขัดกัน ให้ยึดฝั่งนั้น

Evolution Engine v1 รวมกลไกการคัดเลือกแบบหลายมิติ (**Pareto Selection**), การกระจายการประมวลผลแบบฝูง (**Distributed P2P Swarm**), และการจำลองระบบนิเวศชีวิตประดิษฐ์ (**Artificial-Life Ecosystem Co-evolution**) เข้าเป็นแกนหลักของการค้นหา

---

## 1. Metric Definition & Validation Rules

นิยามของ Metric แต่ละตัวใน `evolution.yaml`:
- `name`: ชื่อมาตรวัด (เช่น `throughput_ops`, `latency_ms`, `memory_peak_bytes`)
- `direction`: `maximize` หรือ `minimize`
- `unit`: หน่วยวัด
- `valid_range`: ช่วงค่าที่ยอมรับได้ (`minimum_decimal`, `maximum_decimal`)
- `practical_margin_decimal`: ส่วนต่างขั้นต่ำที่ถือว่ามีความหมายในทางปฏิบัติ
- `failure_policy`: การจัดการเมื่อวัดผลไม่ได้ (เช่น `invalidate_candidate`)
- `preference_weight_decimal`: น้ำหนักความสำคัญสำหรับใช้ตัดสินกรณีเสมอกันบน Pareto front เดียวกัน

---

## 2. Statistical Testing & Multiple Comparison Correction

### 2.1 Difference vs Equivalence Testing
- **[REQ-S10-002] Welch-style Difference Test:** ใช้ตรวจจับความต่างระหว่าง Candidate กับ Baseline ($H_0: \mu_{\text{cand}} = \mu_{\text{base}}$)
- **[REQ-S10-003] TOST (Two One-Sided Tests):** ใช้พิสูจน์ความเทียบเท่าหรือการไม่ถดถอยเกินขอบเขตที่ยอมรับได้ ($\Delta_{\text{margin}}$):
  $$H_{01}: \mu_{\text{cand}} - \mu_{\text{base}} \le -\Delta \quad \text{or} \quad H_{02}: \mu_{\text{cand}} - \mu_{\text{base}} \ge +\Delta$$
- **[REQ-S10-004]** **ห้ามใช้ $p < \alpha$ จาก Difference test เป็นหลักฐานของความเทียบเท่า (Equivalence)**

### 2.2 Holm-Bonferroni Multi-Testing Correction
เมื่อมีการเปรียบเทียบ Candidate หลายตัวกับ Baseline พร้อมกัน เพื่อควบคุม Family-Wise Error Rate (FWER):
1. เรียงลำดับ $p$-values จากน้อยไปมาก: $p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$
2. สำหรับ $k = 1, \dots, m$: ตรวจสอบเงื่อนไข:
   $$p_{(k)} \le \frac{\alpha}{m - k + 1}$$

---

## 3. Canonical Pareto & Diversity Selection Pipeline

ลำดับการคัดเลือก Candidate เข้าสู่ Generation ถัดไป (Deterministic 5-Step Pipeline):

```text
1. Eligibility Verification (ผ่าน Policy, Security, Test, Capability, Oracle)
      │
      ▼
2. Pareto Dominance Ranking (พิจารณาทุก Objective พร้อมกันโดยไม่ใช้ Weight)
      │
      ▼
3. Diversity Score (คัดเลือก Candidate ที่กระจายตัวสูงสุดใน Front เดียวกัน)
      │
      ▼
4. Preference Score (ใช้ Preference Weight เฉพาะกรณีที่ Rank และ Diversity เสมอกัน)
      │
      ▼
5. Canonical Candidate ID (Lexicographical order สำหรับ Deterministic Replay)
```

### 3.1 Diversity Score Formula
$$\text{DiversityScore} = \frac{\text{ASTDistance} + \text{TokenDistance} + \text{BehavioralDistance}}{3}$$

### 3.2 Metric Preference Score Formula (Normalized Utility)
- สำหรับ **`maximize`**: $\text{utility}_i = \text{clamp}\left(\frac{\text{estimate}_i - \min_i}{\max_i - \min_i}, 0, 1\right)$
- สำหรับ **`minimize`**: $\text{utility}_i = 1 - \text{clamp}\left(\frac{\text{estimate}_i - \min_i}{\max_i - \min_i}, 0, 1\right)$

$$\text{PreferenceScore} = \sum_{i} (\text{preference\_weight}_i \times \text{utility}_i)$$

---

## 4. Artificial-Life (ALife) Ecosystem Co-Evolution

เพื่อเร่งการค้นหา Candidate ที่ทนทาน ระบบจำลองระบบนิเวศชีวิตประดิษฐ์ (Co-evolutionary ALife Dynamics):

```text
┌─────────────────────────────────────────────────────────────┐
│                    ALIFE ECOSYSTEM DYNAMICS                 │
├─────────────────────────────────────────────────────────────┤
│  1. Prey Population (Candidate Programs):                   │
│     • มุ่งเน้นการปรับปรุงประสิทธิภาพและผ่าน Test Cases      │
│     • ได้รับพลังงาน (Energy Credits) เมื่อทำ Pareto Score สูง│
│                                                             │
│  2. Predator Population (Adversarial Test Generators):      │
│     • มุ่งเน้นสร้าง Edge Cases, Worst-case Inputs           │
│     • ได้รับพลังงานเมื่อค้นพบ Input ที่ทำให้ Candidate ช้าลง  │
│                                                             │
│  3. Niche Specialization (Environmental Niches):            │
│     • แบ่งพื้นที่ค้นหาออกเป็น Niche ย่อย (เช่น Memory Niche,│
│       CPU Latency Niche, Concurrency Niche) ป้องกันการแย่งชิง│
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Distributed P2P Evolutionary Swarm & Island Topology

เมื่อรันระบบบนหลายเครื่องข่าย (Multi-Node Clusters / Swarm):

```text
┌──────────────┐     Gossip Migration     ┌──────────────┐
│ Island Node A├─────────────────────────►│ Island Node B│
│ (Population) │◄─────────────────────────┤ (Population) │
└──────┬───────┘   Pareto Elite Exchange  └──────┬───────┘
       │                                         │
       │           ┌──────────────┐              │
       └──────────►│ Island Node C│◄─────────────┘
                   │ (Population) │
                   └──────────────┘
```

1. **Island Topology:** แต่ละ Node รัน Evolution Loop ของตัวเองอย่างอิสระ
2. **Periodic Elite Migration:** ทุกๆ $M_{\text{interval}}$ Generations (เช่น ทุก 10 Gens) Node จะส่ง Candidate ที่อยู่บน **Pareto Front ลำดับที่ 1** ไปแลกเปลี่ยนกับโหนดข้างเคียง
3. **Byzantine Fault-Tolerant Verification:** โหนดผู้รับจะนำ Candidate ที่ได้รับมา Re-verify ใน Sandbox ของตัวเองก่อนอนุญาตให้เข้าสู่ประชากร ป้องกันปัญหา Malicious Node Injection

---

## 6. Evolutionary Stagnation Detection & Escalation Ladder

หากประชากรไม่มีการปรับปรุง Pareto Front ต่อเนื่องเกิน $G_{\text{stagnant}}$ Generations:
- **Level 1 (5 Gens):** เพิ่ม Mutation Temperature (เพิ่ม Mutation Rate $\mu: 0.05 \to 0.20$)
- **Level 2 (10 Gens):** กระตุ้น Hyper-Mutation Mode สุ่มเปลี่ยนโครงสร้าง AST แบบวงกว้าง
- **Level 3 (15 Gens):** ฉีด Candidate จาก Long-term Memory (Hippocampal Replay)
- **Level 4 (20 Gens):** ตัดประชากร 50% และฉีดสายพันธุ์สุ่มใหม่ข้ามเกาะ (Cataclysmic Re-seeding)
