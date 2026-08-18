# 16 — Standard Glossary & Domain Terminology

> **Dimension:** Conceptual Clarity, Ubiquitous Language & Cross-Team Alignment  
> **Target Audience:** All Contributors, Developers, QA Engineers, and Domain Experts

เอกสารฉบับนี้รวบรวมนิยามคำศัพท์เฉพาะทาง (Ubiquitous Language) ของระบบ **Evolution Engine** เพื่อสร้างความเข้าใจที่ตรงกันและขจัดความกำกวมในการสื่อสารและการพัฒนา

---

## 🔤 คำศัพท์เฉพาะทางหมวดหมู่ต่างๆ

### 1. หมวดการวิวัฒนาการและพันธุกรรม (Evolutionary Computation)

| คำศัพท์ (Term) | นิยามความหมาย (Definition) |
|---|---|
| **Candidate (Candidate Program)** | โปรแกรมหรือโค้ดสายพันธุ์หนึ่งที่ถูกสร้างขึ้นจากการกลายพันธุ์เพื่อนำไปทดสอบและวัดผล |
| **Generation** | รอบของการวิวัฒนาการประชากร 1 รุ่น ประกอบด้วยชุดของ Candidates และผลการคัดเลือก |
| **Population** | กลุ่มของ Candidates ทั้งหมดที่อาศัยอยู่ใน Generation เดียวกัน |
| **Mutation (การกลายพันธุ์)** | การปรับเปลี่ยนโครงสร้างไวยากรณ์ (AST) หรือค่าคงที่ของโปรแกรมเดิมอย่างเป็นระบบ |
| **Mutation Strategy** | กลยุทธ์หรือตัวดำเนินการกลายพันธุ์เฉพาะด้าน (เช่น M01 Constant, M02 Operator, M09 Quantum Rotation) |
| **Adaptive Mutation (UCB1)** | การปรับสัดส่วนความถี่ในการเลือก Mutation Strategy อัตโนมัติโดยอิงจากประวัติ Reward ในอดีต |
| **Parent Candidate** | Candidate ต้นแบบที่ถูกนำมาใช้เป็นฐานในการสร้าง Candidate รุ่นถัดไป |
| **Elite Candidate** | Candidate ที่ทำคะแนนได้ดีที่สุดบน Pareto Frontier ซึ่งจะถูกเก็บรักษาไว้ไม่ให้สูญหาย |
| **Lineage Graph** | กราฟแบบ Direct Acyclic Graph (DAG) ที่บันทึกสายสัมพันธ์และประวัติการสืบเชื้อสายของ Candidates |
| **Stagnation** | สภาวะที่ประชากรหยุดพัฒนาอย่างต่อเนื่อง ไม่มีการค้นพบ Candidate ที่ดีขึ้นเกินเกณฑ์ที่กำหนด |

---

### 2. หมวดการวัดผลและคณิตศาสตร์การคัดเลือก (Metrics & Selection)

| คำศัพท์ (Term) | นิยามความหมาย (Definition) |
|---|---|
| **Objective** | มาตรวัดประสิทธิภาพเป้าหมาย (เช่น Latency, Memory, Throughput, Correctness Ratio) |
| **Pareto Dominance ($x \succ y$)** | สภาวะที่ Candidate $x$ ชนะ Candidate $y$ โดยไม่มี Objective ใดที่ $x$ แย่กว่า $y$ และมีอย่างน้อย 1 Objective ที่ $x$ ดีกว่าอย่างเด็ดขาด |
| **Pareto Frontier / Front** | กลุ่มของ Candidates ที่ไม่มี Candidate ตัวอื่นใดในประชากรสามารถเอาชนะ (Dominate) ได้ |
| **Diversity Score** | คะแนนวัดความหลากหลายทางโครงสร้างและพฤติกรรมระหว่าง Candidate กับประชากร $[0, 1]$ |
| **Preference Score** | คะแนนรวมอรรถประโยชน์ (Normalized Utility) ถ่วงน้ำหนักด้วย Preference Weight สำหรับใช้ตัดสินเฉพาะกรณีเสมอกันบน Pareto Front เดียวกัน |
| **Practical Margin** | ส่วนต่างขั้นต่ำของค่า Metric ที่ถือว่ามีนัยสำคัญในทางปฏิบัติจริง |
| **Welch's t-test** | สถิติทดสอบความแตกต่างของค่าเฉลี่ย 2 กลุ่มโดยไม่สมมติว่าความแปรปรวนเท่ากัน |
| **TOST (Two One-Sided Tests)** | สถิติทดสอบเพื่อพิสูจน์ว่าประสิทธิภาพของ Candidate เทียบเท่า (Equivalent) หรือไม่แย่ลงกว่า Baseline |
| **Holm-Bonferroni Correction** | กระบวนการปรับแก้ $p$-value เมื่อทดสอบสมมติฐานหลายตัวพร้อมกันเพื่อควบคุม Family-Wise Error Rate |

