# Unified Engine Exception Hierarchy & Diagnostic Classes

> **Subsystem:** Error Handling, Recovery & Diagnostic Telemetry  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** `REQ-S07-003`, `REQ-S08-003`

---

## 1. Complete Exception Class Hierarchy

เพื่อป้องกันการใช้ Generic `Exception` ในการดักจับข้อผิดพลาด และเพื่อให้ระบบสามารถวิเคราะห์หาสาเหตุของปัญหา (Root Cause Analysis) ได้อย่างแม่นยำ Evolution Engine กำหนดลำดับชั้นของ Exception ไว้อย่างเป็นทางการ:

```python
class EvolutionEngineError(Exception):
    """
    Base class สำหรับ Exception ทั้งหมดใน Evolution Engine.
    ทุก Exception ย่อยต้องสืบทอดมาจากคลาสนี้เสมอ.
    """
    def __init__(self, message: str, code: str, details: dict | None = None):
        super().__init__(f"[{code}] {message}")
        self.message = message
        self.code = code
        self.details = details or {}


class PreflightCheckError(EvolutionEngineError):
    """
    เกิดขึ้นเมื่อการตรวจสอบสภาพแวดล้อมก่อนเริ่มระบบ (Preflight Check) ล้มเหลว.
    เช่น: ไวยากรณ์ evolution.yaml ผิดพลาด, ขาด Linux Capabilities, หรือ Path ไม่ถูกต้อง.
    """
    pass


class SandboxSecurityViolationError(EvolutionEngineError):
    """
    เกิดขึ้นเมื่อ Candidate Program พยายามละเมิดขอบเขตความปลอดภัยของ Sandbox.
    เช่น: พยายามเรียก Syscall ต้องห้าม, พยายามเข้าถึง Filesystem นอก /tmp, หรือต่อ Network.
    ส่งผลให้ Candidate เข้าสู่สถานะ QUARANTINED ทันที.
    """
    pass


class ResourceExhaustionError(EvolutionEngineError):
    """
    เกิดขึ้นเมื่อ Candidate Program ใช้ทรัพยากรเกินโควตาที่กำหนดใน cgroups v2.
    เช่น: ติด Timeout (Infinite Loop), เกิด Memory Out-of-Memory (OOM), หรือ PID Exhaustion.
    ส่งผลให้ Candidate ได้รับสถานะ REJECTED.
    """
    pass


class ContractViolationError(EvolutionEngineError):
    """
    เกิดขึ้นเมื่อ Candidate ไม่ผ่าน Capability Gate หรือทำให้พฤติกรรมเดิมของโปรเจกต์เสียหาย.
    เช่น: ไม่ผ่าน Unit Test หรือทำให้เกิด Regression ใน Required Capabilities.
    """
    pass


class OracleEvaluationError(EvolutionEngineError):
    """
    เกิดขึ้นเมื่อชุด Oracle สำหรับเปรียบเทียบผลลัพธ์เสียหาย หรือให้ผล Verdict ที่ไม่สามารถสรุปได้.
    """
    pass


class PersistenceIntegrityError(EvolutionEngineError):
    """
    เกิดขึ้นเมื่อโครงสร้างฐานข้อมูล SQLite ไม่ผ่าน Foreign Key Integrity Check
    หรือไฟล์ใน CAS Storage เกิดการเสียหาย (Checksum Mismatch).
    """
    pass


class SwarmConsensusError(EvolutionEngineError):
    """
    เกิดขึ้นเมื่อ Candidate ที่ได้รับมาจากโหนดภายนอกใน P2P Swarm ไม่ผ่านการ Re-verify
    หรือพบว่าลายเซ็น Cryptographic Signature ไม่ถูกต้อง.
    """
    pass


class StagnationThresholdError(EvolutionEngineError):
    """
    เกิดขึ้นเมื่อประชากรหยุดการพัฒนาต่อเนื่องเกินเกณฑ์ Max Stagnation และผ่านการกระตุ้น
    Escalation Ladder ครบทั้ง 4 ระดับแล้วแต่ยังไม่มีการพัฒนาเพิ่มขึ้น.
    """
    pass
```

---

## 2. Exception-to-State Mapping Table

| Exception Class | รหัส Error Code | Candidate State | Run State | Recovery Action |
|---|---|:---:|:---:|---|
| `PreflightCheckError` | `ERR_PREFLIGHT_FAIL` | `N/A` | `FAILED` | แสดงข้อความแจ้งเตือนคอนฟิกแก่ผู้ใช้ |
| `SandboxSecurityViolationError` | `ERR_SANDBOX_SYSCALL_BLOCKED` | `QUARANTINED` | `RUNNING` | ตัดสิทธิ์ Candidate และบันทึก Evidence |
| `ResourceExhaustionError` | `ERR_SANDBOX_TIMEOUT` / `OOM` | `REJECTED` | `RUNNING` | บันทึก Log และข้ามไป Candidate ถัดไป |
| `ContractViolationError` | `ERR_CAPABILITY_REGRESSION` | `REJECTED` | `RUNNING` | บันทึก Failure Verdict และข้ามไป |
| `OracleEvaluationError` | `ERR_ORACLE_INCONCLUSIVE` | `REJECTED` | `RUNNING` | ปฏิเสธ Candidate และตรวจสอบ Oracle Test |
| `PersistenceIntegrityError` | `ERR_PERSISTENCE_CORRUPTION` | `N/A` | `RECOVERING` | เรียก `RecoveryManager` ทำการกู้คืน State |
| `SwarmConsensusError` | `ERR_SWARM_BYZANTINE_REJECT` | `QUARANTINED` | `RUNNING` | ปฏิเสธ Peer Candidate และบันทึก Blacklist |
| `StagnationThresholdError` | `ERR_STAGNATION_MAX_REACHED` | `N/A` | `COMPLETED` | สรุปผล Pareto Front ที่ดีที่สุดและจบการทำงาน |
