# Domain 23: Seccomp BPF Syscall Filtering Matrix

> **Domain Index:** `DOMAIN-23`  
> **Engineering Scope:** `DIM-221` .. `DIM-230`  
> **Mathematical Equations:** `EQ-221` .. `EQ-230`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 23 กำหนดการกรอง System Calls ระดับเคอร์เนลผ่าน **Seccomp BPF Filter**, ตาราง Syscalls ต้องห้าม 6 หมวดหมู่ (Ptrace, Mount, Kernel Module, Socket, eBPF, Hardware Mem), การบังคับใช้ Default Action `SECCOMP_RET_KILL_PROCESS`, และการบันทึกเหตุการณ์ลงตาราง Quarantine.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-221  │ EQ-221   │ Seccomp BPF Instruction Count Limit       │ N_bpf <= 4096 instructions                                  │
│ DIM-222  │ EQ-222   │ Default Kill Process Action Specification │ DefaultAction === SECCOMP_RET_KILL_PROCESS                  │
│ DIM-223  │ EQ-223   │ Ptrace Process Tracing Denial Invariant   │ Syscall(SYS_ptrace) ==> KILL                                │
│ DIM-224  │ EQ-224   │ Mount Table Filesystem Mutation Denial    │ Syscall(SYS_mount or SYS_umount2) ==> KILL                  │
│ DIM-225  │ EQ-225   │ Kernel Module Dynamic Load Denial Invar   │ Syscall(SYS_init_module or SYS_finit_module) ==> KILL        │
│ DIM-226  │ EQ-226   │ Raw Network Socket Syscall Error Action   │ Syscall(SYS_socket, AF_INET) ==> EPERM                      │
│ DIM-227  │ EQ-227   │ eBPF Privilege Escalation Syscall Denial  │ Syscall(SYS_bpf) ==> KILL                                   │
│ DIM-228  │ EQ-228   │ Direct Hardware Memory Device Open Denial │ Open("/dev/mem") ==> EACCES or KILL                         │
│ DIM-229  │ EQ-229   │ Bootstrap vs Execution Dual-Profile Phase │ Profile(t) = I(t < t_init) Boot + I(t >= t_init) Strict     │
│ DIM-230  │ EQ-230   │ Seccomp Violation Audit Hash Chain Record │ H_sec_violation = SHA-256(SyscallNo || RIP || H_prev)       │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-221` / `EQ-221`: Seccomp BPF Instruction Count Limit
- ขนาดของโปรแกรม BPF Filter ต้องไม่เกิน 4096 Instructions:
  $$N_{\text{bpf}} \le 4096 \quad \text{instructions}$$

### `DIM-222` / `EQ-222`: Default Kill Process Action
- กฎการกรอง Seccomp BPF ใช้หลักการ Whitelist โดยการเรียก Syscall ใดๆ ที่ไม่อยู่ใน Whitelist จะถูกสั่ง Kill Process ทันที:
  $$\text{DefaultAction} \equiv \text{SECCOMP\_RET\_KILL\_PROCESS}$$

### `DIM-223` / `EQ-223`: Ptrace Tracing Denial
- บล็อกคำสั่ง `ptrace` และ `process_vm_readv` เพื่อป้องกันไม่ให้ Candidate ส่องดู Memory ของ Host หรือ Worker ตัวอื่น:
  $$\text{Syscall}(\text{SYS\_ptrace}) \implies \text{KILL}$$

### `DIM-224` / `EQ-224`: Mount Table Filesystem Mutation Denial
- ป้องกันการดัดแปลง Mount Table:
  $$\text{Syscall}(\text{SYS\_mount} \lor \text{SYS\_umount2}) \implies \text{KILL}$$

### `DIM-225` / `EQ-225`: Kernel Module Dynamic Load Denial Invariant
- บล็อกการโหลด Kernel Modules:
  $$\text{Syscall}(\text{SYS\_init\_module} \lor \text{SYS\_finit\_module}) \implies \text{KILL}$$

### `DIM-226` / `EQ-226`: Raw Network Socket Syscall Error Action
- คืนค่า `EPERM` เมื่อพยายามเปิด Network Socket:
  $$\text{Syscall}(\text{SYS\_socket}, \text{AF\_INET}) \implies \text{EPERM}$$

### `DIM-227` / `EQ-227`: eBPF Privilege Escalation Syscall Denial
- บล็อกการโหลดโปรแกรม eBPF จากภายใน Sandbox:
  $$\text{Syscall}(\text{SYS\_bpf}) \implies \text{KILL}$$

### `DIM-228` / `EQ-228`: Direct Hardware Memory Device Open Denial
- บล็อกการเปิด `/dev/mem` หรือ `/dev/kmem`:
  $$\text{Open}(\text{"/dev/mem"}) \implies \text{EACCES} \lor \text{KILL}$$

### `DIM-229` / `EQ-229`: Bootstrap vs Execution Dual-Profile Phase
- สลับ Profile จาก Bootstrap (อนุญาตโหลด Python Runtime) สู่ Strict Profile:
  $$\text{Profile}(t) = \mathbb{I}(t < t_{\text{init}}) \text{Boot} + \mathbb{I}(t \ge t_{\text{init}}) \text{Strict}$$

### `DIM-230` / `EQ-230`: Seccomp Violation Audit Hash Chain Record
- บันทึกการละเมิด Seccomp ลงใน Hash Chain:
  $$H_{\text{sec\_violation}} = \text{SHA-256}(\text{SyscallNo} \parallel \text{RIP} \parallel H_{\text{prev}})$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D23-01` [Seccomp BPF Syscall Trap]:** สั่งรันโค้ดภาษา C ภายใน Sandbox ที่พยายามเรียก `ptrace(PTRACE_TRACEME)` ระบบ Seccomp ต้อง Kill ภายใน 1ms
2. **Test `TC-D23-02` [Socket EPERM Trap]:** พยายามเรียก `socket()` ตรงๆ ตรวจสอบว่าได้ Error Code `EPERM`
3. **Test `TC-D23-03` [eBPF Denial Invariant]:** พยายามเรียก `bpf()` Syscall ตรวจสอบว่า Process ถูก Kill ทันที
4. **Test `TC-D23-04` [Seccomp Violation Audit Trail]:** ยืนยันว่าบันทึกการละเมิดถูกจัดเก็บลงตาราง `quarantine_records` พร้อม Hash ถูกต้อง
