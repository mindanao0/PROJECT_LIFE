# Domain 01: Offline-First & Determinism Foundations

> **Domain Index:** `DOMAIN-01`  
> **Engineering Scope:** `DIM-001` .. `DIM-010`  
> **Mathematical Equations:** `EQ-001` .. `EQ-010`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 01 กำหนดรากฐานของระบบ **Evolution Engine** ในด้านความสามารถในการทำงานแบบตัดขาดจากเครือข่ายภายนอก 100% (Air-Gapped Operation), ความสามารถในการสืบทอด Pseudo-RNG Seed ไปยังทุกกระบวนการกลายพันธุ์, การเข้ารหัสตรวจสอบความสมบูรณ์แบบไม่สูญเสียความแม่นยำ (Lossless Canonical Hashing & Serialization), และการรับประกันความสามารถในการ Replay ผลลัพธ์ซ้ำบิตต่อบิต (`R4 Reproducibility`).

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-001  │ EQ-001   │ Air-Gap Network Independence              │ I(Engine; External_Network) = 0 bits                        │
│ DIM-002  │ EQ-002   │ Deterministic Seed Recurrence             │ S_{t+1} = (a S_t + c) mod m                                 │
│ DIM-003  │ EQ-003   │ Canonical SHA-256 Digest Computation      │ H^{(i)} = f(H^{(i-1)}, M_i), H in {0, 1}^256                │
│ DIM-004  │ EQ-004   │ Unicode NFC Normalization Invariant       │ NFC(NFC(S)) = NFC(S)                                        │
│ DIM-005  │ EQ-005   │ RFC3339 UTC Monotonic Timestamps          │ t_1 < t_2 <=> FormatUTC(t_1) <_lex FormatUTC(t_2)           │
│ DIM-006  │ EQ-006   │ Exact Canonical Decimal String Format     │ d = (-1)^s x m x 10^e, m in Z^+, e in Z                     │
│ DIM-007  │ EQ-007   │ Lossless Canonical JSON Lexicographical   │ KeyOrder(K_1, K_2) = strcmp(K_1, K_2)                       │
│ DIM-008  │ EQ-008   │ Bit-Identical Replay Metric (R4 Level)    │ Pr(Digest(Run_1) = Digest(Run_2) | Seed) = 1.0              │
│ DIM-009  │ EQ-009   │ FSM Logical Transition Determinism (R1)   │ S_FSM(Run_1) === S_FSM(Run_2)                               │
│ DIM-010  │ EQ-010   │ Hardware & Kernel Environment Digest      │ H_env = SHA-256(Kernel || CPU_Arch || Python_Version)       │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-001` / `EQ-001`: Air-Gap Network Independence
- **Requirement:** Core evolution loop ต้องทำงานได้โดยปราศจากการเปิด Network Socket ใดๆ ไปยัง External Gateway
- **Mathematical Form:** ข้อมูลสารสนเทศร่วม (Mutual Information) ระหว่าง Engine State และ External Internet ต้องเป็นศูนย์สมบูรณ์:
  $$I(\text{Engine}; \text{External\_Network}) = 0 \quad \text{bits}$$
- **Kernel Enforcement:** ในขั้นตอน Provision Sandbox สำหรับ Worker ทุกตัว ระบบจะตัด Interface ทั้งหมดยกเว้น `lo` (Loopback) และตั้งค่า `ip link set lo down` ภายใน Network Namespace

### `DIM-002` / `EQ-002`: Deterministic Seed Recurrence
- **Requirement:** การสุ่มทุกจุดในระบบ (การเลือกโหนด AST, การปรับค่าคงที่, การกลายพันธุ์ M01–M10) ต้องถูกคำนวณผ่าน Deterministic PRNG Stream ที่สืบทอดมาจาก Master Seed เพียงตัวเดียว
- **Mathematical Form (64-bit PCG/LCG Generator):**
  $$S_{t+1} = (a S_t + c) \pmod m, \quad a=6364136223846793005, \quad c=1442695040888963407, \quad m=2^{64}$$
- **Sub-seed Branching:** ทุก Generation $g$ และ Candidate $k$ จะได้รับ Sub-seed: $S_{g, k} = \text{SHA-256}(S_{\text{master}} \parallel g \parallel k)$

### `DIM-003` / `EQ-003`: Canonical SHA-256 Digest Computation
- **Requirement:** ทุกไฟล์ซอร์สโค้ด, Payload, และ Artifact ต้องถูกระบุตัวตนด้วย SHA-256 Hash Digest แบบ 64-character lowercase hex string:
  $$H^{(i)} = f(H^{(i-1)}, M_i), \qquad H \in \{0, 1\}^{256}$$
- **Zero Ambiguity:** ป้องกันการปะปนของข้อมูลและการเปลี่ยนแปลงโค้ดโดยไม่ได้รับอนุญาต

### `DIM-004` / `EQ-004`: Unicode NFC Normalization Invariant
- **Requirement:** สตริงโค้ดและชื่อตัวระบุทั้งหมดต้องผ่าน Unicode Normalization Form C (NFC) ก่อนการ Parse และก่อนการคำนวณ Hash:
  $$\text{NFC}(\text{NFC}(S)) \equiv \text{NFC}(S)$$
- **Invariant:** ป้องกันกรณีที่สตริงเดียวกันแต่มี Codepoints ต่างกัน (เช่น precomposed vs decomposed characters) ก่อให้เกิด Hash Mismatch

### `DIM-005` / `EQ-005`: RFC3339 UTC Monotonic Timestamps
- **Requirement:** ค่าเวลาทั้งหมดในระบบต้องบันทึกเป็นสตริง RFC3339 UTC ตามด้วย `Z` เสมอ (เช่น `2026-08-18T15:00:00.000000Z`):
  $$t_1 < t_2 \iff \text{FormatUTC}(t_1) <_{\text{lex}} \text{FormatUTC}(t_2)$$
- **Monotonicity:** การเรียงลำดับสตริงตามตัวอักษร (Lexicographical Order) ต้องตรงกับการเรียงลำดับเวลาทางกายภาพ 100%

### `DIM-006` / `EQ-006`: Exact Canonical Decimal String Format
- **Requirement:** ห้ามใช้ IEEE 754 Binary Floating Point ในการ Serialize ข้อมูลสถิติ, น้ำหนัก Preference หรือคะแนนลงใน Checkpoint และ Manifest เด็ดขาด เพื่อป้องกันความคลาดเคลื่อนข้าม CPU Architecture (x86_64 vs ARM64)
- **Format Standard:** บังคับใช้สตริงทศนิยมมาตรฐาน (เช่น `"0.125000"`) ที่ระบุ Scale และ Precision ชัดเจน:
  $$d = (-1)^s \times m \times 10^e, \quad s \in \{0, 1\}, \quad m \in \mathbb{Z}^+, \quad e \in \mathbb{Z}$$

### `DIM-007` / `EQ-007`: Lossless Canonical JSON Lexicographical
- **Requirement:** การแปลง Python Dictionary เป็น JSON String ใน Manifest และ CAS Payloads ต้องจัดเรียง Keys แบบ Lexicographical Ascending (`sort_keys=True`) และตัด Whitespace ส่วนเกิน:
  $$\text{KeyOrder}(K_1, K_2) = \text{strcmp}(K_1, K_2)$$

### `DIM-008` / `EQ-008`: Bit-Identical Replay Metric (R4 Level)
- **Requirement:** เมื่อสั่ง Replay Run เดิมด้วย Master Seed เดียวกัน บน Environment เดียวกัน ผลลัพธ์ของ Generation Manifest และ Source Files ต้องตรงกันบิตต่อบิต 100%:
  $$\Pr(\text{Digest}(\text{Run}_1) = \text{Digest}(\text{Run}_2) \mid \text{Seed}) = 1.0$$

### `DIM-009` / `EQ-009`: FSM Logical Transition Determinism (R1 Level)
- **Requirement:** ลำดับการเปลี่ยนสถานะของ Finite State Machines ทั้ง 5 ตัว ต้องมีลำดับขั้นตอนเดียวกันเป๊ะในทุกรอบการประมวลผล:
  $$\vec{S}_{\text{FSM}}(\text{Run}_1) \equiv \vec{S}_{\text{FSM}}(\text{Run}_2)$$

### `DIM-010` / `EQ-010`: Hardware & Kernel Environment Digest
- **Requirement:** ทุก Run Manifest ต้องบันทึก Digest ของสภาพแวดล้อมที่ใช้ประมวลผล:
  $$H_{\text{env}} = \text{SHA-256}(\text{Kernel\_Release} \parallel \text{CPU\_Model} \parallel \text{CPython\_Version} \parallel \text{Compiler\_Flags})$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D01-01` [Replay Determinism R4]:** รันการวิวัฒนาการ MVP-01 จำนวน 10 Generations ซ้ำกัน 5 ครั้งด้วย Master Seed `42` ทุก Run ต้องให้ SHA-256 Digest ของ Final Generation Manifest ตรงกันบิตต่อบิต 100%
2. **Test `TC-D01-02` [Air-gap Network Probe]:** สแกน System Call Table ภายใน Sandbox ระหว่างรัน ยืนยันว่าไม่มีการเรียก `connect()`, `sendto()`, หรือ `recvfrom()` ไปยัง IP ภายนอกแม้แต่ครั้งเดียว
3. **Test `TC-D01-03` [Unicode NFC Idempotency]:** ป้อนสตริงภาษาต่างๆ (เช่น ภาษาไทย, ฟรังก์เซส, อีโมจิ) ตรวจสอบว่า `NFC(NFC(S)) == NFC(S)` และคำนวณ Digest ได้ตรงกัน 100%
4. **Test `TC-D01-04` [Decimal Serialization Match]:** สุ่มทศนิยม 1,000 ค่า ตรวจสอบว่าการแปลงไป-มาระหว่าง `Decimal` และ Canonical String ไม่มีการสูญเสียความแม่นยำ
