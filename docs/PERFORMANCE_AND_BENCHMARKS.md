# 14 — Performance Envelopes & Engine Benchmark Targets

> **Dimension:** Performance Engineering, Capacity Planning & Benchmarking  
> **Target Audience:** Performance Engineers and Core Developers

เอกสารฉบับนี้กำหนดกรอบงบประมาณประสิทธิภาพ (Performance Budget) และขอบเขตการใช้ทรัพยากร (Overhead Envelopes) ของตัว Evolution Engine เอง เพื่อให้มั่นใจว่าการวิวัฒนาการทำงานได้อย่างรวดเร็วและไม่สร้าง Overhead ที่ไม่จำเป็น

---

## 1. Engine Overhead Performance Budgets

ในการรันแต่ละ Candidate ตัว Engine ต้องทำงานให้เสร็จภายในกรอบเวลาและทรัพยากรที่กำหนด:

| การทำงานของ Engine (Subsystem) | เวลาเป้าหมาย (P50) | เวลาสูงสุดที่ยอมรับได้ (P99) | เกณฑ์การวัด (Unit) |
|---|:---:|:---:|:---:|
| **AST Parse & Tree Construction** | $< 2.0\text{ ms}$ | $< 5.0\text{ ms}$ | ต่อไฟล์ขนาด $\le 50\text{ KB}$ |
| **AST Safety Invariant Check** | $< 1.0\text{ ms}$ | $< 3.0\text{ ms}$ | ต่อ Candidate AST |
| **Mutation Operator Execution** | $< 0.5\text{ ms}$ | $< 2.0\text{ ms}$ | ต่อ Mutation Attempt |
| **Sandbox Environment Provisioning** | $< 3.0\text{ ms}$ | $< 15.0\text{ ms}$ | Native Namespaces + Mount |
| **SQLite Generation Commit** | $< 10.0\text{ ms}$ | $< 50.0\text{ ms}$ | ต่อ 20 Candidates Batch |
| **CAS fsync & Atomic Write** | $< 5.0\text{ ms}$ | $< 20.0\text{ ms}$ | ต่อ Artifact $\le 1\text{ MB}$ |
| **Pareto Sorting ($N=50, M=3$)** | $< 1.0\text{ ms}$ | $< 5.0\text{ ms}$ | ต่อ Generation Selection |

---

## 2. Resource Footprint & Scalability Ceilings

### Coordinator Node Footprint:
- **Maximum Memory (RAM):** $\le 256\text{ MB}$ สำหรับประชากร 1,000 Candidates Active ในหน่วยความจำ
- **Disk Space Overhead (DB Metadata):** $\le 2\text{ MB}$ ต่อ 100 Generations (ไม่รวม Source Blobs ใน CAS)
- **CPU Coordinator Utilization:** $\le 5\%$ ของ 1 CPU Core (เวลาส่วนใหญ่เป็น I/O และรอมอบหมายงานให้ Worker)

### Worker Sandbox Limits (Per Worker Instance):
- **CPU Quota:** ควบคุมผ่าน `cpu.max` ใน cgroups v2 (Default: 1.0 Core ต่อ Worker)
- **Memory Limit:** ควบคุมผ่าน `memory.max` ใน cgroups v2 (Default: 512MB ต่อ Worker)
- **Temporary Disk Quota:** ควบคุมผ่าน `tmpfs size` (Default: 64MB ต่อ Worker)
- **PID Limit:** ควบคุมผ่าน `pids.max` (Default: 64 PIDs ป้องกัน Fork Bomb)

---

## 3. Scalability Limits & Design Capacities

| มิติ (Dimension) | ขีดจำกัดที่รองรับ (Design Ceiling) | พฤติกรรมเมื่อเกินขีดจำกัด |
|---|:---:|---|
| **Population Size per Generation** | สูงสุด $500$ Candidates | ปฏิเสธในตอน Validate Config |
| **Max Generations per Run** | สูงสุด $10,000$ Generations | บังคับจบ Run ด้วยสถานะ `COMPLETED` |
| **Max Source Files in Target Project** | สูงสุด $2,000$ Python Files | แจ้งเตือน Large Project Warning |
| **Max AST Nodes per Target Function** | สูงสุด $50,000$ Nodes | ข้ามฟังก์ชันขนาดใหญ่เกินเกณฑ์ |
| **Max Metrics per Project** | สูงสุด $10$ Objectives | ปฏิเสธในตอน Validate Config |

---

## 4. Benchmark Verification Protocol for Releases

ก่อนที่ Engine จะผ่านการ Release ในแต่ละเวอร์ชัน ต้องผ่านการทดสอบ Benchmark 3 ระดับ:

1. **Micro-benchmarks:** ทดสอบความเร็วของ AST Visitor, Canonical JSON Serializer, และ Database WAL Commit
2. **End-to-End Synthetic Benchmarks (MVP-01 .. MVP-05):** ตรวจสอบว่ารอบการทำงานตั้งแต่สร้างจนคัดเลือกเสร็จสิ้นภายในเวลาที่กำหนด
3. **Stress & Endurance Benchmarks:** รันต่อเนื่อง 1,000 Generations โดยไม่มี Memory Leak และขนาด Database โตขึ้นในอัตราเชิงเส้น ($O(N)$)
