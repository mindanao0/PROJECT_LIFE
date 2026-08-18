# Domain 25: Threat Vectors, Defense & Automated Quarantine

> **Domain Index:** `DOMAIN-25`  
> **Engineering Scope:** `DIM-241` .. `DIM-250`  
> **Mathematical Equations:** `EQ-241` .. `EQ-250`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 25 กำหนดการสร้างแบบจำลองภัยคุกคาม (Threat Modeling) และขั้นตอนการกักกันผู้ละเมิดอัตโนมัติ (Automated Quarantine Subsystem) เมื่อตรวจพบการโจมตี เช่น Filesystem Traversal, Container Socket Probing, Side-Channel Memory Extraction, Infinite Recursion, หรือ Environment Variable Injection.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-241  │ EQ-241   │ Filesystem Escape Upper Probability Bound │ Pr(Escape(FS)) <= 10^{-15}                                  │
│ DIM-242  │ EQ-242   │ Container Socket Shielding Invariant      │ Stat("/var/run/docker.sock") === ENOENT                     │
│ DIM-243  │ EQ-243   │ Side-Channel Flush Reload Memory Cleaning │ MemZero(Buffer) === 0x00                                    │
│ DIM-244  │ EQ-244   │ Call Stack Exhaustion Recursion Bound     │ StackDepth <= 1000                                          │
│ DIM-245  │ EQ-245   │ Environment Variable Whitelist Filter     │ Env(Sandbox) subseteq {PATH, PYTHONPATH, LANG}              │
│ DIM-246  │ EQ-246   │ Tmpfs Size Exhaustion Hard Ceiling Limit  │ Size(tmpfs) <= 67108864 bytes (64 MB)                       │
│ DIM-247  │ EQ-247   │ Automated Quarantine State Transition     │ Violation ==> State -> QUARANTINED                          │
│ DIM-248  │ EQ-248   │ Security Evidence Snapshot Composite Hash │ H_snapshot = SHA-256(RAM || Stdout || Stderr)               │
│ DIM-249  │ EQ-249   │ Lineage Subtree Disqualification Bound    │ forall c in Descendants(p_malicious), Eligible(c) = False   │
│ DIM-250  │ EQ-250   │ Security Alert Telemetry Emit Latency     │ t_alert <= 100 ms                                           │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-241` / `EQ-241`: Filesystem Escape Upper Probability Bound
- ขอบเขตความน่าจะเป็นที่จะเกิดการหลุดรอดจาก Filesystem Isolation ต้องต่ำกว่า $10^{-15}$:
  $$\Pr(\text{Escape}(\text{FS})) \le 10^{-15}$$

### `DIM-242` / `EQ-242`: Container Socket Shielding Invariant
- ซ่อนและบล็อกการเข้าถึง Docker/Podman Container Sockets ทั้งหมด:
  $$\text{Stat}(\text{"/var/run/docker.sock"}) \equiv \text{ENOENT}$$

### `DIM-243` / `EQ-243`: Side-Channel Flush Reload Memory Cleaning
- เคลียร์หน่วยความจำ Buffer ให้เป็น 0 เพื่อป้องกัน Side-channel Extraction:
  $$\text{MemZero}(\text{Buffer}) \equiv 0\text{x00}$$

### `DIM-244` / `EQ-244`: Call Stack Exhaustion Recursion Bound
- จำกัดความลึกของ Recursion Call Stack ไม่เกิน 1,000 ชั้น:
  $$\text{StackDepth} \le 1000$$

### `DIM-245` / `EQ-245`: Environment Variable Whitelist Filter
- อนุญาตเฉพาะ Environment Variables ที่จำเป็นเท่านั้น:
  $$\text{Env}(\text{Sandbox}) \subseteq \{\text{PATH}, \text{PYTHONPATH}, \text{LANG}\}$$

### `DIM-246` / `EQ-246`: Tmpfs Size Exhaustion Hard Ceiling Limit
- จำกัดขนาด `/tmp` ไม่เกิน 64MB:
  $$\text{Size}(\text{tmpfs}) \le 67108864 \quad \text{bytes (64 MB)}$$

### `DIM-247` / `EQ-247`: Automated Quarantine State Transition
- ทันทีที่เกิด Security Violation ไม่ว่าจาก Static Visitor หรือ Seccomp BPF Candidate จะถูกย้ายเข้าสู่สถานะ `QUARANTINED` และบันทึกลงตาราง `quarantine_records`:
  $$\text{Violation} \implies \text{State} \to \text{QUARANTINED}$$

### `DIM-248` / `EQ-248`: Security Evidence Snapshot Composite Hash
- บันทึก Snapshot ของหลักฐานความผิดพร้อม Hash:
  $$H_{\text{snapshot}} = \text{SHA-256}(\text{RAM} \parallel \text{Stdout} \parallel \text{Stderr})$$

### `DIM-249` / `EQ-249`: Lineage Subtree Disqualification Bound
- ตัดสิทธิ์ลูกหลานทั้งหมดของ Parent ที่มีพฤติกรรมเป็นอันตราย:
  $$\forall c \in \text{Descendants}(p_{\text{malicious}}), \quad \text{Eligible}(c) = \text{False}$$

### `DIM-250` / `EQ-250`: Security Alert Telemetry Emit Latency
- ส่งสัญญาณแจ้งเตือนเหตุการณ์ความปลอดภัยภายในเวลา $\le 100\text{ms}$:
  $$t_{\text{alert}} \le 100\text{ ms}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D25-01` [Shadow File Probe]:** สั่งรันโค้ดเปิด `/etc/shadow` ใน Sandbox ตรวจสอบว่าระบบกักกัน Candidate และสร้าง Quarantine Record
2. **Test `TC-D25-02` [Tmpfs Overflow]:** เขียนไฟล์ 100MB ลง `/tmp` ตรวจสอบว่าติดขีดจำกัด 64MB และไม่กระทบ Host Disk
3. **Test `TC-D25-03` [Environment Variable Leak]:** ส่งโค้ดอ่าน `AWS_SECRET_ACCESS_KEY` ใน Sandbox ตรวจสอบว่ามองไม่เห็นตัวแปรของ Host
4. **Test `TC-D25-04` [Lineage Disqualification]:** กักกัน Candidate สายพันธุ์ A ตรวจสอบว่าลูกหลานของมันถูกตั้งค่า `Eligible = False`
