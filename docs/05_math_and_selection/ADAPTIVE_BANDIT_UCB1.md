# Multi-Armed Bandit Dynamic Strategy (UCB1)

> **Subsystem:** Adaptive Mutation Operator Selection  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S09-004`

---

## 1. UCB1 Mathematical Formulation

$$\text{Score}_i(t) = \bar{X}_i + c \sqrt{\frac{\ln N(t)}{n_i(t)}}$$

โดยที่:
- $\bar{X}_i \in [0, 1]$ คือ Reward เฉลี่ยสะสมของ Mutation Operator $i$
- $n_i(t)$ คือ จำนวนครั้งที่ Operator $i$ ถูกเรียกใช้
- $N(t) = \sum_j n_j(t)$ คือ จำนวนการกลายพันธุ์ทั้งหมด
- $c = \sqrt{2} \approx 1.414$ คือ Exploration Parameter

---

## 2. Exploration Floor & Probability Normalization

เพื่อป้องกันไม่ให้กลยุทธ์ใดกลยุทธ์หนึ่งถูกตัดโอกาสจนมีความน่าจะเป็นเป็น 0 ระบบบังคับใช้ **Exploration Floor $\epsilon = 0.05$**:

$$P_i = (1 - K\epsilon) \frac{\text{Score}_i}{\sum_j \text{Score}_j} + \epsilon$$

โดยที่ $K$ คือจำนวน Operator ทั้งหมดที่เปิดใช้งาน ($K = 10$ สำหรับ M01–M10)
