# 18 — Public API & CLI Reference Manual

> **Dimension:** Interface Contracts & Developer SDK  
> **Package Name:** `evolution_engine`  
> **Executable:** `evolve`

เอกสารฉบับนี้เป็นคู่มืออ้างอิงฟังก์ชันและคำสั่งฉบับสมบูรณ์ (Complete Reference Manual) สำหรับทั้ง Python SDK (`EvolutionEngine`) และ Command-Line Interface (`evolve`)

---

## 1. Python SDK Reference (`evolution_engine.EvolutionEngine`)

```python
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from evolution_engine.types import (
    RunId, CandidateId, ValidationReport, RunStatus, RunState,
    EvolutionReport, ExportManifest, SwarmStatus
)

class EvolutionEngine:
    """
    Main entry-point class for orchestrating evolutionary runs.
    """

    @classmethod
    def create(cls, config_path: str) -> "EvolutionEngine":
        """
        สร้าง Engine Instance จากไฟล์คอนฟิก (evolution.yaml).
        
        :param config_path: Path ไปยังไฟล์ evolution.yaml
        :return: EvolutionEngine instance
        :raises PreflightCheckError: เมื่อคอนฟิกไม่ผ่านการตรวจสอบไวยากรณ์หรือ Schema
        """
        ...

    def validate_project(self, project_path: str) -> ValidationReport:
        """
        ตรวจสอบความถูกต้องของโปรเจกต์เป้าหมาย โครงสร้างไฟล์ และ Sandbox.
        
        :param project_path: Path ไปยังโฟลเดอร์โปรเจกต์เป้าหมาย
        :return: ValidationReport (is_valid, errors, warnings, config_digest)
        """
        ...

    def start_run(self, project_path: str, seed: Optional[int] = None) -> RunId:
        """
        เริ่มต้นการรัน Evolution Process ใหม่.
        
        :param project_path: Path ไปยังโปรเจกต์เป้าหมาย
        :param seed: RNG Seed สำหรับกำหนดความสามารถในการ Replay (Optional)
        :return: RunId ประจำรอบการประมวลผล
        :raises SandboxSecurityViolationError: เมื่อระบบ Sandbox ไม่ผ่าน capability probes
        """
        ...

    def pause_run(self, run_id: RunId) -> RunState:
        """
        พักการทำงานของ Run ชั่วคราว (Transition: RUNNING -> PAUSED).
        """
        ...

    def resume_run(self, run_id: RunId) -> RunState:
        """
        ดำเนินการต่อจากจุดที่พักไว้ (Transition: PAUSED -> RUNNING).
        """
        ...

    def abort_run(self, run_id: RunId) -> RunState:
        """
        สั่งหยุดการทำงานของ Run อย่างปลอดภัยและบันทึก Checkpoint สุดท้าย.
        """
        ...

    def get_status(self, run_id: RunId) -> RunStatus:
        """
        อ่านสถานะปัจจุบันของ Run (Current Generation, Pareto Front Size, Elapsed Time).
        """
        ...

    def get_report(self, run_id: RunId) -> EvolutionReport:
        """
        ดึงรายงานสรุปผลการวิวัฒนาการ ค่า Metric Gains และประวัติ Lineage Graph.
        """
        ...

    def export_candidate(
        self,
        candidate_id: CandidateId,
        destination: str,
        mode: str = "SAFE_EXPORT_ONLY"
    ) -> ExportManifest:
        """
        ส่งออก Candidate Code ที่ผ่านการคัดเลือกไปยังไดเรกทอรีปลายทาง.
        
        :param candidate_id: ID ของ Candidate ที่ต้องการส่งออก
        :param destination: ตำแหน่งโฟลเดอร์ปลายทาง
        :param mode: โหมดการส่งออก (Default: SAFE_EXPORT_ONLY)
        :return: ExportManifest พร้อม SHA-256 Digest
        """
        ...
        ...
```

---

## 2. CLI Command Surface Reference (`evolve`)

### 2.1 Global Flags
```text
--json              ส่งผลลัพธ์เป็น Structured JSON Envelope ทาง stdout
--quiet, -q         ปิดการแสดงผลข้อความแจ้งเตือนที่ไม่จำเป็น
--verbose, -v       เปิดการแสดงผล Debug Log ละเอียด
--version           แสดงหมายเลขเวอร์ชันของ Engine (10.2.2)
--help, -h          แสดงคำแนะนำการใช้งานคำสั่ง
```

---

### 2.2 Subcommands & Options

#### `evolve init`
สร้างโครงสร้างและไฟล์ `evolution.yaml` เริ่มต้นในไดเรกทอรีปัจจุบัน
```bash
evolve init [--level function|module|project] [--name <project-name>]
```

#### `evolve validate`
ตรวจสอบความสมบูรณ์ของโปรเจกต์และคอนฟิก
```bash
evolve validate [--project <path>] [--json]
```

#### `evolve run`
เริ่มต้น Evolution Run
```bash
evolve run [--project <path>] [--seed <int>] [--generations <int>] [--background]
```

#### `evolve status`
ดูสถานะการทำงานปัจจุบัน
```bash
evolve status [--run-id <id>] [--json]
```

#### `evolve report`
สร้างรายงานสรุปผล
```bash
evolve report [--run-id <id>] [--format json|markdown|html] [--output <file>]
```

#### `evolve export`
ส่งออก Candidate Code
```bash
evolve export --candidate-id <id> --destination <path> [--mode SAFE_EXPORT_ONLY]
```

เชื่อมต่อเข้าเครือข่าย Swarm
```bash
```

#### `evolve doctor`
วินิจฉัยสภาพแวดล้อมระบบและ Sandbox Probes
```bash
evolve doctor [--sandbox-probes] [--verify-integrity] [--reconcile-db]
```
