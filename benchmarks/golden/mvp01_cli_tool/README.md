# Benchmark Case MVP-01: CLI Text Utility

> **Case ID:** `MVP-01`  
> **Project Type:** Single-File CLI Tool  
> **Primary Objective:** Reduce P99 Startup and Command Latency  
> **Target Speedup:** $\ge 1.5\times$  
> **Allowed Mutations:** `M01` (Constants), `M02` (Operators), `M03` (Boundaries)

---

## 1. Workload Description
โปรเจกต์เครื่องมือ Command Line ตัวเดี่ยวที่ใช้ Argument Parsing และ Regular Expressions ในการค้นหาและแปลงข้อความขนาดใหญ่ การวิวัฒนาการเน้นการปรับแต่ง Regex Compilation Flag, การจัดสรร Buffer และการลดการค้นหาซ้ำซ้อน.

## 2. Oracle Verification Rules
- ต้องผ่าน Unit Tests ใน `tests/test_cli.py` 100%
- Exit code และผลลัพธ์ stdout ต้องตรงกับ Baseline ดั้งเดิมทุกตัวอักษร