---

### 3. หมวดความปลอดภัยและการกักกัน (Sandbox & Security)

| คำศัพท์ (Term) | นิยามความหมาย (Definition) |
|---|---|
| **Sandbox (PROFILE_A_LINUX)** | สภาพแวดล้อมจำลองการรันโค้ดที่แยกกระบวนการอย่างเข้มงวดด้วย Linux Namespaces, cgroups v2 และ Seccomp |
| **Unprivileged Identity** | การรัน Process ด้วยสิทธิ์ผู้ใช้ทั่วไปที่ไม่ใช่ Root (`uid != 0`, `gid != 0`) |
| **Seccomp BPF** | กลไกของ Linux Kernel ในการกรองและบล็อก System Calls อันตราย |
| **Quarantine (การกักกัน)** | การแยก Candidate ที่มีความพยายามละเมิดความปลอดภัยของ Sandbox ออกจากกระบวนการวิวัฒนาการทันที |
| **EE-CRYPTO-1** | มาตรฐานโปรไฟล์ลายเซ็นดิจิทัล Ed25519 ร่วมกับ SHA-256 สำหรับอนุมัติการ Deploy และ Self-Evolution |
| **Multisig Quorum** | การลงนามร่วมโดยกุญแจที่ได้รับอนุญาตอย่างน้อย 2 ใน 3 ดอก (2-of-3 Ed25519) |

---

### 4. หมวดการจัดเก็บและข้อมูล (Storage & Persistence)

| คำศัพท์ (Term) | นิยามความหมาย (Definition) |
|---|---|
| **CAS (Content-Addressed Storage)** | ระบบจัดเก็บไฟล์ที่ใช้ SHA-256 Hash ของเนื้อหาไฟล์เป็นชื่อและตำแหน่งจัดเก็บ ทำให้ไฟล์เป็น Immutable |
| **Audit Hash Chain** | บันทึกประวัติเหตุการณ์การทำงานแบบโซ่แฮชต่อเนื่อง (Cryptographic Hash Chain) ป้องกันการแก้ไขประวัติย้อนหลัง |
| **Generation Manifest** | ไฟล์ JSON สรุปสถานะ Candidates, Hashes, และผลการตัดสินใจทั้งหมดในแต่ละรุ่น |
| **Checkpoint** | จุดบันทึกสถานะชั่วคราวลงใน CAS และ Database เพื่อรองรับการกู้คืนระบบหลังเครื่องดับ |
| **Single-Writer Coordinator** | สถาปัตยกรรมที่กำหนดให้ Coordinator Node เป็นผู้เขียนข้อมูลลง SQLite และ CAS เพียงรายเดียวเพื่อตัดปัญหา Data Race |

---

### 5. หมวดความสามารถขั้นสูง (Advanced Paradigms)

| คำศัพท์ (Term) | นิยามความหมาย (Definition) |
|---|---|
| **Qubit Representation** | การแทนสถานะความน่าจะเป็นของยีนในการกลายพันธุ์ด้วย Quantum Bit Vector $[\alpha, \beta]^T$ |
| **Quantum Rotation Gate** | เมทริกซ์การหมุนเวกเตอร์ความน่าจะเป็นเพื่อปรับสมดุลระหว่าง Exploration และ Exploitation |
| **Universal AST (UAST)** | โครงสร้างไวยากรณ์กลางที่ใช้เชื่อมโยงการแปลงโค้ดระหว่างภาษา Python และ Native Languages (Rust/C++) |
| **P2P Swarm Topology** | เครือข่ายแบบกระจายศูนย์ที่เชื่อมโยงหลายโหนดเข้าด้วยกันเพื่อแลกเปลี่ยน Pareto Elite ข้ามเครื่อง |
| **ALife Co-Evolution** | การจำลองระบบนิเวศระหว่าง Prey (Candidate Programs) และ Predator (Adversarial Test Generators) |
| **Niche Specialization** | การแบ่งพื้นที่วิวัฒนาการออกเป็นกลุ่มเฉพาะด้านเพื่อป้องกันการผูกขาดของสายพันธุ์เดียว |
