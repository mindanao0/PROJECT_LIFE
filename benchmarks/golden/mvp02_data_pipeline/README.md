# Benchmark Case MVP-02: Data Pipeline Engine

> **Case ID:** `MVP-02`  
> **Project Type:** Multi-File Batch Data Processing Pipeline  
> **Primary Objective:** Maximize Item Processing Throughput (items/sec)  
> **Target Speedup:** $\ge 2.0\times$  
> **Allowed Mutations:** `M05` (Standard Lib), `M06` (Pure Extract), `M07` (Inlining), `M08` (Data Structures)

---

## 1. Workload Description
ไปป์ไลน์ประมวลผลข้อมูล JSON และ CSV หลายไฟล์ที่มีลูปวนซ้ำขนาดใหญ่ การวิวัฒนาการเน้นการแปลง `list` สู่ `deque`/`set`, การแปลงลูปเป็น Generator Expressions, และการ Inlining ฟังก์ชัน Helper.

## 2. Oracle Verification Rules
- ข้อมูล Output Dataset หลังประมวลผลต้องมี Schema และค่าถูกต้องตรงกับ Baseline 100%
