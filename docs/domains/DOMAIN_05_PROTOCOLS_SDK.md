# Domain 05: Architecture Protocols & Public SDK Surfaces

> **Domain Index:** `DOMAIN-05`  
> **Engineering Scope:** `DIM-041` .. `DIM-050`  
> **Mathematical Equations:** `EQ-041` .. `EQ-050`  
> **Authority Level:** NORMATIVE MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 05 กำหนดสัญญาอินเทอร์เฟซเชิงสถาปัตยกรรม (Architecture Protocols) ผ่าน **22 Typed Python Protocols (`typing.Protocol`)**, พื้นผิว SDK สาธารณะ (Class `EvolutionEngine`), คำสั่ง CLI `evolve`, และการส่งออกผลลัพธ์ผ่าน Structured JSON Envelopes.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-041  │ EQ-041   │ Typed Python Protocol Package Soundness   │ S <= T ==> forall x: S, P(x) ==> P(x: T)                    │
│ DIM-042  │ EQ-042   │ SourceAnalyzer Linear Parse Complexity    │ C_parse(B) = O(|B|)                                         │
│ DIM-043  │ EQ-043   │ Mutation Strategy Protocol Formal Mapping │ M: AST x N -> AST' x Delta                                  │
│ DIM-044  │ EQ-044   │ Sandbox Manager Security Boundary Metric  │ Pr(Escape(Sandbox)) <= 2^{-128}                             │
│ DIM-045  │ EQ-045   │ Pareto Selector Monotonic Cardinality     │ |Select(P, K)| = K <= |P|                                   │
│ DIM-046  │ EQ-046   │ SDK State Method Idempotency Invariant    │ SDK.pause(R) = PAUSED ==> SDK.pause(R) = PAUSED             │
│ DIM-047  │ EQ-047   │ CLI Exit Code Discrete Mapping Function   │ ExitCode(e) = I(e != empty) * (1 + CodeID(e))               │
│ DIM-048  │ EQ-048   │ JSON Output stdout Envelope Completeness  │ stdout = JSON({"status": s, "data": d, "error": e})         │
│ DIM-049  │ EQ-049   │ Strict Argv Array Parameter Enforcement   │ Exec(vec{A}) ==> ShellExecution = False                     │
│ DIM-050  │ EQ-050   │ Public SDK Asyncio Throughput Scaling     │ T_async = (N_tasks / sum tau_i) * P_concurrency             │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-041` / `EQ-041`: Typed Python Protocol Package Soundness
- **Requirement:** โมดูลทั้ง 22 ตัวในระบบต้องสื่อสารกันผ่าน `typing.Protocol` ที่มีการระบุ Type Hints แบบ Strict (MyPy/Pyright Pass 100%)
- **Mathematical Form (Liskov Substitution Principle):**
  $$S \le T \implies \forall x: S, \quad P(x) \implies P(x: T)$$

### `DIM-042` / `EQ-042`: SourceAnalyzer Linear Parse Complexity
- การสแกนโค้ดต้องใช้เวลาเชิงเส้นตรงเทียบกับขนาดไบต์ของซอร์สโค้ด:
  $$C_{\text{parse}}(B) = \mathcal{O}(|B|)$$

### `DIM-043` / `EQ-043`: Mutation Strategy Protocol Formal Mapping
- ทุก Mutation Strategy ต้องสอดคล้องกับ Protocol Signature:
  $$\mathcal{M}: \text{AST} \times \mathbb{N} \longrightarrow \text{AST}' \times \Delta_{\text{metadata}}$$

### `DIM-044` / `EQ-044`: Sandbox Manager Security Boundary Metric
- ความน่าจะเป็นที่ Sandbox Manager จะปล่อยให้ Process หลุดรอดขอบเขตต้องต่ำกว่า $2^{-128}$:
  $$\Pr(\text{Escape}(\text{Sandbox})) \le 2^{-128}$$

### `DIM-045` / `EQ-045`: Pareto Selector Monotonic Cardinality
- ฟังก์ชันการคัดเลือก Pareto ต้องคืนค่าจำนวน Candidates เท่ากับ $K$ เสมอ (หากประชากรมี $\ge K$):
  $$|\text{Select}(P, K)| = K \le |P|$$

### `DIM-046` / `EQ-046`: SDK State Method Idempotency Invariant
- การเรียกใช้เมธอดสถานะซ้ำๆ ต้องคงสถานะเดิมเสมอ:
  $$\text{SDK}.\text{pause}(R) = \text{PAUSED} \implies \text{SDK}.\text{pause}(R) = \text{PAUSED}$$

### `DIM-047` / `EQ-047`: CLI Exit Code Discrete Mapping Function
- รหัส Exit Code ของ CLI ต้องถูกแมปอย่างแน่นอนกับชนิด Error:
  $$\text{ExitCode}(e) = \mathbb{I}(e \ne \emptyset) \cdot (1 + \text{CodeID}(e))$$

### `DIM-048` / `EQ-048`: JSON Output stdout Envelope Completeness
- ทุกคำสั่งของ CLI เมื่อใส่แฟล็ก `--json` ต้องส่งออก Envelope โครงสร้างมาตรฐาน:
  $$\text{stdout} = \text{JSON}(\{\text{"status"}: s, \text{"data"}: d, \text{"error"}: e\})$$

### `DIM-049` / `EQ-049`: Strict Argv Array Parameter Enforcement
- **Requirement:** การเรียกใช้ Process ใน Sandbox ต้องส่ง Arguments ผ่าน Vector Array $\vec{A} = [a_0, a_1, \dots, a_k]$ โดยห้ามใช้ Shell String Concatenation (`shell=False`) เด็ดขาดเพื่อขจัดช่องโหว่ Shell Injection:
  $$\text{Exec}(\vec{A}) \implies \text{ShellExecution} = \text{False}$$

### `DIM-050` / `EQ-050`: Public SDK Asyncio Throughput Scaling
- การประมวลผลงานแบบ Asynchronous ของ SDK สเกลตามจำนวน Concurrency:
  $$T_{\text{async}} = \frac{N_{\text{tasks}}}{\sum_{i=1}^{N} \tau_i} \cdot P_{\text{concurrency}}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D05-01` [Strict Type Checking]:** รัน `mypy --strict` บน Protocol Package ทั้ง 22 ตัว ต้องไม่มี Type Error แม้แต่จุดเดียว
2. **Test `TC-D05-02` [CLI JSON Envelope]:** รันคำสั่ง `evolve validate --json` ตรวจสอบว่า stdout สามารถถูก Parse เป็น JSON ตาม Schema ได้อย่างถูกต้อง
3. **Test `TC-D05-03` [SDK Method Idempotency]:** เรียก `engine.pause()` สองครั้งติดต่อกัน ยืนยันว่าคืนค่า `PAUSED` ทั้งสองครั้ง
4. **Test `TC-D05-04` [Argv Array Injection Attack]:** ส่งคำสั่งที่มี `"; rm -rf /"` ใน Argument ตัวที่สอง ยืนยันว่าถูกส่งเป็น Argument ตัวอักษรธรรมดาและไม่ถูกรันโดยเชลล์
