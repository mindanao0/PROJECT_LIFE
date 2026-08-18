# Benchmark Case MVP-03: REST API Service

> **Case ID:** `MVP-03`  
> **Project Type:** Asynchronous Microservice (FastAPI/Aiohttp)  
> **Primary Objective:** Minimize HTTP P99 Request Latency  
> **Target Speedup:** $\ge 1.8\times$  
> **Allowed Mutations:** `M01`, `M02`, `M07`, `M08` (Async Invariant Enforced)

---

## 1. Workload Description
เว็บเซอร์วิสแบบ Asynchronous ที่รับคำขอ HTTP และดึงข้อมูล JSON จากหน่วยความจำ การวิวัฒนาการต้องรักษาคำสั่ง `await` ไม่ให้กลายเป็น Blocking Code (ตามกฎ `DIM-057`).

## 2. Oracle Verification Rules
- ผ่าน Integration Tests และคืนค่า HTTP Status Code 200 พร้อม JSON Payload ที่ตรงกัน
