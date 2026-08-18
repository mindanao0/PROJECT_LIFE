# Benchmark Case MVP-12: ALife Co-Evolutionary Ecosystem

> **Case ID:** `MVP-12`  
> **Project Type:** Predator-Prey Ecological Simulation  
> **Primary Objective:** Maximize Co-evolutionary Strategy Fitness  
> **Target Speedup:** $\ge 2.5\times$ Cycle Throughput  
> **Allowed Mutations:** `M01`, `M02`, `M04`, `M08`

---

## 1. Workload Description
การจำลองปฏิสัมพันธ์ระหว่างสิ่งมีชีวิต 2 ชนิด (ผู้ล่าและเหยื่อ) 1,000 ประชากร โดยใช้สมการ Lotka-Volterra Differential Equations.

## 2. Oracle Verification Rules
- ระบบนิเวศต้องไม่เกิด Extinction Cascade ภายใน 100 รอบจำลอง และสมดุลประชากรต้องคงตัว
