# PROFILE_A_LINUX Security Specification & Conformance Matrix

> **Subsystem:** Hardened OS-Level Sandbox Baseline  
> **Authority Level:** NORMATIVE (`REQ-S12-001` .. `REQ-S12-020`)

---

## 1. Supported Linux Kernel Conformance Matrix

| Lane | Linux Kernel Line | Sandbox Backend | Architecture | Required Purpose |
|---|---|---|---|---|
| **A1** | Linux 6.1 LTS | Native Namespaces + cgroups v2 + Seccomp | x86_64 | Oldest supported baseline |
| **A2** | Linux 6.6 LTS | Rootless OCI Reference Backend (`runc`) | x86_64 | Container compatibility |
| **A3** | Linux 6.12 LTS | Native Namespaces + cgroups v2 + Seccomp | x86_64 | Newer LTS baseline |
| **A4** | Linux 6.18 LTS | Rootless OCI Reference Backend (`runc`) | x86_64 | Current LTS baseline |

---

## 2. Invariants & Security Baseline

1. **Linux-Only Normative Evidence [REQ-S12-001]:** หลักฐาน Release Evidence ที่ผ่านการรับรองความปลอดภัย ต้องถูกสร้างบน **`PROFILE_A`** บน Linux Kernel เท่านั้น
2. **Unprivileged Identity:** Candidate Process ทั้งหมดต้องรันด้วยสิทธิ์ Unprivileged UID/GID (`uid != 0`, `gid != 0`)
3. **No Network Access:** ห้ามเชื่อมต่อเครือข่ายภายนอก (Network Namespace Loopback Down)
4. **Kernel Monkeypatch Rejection [REQ-S12-003]:** Python socket monkeypatch ไม่ถือเป็น Security Boundary ต้องตัดขาดในระดับ Kernel
