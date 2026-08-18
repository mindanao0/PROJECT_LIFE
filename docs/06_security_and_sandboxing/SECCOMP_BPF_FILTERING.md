# Seccomp BPF System Call Filtering Specification

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** SECURITY SPECIFICATION (L1 Authority)
> **Target Subsystem:** Kernel Syscall Filter & Process Hardening  
> **Governing Equations:** `EQ-221` .. `EQ-230` (Seccomp BPF Bounds)

---

## 1. Filter Architecture & Default Action

ระบบ Sandbox ทำงานภายใต้การกรอง Seccomp BPF (Berkeley Packet Filter) ที่ระดับเคอร์เนล โดยกำหนด Default Action เป็น **`SECCOMP_RET_KILL_PROCESS`** สำหรับทุก System Call ที่ไม่ได้ระบุใน Whitelist:
$$\text{DefaultAction} \equiv \text{SECCOMP\_RET\_KILL\_PROCESS}$$

---

## 2. Comprehensive System Call Filtering Matrix

```text
┌───────────────────────────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────┐
│ Syscall Name                  │ Filter Action                             │ Security Rationale                              │
├───────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ ptrace, process_vm_readv      │ SECCOMP_RET_KILL_PROCESS                  │ ป้องกันการ Trace/Dump Memory ของ Host / Worker  │
│ mount, umount2, pivot_root    │ SECCOMP_RET_KILL_PROCESS                  │ ป้องกันการดัดแปลง Mount Table ของระบบ          │
│ init_module, finit_module     │ SECCOMP_RET_KILL_PROCESS                  │ ป้องกันการโหลด Kernel Rootkit                   │
│ bpf                           │ SECCOMP_RET_KILL_PROCESS                  │ ป้องกันการโจมตีผ่าน Kernel eBPF Subsystem       │
│ kexec_load, reboot            │ SECCOMP_RET_KILL_PROCESS                  │ ป้องกันการสั่ง Reboot หรือเปลี่ยน Kernel Image  │
│ clone, clone3, fork, vfork    │ SECCOMP_RET_ALLOW (pids <= 64 via cgroup) │ อนุญาตให้ Fork Process ย่อยได้ภายในโควต้า cgroup│
│ socket (AF_INET, AF_INET6)    │ SECCOMP_RET_ERRNO (EPERM)                 │ บล็อกการเปิด Network Sockets ทุกชนิด             │
│ socket (AF_UNIX)              │ SECCOMP_RET_ALLOW (IPC via coordinator)   │ อนุญาตเฉพาะ Local IPC ไปยัง Coordinator เท่านั้น│
│ open, openat, read, write     │ SECCOMP_RET_ALLOW (Scoped to tmpfs/mount) │ อนุญาตการอ่านเขียนไฟล์ภายใต้ Read-Only Policy   │
└───────────────────────────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

## 3. Dual-Profile Phase Transition

1. **Phase 1 (Bootstrap Profile):** เปิดให้ Python Runtime โหลดไฟล์ Standard Library และ Initial Modules จากดิสก์
2. **Phase 2 (Strict Execution Profile):** ก่อนที่ Candidate Function จะเริ่มรัน Sandbox Manager จะสลับโหมดเข้าสู่ Strict Profile โดยปิดสิทธิ์การเข้าถึงไฟล์ระบบทั้งหมดและล็อก `no_new_privs`
