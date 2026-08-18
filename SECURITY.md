# Security Policy — Evolution Engine

> **Specification Reference:** Section 12 & Section 20  
> **Security Baseline:** `PROFILE_A_LINUX`  
> **Cryptographic Profile:** `EE-CRYPTO-1` (Ed25519)

Evolution Engine ให้ความสำคัญสูงสุดกับความปลอดภัยในการรันโค้ดที่ไม่น่าไว้วางใจ (Untrusted Code Execution) เอกสารฉบับนี้ระบุนโยบายความปลอดภัย ขอบเขตการคุ้มครอง และแนวทางการรายงานช่องโหว่

---

## 1. Security Architecture & Threat Model

เนื่องจาก Engine มีหน้าที่ประเมิน Candidate Programs ซึ่งอาจถูกสร้างขึ้นโดยมีบั๊ก มีการใช้ทรัพยากรผิดปกติ หรือมีคำสั่งพยายามโจมตีระบบ Host:

1. **Kernel-enforced Sandbox (PROFILE_A_LINUX):**
   - ทุก Candidate ต้องรันในสภาพแวดล้อม Unprivileged User
   - แยก Namespaces ทั้งหมด: `User`, `Mount`, `PID`, `Network`, `IPC`
   - บล็อกการเข้าถึง Network ทั้งหมด (`Network Namespace` ปิด loopback)
   - ป้องกัน Fork Bomb และ Memory Leak ด้วย `cgroups v2` (`pids.max`, memory limit, cpu quota)
   - บังคับใช้ `no_new_privs` และ Drop Linux Capabilities ทั้งหมด
   - Mount Workspace เป็น **Read-Only** อนุญาตเขียนได้เฉพาะ `/tmp` (tmpfs จำกัดขนาด 64MB)
   - กรอง System Calls ด้วย **Seccomp Filters**
2. **Quarantine Procedure:**
   - Candidate ใดๆ ที่พยายามละเมิด Sandbox (เช่น พยายามแตะไฟล์นอก Workspace, สั่ง Network Call หรือเรียก Fork Bomb) จะถูกตัดสถานะเป็น `QUARANTINED` ทันที และบันทึกหลักฐานความผิดพลาดลงในตาราง `quarantine_records`

---

## 2. Supported Versions & Deployment Modes

| Deployment Mode | Security Guarantee | Production Promotion |
|---|---|---|
| **`SAFE_EXPORT_ONLY`** (Default) | Sandbox Hardened, ห้ามแก้ไขโค้ดจริงบน Host | ไม่อนุญาต (Export to temp/target folder only) |
| **`GOVERNED_CANARY`** | ควบคุมด้วยสถิติ Rollback Thresholds | ต้องมี Human Multisig Approval (2-of-3 Ed25519) |
| **`PRODUCTION_ACTIVE`** | Production Governed Environment | ต้องผ่าน Gate M12 และ Multisig Quorum |
| **`SELF_EVOLUTION_SANDBOX`** | Evaluator และ Root Policy เป็น Immutable | ต้องผ่าน Gate M13 และ Root-of-Trust Ceremony |

---

## 3. Reporting a Vulnerability

หากคุณพบช่องโหว่ด้านความปลอดภัย (เช่น Sandbox Escape, Seccomp Bypass, Cryptographic Collision หรือ Invariant Leakage):

1. **อย่าเปิดเผยข้อมูลช่องโหว่ใน Public Issue Tracker**
2. กรุณาส่งรายงานรายละเอียดมาที่ทีมรักษาความปลอดภัยพร้อมข้อมูล:
   - รายละเอียดช่องโหว่และขั้นตอนการจำลองสถานการณ์ (Reproduction Steps)
   - เวอร์ชันของ Kernel, CPython, และ OS ที่ทดสอบ
   - ตัวอย่าง Candidate Program หรือ Payload ที่ใช้ทดสอบ
3. ทีมงานจะตอบรับรายงานภายใน 48 ชั่วโมง และดำเนินการแก้ไขผ่านกระบวนการ **Governed Specification Change**
