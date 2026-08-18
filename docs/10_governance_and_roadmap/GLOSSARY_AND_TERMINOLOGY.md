# Ubiquitous Domain Terminology & Glossary

> **Subsystem:** Standard System Vocabulary & Cross-Team Alignment  
> **Authority Level:** NORMATIVE MASTER GLOSSARY

---

## 1. Domain Terminology Dictionary

```text
┌────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ คำศัพท์ (Term)             │ นิยามความหมายทางเทคนิค (Technical Definition)                          │
├────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Candidate                  │ โปรแกรมหรือโค้ดสายพันธุ์หนึ่งที่ถูกสร้างขึ้นจากการกลายพันธุ์เพื่อทดสอบ  │
│ Generation                 │ รอบของการวิวัฒนาการประชากร 1 รุ่น ประกอบด้วยชุด Candidate และผลการวัด  │
│ Population                 │ กลุ่มของ Candidates ทั้งหมดที่อาศัยอยู่ใน Generation เดียวกัน          │
│ Pareto Dominance (x ≻ y)   │ สภาวะที่ Candidate x ไม่แย่กว่า y ในทุกเป้าหมาย และดีกว่าในอย่างน้อย 1  │
│ Pareto Frontier            │ กลุ่มของ Candidates ที่ไม่มี Candidate ตัวอื่นใดสามารถเอาชนะได้        │
│ Diversity Score            │ คะแนนวัดความหลากหลายทางพันธุกรรมและพฤติกรรม Normalized ในช่วง [0, 1]   │
│ Preference Score           │ คะแนนอรรถประโยชน์รวมสำหรับใช้ตัดสินเสมอกันบน Pareto Front เดียวกัน    │
│ Practical Margin (Δ)       │ ส่วนต่างขั้นต่ำของค่า Metric ที่ถือว่ามีนัยสำคัญในทางปฏิบัติ           │
│ TOST                       │ Two One-Sided Tests สำหรับพิสูจน์ความไม่ถดถอยของประสิทธิภาพเทียบ Baseline│
│ UCB1                       │ Upper Confidence Bound 1 อัลกอริทึมจัดสรรสัดส่วน Mutation อัตโนมัติ    │
│ Qubit Vector               │ เวกเตอร์ความน่าจะเป็น [α, β]^T สำหรับแทนสถานะของยีนในการกลายพันธุ์      │
│ Universal AST (UAST)       │ โครงสร้างไวยากรณ์กลางสำหรับแปลงโค้ดข้ามภาษาระหว่าง Python และ Native   │
│ Single-Writer Coordinator  │ สถาปัตยกรรมที่ให้โหนดกลางเป็นผู้เขียน SQLite และ CAS เพียงรายเดียว    │
│ CAS                        │ Content-Addressed Storage ระบบจัดเก็บไฟล์ที่ใช้ SHA-256 เป็นชื่อไฟล์   │
│ PROFILE_A_LINUX            │ มาตรฐานความปลอดภัยสูงสุดบน Linux (Namespaces, cgroups v2, Seccomp)     │
│ EE-CRYPTO-1                │ โปรไฟล์ลายเซ็นดิจิทัล Ed25519 ร่วมกับ SHA-256 และ Multisig Quorum 2-of-3│
│ Quarantine                 │ การตัดสิทธิ์และกักกัน Candidate ที่พยายามละเมิด Sandbox ทันที          │
│ Flaky Test                 │ การทดสอบที่ให้ผล PASS/FAIL สลับไปมาบน Candidate เดิมโดยไม่มีการแก้โค้ด │
│ Traceability Matrix        │ ตารางผูกโยง Requirement ID เข้ากับโค้ดจริงและชุดทดสอบแบบอัตโนมัติ      │
└────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```
