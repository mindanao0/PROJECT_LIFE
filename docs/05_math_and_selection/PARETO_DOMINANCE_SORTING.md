# Multi-Objective Pareto Dominance & Fast Sorting ($O(MN^2)$)

> **Subsystem:** Multi-Objective Pareto Selection  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S10-001` .. `REQ-S10-005`

---

## 1. Formal Pareto Dominance Definition

กำหนดให้ $x, y \in \mathcal{P}$ เป็น Candidate 2 ตัว และมี $M$ วัตถุประสงค์ (Objectives) $f_1, f_2, \dots, f_M$:

Candidate $x$ **ชนะแบบครอบงำ (Dominates)** Candidate $y$ (สัญลักษณ์ $x \succ y$) ก็ต่อเมื่อ:

$$\forall i \in \{1, \dots, M\}, \quad f_i(x) \succeq f_i(y) \quad \land \quad \exists j \in \{1, \dots, M\}, \quad f_j(x) \succ f_j(y)$$

โดยที่:
- สำหรับ **`maximize`**: $a \succeq b \iff a \ge b$ และ $a \succ b \iff a > b$
- สำหรับ **`minimize`**: $a \succeq b \iff a \le b$ และ $a \succ b \iff a < b$

---

## 2. Fast Non-Dominated Sorting Algorithm

```python
def fast_non_dominated_sort(population: list, objectives: list) -> list[list]:
    """
    จัดกลุ่มประชากรออกเป็นลำดับชั้น Pareto Fronts: F_1, F_2, F_3, ...
    ความซับซ้อนของการประมวลผล: O(M * N^2)
    """
    fronts: list[list] = [[]]
    domination_count: dict = {}      # n_p: จำนวน candidate ที่ dominate p
    dominated_candidates: dict = {}  # S_p: รายชื่อ candidate ที่ p ไป dominate

    for p in population:
        domination_count[p] = 0
        dominated_candidates[p] = []
        for q in population:
            if dominates(p, q, objectives):
                dominated_candidates[p].append(q)
            elif dominates(q, p, objectives):
                domination_count[p] += 1

        # หากไม่มีใคร dominate p แสดงว่า p อยู่บน Front ที่ 1 (F_1)
        if domination_count[p] == 0:
            p.pareto_rank = 1
            fronts[0].append(p)

    i = 0
    while len(fronts[i]) > 0:
        next_front = []
        for p in fronts[i]:
            for q in dominated_candidates[p]:
                domination_count[q] -= 1
                if domination_count[q] == 0:
                    q.pareto_rank = i + 2
                    next_front.append(q)
        i += 1
        fronts.append(next_front)

    return [f for f in fronts if len(f) > 0]
```
