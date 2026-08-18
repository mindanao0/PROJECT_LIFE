# Benchmark Case MVP-13: AST Architectural Refactoring

> **Case ID:** `MVP-13`  
> **Project Type:** Code Refactoring & Inlining Suite  
> **Primary Objective:** Maximize Execution Speed while keeping Structural Delta $\le 15\%$  
> **Target Speedup:** $\ge 1.7\times$  
> **Allowed Mutations:** `M05`, `M06`, `M07`

---

## 1. Workload Description
การปรับโครงสร้างซอร์สโค้ดระดับสถาปัตยกรรม (Architectural Inlining, Pure Function Extraction) โดยรักษารูปแบบโค้ดให้อ่านง่าย และขนาดการเปลี่ยนแปลง AST Delta ต่ำกว่า 15%.

## 2. Oracle Verification Rules
- Public API และ Unit Tests ทั้งหมดต้องผ่าน และ Tree Edit Distance ต้องเป็นไปตามโควต้า
