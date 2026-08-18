# Population Diversity & Tree Edit Distances

> **Subsystem:** Diversity Preservation Science  
> **Authority Level:** NORMATIVE (`REQ-S10-006`)

---

## 1. Normalized Diversity Score Formula

$$\text{DiversityScore}(c, P) = \frac{d_{\text{AST}}(c, P) + d_{\text{Token}}(c, P) + d_{\text{Behavior}}(c, P)}{3}$$

- ค่าคะแนนจะถูก Normalize ให้อยู่ในช่วง $[0, 1]$ เสมอ

---

## 2. Zhang-Shasha AST Tree Edit Distance ($d_{\text{AST}}$)

$$d_{\text{AST}}(T_1, T_2) = \frac{\text{TreeEditDistance}(T_1, T_2)}{\max(|T_1|, |T_2|)}$$

- การดำเนินการบน Node ของ Abstract Syntax Tree ประกอบด้วย:
  - $\text{Cost}(\text{Insert Node}) = 1$
  - $\text{Cost}(\text{Delete Node}) = 1$
  - $\text{Cost}(\text{Relabel Node}) = 1 \text{ (if type mismatch) else } 0$

---

## 3. Normalized Levenshtein Token Distance ($d_{\text{Token}}$)

$$d_{\text{Token}}(S_1, S_2) = \frac{\text{LevenshteinDistance}(\text{tokens}(S_1), \text{tokens}(S_2))}{\max(|\text{tokens}(S_1)|, |\text{tokens}(S_2)|)}$$
