# Benchmark Case MVP-11: Multi-Tenant Sandbox Executor

> **Case ID:** `MVP-11`  
> **Project Type:** Hardened Security Sandbox Harness  
> **Primary Objective:** Maximize Containment Isolation & Defense Verification  
> **Target Speedup:** $\ge 1.0\times$ (Zero Security Leaks)  
> **Allowed Mutations:** `M01`, `M02`, `M03`

---

## 1. Workload Description
การทดสอบรันโค้ดมุ่งร้าย 8 ชนิด (Path Traversal, Fork Bomb, Memory Exhaustion, Raw Sockets, ptrace) ภายใต้ Linux Namespaces, cgroups v2, และ Seccomp BPF.

## 2. Oracle Verification Rules
- การโจมตีทั้ง 8 รูปแบบต้องถูกตรวจพบ และย้ายสถานะสู่ `QUARANTINED` 100% โดยไม่กระทบ Host
