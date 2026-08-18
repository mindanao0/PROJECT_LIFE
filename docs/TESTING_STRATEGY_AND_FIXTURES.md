# 17 — Comprehensive Testing Strategy & Fixture Matrix

> **Dimension:** Quality Assurance, Test Automation & Formal Verification  
> **Target Audience:** QA Engineers, Test Automation Specialists, and Core Developers

เอกสารฉบับนี้กำหนดกรอบกลยุทธ์การทดสอบ 7 ระดับ (7-Tier Testing Strategy) พร้อมรายชื่อ Test Suites, Property-Based Testing Rules, และ Negative Security Corpus เพื่อการันตีความทนทานและความถูกต้องของ Evolution Engine

---

## 🏗️ 7-Tier Testing Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│ Level 7: Golden Test Corpus Conformance (MVP-01 .. MVP-14)  │
├─────────────────────────────────────────────────────────────┤
│ Level 6: Crash Recovery & CAS Reconciliation Tests          │
├─────────────────────────────────────────────────────────────┤
│ Level 5: Negative Security & Sandbox Attack Vectors         │
├─────────────────────────────────────────────────────────────┤
│ Level 4: FSM Reachability & Illegal Transition Tests        │
├─────────────────────────────────────────────────────────────┤
│ Level 3: Property-Based Testing (Hypothesis PBT)            │
├─────────────────────────────────────────────────────────────┤
│ Level 2: Schema & Fixture Meta-Validation (Draft 2020-12)   │
├─────────────────────────────────────────────────────────────┤
│ Level 1: Unit & AST Visitor Determinism Tests               │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Level 1 & 2: Unit & Schema Meta-Validation

- **Unit Tests (`tests/unit/`):**
  - ทดสอบ AST Transformer แต่ละตัว (M01 ถึง M10) ว่าผลิตโค้ดที่ถูกต้องทางไวยากรณ์
  - ทดสอบ Canonical Serializer ว่าจัดเรียง Keys และแปลง RFC3339 UTC timestamps ถูกต้อง
- **Schema Meta-Validation (`tests/schema/`):**
  - ทุกไฟล์ใน `schemas/*.schema.json` (26 ไฟล์) ต้องผ่าน Meta-schema Draft 2020-12
  - ทุก Schema ต้องมีอย่างน้อย 1 `valid/*.json` fixture ที่ผ่าน และ 3 `invalid/*.json` fixtures ที่ถูก reject

---

## 2. Level 3: Property-Based Testing (PBT via Hypothesis)

การใช้ Hypothesis เพื่อสุ่ม Generate ข้อมูลทดสอบตาม Invariants:

```python
from hypothesis import given, strategies as st

# Invariant 1: Canonical Decimal Serializer Roundtrip
@given(st.decimals(min_value=-1e12, max_value=1e12, places=6))
def test_decimal_string_canonical_roundtrip(d):
    d_str = canonical_decimal_serialize(d)
    assert canonical_decimal_deserialize(d_str) == d

# Invariant 2: Pareto Dominance Asymmetry
@given(st.lists(st.floats(allow_nan=False), min_size=2, max_size=5))
def test_pareto_dominance_asymmetry(metrics_a, metrics_b):
    a_dom_b = dominates(metrics_a, metrics_b)
    b_dom_a = dominates(metrics_b, metrics_a)
    assert not (a_dom_b and b_dom_a), "Pareto dominance must be strictly asymmetric!"
```

---

## 3. Level 4: FSM Reachability & Illegal Transition Tests

ทดสอบ State Machines ทั้ง 5 ตัว (Candidate, Run, Recovery, Governance, Deployment):
1. **Reachability Test:** ยืนยันว่าทุก State สามารถเดินทางไปถึงได้จาก Initial State
2. **Deadlock Test:** ยืนยันว่าไม่มี Non-terminal State ใดที่ไม่มีทางออก (Outgoing transitions $> 0$)
3. **Illegal Transition Rejection:** ทดสอบการยิง Transition ที่ไม่อนุญาต (เช่น `CREATED` $\rightarrow$ `EXECUTING` โดยไม่ผ่าน Validation) ต้องถูก Reject ด้วย Exception และบันทึก Audit Event

---

## 4. Level 5: Negative Security Corpus (`tests/security/`)

ชุดทดสอบการเจาะระบบเพื่อทดสอบความแข็งแกร่งของ Sandbox PROFILE_A_LINUX:

| Test Fixture | พฤติกรรมที่ทดสอบ (Attack Vector) | ผลลัพธ์ที่คาดหวัง |
|---|---|:---:|
| `sec_01_fs_escape.py` | พยายามอ่าน `/etc/shadow`, `~/.ssh/id_rsa`, `/proc/kcore` | `QUARANTINED` |
| `sec_02_net_connect.py` | พยายามสร้าง TCP Socket เชื่อมต่อไปยัง IP ภายนอก | `QUARANTINED` |
| `sec_03_fork_bomb.py` | พยายามรัน `while True: os.fork()` ไม่สิ้นสุด | `QUARANTINED` / `REJECTED` |
| `sec_04_ptrace_attach.py`| พยายามสั่ง `ptrace` เกาะ Process อื่นบน Host | `QUARANTINED` |
| `sec_05_tmp_exhaust.py` | พยายามเขียนไฟล์ลง `/tmp` เกิน 64MB Quota | `REJECTED: OOM/DISK` |

---

## 5. Level 6: Crash Recovery & CAS Reconciliation Tests

การจำลองเซิร์ฟเวอร์ดับระหว่างการทำงานเพื่อทดสอบ Recovery State Machine:

```text
จุดที่ทำการ Inject Crash:
1. Crash ขณะเขียน CAS Temp File (ก่อน Fsync)  -> ผลลัพธ์: ทิ้ง Temp file และเริ่มใหม่
2. Crash หลัง CAS Durable แต่ก่อน DB Commit    -> ผลลัพธ์: Rollback SQLite Transaction
3. Crash ขณะ Commit SQLite Transaction        -> ผลลัพธ์: Reconstruct Manifest จาก CAS
4. Crash หลัง Commit Generation Manifest       -> ผลลัพธ์: Idempotent Resume ทันที
```

---

## 6. Level 7: Golden Test Corpus Conformance (MVP-01 .. MVP-14)

รันชุดทดสอบความถูกต้องสมบูรณ์แบบ End-to-End กับ 14 Golden Projects:
- ตรวจสอบว่า `baseline_hash` ตรงกับค่าจริงที่ประกาศไว้
- ตรวจสอบว่าการ Replay ด้วย Seed เดิมให้ผลลัพธ์แบบ Bit-Identical (`R4 Reproducibility`)
- ตรวจสอบว่า Audit Hash Chain มีความต่อเนื่องตั้งแต่ Genesis จนถึง Release Event
