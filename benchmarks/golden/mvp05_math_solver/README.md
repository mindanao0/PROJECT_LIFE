# Benchmark Case MVP-05: Mathematical Solver

> **Case ID:** `MVP-05`  
> **Project Type:** Numerical Linear Algebra & Optimization Solver  
> **Primary Objective:** Minimize Solver Computation Time (ms)  
> **Target Speedup:** $\ge 3.0\times$  
> **Allowed Mutations:** `M01`, `M02`, `M05`, `M07`

---

## 1. Workload Description
การคำนวณแก้สมการเมทริกซ์และ Floating-Point Algorithms การวิวัฒนาการเน้นการจัดรูปสมการพีชคณิตเพื่อลดจำนวนการคูณ และการใช้ Builtin Vectorized Helpers.

## 2. Oracle Verification Rules
- ผ่าน Hypothesis Property-Based Testing บนตัวเลขสุ่ม 1,000 ชุด โดยมี Relative Error $\le 10^{-6}$
