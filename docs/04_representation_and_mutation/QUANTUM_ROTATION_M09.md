# Quantum Rotation Gate Mutation Operator Specification (M09)

> **Authority Level:** NORMATIVE COMPILER SPECIFICATION (L4 Authority)  
> **Target Subsystem:** Quantum-Inspired Mutation Pipeline  
> **Governing Equations:** `EQ-141` .. `EQ-150` (Quantum Probability & Annealing Schedule)

---

## 1. Mathematical Theory & Qubit Chromosome Encoding

ตัวดำเนินการ **M09 (Quantum-Inspired Mutation)** แปลงการแสดงข้อมูลของ Candidate ให้อยู่ในรูปของ **Qubit Chromosome** ความยาว $L$:
$$Q = [q_1, q_2, \dots, q_L], \qquad q_j = \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}, \qquad |\alpha_j|^2 + |\beta_j|^2 = 1$$
- $|\alpha_j|^2$: ความน่าจะเป็นที่จะคงโหนด AST ดั้งเดิมไว้ ($0$)
- $|\beta_j|^2$: ความน่าจะเป็นที่จะกระตุ้นการกลายพันธุ์ในตำแหน่ง $j$ ($1$)

---

## 2. Quantum Rotation Gate Operator $\mathbf{R}(\Delta \theta)$

การอัปเดตสถานะของ Qubit ในแต่ละรอบจะกระทำผ่าน Rotation Gate Matrix:
$$\begin{bmatrix} \alpha_j(t+1) \\ \beta_j(t+1) \end{bmatrix} = \begin{bmatrix} \cos(\Delta \theta_j) & -\sin(\Delta \theta_j) \\ \sin(\Delta \theta_j) & \cos(\Delta \theta_j) \end{bmatrix} \begin{bmatrix} \alpha_j(t) \\ \beta_j(t) \end{bmatrix}$$

### 2.1 Dynamic Annealing Schedule & Decay
ขนาดของมุมหมุนจะค่อยๆ ลดลงตาม Generation:
$$\Delta \theta_j(t) = \text{sgn}(\text{Best}_j - \text{Current}_j) \cdot \theta_0 \cdot \exp\left(-\gamma \cdot \frac{t}{T_{\max}}\right)$$
โดยกำหนด $\theta_0 = 0.05 \pi$, $\gamma = 2.0$, และ $T_{\max} = G_{\max}$

---

## 3. Superposition Measurement Collapse & AST Mapping

การสร้าง Candidate Concrete โค้ดจะกระทำผ่านการวัด (Measurement Collapse):
$$x_j = \begin{cases} 1 & \text{if } r_j < |\beta_j|^2 \quad (r_j \sim \text{PRNG}(S_{\text{quantum}})) \\ 0 & \text{otherwise} \end{cases}$$
เมื่อ $x_j = 1$ โหนด AST ณ ตำแหน่ง $j$ จะถูกแทนที่ด้วย Candidate Subtree ที่สร้างขึ้นใหม่
