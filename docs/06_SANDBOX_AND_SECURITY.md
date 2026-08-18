# 06 — Hardened Sandbox Isolation, Seccomp & Security Policy

> **Active Requirements Covered:** `REQ-S12-001` .. `REQ-S12-020`, `REQ-S20-001`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Not normative.  
> **Canonical source:** [`docs/06_security_and_sandboxing/`](./06_security_and_sandboxing/) — เมื่อขัดกัน ให้ยึดฝั่งนั้น

Evolution Engine มีหน้าที่ประเมินและรัน Candidate Programs ซึ่งอาจมีบั๊ก การกินทรัพยากรไม่สิ้นสุด (Infinite Loop / Fork Bomb) หรือมีโค้ดอันตราย ดังนั้นการรัน Candidate ทุกตัวจะต้องกระทำใน **Hardened Isolation Boundary** ที่รัดกุมในระดับ OS Kernel

---

## 1. Security Baseline Matrix & Linux Conformance Lanes

```text
Linux   PROFILE_A  Full supported security baseline (Mandatory for Release Evidence)
macOS   PROFILE_C  Development-only limited isolation (Local testing only)
Windows PROFILE_D  Unsupported for secure candidate execution
```

- **[REQ-S12-001]** หลักฐาน Release Evidence ที่ผ่านการรับรองความปลอดภัย ต้องรันบน **`PROFILE_A`** เท่านั้น

### PROFILE_A Linux Conformance Lanes:
| Lane | Linux Kernel Line | Sandbox Backend | Architecture | Required Purpose |
|---|---|---|---|---|
| **A1** | Linux 6.1 LTS | Native Namespaces + cgroups v2 + Seccomp | x86_64 | Oldest supported baseline |
| **A2** | Linux 6.6 LTS | Rootless OCI Reference Backend (`runc`) | x86_64 | Container compatibility |
| **A3** | Linux 6.12 LTS | Native Namespaces + cgroups v2 + Seccomp | x86_64 | Newer LTS baseline |
| **A4** | Linux 6.18 LTS | Rootless OCI Reference Backend (`runc`) | x86_64 | Current LTS baseline |

---

## 2. PROFILE_A_LINUX Invariants

ทุก Candidate Process ที่รันใน Linux Sandbox ต้องถูกบังคับใช้กฎต่อไปนี้:

1. **Unprivileged Execution:** รันด้วยสิทธิ์ Unprivileged User (`uid != 0`, `gid != 0`)
2. **Linux Namespaces (เต็มรูปแบบ):**
   - `User Namespace`
   - `Mount Namespace` (แยก Root Filesystem)
   - `PID Namespace` (ซ่อน Process อื่นบน Host)
   - `Network Namespace` (Loopback down / ห้ามเข้าถึงเครือข่าย)
   - `IPC Namespace` (แยก Shared Memory / Message Queues)
3. **cgroups v2 Enforcement:**
   - จำกัด Memory Limit (ป้องกัน OOM บน Host)
   - จำกัด CPU Quota (ป้องกัน 100% CPU starvation)
   - จำกัด `pids.max` (ป้องกัน Fork Bomb / Thread Exhaustion)
4. **Kernel Hardening:**
   - บังคับใช้ `no_new_privs = 1`
   - Drop Ambient และ Effective Linux Capabilities ทั้งหมด
5. **Mount Isolation Policy:**
   - Candidate Workspace ถูก Mount แบบ **Read-Only**
   - Temporary Directory (`/tmp`) เป็น **tmpfs** จำกัดขนาด (Default 64MB) พร้อมแฟล็ก `noexec`, `nosuid`, `nodev`
   - Deny Host Credentials: บล็อก `~/.ssh`, `~/.aws`, `~/.kube`, `~/.gnupg`
   - Deny Container Sockets: บล็อก `/var/run/docker.sock`, `/run/containerd/containerd.sock`
6. **Subprocess Policy:** Default สำหรับ Candidate คือ **DENY subprocess**

- **[REQ-S12-003]** **Python socket monkeypatch ไม่ถือเป็น Security Boundary** (ต้องตัดในระดับ Network Namespace ของ Kernel)

---

## 3. Seccomp Profiles & Forbidden Capabilities

### Forbidden Capability Classes:
- `ptrace` (ป้องกันการ inspect memory นอก process)
- `mount / umount / pivot_root` (ป้องกันการแก้ mount table)
- `namespace escape`
- `kernel module loading` (`init_module`, `finit_module`)
- `bpf` / `perf_event_open` (ป้องกัน eBPF privilege escalation)
- `raw device access` (`/dev/mem`, `/dev/kmem`, `/proc/kcore`)
- `raw network sockets` (`AF_INET`, `AF_PACKET`)

### การแบ่ง Profile:
- `seccomp-bootstrap`: อนุญาต Syscalls ที่จำเป็นสำหรับการ initialize CPython runtime
- `seccomp-candidate`: กรองและบล็อก Syscalls อันตรายทั้งหมด (Default action = `SECCOMP_RET_KILL_PROCESS`)

---

## 4. Cryptographic Trust Profile (EE-CRYPTO-1)

สำหรับการอนุมัติการ Deploy ในระดับ M12 และ Self-Evolution ในระดับ M13:

```yaml
profile_id: "EE-CRYPTO-1"
content_digest: "SHA-256"
signature_algorithm: "Ed25519"
public_key_encoding: "raw-32-byte-base64url-no-padding"
signature_encoding: "raw-64-byte-base64url-no-padding"
key_id: "SHA-256(raw_public_key)"
nonce_minimum_bits: 128
```

- **[REQ-S12-014]** ไม่อนุญาตให้ทำ Algorithm Negotiation (ป้องกัน Downgrade Attack)
- **[REQ-S12-019]** Production Approval ในระดับ M12 ต้องใช้ **2-of-3 Distinct Authorized Ed25519 Keys**
- **[REQ-S20-001]** ไม่มี Boolean Flag เช่น `trusted=true` ที่ใช้แทนการตรวจสอบ Cryptographic Signature ได้
