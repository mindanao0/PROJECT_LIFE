# 07 — Schemas, Protocols & Public Interfaces

> **Active Requirements Covered:** `REQ-S06-001` .. `REQ-S07-003`, `REQ-S15-001` .. `REQ-S15-007` (Unified v1 Full Scope)  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Not normative.  
> **Canonical source:** [`docs/07_schemas_and_protocols/`](./07_schemas_and_protocols/) — เมื่อขัดกัน ให้ยึดฝั่งนั้น

Evolution Engine v1 นิยามอินเทอร์เฟซสาธารณะ (Public Surface), โปรโตคอลภายใน 22 โปรโตคอล (Typed Protocols) ครอบคลุมทั้ง Core Engine, Quantum Search, P2P Swarm และ ALife Ecosystem

---

## 1. Canonical CLI (`evolve`)

```bash
evolve init          # สร้าง evolution.yaml และโครงสร้างเริ่มต้น
evolve validate      # ตรวจสอบความถูกต้องของโปรเจกต์และคอนฟิก
evolve run           # เริ่มต้นการวิวัฒนาการ
evolve status        # ดูสถานะปัจจุบันของ Run
evolve pause         # พักการทำงานชั่วคราว
evolve resume        # ดำเนินการต่อจากจุดที่พัก
evolve abort         # ยกเลิกการรันและเข้าสู่สถานะ ABORTED
evolve report        # สร้างรายงานผลการวิวัฒนาการและ Pareto Frontier
evolve export        # ส่งออก Candidate โค้ด (รองรับทั้ง Pure Python และ Rust/C Native Extension)
evolve swarm join    # เชื่อมต่อเข้าร่วม P2P Evolutionary Swarm Network
evolve db migrate    # รันการอัปเกรดฐานข้อมูล SQLite
evolve doctor        # ตรวจสอบความพร้อมของระบบ, Sandbox และ Native Toolchain
```

---

## 2. Canonical Python SDK (`EvolutionEngine`)

```python
class EvolutionEngine:
    def create(self, config_path: str) -> "EvolutionEngine": ...
    def validate_project(self, project_path: str) -> ValidationReport: ...
    def start_run(self, project_path: str) -> RunId: ...
    def pause_run(self, run_id: RunId) -> RunState: ...
    def resume_run(self, run_id: RunId) -> RunState: ...
    def abort_run(self, run_id: RunId) -> RunState: ...
    def get_status(self, run_id: RunId) -> RunStatus: ...
    def get_report(self, run_id: RunId) -> EvolutionReport: ...
    def export_candidate(self, candidate_id: CandidateId, destination: str) -> ExportManifest: ...
    def connect_swarm(self, peer_addresses: list[str]) -> SwarmStatus: ...
```

---

## 3. Complete Typed Protocol Suite (22 Protocols)

| Protocol | หน้าที่รับผิดชอบ | Input หลัก | Output หลัก |
|---|---|---|---|
| **ProjectAdapter** | อ่านและวิเคราะห์โปรเจกต์เป้าหมาย | `project_path` | `ProjectManifest` |
| **SourceAnalyzer** | แปลง Source เป็น AST/CST/UAST Representation | `immutable_snapshot` | `ProgramRepresentation` |
| **MutationStrategy** | กลายพันธุ์โค้ดตามกลยุทธ์ (M01–M10) | `parent_repr`, `context`, `RNG` | `MutationResult` |
| **MutationEngine** | ประสานงานประชากรและการกลายพันธุ์ | `parent_population`, `registry` | `CandidateDrafts` |
| **QuantumSearchAdapter** | ปรับ Qubit Probability Vector หมุน Rotation Gate | `q_vector`, `best_solution` | `UpdatedQVector` |
| **PolyglotBridge** | แปลง Python AST $\leftrightarrow$ Rust/C Native Kernel | `ast_subtree`, `target_lang` | `CompiledNativeModule` |
| **PopulationManager** | บริหารจัดการสมาชิกรุ่น | `candidates`, `decisions` | `PopulationSnapshot` |
| **EcosystemManager** | บริหาร Predator-Prey Dynamics และ Niche Energy | `prey_pop`, `predator_pop` | `EcosystemState` |
| **SwarmCoordinator** | จัดการ P2P Gossip Migration และ Elite Exchange | `local_pareto`, `peer_network` | `SwarmSyncReceipt` |
| **SandboxManager** | เตรียมและรัน Process ใน Sandbox | `CandidateArtifact`, `Request` | `ExecutionResult` |
| **TestRunner** | รันชุดทดสอบ Behavior | `execution_artifact`, `TestPlan` | `TestSuiteResult` |
| **CapabilityVerifier** | ยืนยันว่าคุณสมบัติเดิมไม่เสียหาย | `test_results`, `contract` | `CapabilityVerdict` |
| **OracleRunner** | เปรียบเทียบผลลัพธ์กับ Oracle | `candidate`, `oracle_plan` | `OracleVerdict` |
| **MetricRunner** | วัดผลมาตรวัดประสิทธิภาพ | `candidate`, `objective` | `MetricMeasurement` |
| **ParetoSelector** | จัดอันดับ Pareto และคัดเลือก | `candidates`, `objectives` | `SelectionDecision` |
| **EvidenceStore** | บันทึกหลักฐานที่ลงนาม/คำนวณ Digest | `evidence_inputs` | `EvidenceRecord` |
| **ArtifactStore** | จัดการไฟล์ CAS Storage | `bytes`, `metadata` | `ArtifactRef` |
| **LineageRepository** | บันทึกสายสัมพันธ์วิวัฒนาการ | `lineage_events` | `LineageSnapshot` |
| **CheckpointManager** | บันทึก Checkpoint เพื่อกู้คืน | `run_state` | `CheckpointRef` |
| **RecoveryManager** | กู้คืนระบบหลัง Crash | `checkpoint`, `manifests` | `RecoveryResult` |
| **PolicyEngine** | ตรวจสอบนโยบายความปลอดภัย | `candidate_context` | `PolicyVerdict` |
| **DeploymentManager** | ส่งออก/จัดเตรียมการ Deploy | `approved_artifact`, `mode` | `DeploymentResult` |

---

## 4. Exact 26 JSON Schema Package (M3 Deliverable)

รายการไฟล์ JSON Schema (Draft 2020-12) ทั้ง 26 ตัวในโฟลเดอร์ `schemas/`:

```text
01 candidate.schema.json                14 environment.schema.json
02 candidate_state.schema.json          15 lineage_node.schema.json
03 mutation.schema.json                 16 lineage_edge.schema.json
04 mutation_result.schema.json          17 selection_decision.schema.json
05 population.schema.json               18 policy_snapshot.schema.json
06 generation.schema.json               19 provenance_certificate.schema.json
07 run.schema.json                      20 reproducibility_certificate.schema.json
08 baseline.schema.json                 21 checkpoint.schema.json
09 project_manifest.schema.json         22 recovery_manifest.schema.json
10 capability_contract.schema.json      23 release_gate.schema.json
11 objective.schema.json                24 quarantine_record.schema.json
12 metric_result.schema.json            25 memory_record.schema.json
13 oracle_result.schema.json            26 engine_config.schema.json
```
