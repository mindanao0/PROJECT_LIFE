# Benchmark Case MVP-04: Memory Graph Engine

> **Case ID:** `MVP-04`  
> **Project Type:** In-Memory Directed Graph Engine  
> **Primary Objective:** Minimize Peak RAM Footprint (MB)  
> **Target Speedup:** $\ge 1.4\times$ Memory Reduction  
> **Allowed Mutations:** `M06` (Pure Extract), `M08` (Data Structure Optimizer)

---

## 1. Workload Description
เอนจินค้นหากราฟในหน่วยความจำ (BFS/DFS/Shortest Path) บนโหนด 100,000 โหนด การวิวัฒนาการเน้นการปรับใช้ Adjacency List ที่ประหยัดหน่วยความจำ และหลีกเลี่ยงการสร้าง Cyclic Reference.

## 2. Oracle Verification Rules
- เส้นทางสั้นที่สุดและผลลัพธ์ Topological Sort ต้องถูกต้องตรงกับกราฟอ้างอิง
