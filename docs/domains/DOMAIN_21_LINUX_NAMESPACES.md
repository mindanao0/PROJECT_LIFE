# Domain 21: PROFILE_A_LINUX Kernel Namespaces Isolation

> **Domain Index:** `DOMAIN-21`  
> **Engineering Scope:** `DIM-201` .. `DIM-210`  
> **Mathematical Equations:** `EQ-201` .. `EQ-210`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 21 กำหนดมาตรฐานความปลอดภัยระดับเคอร์เนลลีนุกซ์ **`PROFILE_A_LINUX`** ครอบคลุมการแยก 5 Mandatory Namespaces (User, Mount, PID, Net, IPC), การตัดสิทธิ์ Capabilities (`CapEff = 0`), และการล็อกบิต `no_new_privs`.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-201  │ EQ-201   │ User Namespace Unprivileged UID Mapping   │ map: uid_sandbox |-> uid_unprivileged != 0                  │
│ DIM-202  │ EQ-202   │ Mount Namespace Read-Only Isolation       │ MountFlags(CodeRoot) land MS_RDONLY === MS_RDONLY           │
│ DIM-203  │ EQ-203   │ PID Namespace Host Process Shielding      │ MaxPID(Sandbox) <= 64 << PID_host                           │
│ DIM-204  │ EQ-204   │ Net Namespace Zero Egress Loopback Down   │ Interfaces(NetNS) \ {lo} = empty                            │
│ DIM-205  │ EQ-205   │ IPC Namespace Memory Isolation Invariant  │ SharedMem(Sandbox) intersect SharedMem(Host) = empty        │
│ DIM-206  │ EQ-206   │ UTS Namespace Hostname Masking Constant   │ Hostname(Sandbox) === "sandbox"                             │
│ DIM-207  │ EQ-207   │ Cgroup Namespace Virtualization Root      │ CgroupRoot(Sandbox) === "/evolution/candidate"              │
│ DIM-208  │ EQ-208   │ Strict No New Privileges Bit Enforcement  │ prctl(PR_SET_NO_NEW_PRIVS, 1) = 0                           │
│ DIM-209  │ EQ-209   │ Drop All Linux Effective Capabilities     │ CapEff === 0x0000000000000000                               │
│ DIM-210  │ EQ-210   │ Rootless OCI Reference Runtime Exit Bound │ ExitStatus(runc) in [0, 255]                                │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-201` / `EQ-201`: User Namespace Unprivileged Mapping
- แมป UID ของ Process ภายใน Sandbox เข้ากับ Unprivileged UID นอก Sandbox เพื่อป้องกัน Root Privilege Escalation:
  $$\text{map}: \text{uid}_{\text{sandbox}} \mapsto \text{uid}_{\text{unprivileged}} \ne 0$$

### `DIM-202` / `EQ-202`: Mount Namespace Read-Only Isolation
- ซอร์สโค้ดและไลบรารีระบบถูกเมานต์เป็น Read-Only (`MS_RDONLY`):
  $$\text{MountFlags}(\text{CodeRoot}) \land \text{MS\_RDONLY} \equiv \text{MS\_RDONLY}$$

### `DIM-203` / `EQ-203`: PID Namespace Host Process Shielding
- แยก PID Namespace ทำให้มองไม่เห็น Process อื่นบน Host:
  $$\text{MaxPID}(\text{Sandbox}) \le 64 \ll \text{PID}_{\text{host}}$$

### `DIM-204` / `EQ-204`: Net Namespace Zero Egress Loopback Down
- ตัด Network Interfaces ทั้งหมดทิ้ง:
  $$\text{Interfaces}(\text{NetNS}) \setminus \{\text{lo}\} = \emptyset$$

### `DIM-205` / `EQ-205`: IPC Namespace Memory Isolation Invariant
- ห้ามแชร์ Shared Memory Segment ข้าม Sandbox:
  $$\text{SharedMem}(\text{Sandbox}) \cap \text{SharedMem}(\text{Host}) = \emptyset$$

### `DIM-206` / `EQ-206`: UTS Namespace Hostname Masking Constant
- ซ่อน Hostname ที่แท้จริงของเครื่อง Host:
  $$\text{Hostname}(\text{Sandbox}) \equiv \text{"sandbox"}$$

### `DIM-207` / `EQ-207`: Cgroup Namespace Virtualization Root
- Virtualize Cgroup Root Path:
  $$\text{CgroupRoot}(\text{Sandbox}) \equiv \text{"/evolution/candidate"}$$

### `DIM-208` / `EQ-208`: Strict No New Privileges Bit Enforcement
- ล็อกบิตป้องกันการยกระดับสิทธิ์ผ่าน setuid/setgid:
  $$\text{prctl}(\text{PR\_SET\_NO\_NEW\_PRIVS}, 1) = 0$$

### `DIM-209` / `EQ-209`: Drop All Linux Effective Capabilities
- ตัดสิทธิ์ Linux Capabilities ทั้งหมดทิ้ง:
  $$\text{CapEff} \equiv 0\text{x0000000000000000}, \quad \text{CapPrm} \equiv 0\text{x0000000000000000}$$

### `DIM-210` / `EQ-210`: Rootless OCI Reference Runtime Exit Bound
- รองรับการรันผ่าน Rootless OCI Runtime (`runc`/`crun`):
  $$\text{ExitStatus}(\text{runc}) \in [0, 255]$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D21-01` [Capability Probe]:** อ่าน `/proc/self/status` ภายใน Sandbox ตรวจสอบว่า `CapEff` เป็น 0 ทั้งหมด
2. **Test `TC-D21-02` [Network Egress Denial]:** สั่งเปิด Socket ภายใน Sandbox ยืนยันว่าคืนค่า `Network is unreachable`
3. **Test `TC-D21-03` [Mount Read-Only Enforcement]:** พยายามเขียนไฟล์ลงใน Code Mount ตรวจสอบว่าได้ Error `Read-only file system`
4. **Test `TC-D21-04` [PID Shielding Check]:** รัน `ps aux` ภายใน Sandbox ยืนยันว่าเห็นเฉพาะ PID ใน Sandbox เท่านั้น
