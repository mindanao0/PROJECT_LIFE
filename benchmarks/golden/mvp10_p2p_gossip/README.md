# Benchmark Case MVP-10: P2P Gossip Swarm Node

> **Case ID:** `MVP-10`  
> **Project Type:** Distributed P2P Gossip Node  
> **Primary Objective:** Minimize Network Bandwidth Usage (KB) per Consensus Round  
> **Target Speedup:** $\ge 1.6\times$ Bandwidth Efficiency  
> **Allowed Mutations:** `M05`, `M07`, `M08`

---

## 1. Workload Description
โหนดเครือข่าย P2P ที่แลกเปลี่ยนข้อความผ่าน Epidemic Gossip Protocol ภายใต้สภาพแวดล้อม 50 โหนดจำลอง การวิวัฒนาการเน้นการบีบอัด Message Payload และการกรอง Duplicate Message ID ด้วย Bloom Filter.

## 2. Oracle Verification Rules
- ข้อมูลต้องกระจายครบทุกโหนด (Consensus Reached) ภายใต้ทฤษฎี Byzantine Fault Tolerance ($N \ge 3f + 1$)
