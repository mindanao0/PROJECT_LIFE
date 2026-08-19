<!-- ACTIVE_SPEC_BEGIN -->

# Evolution Engine — Implementation Plan (Plan 10.2.2 Implementation-Start Canonical Release) [NORMATIVE]

> **Status:** Canonical Implementation Specification — Documentation Closed; Ready to Start M3; Implementation & Evidence Pending  
> **Version:** 10.2.2  
> **Project Type:** Offline-first autonomous evolutionary software system  
> **Primary Language:** Python  
> **Core AI Dependency:** None  
> **LLM Dependency:** None  
> **Evolution Model:** Population-based evolutionary computation  
> **Current Maturity:** M2_REQUIREMENTS_CANONICAL  
> **Default Deployment Mode:** SAFE_EXPORT_ONLY  
> **Active Contract:** Only content between `ACTIVE_SPEC_BEGIN` and `ACTIVE_SPEC_END` is authoritative. The in-file historical archive is non-normative and superseded.

---

## 0.1 Rewrite Intent [INFORMATIVE]

เอกสารฉบับนี้เป็น **canonical rewrite lineage** ที่เริ่มจาก Plan 10.2.0 และได้รับ implementation-closure amendment ใน Plan 10.2.2 ไม่ใช่ patch ต่อท้าย active definition เก่า

กฎของ rewrite นี้:

- ลบ pattern แบบ “เพิ่ม Section ใหม่เพื่อทับ Section เก่า”
- เหลือ source of truth เพียงชุดเดียวต่อหัวข้อ
- ไม่ประกาศ `EXECUTION_READY`, `M11`, `100% complete`, `[IMPL]`, `[TEST]` หรือ `[EVID]` หากยังไม่มี artifact/test/evidence จริง
- ห้ามใช้ hash ที่แต่งขึ้นเพื่อทำเหมือน fixture มีอยู่แล้ว
- ห้ามใช้ unconditional-success stubs, empty bodies หรือ omitted bodies เป็นหลักฐานว่า contract ถูก implement
- Requirement ที่อยู่ในเอกสารนี้มีสถานะ `[REQ]` เว้นแต่มี repository evidence จริงแนบมาพิสูจน์สถานะที่สูงกว่า
- Research features ไม่เป็น dependency ของ Core
- หาก implementation artifact ขัดกับเอกสารนี้ ให้ build fail จนกว่าจะมี governed spec change

---

## 0.2 What Was Removed [INFORMATIVE]

ฉบับก่อนหน้ามี numbered sections จำนวนมากที่สะสม freeze เก่า, patch เก่า, duplicated formulas, duplicated resilience boilerplate และ canonical definitions หลายชุด

สิ่งเหล่านี้ถูกถอดออกจาก **active contract**:

- Plan 7.0 / 8.0 / 9.0 / 10.0 / 10.1 freeze blocks
- stale `active_version` values
- duplicated Candidate FSM definitions
- duplicated canonical JSON/float rules
- duplicated CLI/SDK definitions
- fake/example Golden Corpus hashesที่ถูกนำเสนอเหมือนค่าจริง
- unverified unconditional-success validator stubs
- legacy completion marks ที่ไม่มี implementation evidence
- claim ว่ามี 26 schemas / 29 tables / M11 โดยไม่มี artifact รองรับ
- generic repeated formulasที่ไม่ได้เปลี่ยน semantics ของ section

Historical content และรายละเอียดเดิมถูกเก็บครบใน **Appendix C — Full Historical & Design Archive** ภายในไฟล์เดียวกัน แต่ archive ไม่มีอำนาจ override Active Specification. Research concepts ที่ยังอาจพัฒนาในอนาคตถูกสรุปไว้ใน Research Backlog ของ active contract ด้วย

---

## 0.3 Single-File Usage Rule [NORMATIVE]

ไฟล์นี้ตั้งใจให้เป็น **ไฟล์เดียวสำหรับทั้ง implementation contract และ design archive** โดยมีกฎตายตัว:

```text
ACTIVE_SPEC_BEGIN ... ACTIVE_SPEC_END
    = source of truth สำหรับ implementation, tests, CI, release gates และ evidence

ARCHIVE_BEGIN ... ARCHIVE_END
    = historical/design reference เท่านั้น
    = ห้ามใช้เป็น active requirement โดยตรง
```

[REQ][REQ-S00-001] เครื่องมือ CI/spec linter ต้องอ่านเฉพาะ Active Specification เมื่อตรวจ canonical conflicts, requirement status, table/schema counts, FSM uniqueness และ release-gate semantics

[REQ][REQ-S00-002] ถ้า archive มีข้อความ `[HISTORICAL-NORMATIVE]`, `[SUPERSEDED]`, `M11`, `100%`, freeze รุ่นเก่า หรือ definition ที่ขัดกับ Active Specification ให้ถือว่า **ไม่มีผลบังคับทั้งหมด**

[REQ][REQ-S00-003] รายละเอียดจาก archive จะกลับมาเป็น active requirement ได้เฉพาะผ่าน Governed Specification Change ใน Section 27 เท่านั้น

[REQ][REQ-S00-004] ห้ามลบ archive เพียงเพื่อให้ spec สั้นลง เว้นแต่มี governed archival policy และมี checksum/reference ที่ทำให้ข้อมูลไม่สูญหาย

---

## 0.4 Plan 10.2.2 Implementation-Closure Amendments [INFORMATIVE]

Plan 10.2.2 ปิดช่องว่างก่อนเริ่ม implementation จำนวน 9 กลุ่ม โดยไม่เพิ่ม scope ของ Core v1:

1. เพิ่ม stable Requirement ID ให้ทุก active `[REQ]` และกำหนด lifecycle/traceability ของ ID
2. เพิ่ม Run, Recovery และ Governance FSM ที่ machine-checkable
3. แยก semantics ของ Pareto dominance, diversity และ metric preference weights
4. กำหนด canonical owner และ precedence ของ configuration ทุกชั้น
5. เพิ่ม relational integrity, state constraints และ index requirements ให้ 29-table DDL
6. กำหนด Linux conformance matrix และ cryptographic profile สำหรับ Security/Evidence
7. เพิ่ม mandatory vertical slice ก่อนสร้างระบบเต็ม
8. ทำ M3 schema package เป็น implementation deliverable แรก พร้อม fixtures/manifest
9. กำหนด generated Active-Spec View โดย canonical source ยังเป็น single file นี้

การแก้ครั้งนี้ผ่าน workflow ใน Section 27 ในฐานะ pre-implementation governed clarification; evidence เดิมไม่มีให้ invalidate และ maturity ยังคงเป็น M2

---

## 0.5 Active Contract Location & Historical Archive [NORMATIVE]

ไฟล์นี้ **เป็น canonical source เอง** ไม่ใช่ derived view

```text
active contract:  spec/ACTIVE_CONTRACT.md          (rank 2 ใน spec/authority.yaml)
canonical data:   spec/*.yaml, spec/**/*.yaml, schemas/*.json   (rank 1)
historical:       spec/archive/Plan_10_2_0_Historical_Archive.md (NON-NORMATIVE)
```

เดิม section นี้กำหนดโมเดล single-file master + generator (`tools/render_active_spec.py`)
โดยให้ไฟล์นี้เป็น read-only build artifact ที่ห้ามแก้ด้วยมือ โมเดลนั้นถูกยกเลิกที่
[`CR-0001`](change_records/CR-0001-active-contract-becomes-source.md) เพราะทั้ง master และ generator
ไม่มีอยู่จริง ทำให้ไม่มีวิธีแก้สเปกอย่างถูกกฎแม้แต่วิธีเดียว

`REQ-S00-005`, `REQ-S00-006`, `REQ-S00-007` และ `REQ-S00-008` ถูกถอนที่ CR-0001
ID ทั้งสี่สงวนถาวรและห้ามนำกลับมาใช้ใหม่ตาม Section 2.4

[REQ][REQ-S00-009] archive manifest ต้องบันทึก SHA-256 ของ archive ที่กู้คืนไว้ เพื่อพิสูจน์ว่า archive ไม่สูญหาย; manifest อยู่ที่ `spec/archive/manifest.json` และ CI job `spec_archive_checksum_match` ต้องคำนวณซ้ำแล้วเทียบ

[REQ][REQ-S00-010] การแก้ `spec/ACTIVE_CONTRACT.md` ต้องผ่าน Section 27 governed change และบันทึกเป็นไฟล์ใน `spec/change_records/`; commit ที่แก้ contract โดยไม่มี change record = CI failure

---

# 1. Vision & System Identity [NORMATIVE]

## 1.1 Core Vision [NORMATIVE]

[REQ][REQ-S01-001] Evolution Engine ต้องเป็นระบบที่รับ Python project แล้วสร้างประชากรของ candidate programs จาก source เดิม เพื่อ:

```text
Observe
-> Understand
-> Represent
-> Mutate
-> Generate Population
-> Isolate
-> Test
-> Reject Invalid Candidates
-> Measure
-> Compare
-> Select
-> Remember
-> Adapt Mutation Strategy
-> Create Next Generation
-> Repeat
```

[REQ][REQ-S01-002] Evolution scope ต้องรองรับตามลำดับ maturity:

```text
Function
-> Module
-> Project
-> Engine Self-Evolution (M13 only)
```

[REQ][REQ-S01-003] เป้าหมายคือ reusable evolutionary software system ไม่ใช่ AI coding assistant, autocomplete, LLM agent หรือ random text mutator

[REQ][REQ-S01-004] LLM ไม่เป็น dependency ของ Core

---

## 1.2 Core Principles [NORMATIVE]

[REQ][REQ-S01-005] **Offline First** — evolution loop ต้องทำงานได้โดยไม่เรียก cloud service

[REQ][REQ-S01-006] **Deterministic Where Possible** — parsing, candidate identity, artifact hashing, ordering, lineage และ seeded randomness ต้อง replay ได้ตามระดับ reproducibility ที่ประกาศ

[REQ][REQ-S01-007] **Project Owns Its Objectives** — project กำหนด metrics, directions, trade-offs, constraints, stopping rules และ acceptable regression ภายใน safety ceiling ของ Engine

[REQ][REQ-S01-008] **Preserve Capabilities** — optimization ห้ามทำลาย capability ที่ถูกประกาศเป็น required

[REQ][REQ-S01-009] **Never Destroy Audit History** — metadata ที่จำเป็นต่อ lineage, evidence, recovery และ audit ห้ามถูก GC แบบทำให้ reconstruct ไม่ได้

[REQ][REQ-S01-010] **Safe by Default** — default deployment mode คือ `SAFE_EXPORT_ONLY`

[REQ][REQ-S01-011] **Controlled Self-Evolution** — candidate engine ห้ามแก้ evaluator/policy/root-of-trust ที่ใช้ตัดสินตัวเอง

---

# 2. Canonical Authority, Versioning & Requirement Status [NORMATIVE]

## 2.1 Authority Rule [NORMATIVE]

ลำดับ authority ที่ active contract ใช้:

```text
L0  Safety & Root-of-Trust invariants
L1  Security sandbox invariants
L2  Active FSM definitions
L3  Active schema/data invariants
L4  Active protocol/interface contracts
L5  Persistence/recovery invariants
L6  Measurement/selection semantics
L7  Project-owned objectives
L8  Informative examples
L9  Research backlog
```

[REQ][REQ-S02-001] Lower-priority rule ห้าม override higher-priority rule

[REQ][REQ-S02-002] ไม่มี historical freeze ใด active หลัง version `10.2.2`

[REQ][REQ-S02-003] เฉพาะข้อความภายใน `ACTIVE_SPEC_BEGIN` / `ACTIVE_SPEC_END` เท่านั้นที่มี canonical authority; Appendix C ถูก exclude จาก active-spec lint และ requirement counting

---

## 2.2 Active Version Manifest [NORMATIVE]

```yaml
active_contract:
  plan_version: "10.2.2"
  contract_version: "10.2.2"
  schema_bundle_version: "10.2.2"
  protocol_version: "10.2.2"
  candidate_fsm_version: "10.2.2"
  run_fsm_version: "10.2.2"
  recovery_fsm_version: "10.2.2"
  governance_fsm_version: "10.2.2"
  deployment_fsm_version: "10.2.2"
  measurement_contract_version: "10.2.2"
  persistence_contract_version: "10.2.2"
  security_profile_version: "10.2.2"
  supersedes:
    - "10.2.1"
    - "10.2.0"
    - "10.1.0"
    - "10.0.0"
    - "9.0.0"
    - "8.0.0"
    - "7.0.0"
```

[REQ][REQ-S02-004] `spec/authority.yaml` และ `spec/version_manifest.yaml` เมื่อถูกสร้างใน repository ต้องตรงกับ section นี้แบบ machine-checkable

---

## 2.3 Requirement Lifecycle [NORMATIVE]

สถานะ requirement มีเพียง:

```text
REQ  = requirement defined
IMPL = implementation artifact exists
TEST = required conformance tests pass
EVID = signed/hashed evidence bundle exists
```

Promotion rule:

```text
REQ -> IMPL -> TEST -> EVID
```

[REQ][REQ-S02-005] ห้ามข้ามสถานะ

[REQ][REQ-S02-006] เอกสารนี้ถือ requirement ทั้งหมดเป็น `REQ` จนกว่าจะมี evidence จาก repository/CI จริง

---

## 2.4 Requirement Identity & Traceability Contract [NORMATIVE]

Canonical requirement expression:

```text
[STATUS][REQ-S<section>-<sequence>] requirement text

example:
STATUS=REQ ID=REQ-S05-001 TEXT="shell=false เสมอใน Core"
```

Rules:

- `STATUS` เป็นหนึ่งใน `REQ`, `IMPL`, `TEST`, `EVID`
- ID ใช้ top-level section number แบบสองหลัก และ sequence แบบสามหลัก
- requirement แบบหลายบรรทัดใช้ ID เดียวที่บรรทัดแรก; block/list/table ที่ต่อเนื่องเป็นส่วนหนึ่งของ requirement นั้น
- ID ที่ publish แล้ว immutable และห้ามนำกลับมาใช้ใหม่ แม้ requirement ถูกถอน
- requirement ใหม่ใช้เลขว่างถัดไปโดยห้าม renumber ID เดิม

[REQ][REQ-S02-007] ทุก active normative requirement ต้องมี Requirement ID ที่ unique และตรง regex `^REQ-S[0-9]{2}-[0-9]{3}$`

[REQ][REQ-S02-008] `spec/requirements.yaml` ต้องมีอย่างน้อย `id`, `section`, `status`, `text_digest`, `owner`, `verification_method`, `test_refs`, `evidence_refs` และ `release_gates` ต่อ requirement

[REQ][REQ-S02-009] CI ต้อง fail เมื่อพบ requirement ไม่มี ID, ID ซ้ำ, ID ถูก reuse, status ถอยหลังโดยไม่มี governed invalidation หรือ text เปลี่ยนโดยไม่เปลี่ยน `text_digest`

[REQ][REQ-S02-010] การย้าย requirement ข้าม section ต้องคง ID เดิมและบันทึก previous section ใน change record; section component ของ ID เป็น provenance ไม่ใช่ mutable locator

---

# 3. Scope, Runtime & Dependency Boundary [NORMATIVE]

## 3.1 Core v1 Scope [NORMATIVE]

Core v1 ประกอบด้วย:

- source/project discovery
- Python representation
- mutation engine
- population management
- sandbox execution
- tests/capability gates
- project metrics
- Pareto selection
- evolution memory
- lineage
- adaptive mutation
- checkpoint/recovery
- reproducibility
- report/export
- SAFE deployment artifact

ไม่รวมใน Core v1:

- production auto-promotion
- engine self-evolution
- cross-language mutation
- P2P swarm
- quantum-inspired search
- artificial-life infrastructure
- hardware-specific evolutionary kernels

---

## 3.2 Supported Runtime [NORMATIVE]

เพื่อหยุด ambiguity เรื่อง AST/typing/process semantics, rewrite นี้กำหนด runtime baseline ใหม่:

```yaml
python_runtime:
  implementation: "CPython"
  supported_minor: "3.12"
  version_policy: "latest security patch within 3.12.x"
  unsupported:
    - "PyPy"
    - "CPython < 3.12"
    - "CPython > 3.12 unless conformance matrix passes"
```

[REQ][REQ-S03-001] การรองรับ Python minor อื่นต้องผ่าน version-specific AST, subprocess, sandbox และ replay tests ก่อน

---

## 3.3 Dependency Groups [NORMATIVE]

```text
core_runtime:
  Python standard library only

validation_tooling:
  jsonschema
  type checker
  spec/schema linters

format_preserving_optional:
  LibCST

security_backend:
  Linux kernel namespaces
  cgroups v2
  seccomp backend
  container backend where required

crypto_backend_m12_m13:
  Ed25519 implementation
  secure key-storage adapter
  offline revocation verifier

development:
  pytest
  static analysis
  property-based testing tools

research:
  torch
  qiskit
  experimental optimizers
```

[REQ][REQ-S03-002] Core runtime ห้าม import Research group

[REQ][REQ-S03-003] Validation tooling สามารถเป็น third-party ได้ แต่ต้อง installable/offline-cacheable และไม่เป็น network dependency ระหว่าง evolution run

[REQ][REQ-S03-004] exact package versions ต้องถูก pin ใน lock artifact ก่อน M4

[REQ][REQ-S03-005] crypto backend เป็น required dependency เฉพาะ M12/M13, ต้อง pin/offline-cache และห้ามถูก import ใน candidate process; M11 ใช้ SHA-256 digest verification จาก Python standard library ได้โดยไม่ต้องมี signing key

---

# 4. Canonical Repository Layout [NORMATIVE]

```text
evolution-engine/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── SECURITY.md
├── CONTRIBUTING.md
│
├── spec/
│   ├── authority.yaml
│   ├── version_manifest.yaml
│   ├── requirements.yaml
│   ├── traceability.yaml
│   ├── maturity.yaml
│   ├── release_gates.yaml
│   ├── fsm/
│   │   ├── candidate.yaml
│   │   ├── run.yaml
│   │   ├── deployment.yaml
│   │   ├── recovery.yaml
│   │   └── governance.yaml
│   ├── measurement/
│   │   ├── protocol.yaml
│   │   └── reproducibility.yaml
│   └── sandbox/
│       ├── profile-a-linux.yaml
│       ├── mounts.yaml
│       ├── env-allowlist.yaml
│       └── negative-tests.yaml
│
├── schemas/
│   └── <26 canonical schemas>
│
├── src/evolution_engine/
│   ├── core/
│   ├── project/
│   ├── analysis/
│   ├── mutation/
│   ├── population/
│   ├── execution/
│   ├── testing/
│   ├── metrics/
│   ├── selection/
│   ├── memory/
│   ├── lineage/
│   ├── recovery/
│   ├── evidence/
│   ├── policy/
│   ├── deployment/
│   └── protocols/
│
├── migrations/
├── benchmarks/golden/
├── tools/
│   ├── render_active_spec.py
│   └── validate_schemas.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── conformance/
│   ├── security/
│   ├── recovery/
│   ├── replay/
│   └── golden/
└── runtime/
```

[REQ][REQ-S04-001] generated Active-Spec View ห้าม commit เป็น source of truth; ถ้า repository เลือก commit เพื่อ review ต้องมี CI regeneration check ตาม Section 0.5

---

# 5. Project Contract & Configuration [NORMATIVE]

## 5.1 Project Layout [NORMATIVE]

```text
target-project/
├── src/
├── tests/
├── benchmark/
├── evolution.yaml
└── pyproject.toml
```

[REQ][REQ-S05-001] Candidate mutation ห้ามแก้ immutable evaluation assets เว้นแต่ project policy ระบุ explicit governed mutability

---

## 5.2 Canonical Command Model [NORMATIVE]

Raw shell strings ถูกยกเลิกจาก active contract

Command object:

```yaml
command:
  argv: ["python", "-m", "pytest", "tests"]
  cwd: "."
  env: {}
  timeout_seconds: 30
```

[REQ][REQ-S05-002] `shell=false` เสมอใน Core

[REQ][REQ-S05-003] `argv` เป็น list ของ strings

[REQ][REQ-S05-004] `cwd` ต้อง resolve ภายใน sandbox workspace

[REQ][REQ-S05-005] `env` ผ่าน allowlist เท่านั้น

[REQ][REQ-S05-006] ห้าม command substitution, shell pipe, redirect หรือ shell expansion ใน canonical command object

---

## 5.3 Canonical `evolution.yaml` [NORMATIVE]

```yaml
project:
  name: "example-project"
  language: "python"
  version: "1.0"

evolution:
  level: "function"
  population_size: 20
  seed: 12345

metrics:
  - name: "correctness"
    direction: "maximize"
    unit: "ratio"
    valid_range:
      minimum_decimal: "0"
      maximum_decimal: "1"
    practical_margin_decimal: "0.001"
    failure_policy: "invalidate_candidate"
    preference_weight_decimal: "0.7"
    command:
      argv: ["python", "benchmark/correctness.py"]
      cwd: "."
      env: {}
      timeout_seconds: 30

  - name: "latency_ms"
    direction: "minimize"
    unit: "ms"
    valid_range:
      minimum_decimal: "0"
      maximum_decimal: "60000"
    practical_margin_decimal: "1.0"
    failure_policy: "invalidate_candidate"
    preference_weight_decimal: "0.3"
    command:
      argv: ["python", "benchmark/latency.py"]
      cwd: "."
      env: {}
      timeout_seconds: 30

selection:
  method: "pareto"
  preference_weights_usage: "same_front_tie_break_only"
  tie_break_order:
    - "pareto_rank"
    - "diversity_score"
    - "preference_score"
    - "canonical_candidate_id"

constraints:
  capability_commands:
    - argv: ["python", "-m", "pytest", "tests/capability"]
      cwd: "."
      env: {}
      timeout_seconds: 60

sandbox:
  profile: "PROFILE_A_LINUX"
  network: "deny"
  writable_tmp_bytes: 67108864

deployment:
  mode: "SAFE_EXPORT_ONLY"

stopping:
  target_rule: null
  max_generations: 100
  max_stagnation: 20
  max_runtime_seconds: 3600
```

---

## 5.4 Configuration Ownership, Resolution & Precedence [NORMATIVE]

Canonical owner ของ field ที่เคยซ้ำ:

| Field | Canonical owner |
|---|---|
| `level`, `population_size`, `seed` | `evolution` |
| `max_generations`, `max_stagnation`, `max_runtime_seconds`, `target_rule` | `stopping` |
| metric validity/margin/preference | each `metrics[]` item |
| selection/tie-break semantics | `selection` |
| isolation limits | `sandbox` |
| export/promotion behavior | `deployment` |

Resolved-config precedence จากต่ำไปสูง:

```text
1 engine defaults declared by engine_config schema version
2 project evolution.yaml
3 explicit schema-allowed CLI overrides
```

[REQ][REQ-S05-007] environment variables ห้าม override semantic configuration โดยปริยาย; env ที่อนุญาตต้องถูก map เป็น explicit field และบันทึก source provenance

[REQ][REQ-S05-008] YAML duplicate keys, unknown fields, deprecated aliasesร่วมกับ canonical field หรือ field ที่อยู่ผิด canonical owner = validation failure

[REQ][REQ-S05-009] CLI override อนุญาตเฉพาะ field ที่ schema ประกาศ `cli_overridable=true`; resolved value, original source และ override source ต้องถูกบันทึกก่อนเริ่ม run

[REQ][REQ-S05-010] resolved configuration ต้องผ่าน schema validationแล้ว canonicalize ก่อนคำนวณ `ConfigHash`; execution ห้ามอ่านค่าจาก untracked source หลัง hash ถูกสร้าง

[REQ][REQ-S05-011] decimal ที่มีผลต่อ hash เช่น margin, weight, rate และ threshold ต้องใช้ canonical decimal string ไม่ใช้ binary floating-point

[REQ][REQ-S05-012] `evolve validate --json` ต้องคืน resolved-config digest, provenance ต่อ field และ validation diagnostics โดยไม่เปิดเผย secret values

---

# 6. Public CLI & SDK [NORMATIVE]

## 6.1 Canonical CLI [NORMATIVE]

Canonical executable มีชื่อเดียว:

```text
evolve
```

Command surface:

```text
evolve init
evolve validate
evolve preflight
evolve run
evolve step
evolve status
evolve pause
evolve resume
evolve abort
evolve report
evolve export
evolve replay
evolve db migrate
evolve doctor
```

`evolve preflight` ผูกกับ Run state `PREFLIGHT_PASSED`, `evolve step` กับ `GENERATION_COMMITTED`
และ `evolve abort` กับ terminal state `ABORTED` ตาม `spec/fsm_states_57.yaml`
คำสั่ง `evolve stop` เดิมถูกเปลี่ยนชื่อเป็น `evolve abort` เพราะ Run FSM เลิกใช้สถานะหยุดแบบเดิมแล้ว และใช้ `ABORTED` แทน

[REQ][REQ-S06-001] legacy long-form executable name ไม่ใช่ canonical executable และห้ามใช้ใน active examples

Exit codes:

```text
0   success
2   invalid configuration/usage
10  validation failure
20  candidate/evaluation failure
30  security policy failure
40  persistence/recovery failure
50  evidence/release-gate failure
70  internal engine error
```

stdout/stderr:

- stdout = machine-readable or requested human output
- stderr = diagnostics
- `--json` ต้องให้ stable structured envelope

---

## 6.2 Canonical Python SDK [NORMATIVE]

Public class เดียว:

```text
EvolutionEngine
```

Required operations:

| Operation | Input | Output |
|---|---|---|
| create | config path/object | engine instance |
| validate_project | project path | ValidationReport |
| preflight | project path | PreflightReport |
| start_run | project path | RunId |
| step_run | RunId | GenerationSummary |
| pause_run | RunId | RunState |
| resume_run | RunId | RunState |
| abort_run | RunId | RunState |
| get_status | RunId | RunStatus |
| get_report | RunId | EvolutionReport |
| export_candidate | CandidateId, destination | ExportManifest |
| replay_run | RunId, target R-level | ReproducibilityCertificate |

SDK surface นี้เป็น synchronous และเป็น canonical เพียงชุดเดียว
เอกสารใน `docs/` ห้ามประกาศ surface ที่ต่างจากตารางนี้

[REQ][REQ-S06-002] Public API ห้ามคืน raw `dict`/`object` ใน stable surface

---

# 7. Canonical Types & Protocol Boundary [NORMATIVE]

## 7.1 Core Identifier Types [NORMATIVE]

```text
ProjectId
RunId
GenerationId
CandidateId
MutationId
EvaluationAttemptId
TestId
CapabilityId
ObjectiveId
EvidenceId
ArtifactId
CheckpointId
DeploymentId
ApprovalCertificateId
```

[REQ][REQ-S07-001] ID generation ต้อง deterministic เมื่อ identity เป็น content-derived และ random/monotonic เมื่อ identity เป็น event-derived

[REQ][REQ-S07-002] ID format และ collision behavior ต้องถูก schema-test ก่อน M4

---

## 7.2 Required Protocols [NORMATIVE]

| Protocol | Required Input | Required Output |
|---|---|---|
| ProjectAdapter | project path | ProjectManifest |
| SourceAnalyzer | immutable source snapshot | ProgramRepresentation |
| MutationStrategy | parent representation + MutationContext + RNG | MutationResult |
| MutationEngine | parent population + registry | CandidateDrafts |
| PopulationManager | candidates + selection decisions | PopulationSnapshot |
| SandboxManager | CandidateArtifact + SandboxRequest | SandboxExecutionResult |
| TestRunner | execution artifact + TestPlan | TestSuiteResult |
| CapabilityVerifier | test results + contract | CapabilityVerdict |
| OracleRunner | candidate + oracle plan | OracleVerdict |
| MetricRunner | candidate + objective | MetricMeasurement |
| ParetoSelector | eligible candidates + objectives | SelectionDecision |
| EvidenceStore | evidence inputs | EvidenceRecord |
| ArtifactStore | bytes + metadata | ArtifactRef |
| LineageRepository | lineage events | LineageSnapshot |
| CheckpointManager | run state | CheckpointRef |
| RecoveryManager | checkpoint + durable manifests | RecoveryResult |
| PolicyEngine | candidate context | PolicyVerdict |
| DeploymentManager | approved artifact + mode | DeploymentResult |
| AuditLog | audit event | AuditReceipt |

[REQ][REQ-S07-003] Protocol modelsต้องมี concrete dataclass/enum/schema counterpartsก่อน M4

---

# 8. Candidate Lifecycle & Evaluation Pipeline [NORMATIVE]

## 8.1 Canonical Candidate State Machine [NORMATIVE]

Candidate lifecycle state มีชุดเดียว:

```text
CREATED
MATERIALIZED
STATIC_VALIDATED
POLICY_VALIDATED
SECURITY_VALIDATED
SANDBOX_READY
EXECUTING
EXECUTED
TESTING
ORACLE_VERIFIED
CAPABILITY_VERIFIED
METRIC_EVALUATED
EVIDENCE_VERIFIED
ELIGIBLE
SELECTED
REJECTED
QUARANTINED
```

Execution outcome **ไม่ใช่ Candidate lifecycle state**:

```text
SUCCESS
TIMEOUT
CRASHED
OOM
RESOURCE_EXCEEDED
SECURITY_VIOLATION
```

Reason codes แยกจาก lifecycle state

Canonical transitions:

```text
CREATED -> MATERIALIZED | REJECTED
MATERIALIZED -> STATIC_VALIDATED | REJECTED
STATIC_VALIDATED -> POLICY_VALIDATED | REJECTED
POLICY_VALIDATED -> SECURITY_VALIDATED | REJECTED
SECURITY_VALIDATED -> SANDBOX_READY | QUARANTINED | REJECTED
SANDBOX_READY -> EXECUTING
EXECUTING -> EXECUTED | REJECTED | QUARANTINED
EXECUTED -> TESTING
TESTING -> ORACLE_VERIFIED | REJECTED
ORACLE_VERIFIED -> CAPABILITY_VERIFIED | REJECTED
CAPABILITY_VERIFIED -> METRIC_EVALUATED | REJECTED
METRIC_EVALUATED -> EVIDENCE_VERIFIED | REJECTED
EVIDENCE_VERIFIED -> ELIGIBLE | REJECTED
ELIGIBLE -> SELECTED | REJECTED | QUARANTINED
```

Terminal states:

```text
SELECTED
REJECTED
QUARANTINED
```

Disposition mapping:

```text
TIMEOUT/CRASHED/OOM/RESOURCE_EXCEEDED -> REJECTED
SECURITY_VIOLATION -> QUARANTINED
```

[REQ][REQ-S08-001] Retry สร้าง `EvaluationAttempt` ใหม่ แต่ห้ามเปลี่ยน failed attempt ให้เป็น PASS

---

## 8.2 Canonical Evaluation Ordering [NORMATIVE]

```text
1  Candidate Created
2  Materialize isolated snapshot
3  Static Validation
4  Policy Gate
5  Security Gate
6  Sandbox Provision
7  Execute
8  Behavior/Test Suite
9  Oracle Verification
10 Capability Verification
11 Metric Measurement
12 Metric Validation/Normalization
13 Evidence Construction
14 Eligibility Decision
15 Pareto/Trade-off Selection
```

[REQ][REQ-S08-002] Candidate ที่ไม่ผ่านขั้นก่อนหน้า ห้ามได้ optimization score จากขั้นหลัง

---

## 8.3 Canonical Run State Machine [NORMATIVE]

Run states:

```text
INITIATED
CONFIG_LOADED
PREFLIGHT_PASSED
RUNNING
PAUSED
GENERATION_COMMITTED
CHECKPOINTING
COMPLETED
FAILED
ABORTED
RECOVERING
```

Canonical transitions:

```text
INITIATED -> CONFIG_LOADED
CONFIG_LOADED -> PREFLIGHT_PASSED | FAILED
PREFLIGHT_PASSED -> RUNNING | FAILED
RUNNING -> PAUSED | GENERATION_COMMITTED | FAILED | ABORTED
PAUSED -> RUNNING | ABORTED
GENERATION_COMMITTED -> RUNNING | CHECKPOINTING
CHECKPOINTING -> COMPLETED | FAILED
RECOVERING -> RUNNING | COMPLETED | FAILED
<any non-terminal state> -> RECOVERING
```

`<any non-terminal state> -> RECOVERING` เกิดได้เฉพาะตอน coordinator restart พบ unclean run เท่านั้น

Terminal states:

```text
COMPLETED
FAILED
ABORTED
```

[REQ][REQ-S08-003] `pause_run` รับได้เฉพาะ `RUNNING`; `resume_run` รับได้เฉพาะ `PAUSED`; `abort_run` รับได้จาก `RUNNING` หรือ `PAUSED` เท่านั้น

[REQ][REQ-S08-004] คำสั่งซ้ำที่ state เป้าหมายอยู่แล้วต้องตอบแบบ idempotent พร้อม audit receipt แต่ห้ามสร้าง state transition ปลอม

[REQ][REQ-S08-005] invalid Run transition ต้องถูกปฏิเสธด้วย persistence/recovery error class และบันทึก attempted transition โดยห้ามแก้ durable state

[REQ][REQ-S08-006] startup ที่พบ unclean non-terminal run ต้องเข้า `RECOVERING` ก่อน execute candidate เพิ่ม

---

## 8.4 Canonical Recovery State Machine [NORMATIVE]

Recovery states:

```text
DETECT_CRASH
SCAN_WAL_AND_CAS
VERIFY_LAST_GEN_HASH
ROLLBACK_UNCOMMITTED
REPLAY_COMMITTED
ENTER_EMERGENCY_SAFE_MODE
RECONSTRUCT_FROM_CAS
RECONCILE_DB_STATE
RESTORED_READY
```

Canonical transitions:

```text
DETECT_CRASH -> SCAN_WAL_AND_CAS
SCAN_WAL_AND_CAS -> VERIFY_LAST_GEN_HASH
VERIFY_LAST_GEN_HASH -> ROLLBACK_UNCOMMITTED | ENTER_EMERGENCY_SAFE_MODE
ROLLBACK_UNCOMMITTED -> REPLAY_COMMITTED
REPLAY_COMMITTED -> RECONCILE_DB_STATE
ENTER_EMERGENCY_SAFE_MODE -> RECONSTRUCT_FROM_CAS
RECONSTRUCT_FROM_CAS -> RECONCILE_DB_STATE
RECONCILE_DB_STATE -> RESTORED_READY | ENTER_EMERGENCY_SAFE_MODE
```

Terminal states:

```text
RESTORED_READY
```

Recovery ที่จบไม่ได้จะค้างอยู่ที่ `ENTER_EMERGENCY_SAFE_MODE` ซึ่งต้องมี operator ตัดสินใจ ไม่ใช่ retry อัตโนมัติ

[REQ][REQ-S08-007] `RESTORED_READY` ต้องคืน verified resume target (`RUNNING`, `PAUSED` หรือ `COMPLETED`) และ recovery evidence; ห้าม infer เป้าหมายจาก unverified cache

[REQ][REQ-S08-008] digest mismatch, audit gap ที่ repair ไม่ได้, ambiguous generation head หรือ policy/environment mismatch ต้องไป `ENTER_EMERGENCY_SAFE_MODE` ไม่ใช่ retry-as-success

[REQ][REQ-S08-009] Recovery step ต้อง idempotent และบันทึก input/output digest เพื่อ resume หลัง crash ได้โดยไม่ทำ durable record ซ้ำ

---

## 8.5 Canonical Governance State Machine [NORMATIVE]

Governance states:

```text
PROPOSAL_SUBMITTED
LINTERS_PASSED
IMPACT_ANALYZED
MULTI_PARTY_REVIEW
VOTING_OPEN
QUORUM_REACHED
SIGNATURES_COLLECTED
RATIFIED_CANONICAL
SCHEMA_MIGRATED
EVIDENCE_ARCHIVED
REJECTED
SUPERSEDED
```

Canonical transitions:

```text
PROPOSAL_SUBMITTED -> LINTERS_PASSED | REJECTED
LINTERS_PASSED -> IMPACT_ANALYZED | REJECTED
IMPACT_ANALYZED -> MULTI_PARTY_REVIEW | REJECTED
MULTI_PARTY_REVIEW -> VOTING_OPEN | REJECTED
VOTING_OPEN -> QUORUM_REACHED | REJECTED
QUORUM_REACHED -> SIGNATURES_COLLECTED | REJECTED
SIGNATURES_COLLECTED -> RATIFIED_CANONICAL | REJECTED
RATIFIED_CANONICAL -> SCHEMA_MIGRATED
SCHEMA_MIGRATED -> EVIDENCE_ARCHIVED
EVIDENCE_ARCHIVED -> SUPERSEDED
```

`EVIDENCE_ARCHIVED -> SUPERSEDED` ถูก trigger จากการ ratify proposal ใหม่ที่แทนที่ฉบับนี้ ไม่ใช่จากตัว proposal เอง

Terminal states:

```text
REJECTED
SUPERSEDED
```

[REQ][REQ-S08-010] change author ห้ามเป็น sole approver ของ change ที่กระทบ L0-L3; reviewer identity, role, decision และ proposal digest ต้องอยู่ใน audit evidence

[REQ][REQ-S08-011] `RATIFIED_CANONICAL` ต้อง bind exact spec version, changed Requirement IDs, invalidated evidence และ gate results; approval ของ digest เก่าห้ามใช้กับเนื้อหาใหม่

[REQ][REQ-S08-012] `spec/fsm/run.yaml`, `recovery.yaml` และ `governance.yaml` ต้อง encode state/transition/terminal sets ตรง section นี้และผ่าน reachability, illegal-transition และ terminal-state tests

---

# 9. Program Representation & Mutation [NORMATIVE]

## 9.1 Representation Authority [NORMATIVE]

```text
AST = semantic structure / core identity input
CST = optional format-preserving rewrite
CFG = analysis aid
SSA = optional analysis aid
Source bytes = exported artifact identity
```

[REQ][REQ-S09-001] ห้าม import target project ใน host process เพื่อวิเคราะห์ source

[REQ][REQ-S09-002] static parse เป็น default discovery path

---

## 9.2 Mutation Families [NORMATIVE]

Core mutation registryเริ่มด้วย:

```text
M01 constant mutation
M02 operator mutation
M03 condition/boundary mutation
M04 loop/control-flow mutation
M05 function-call replacement
M06 function extraction
M07 function inlining/combination
M08 data-structure replacement
```

Module/project mutation M09+ ไม่เป็น M9 maturity requirement จนกว่า Function-level Core ผ่านก่อน

[REQ][REQ-S09-003] ทุก mutation บันทึก:

```text
mutation_id
strategy_id
parent_candidate_id
seed
parameters
source_before_hash
source_after_hash
structural_delta
```

---

## 9.3 Adaptive Mutation [NORMATIVE]

Core default algorithm:

```text
UCB1 with non-zero exploration floor
```

[REQ][REQ-S09-004] reward ต้องมาจาก valid, capability-preserving candidate เท่านั้น

[REQ][REQ-S09-005] research algorithms เช่น Thompson Sampling, Bayesian search, island model ห้ามเปลี่ยน Core selection semantics โดยไม่ผ่าน governed spec change

---

# 10. Metrics, Statistics & Selection [NORMATIVE]

## 10.1 Metric Value Rules [NORMATIVE]

Metric definition:

```text
name
direction = maximize|minimize
unit
measurement command
valid range
failure policy
practical margin
```

Invalid metric values:

```text
NaN
Infinity
-Infinity
missing required metric
unit mismatch
```

ทั้งหมดให้ candidate metric verdict = INVALID

---

## 10.2 Canonical Sampling Protocol [NORMATIVE]

Measurement state machine:

```text
WARMUP
-> FAST_SCREEN
-> CONFIRMATORY
-> MULTIPLE_COMPARISON_CORRECTION
-> RELEASE_CERTIFICATION
```

Defaults:

```yaml
warmup_runs: 5
fast_screen_samples: 5
confirmatory_min_samples: 30
confirmatory_max_samples: 200
family_alpha_decimal: "0.001"
multiple_comparison: "Holm-Bonferroni"
equivalence_alpha_decimal: "0.05"
```

[REQ][REQ-S10-001] Sequential stopping อนุญาตเฉพาะเมื่อ stopping rule ถูกประกาศก่อนเริ่ม measurement

---

## 10.3 Difference vs Equivalence [NORMATIVE]

[REQ][REQ-S10-002] Welch-style difference test ใช้เพื่อตรวจ “แตกต่างหรือไม่”

[REQ][REQ-S10-003] TOST หรือ confidence-interval equivalence rule ใช้เพื่อตรวจ “equivalent/non-inferior”

[REQ][REQ-S10-004] ห้ามใช้ `p < threshold` จาก difference test เป็นหลักฐาน equivalence

Equivalence ต้องมี project-owned margin เช่น:

```yaml
equivalence_margin:
  latency_pct_decimal: "1.0"
  memory_pct_decimal: "1.0"
```

---

## 10.4 Direction-Aware Better Rule [NORMATIVE]

สำหรับ maximize:

```text
candidate_lower_bound > baseline + practical_margin
```

สำหรับ minimize:

```text
candidate_upper_bound < baseline - practical_margin
```

[REQ][REQ-S10-005] Selection engine ห้ามใช้ comparison operator เดียวกับทุก metric

---

## 10.5 Pareto & Diversity [NORMATIVE]

Eligibility ก่อน Pareto:

```text
policy pass
security pass
test pass
oracle acceptable
capability pass
required metrics valid
evidence complete
```

Diversity components ต้อง normalize เป็น `[0,1]` ก่อน weighted combination:

```text
normalized AST distance
normalized token distance
behavioral distance
```

Default diversity score:

```text
DiversityScore = (ASTDistance + TokenDistance + BehavioralDistance) / 3
```

ถ้า project override diversity weights ต้องระบุครบทุก component เป็น canonical decimal string ที่ไม่ติดลบและรวมกันเท่ากับ `1` แบบ exact decimal

Metric preference score ใช้ normalized objective utility:

```text
maximize: utility_i = clamp((estimate_i - min_i) / (max_i - min_i), 0, 1)
minimize: utility_i = 1 - clamp((estimate_i - min_i) / (max_i - min_i), 0, 1)

PreferenceScore = sum(preference_weight_i * utility_i)
```

Canonical selection order:

```text
1 eligibility gates
2 Pareto front/rank using objective direction; metric weights ignored
3 higher DiversityScore within the same Pareto front
4 higher PreferenceScore only when Pareto rank and canonicalized DiversityScore tie
5 lexicographically smaller canonical CandidateId
```

[REQ][REQ-S10-006] `preference_weight_decimal` ห้ามเปลี่ยน eligibility, confidence/equivalence verdict หรือ Pareto dominance

[REQ][REQ-S10-007] ถ้ามี metric weight อย่างน้อยหนึ่งตัว ต้องมีครบทุก required objective, ทุกค่าไม่ติดลบ และผลรวม exact decimal เท่ากับ `1`; ไม่ครบหรือรวมผิด = invalid configuration

[REQ][REQ-S10-008] valid range ที่ใช้ normalize ต้องถูก freeze ก่อนเริ่ม run, ต้องมี `max > min` และห้ามเรียนรู้ range จาก candidate population เดียวกัน

[REQ][REQ-S10-009] Pareto comparison, diversity score และ preference score ต้องคำนวณด้วย deterministic Decimal/rational semantics ที่ versioned ใน measurement contract

[REQ][REQ-S10-010] tie-break สุดท้ายต้องใช้ canonical CandidateId order เสมอเพื่อให้ replay deterministic

---

# 11. Canonical Serialization, Identity & Reproducibility [NORMATIVE]

## 11.1 Hash-Critical Serialization [NORMATIVE]

เพื่อหลีกเลี่ยง conflict เรื่อง float 6 decimals vs lossless float:

[REQ][REQ-S11-001] **Hash-critical manifests ห้ามใช้ binary floating-point fields**

ใช้:

- integer สำหรับ count/bytes/ns
- decimal string สำหรับ exact decimal measurement
- enum/string สำหรับ categorical values

Canonical JSON rules:

```text
UTF-8
Unicode NFC
object keys sorted lexicographically
no duplicate keys
no NaN/Infinity
timestamps UTC RFC3339 with Z
relative POSIX paths
no insignificant whitespace
```

[REQ][REQ-S11-002] canonical serializer ต้องมี golden byte test vectors

[REQ][REQ-S11-003] กฎ canonical bytes ทั้งชุดอยู่ที่ `spec/reproducibility.yaml` (rank 1) ซึ่งตรึง null-vs-absent, integer bound, escaping, decimal form และ trailing newline เพิ่มจากแปดข้อข้างบน; reference implementation คือ `tools/canonical_bytes.py` และ golden vectors อยู่ที่ `tests/golden/canonical_bytes_vectors.json`

---

## 11.2 Content Identity [NORMATIVE]

```text
ArtifactHash = SHA-256(canonical bytes)
ConfigHash = SHA-256(canonical config)
EnvironmentHash = SHA-256(canonical environment manifest)
PolicyHash = SHA-256(canonical policy snapshot)
EvidenceDigest = SHA-256(canonical evidence envelope)
CandidateId = SHA-256(canonical bytes ของ candidate identity envelope)
GenerationId = SHA-256(canonical bytes ของ {run_id, generation_index})
```

[REQ][REQ-S11-004] identifier ทุกตัวต้องประกาศใน `spec/reproducibility.yaml` ว่าเป็น content-derived หรือ event-derived; content-derived ต้องมีสูตรและ representation ที่ตรึงแล้ว และห้ามใช้ค่าสุ่ม เพราะ REQ-S10-010 ใช้ลำดับของ `CandidateId` เป็น tie-break สุดท้าย

---

## 11.3 Reproducibility Levels [NORMATIVE]

```text
R0 Replayable
R1 Logical Deterministic
R2 Metric Reproducible
R3 Statistically Equivalent
R4 Bit-Identical Artifact
```

R4 scope:

```text
source bytes
canonical manifests
selected candidate identity
artifact bytes
```

R4 **ไม่** หมายถึง wall-clock timing และ host timestamps ต้องตรงทุกบิต

[REQ][REQ-S11-005] R0–R4 ต้องมีนิยามเชิงปฏิบัติและวิธีตรวจต่อระดับใน `spec/reproducibility.yaml`; ระดับที่ทำได้จริงต่อ run ต้องบันทึกที่คอลัมน์ `runs.reproducibility_level` และเป้าหมายที่ประกาศไว้ที่ `runs.reproducibility_target`

---

# 12. Sandbox & Security [NORMATIVE]

## 12.1 Security Matrix [NORMATIVE]

```text
Linux   PROFILE_A  Full supported security baseline
macOS   PROFILE_C  Development-only limited isolation
Windows PROFILE_D  Unsupported for secure candidate execution
```

[REQ][REQ-S12-001] Secure release evidenceต้องมาจาก `PROFILE_A`

---

## 12.2 PROFILE_A_LINUX Invariants [NORMATIVE]

[REQ][REQ-S12-002] Linux sandbox ต้อง:

- run as unprivileged identity
- use user namespace where supported by deployment model
- use mount namespace
- use PID namespace
- use network namespace
- use IPC namespace
- use cgroups v2
- apply `no_new_privs`
- drop ambient/effective capabilities
- expose candidate workspace read-only except declared writable temp
- deny host credential paths
- deny container runtime sockets
- deny host network
- deny privileged device access
- close/invalidate inherited file descriptors
- kill process tree on timeout
- record kernel-enforced violation reason

[REQ][REQ-S12-003] Python socket monkeypatch ไม่ถือเป็น security boundary

---

## 12.3 Mount Policy [NORMATIVE]

```yaml
mounts:
  candidate_source:
    mountpoint: "/workspace"
    access: "read-only"

  temp:
    mountpoint: "/tmp"
    type: "tmpfs"
    max_bytes: 67108864
    flags: ["noexec", "nosuid", "nodev"]

  proc:
    mode: "restricted"

denied:
  - "/var/run/docker.sock"
  - "/run/podman/podman.sock"
  - "/run/containerd/containerd.sock"
  - "~/.ssh"
  - "~/.aws"
  - "~/.kube"
  - "~/.gnupg"
  - "/proc/kcore"
  - "/sys/firmware"
```

[REQ][REQ-S12-004] symlink/hardlink/path traversal ต้อง resolve หลัง canonical path check ภายใน sandbox root

---

## 12.4 Seccomp Policy [NORMATIVE]

เอกสารนี้ **ไม่ freeze syscall allowlist แบบสั้นที่อาจรัน CPython ไม่ได้**

Canonical rule:

[REQ][REQ-S12-005] `seccomp-bootstrap` และ `seccomp-candidate` เป็น profile แยกกัน

[REQ][REQ-S12-006] profiles ต้องถูกสร้าง/ทดสอบกับ CPython 3.12 และ supported Linux kernel matrix

[REQ][REQ-S12-007] default action = deny/kill ตาม severity policy

[REQ][REQ-S12-008] forbidden capability classesต้องครอบคลุมอย่างน้อย:

```text
ptrace
mount manipulation
namespace escape
kernel module loading
bpf/perf privilege paths
raw device access
container runtime sockets
host credential access
```

[REQ][REQ-S12-009] exact syscall listsเป็น generated/tested artifact ไม่ใช่ prose claim

---

## 12.5 Candidate Subprocess Policy [NORMATIVE]

Default Core:

```text
candidate subprocess = DENY
```

Project ที่จำเป็นต้อง spawn subprocess ต้องเลือก explicit sandbox profile ที่:

- กำหนด `pids.max`
- กำหนด executable allowlist
- ไม่เปิด host namespace
- ยังปิด network/credentials
- ผ่าน security corpus

---

## 12.6 PROFILE_A Linux & Container Conformance Matrix [NORMATIVE]

Canonical Core v1 release architecture คือ `x86_64`; `arm64` เป็น provisional จนกว่าจะผ่าน matrix เดียวกันครบ

Patch level ไม่ถูก freeze ใน prose นี้ แต่แต่ละ release ต้อง pin image/kernel/runtime digest และใช้ latest security patch ที่มีใน kernel line นั้น ณ วันที่สร้าง evidence

| Lane | Kernel line | Sandbox backend | Architecture | Required purpose |
|---|---|---|---|---|
| A1 | Linux 6.1 LTS | native namespaces + cgroups v2 + seccomp | x86_64 | oldest supported baseline |
| A2 | Linux 6.6 LTS | rootless OCI reference backend | x86_64 | container compatibility |
| A3 | Linux 6.12 LTS | native namespaces + cgroups v2 + seccomp | x86_64 | newer LTS compatibility |
| A4 | Linux 6.18 LTS | rootless OCI reference backend | x86_64 | current-LTS compatibility at Plan 10.2.2 freeze |

`rootless OCI reference backend` สำหรับ M6 ต้องใช้ `runc` ที่ pin exact version/digest ใน environment lock; runtime อื่นเป็น unsupported จนกว่าจะผ่าน corpus เดียวกัน

Required capability probes ก่อนรับ workload:

```text
user/mount/PID/network/IPC namespaces or equivalent pre-created rootless OCI isolation
cgroups v2 unified hierarchy with writable delegated subtree
seccomp filter mode
no_new_privs
capability drop verification
read-only bind/remount enforcement
tmpfs quota enforcement
process-tree kill and pids.max enforcement
network-deny verification
container-socket and credential-path denial
```

[REQ][REQ-S12-010] ทุก PROFILE_A lane ต้อง fail closed ก่อน materialize candidate เมื่อ capability probe ใดไม่ผ่าน; ห้าม downgrade อัตโนมัติเป็น PROFILE_C

[REQ][REQ-S12-011] release evidence ต้องบันทึก kernel release/build, architecture, relevant kernel capability probes, backend name/version/digest, cgroup mode, seccomp profile digest และ negative-corpus result

[REQ][REQ-S12-012] distribution kernel ใช้ได้เมื่ออยู่บน supported kernel line และผ่าน capability probes/negative corpus; version string เพียงอย่างเดียวไม่ถือเป็น evidence

[REQ][REQ-S12-013] การถอด kernel line หรือเพิ่ม backend/architecture ต้องผ่าน governed spec change และ re-run security/replay evidence ที่ได้รับผลกระทบ

> [INFORMATIVE] Kernel lines ใน matrix อิง longterm lines ที่ kernel.org แสดง ณ Plan 10.2.2; exact patch release ถูก pin ใน CI/environment manifest แทนการฝังเลข patch ที่ล้าสมัยในสเปก

---

## 12.7 Cryptographic & Trust Profile [NORMATIVE]

Canonical profile:

```yaml
profile_id: "EE-CRYPTO-1"
content_digest: "SHA-256"
signature_algorithm: "Ed25519"
public_key_encoding: "raw-32-byte-base64url-no-padding"
signature_encoding: "raw-64-byte-base64url-no-padding"
key_id: "SHA-256(raw_public_key)"
nonce_minimum_bits: 128
canonical_payload: "Section 11.1 canonical JSON"
```

Canonical signed envelope ก่อนเพิ่ม signature:

```text
profile_id
domain = "EvolutionEngine"
payload_type
payload_digest
signer_key_id
signer_role
issued_at_utc
expires_at_utc
nonce
proposal_or_evidence_context
```

Signature คำนวณเหนือ canonical bytes ของ envelope ข้างต้น; `signature` ไม่รวมอยู่ใน signed bytes ของตัวเอง

[REQ][REQ-S12-014] EE-CRYPTO-1 ห้าม algorithm negotiation; unknown profile/algorithm, malformed key/signature หรือ profile downgrade = verification failure

[REQ][REQ-S12-015] nonce ต้องมาจาก OS cryptographic RNG, ห้ามซ้ำภายใน signer key และ scope เดียวกัน และ verifier ต้อง reject replayed nonce

[REQ][REQ-S12-016] trust store ต้อง bind key ID, raw public key, allowed roles, validity interval, revocation state และ rotation lineage; boolean เช่น `trusted=true` ไม่ใช่หลักฐาน

[REQ][REQ-S12-017] private key ห้ามอยู่ใน candidate workspace, CAS, log หรือ evidence bundle; signing ต้องผ่าน isolated signer/key-storage adapter

[REQ][REQ-S12-018] verifier ต้องตรวจ canonical payload digest, signature, signer role, distinct signer IDs, quorum, validity/expiry, revocation, nonce replay และ exact proposal context ทุกครั้ง

[REQ][REQ-S12-019] M12 production approval ใช้ 2-of-3 distinct authorized Ed25519 keys; M13 trust manifest/evaluator promotion ต้องใช้ policy-defined quorum ที่อย่างน้อย 2-of-3 และห้ามต่ำกว่า M12

[REQ][REQ-S12-020] cryptographic test vectors ต้องมี valid, wrong payload, wrong domain, wrong role, duplicate signer, expired, revoked, malformed signature, nonce replay และ algorithm-downgrade cases

---

# 13. Persistence Model [NORMATIVE]

## 13.1 Storage Responsibilities [NORMATIVE]

```text
SQLite:
  relational metadata
  state
  decisions
  evidence references
  audit index

CAS:
  source snapshots
  immutable manifests
  test artifacts
  metric artifacts
  evidence payloads
  checkpoint payloads
```

[REQ][REQ-S13-001] ทุก generation ต้องมี durable generation manifest ใน CAS เพื่อให้ reconstruct DB ได้แม้ SQLite เสีย

---

## 13.2 Canonical 29-Table SQLite DDL [NORMATIVE]

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    project_version TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE RESTRICT,
    config_hash TEXT NOT NULL,
    policy_hash TEXT NOT NULL,
    environment_hash TEXT NOT NULL,
    run_state TEXT NOT NULL CHECK(run_state IN (
        'INITIATED','CONFIG_LOADED','PREFLIGHT_PASSED','RUNNING','PAUSED',
        'GENERATION_COMMITTED','CHECKPOINTING','COMPLETED','FAILED',
        'ABORTED','RECOVERING'
    )),
    seed_hex TEXT NOT NULL,
    reproducibility_target TEXT NOT NULL CHECK(reproducibility_target IN ('R0','R1','R2','R3','R4')),
    reproducibility_level TEXT CHECK(reproducibility_level IN ('R0','R1','R2','R3','R4')),
    created_at_utc TEXT NOT NULL
);

CREATE TABLE generations (
    generation_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    generation_index INTEGER NOT NULL CHECK(generation_index >= 0),
    manifest_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    status TEXT NOT NULL CHECK(status IN (
        'PREPARING','CAS_OBJECTS_DURABLE','DB_TRANSACTION_OPEN','DB_ROWS_WRITTEN',
        'DB_COMMITTED','GENERATION_MANIFEST_DURABLE','COMMITTED'
    )),
    UNIQUE(run_id, generation_index)
);

CREATE TABLE candidates (
    candidate_id TEXT PRIMARY KEY,
    generation_id TEXT NOT NULL REFERENCES generations(generation_id) ON DELETE CASCADE,
    source_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    source_hash TEXT NOT NULL,
    candidate_state TEXT NOT NULL CHECK(candidate_state IN (
        'CREATED','MATERIALIZED','STATIC_VALIDATED','POLICY_VALIDATED',
        'SECURITY_VALIDATED','SANDBOX_READY','EXECUTING','EXECUTED','TESTING',
        'ORACLE_VERIFIED','CAPABILITY_VERIFIED','METRIC_EVALUATED',
        'EVIDENCE_VERIFIED','ELIGIBLE','SELECTED','REJECTED','QUARANTINED'
    )),
    rejection_reason TEXT,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE candidate_parents (
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    parent_candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    parent_order INTEGER NOT NULL CHECK(parent_order >= 0),
    PRIMARY KEY(candidate_id, parent_candidate_id),
    UNIQUE(candidate_id, parent_order),
    CHECK(candidate_id <> parent_candidate_id)
);

CREATE TABLE population_memberships (
    generation_id TEXT NOT NULL REFERENCES generations(generation_id) ON DELETE CASCADE,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('PARENT','OFFSPRING','ELITE','SURVIVOR')),
    PRIMARY KEY(generation_id, candidate_id)
);

CREATE TABLE mutation_strategies (
    strategy_id TEXT PRIMARY KEY,
    strategy_version TEXT NOT NULL,
    risk_level TEXT NOT NULL CHECK(risk_level IN ('LOW','MEDIUM','HIGH')),
    enabled INTEGER NOT NULL CHECK(enabled IN (0,1)),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count >= 0),
    improvement_count INTEGER NOT NULL DEFAULT 0 CHECK(improvement_count >= 0)
);

CREATE TABLE mutation_attempts (
    mutation_attempt_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    strategy_id TEXT NOT NULL REFERENCES mutation_strategies(strategy_id) ON DELETE RESTRICT,
    parent_candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    rng_seed_hex TEXT NOT NULL,
    parameters_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    status TEXT NOT NULL CHECK(status IN ('CREATED','APPLIED','INVALID','FAILED'))
);

CREATE TABLE evaluation_attempts (
    evaluation_attempt_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    attempt_index INTEGER NOT NULL CHECK(attempt_index >= 0),
    execution_status TEXT NOT NULL CHECK(execution_status IN (
        'SUCCESS','TIMEOUT','CRASHED','OOM','RESOURCE_EXCEEDED','SECURITY_VIOLATION'
    )),
    exit_code INTEGER,
    wall_time_ns INTEGER CHECK(wall_time_ns IS NULL OR wall_time_ns >= 0),
    cpu_time_ns INTEGER CHECK(cpu_time_ns IS NULL OR cpu_time_ns >= 0),
    peak_rss_bytes INTEGER CHECK(peak_rss_bytes IS NULL OR peak_rss_bytes >= 0),
    stdout_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    stderr_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(candidate_id, attempt_index)
);

CREATE TABLE test_definitions (
    test_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    test_version TEXT NOT NULL,
    test_kind TEXT NOT NULL,
    definition_hash TEXT NOT NULL,
    UNIQUE(project_id, test_version)
);

CREATE TABLE test_results (
    test_result_id TEXT PRIMARY KEY,
    evaluation_attempt_id TEXT NOT NULL REFERENCES evaluation_attempts(evaluation_attempt_id) ON DELETE CASCADE,
    test_id TEXT NOT NULL REFERENCES test_definitions(test_id) ON DELETE RESTRICT,
    result_value TEXT NOT NULL CHECK(result_value IN ('PASS','FAIL','ERROR','FLAKY','SKIPPED','INCONCLUSIVE')),
    duration_ns INTEGER CHECK(duration_ns IS NULL OR duration_ns >= 0),
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(evaluation_attempt_id, test_id)
);

CREATE TABLE capability_definitions (
    capability_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    capability_version TEXT NOT NULL,
    required INTEGER NOT NULL CHECK(required IN (0,1)),
    definition_hash TEXT NOT NULL,
    UNIQUE(project_id, capability_version)
);

CREATE TABLE capability_results (
    capability_result_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    capability_id TEXT NOT NULL REFERENCES capability_definitions(capability_id) ON DELETE RESTRICT,
    verdict TEXT NOT NULL CHECK(verdict IN ('PASS','FAIL','INCONCLUSIVE')),
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(candidate_id, capability_id)
);

CREATE TABLE objective_definitions (
    objective_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    objective_version TEXT NOT NULL,
    name TEXT NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('maximize','minimize')),
    unit TEXT NOT NULL,
    practical_margin_decimal TEXT NOT NULL,
    UNIQUE(project_id, name, objective_version)
);

CREATE TABLE metric_results (
    metric_result_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    objective_id TEXT NOT NULL REFERENCES objective_definitions(objective_id) ON DELETE RESTRICT,
    sample_count INTEGER NOT NULL CHECK(sample_count >= 0),
    estimate_decimal TEXT NOT NULL,
    lower_bound_decimal TEXT,
    upper_bound_decimal TEXT,
    measurement_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(candidate_id, objective_id)
);

CREATE TABLE oracle_results (
    oracle_result_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    oracle_version TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('PASS','FAIL','INCONCLUSIVE','NOT_REQUIRED')),
    oracle_digest TEXT NOT NULL,
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(candidate_id, oracle_version)
);

CREATE TABLE selection_decisions (
    selection_decision_id TEXT PRIMARY KEY,
    generation_id TEXT NOT NULL REFERENCES generations(generation_id) ON DELETE CASCADE,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    decision TEXT NOT NULL CHECK(decision IN ('SELECTED','RETAINED','REJECTED')),
    reason_code TEXT NOT NULL,
    rank_index INTEGER CHECK(rank_index IS NULL OR rank_index >= 0),
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT
);

CREATE TABLE policy_snapshots (
    policy_snapshot_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    policy_version TEXT NOT NULL,
    policy_hash TEXT NOT NULL,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(run_id, policy_version)
);

CREATE TABLE environment_manifests (
    environment_manifest_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    environment_hash TEXT NOT NULL,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(run_id, environment_hash)
);

CREATE TABLE artifacts (
    artifact_id TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL UNIQUE,
    size_bytes INTEGER NOT NULL CHECK(size_bytes >= 0),
    media_type TEXT NOT NULL,
    cas_relative_path TEXT NOT NULL UNIQUE,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE artifact_refs (
    artifact_ref_id TEXT PRIMARY KEY,
    owner_type TEXT NOT NULL CHECK(owner_type IN (
        'PROJECT','RUN','GENERATION','CANDIDATE','MUTATION_ATTEMPT','EVALUATION_ATTEMPT',
        'TEST_RESULT','CAPABILITY_RESULT','METRIC_RESULT','ORACLE_RESULT',
        'SELECTION_DECISION','CHECKPOINT','RECOVERY','EVIDENCE','AUDIT','DEPLOYMENT'
    )),
    owner_id TEXT NOT NULL,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    ref_role TEXT NOT NULL,
    UNIQUE(owner_type, owner_id, artifact_id, ref_role)
);

CREATE TABLE lineage_edges (
    lineage_edge_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    parent_candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    child_candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    mutation_attempt_id TEXT REFERENCES mutation_attempts(mutation_attempt_id) ON DELETE SET NULL,
    relationship TEXT NOT NULL CHECK(relationship IN ('MUTATION','CROSSOVER','CLONE','ROLLBACK')),
    UNIQUE(parent_candidate_id, child_candidate_id, relationship)
);

CREATE TABLE checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    generation_id TEXT NOT NULL REFERENCES generations(generation_id) ON DELETE CASCADE,
    manifest_artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    random_state_artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE recovery_records (
    recovery_record_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE RESTRICT,
    checkpoint_id TEXT REFERENCES checkpoints(checkpoint_id) ON DELETE SET NULL,
    started_at_utc TEXT NOT NULL,
    finished_at_utc TEXT,
    recovery_status TEXT NOT NULL CHECK(recovery_status IN (
        'DETECT_CRASH','SCAN_WAL_AND_CAS','VERIFY_LAST_GEN_HASH',
        'ROLLBACK_UNCOMMITTED','REPLAY_COMMITTED','ENTER_EMERGENCY_SAFE_MODE',
        'RECONSTRUCT_FROM_CAS','RECONCILE_DB_STATE','RESTORED_READY'
    )),
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT
);

CREATE TABLE evidence_records (
    evidence_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE RESTRICT,
    candidate_id TEXT REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    evidence_type TEXT NOT NULL,
    evidence_digest TEXT NOT NULL,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    status TEXT NOT NULL CHECK(status IN ('CREATED','VERIFIED','INVALID','REVOKED')),
    created_at_utc TEXT NOT NULL
);

CREATE TABLE audit_events (
    audit_event_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES runs(run_id) ON DELETE RESTRICT,
    sequence_no INTEGER NOT NULL CHECK(sequence_no >= 0),
    previous_event_hash TEXT REFERENCES audit_events(event_hash) ON DELETE RESTRICT,
    event_hash TEXT NOT NULL UNIQUE,
    actor TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    created_at_utc TEXT NOT NULL,
    UNIQUE(run_id, sequence_no)
);

CREATE TABLE quarantine_records (
    quarantine_record_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    reason_code TEXT NOT NULL,
    security_profile_version TEXT NOT NULL,
    evidence_artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE deployments (
    deployment_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    deployment_mode TEXT NOT NULL CHECK(deployment_mode IN (
        'SAFE_EXPORT_ONLY','GOVERNED_CANARY','PRODUCTION_ACTIVE','SELF_EVOLUTION_SANDBOX'
    )),
    target_environment TEXT NOT NULL,
    deployment_state TEXT NOT NULL CHECK(deployment_state IN (
        'EXPORT_PREPARED','SIGNATURE_VERIFIED','PACKAGE_BUNDLED',
        'CANARY_PROVISIONED','CANARY_EVALUATING','PROMOTED_FULL_TRAFFIC',
        'ROLLED_BACK','ARCHIVED_PRODUCTION'
    )),
    config_hash TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE approval_certificates (
    approval_certificate_id TEXT PRIMARY KEY,
    deployment_id TEXT NOT NULL REFERENCES deployments(deployment_id) ON DELETE CASCADE,
    proposal_digest TEXT NOT NULL,
    signer_set_digest TEXT NOT NULL,
    quorum_required INTEGER NOT NULL CHECK(quorum_required > 0),
    quorum_verified INTEGER NOT NULL CHECK(quorum_verified IN (0,1)),
    expires_at_utc TEXT NOT NULL,
    certificate_artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT
);

-- Indices (56 Indices for Query Performance & Invariant Verification)
CREATE INDEX idx_runs_project ON runs(project_id);
CREATE INDEX idx_generations_run ON generations(run_id, generation_index);
CREATE INDEX idx_candidates_generation ON candidates(generation_id);
CREATE INDEX idx_candidate_parents_parent ON candidate_parents(parent_candidate_id);
CREATE INDEX idx_population_candidate ON population_memberships(candidate_id);
CREATE INDEX idx_mutation_candidate ON mutation_attempts(candidate_id);
CREATE INDEX idx_mutation_strategy ON mutation_attempts(strategy_id);
CREATE INDEX idx_mutation_parent ON mutation_attempts(parent_candidate_id);
CREATE INDEX idx_eval_candidate ON evaluation_attempts(candidate_id, attempt_index);
CREATE INDEX idx_test_def_project ON test_definitions(project_id);
CREATE INDEX idx_test_result_test ON test_results(test_id);
CREATE INDEX idx_capability_def_project ON capability_definitions(project_id);
CREATE INDEX idx_capability_result_capability ON capability_results(capability_id);
CREATE INDEX idx_objective_project ON objective_definitions(project_id);
CREATE INDEX idx_metric_objective ON metric_results(objective_id);
CREATE INDEX idx_oracle_candidate ON oracle_results(candidate_id);
CREATE INDEX idx_selection_candidate ON selection_decisions(candidate_id);
CREATE INDEX idx_policy_run ON policy_snapshots(run_id);
CREATE INDEX idx_environment_run ON environment_manifests(run_id);
CREATE INDEX idx_artifact_ref_artifact ON artifact_refs(artifact_id);
CREATE INDEX idx_artifact_ref_owner ON artifact_refs(owner_type, owner_id);
CREATE INDEX idx_lineage_parent ON lineage_edges(parent_candidate_id);
CREATE INDEX idx_lineage_child ON lineage_edges(child_candidate_id);
CREATE INDEX idx_lineage_run ON lineage_edges(run_id);
CREATE INDEX idx_checkpoint_run_generation ON checkpoints(run_id, generation_id);
CREATE INDEX idx_recovery_run ON recovery_records(run_id);
CREATE INDEX idx_recovery_checkpoint ON recovery_records(checkpoint_id);
CREATE INDEX idx_evidence_run ON evidence_records(run_id);
CREATE INDEX idx_evidence_candidate ON evidence_records(candidate_id);
CREATE INDEX idx_audit_run_sequence ON audit_events(run_id, sequence_no);
CREATE INDEX idx_quarantine_candidate ON quarantine_records(candidate_id);
CREATE INDEX idx_deployment_candidate_state ON deployments(candidate_id, deployment_state);
CREATE INDEX idx_approval_deployment ON approval_certificates(deployment_id);

-- Added: indices for ON DELETE RESTRICT parent scans and REQ-S13-005 query-plan assertions
CREATE INDEX idx_approval_certificates_certificate_artifact_id ON approval_certificates(certificate_artifact_id);
CREATE INDEX idx_audit_events_payload_artifact_id ON audit_events(payload_artifact_id);
CREATE INDEX idx_audit_events_previous_event_hash ON audit_events(previous_event_hash);
CREATE INDEX idx_candidates_source_artifact_id ON candidates(source_artifact_id);
CREATE INDEX idx_capability_results_evidence_artifact_id ON capability_results(evidence_artifact_id);
CREATE INDEX idx_checkpoints_generation_id ON checkpoints(generation_id);
CREATE INDEX idx_checkpoints_manifest_artifact_id ON checkpoints(manifest_artifact_id);
CREATE INDEX idx_checkpoints_random_state_artifact_id ON checkpoints(random_state_artifact_id);
CREATE INDEX idx_environment_manifests_artifact_id ON environment_manifests(artifact_id);
CREATE INDEX idx_evaluation_attempts_stderr_artifact_id ON evaluation_attempts(stderr_artifact_id);
CREATE INDEX idx_evaluation_attempts_stdout_artifact_id ON evaluation_attempts(stdout_artifact_id);
CREATE INDEX idx_evidence_records_artifact_id ON evidence_records(artifact_id);
CREATE INDEX idx_generations_manifest_artifact_id ON generations(manifest_artifact_id);
CREATE INDEX idx_lineage_edges_mutation_attempt_id ON lineage_edges(mutation_attempt_id);
CREATE INDEX idx_metric_results_measurement_artifact_id ON metric_results(measurement_artifact_id);
CREATE INDEX idx_mutation_attempts_parameters_artifact_id ON mutation_attempts(parameters_artifact_id);
CREATE INDEX idx_oracle_results_evidence_artifact_id ON oracle_results(evidence_artifact_id);
CREATE INDEX idx_policy_snapshots_artifact_id ON policy_snapshots(artifact_id);
CREATE INDEX idx_quarantine_records_evidence_artifact_id ON quarantine_records(evidence_artifact_id);
CREATE INDEX idx_recovery_records_evidence_artifact_id ON recovery_records(evidence_artifact_id);
CREATE INDEX idx_selection_decisions_evidence_artifact_id ON selection_decisions(evidence_artifact_id);
CREATE INDEX idx_selection_decisions_generation_id ON selection_decisions(generation_id);
CREATE INDEX idx_test_results_evidence_artifact_id ON test_results(evidence_artifact_id);

-- Added: engine-scoped audit events (run_id IS NULL) need sequence uniqueness too;
-- SQL treats each NULL as distinct so UNIQUE(run_id, sequence_no) does not cover them.
CREATE UNIQUE INDEX ux_audit_engine_sequence ON audit_events(sequence_no) WHERE run_id IS NULL;
```

[REQ][REQ-S13-002] ทุก direct artifact reference column ต้องมี Foreign Key ไป `artifacts(artifact_id)` พร้อม `ON DELETE RESTRICT`; nullable ได้เฉพาะ lifecycle stage ที่ artifact ยังไม่เกิด

[REQ][REQ-S13-003] `artifact_refs.owner_id` เป็น polymorphic reference จึงต้องมี generated integrity triggers หรือ transaction-level verifier ที่ fail commit เมื่อ owner ไม่มีจริง; conformance tests ต้องครอบคลุม owner type ทุกชนิด

[REQ][REQ-S13-004] canonical state/verdict/role vocabularies ใน DDL, FSM YAML, schemas และ typed enums ต้อง generate/compare จาก registry เดียว; mismatch = CI failure

[REQ][REQ-S13-005] ทุก migration install/upgrade ต้องรัน `PRAGMA foreign_key_check`, `PRAGMA integrity_check`, state-constraint negative tests และ query-plan assertions สำหรับ indexed foreign-key paths

[REQ][REQ-S13-006] timestamps, SHA-256 strings, decimal strings และ reason codes ที่ SQLite `CHECK` ตรวจได้ไม่ครบต้องถูก validate โดย typed boundary ก่อน transaction และทดสอบด้วย invalid fixtures

[REQ][REQ-S13-007] `approval_certificates.quorum_verified` เป็น derived cached resultที่เขียนได้เฉพาะ cryptographic verifier พร้อม certificate artifact; input/API caller ห้ามกำหนดค่าเอง

[REQ][REQ-S13-008] Schema migration filesต้องสร้างตามลำดับ immutable migration IDs

[REQ][REQ-S13-009] migration downgrade ที่ไม่ปลอดภัยต้องถูกปฏิเสธ

<!-- INTEGRITY_TRIGGERS_BEGIN -->

```sql
-- Integrity triggers (REQ-S13-003). Generated by tools/generate_integrity_triggers.py
-- from the DDL above; the owner_type -> table mapping is read out of the schema so a
-- trigger cannot reference a table or column that does not exist.

-- 1. Polymorphic owner validation for artifact_refs, covering all 16 owner types.
CREATE TRIGGER trg_artifact_refs_owner_exists
BEFORE INSERT ON artifact_refs
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN NEW.owner_type = 'AUDIT' AND NOT EXISTS (
                 SELECT 1 FROM audit_events WHERE audit_event_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in audit_events')
        WHEN NEW.owner_type = 'CANDIDATE' AND NOT EXISTS (
                 SELECT 1 FROM candidates WHERE candidate_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in candidates')
        WHEN NEW.owner_type = 'CAPABILITY_RESULT' AND NOT EXISTS (
                 SELECT 1 FROM capability_results WHERE capability_result_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in capability_results')
        WHEN NEW.owner_type = 'CHECKPOINT' AND NOT EXISTS (
                 SELECT 1 FROM checkpoints WHERE checkpoint_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in checkpoints')
        WHEN NEW.owner_type = 'DEPLOYMENT' AND NOT EXISTS (
                 SELECT 1 FROM deployments WHERE deployment_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in deployments')
        WHEN NEW.owner_type = 'EVALUATION_ATTEMPT' AND NOT EXISTS (
                 SELECT 1 FROM evaluation_attempts WHERE evaluation_attempt_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in evaluation_attempts')
        WHEN NEW.owner_type = 'EVIDENCE' AND NOT EXISTS (
                 SELECT 1 FROM evidence_records WHERE evidence_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in evidence_records')
        WHEN NEW.owner_type = 'GENERATION' AND NOT EXISTS (
                 SELECT 1 FROM generations WHERE generation_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in generations')
        WHEN NEW.owner_type = 'METRIC_RESULT' AND NOT EXISTS (
                 SELECT 1 FROM metric_results WHERE metric_result_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in metric_results')
        WHEN NEW.owner_type = 'MUTATION_ATTEMPT' AND NOT EXISTS (
                 SELECT 1 FROM mutation_attempts WHERE mutation_attempt_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in mutation_attempts')
        WHEN NEW.owner_type = 'ORACLE_RESULT' AND NOT EXISTS (
                 SELECT 1 FROM oracle_results WHERE oracle_result_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in oracle_results')
        WHEN NEW.owner_type = 'PROJECT' AND NOT EXISTS (
                 SELECT 1 FROM projects WHERE project_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in projects')
        WHEN NEW.owner_type = 'RECOVERY' AND NOT EXISTS (
                 SELECT 1 FROM recovery_records WHERE recovery_record_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in recovery_records')
        WHEN NEW.owner_type = 'RUN' AND NOT EXISTS (
                 SELECT 1 FROM runs WHERE run_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in runs')
        WHEN NEW.owner_type = 'SELECTION_DECISION' AND NOT EXISTS (
                 SELECT 1 FROM selection_decisions WHERE selection_decision_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in selection_decisions')
        WHEN NEW.owner_type = 'TEST_RESULT' AND NOT EXISTS (
                 SELECT 1 FROM test_results WHERE test_result_id = NEW.owner_id)
             THEN RAISE(ABORT, 'artifact_refs: owner_id not found in test_results')
    END;
END;

-- 2. Audit chain sequence must advance by exactly one, per run scope.
--    run_id IS NULL is the engine scope and is counted separately.
CREATE TRIGGER trg_audit_events_sequence_is_gapless
BEFORE INSERT ON audit_events
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN NEW.sequence_no != (
                 SELECT COALESCE(MAX(sequence_no) + 1, 0) FROM audit_events
                 WHERE run_id IS NEW.run_id)
             THEN RAISE(ABORT, 'audit_events: sequence_no must advance by exactly 1 with no gap')
    END;
END;

-- 3. A candidate in a terminal state is immutable.
CREATE TRIGGER trg_candidates_terminal_is_immutable
BEFORE UPDATE OF source_hash, generation_id, source_artifact_id ON candidates
FOR EACH ROW
WHEN OLD.candidate_state IN ('SELECTED', 'REJECTED', 'QUARANTINED')
BEGIN
    SELECT RAISE(ABORT, 'candidates: a terminal candidate cannot be modified');
END;

-- 4. Lineage must not contain a direct self loop.
CREATE TRIGGER trg_lineage_edges_no_self_loop
BEFORE INSERT ON lineage_edges
FOR EACH ROW
WHEN NEW.parent_candidate_id = NEW.child_candidate_id
BEGIN
    SELECT RAISE(ABORT, 'lineage_edges: a candidate cannot be its own parent');
END;
```

<!-- INTEGRITY_TRIGGERS_END -->

---

# 14. Atomic Commit, CAS & Recovery [NORMATIVE]

## 14.1 Generation Commit State Machine [NORMATIVE]

ห้ามเรียก SQLite + filesystem ว่า “atomic” โดยไม่มี recovery semantics

Canonical commit states:

```text
PREPARING
CAS_OBJECTS_DURABLE
DB_TRANSACTION_OPEN
DB_ROWS_WRITTEN
DB_COMMITTED
GENERATION_MANIFEST_DURABLE
COMMITTED
```

Crash recovery rule:

| Crash point | Recovery |
|---|---|
| before CAS durable | discard temp |
| after CAS durable, before DB commit | objects become unreferenced and GC-eligible after audit |
| during DB transaction | SQLite rollback + retry from durable input |
| after DB commit, before generation manifest | reconstruct manifest from committed rows + durable CAS |
| after generation manifest | idempotently mark COMMITTED |

[REQ][REQ-S14-001] CAS write = temp file -> fsync file -> atomic rename -> fsync parent directory

[REQ][REQ-S14-002] generation manifestต้องรวม candidate IDs, artifact hashes, policy hash, environment hash, RNG state hash และ selection decisions

---

## 14.2 Recovery Objectives [NORMATIVE]

Target:

```text
RPO <= 1 committed generation
RTO <= 60 seconds
```

แต่ target นี้ **ยังไม่ถือ TEST/EVID** จนกว่าจะมี benchmark envelope

Evidence ต้องระบุ:

```text
dataset bytes
artifact count
candidate count
storage type
host profile
recovery mode
measured RPO
measured RTO
```

---

# 15. Canonical Schema Package [NORMATIVE]

## 15.1 Exact 26 Schema Registry [NORMATIVE]

```text
01 candidate.schema.json
02 candidate_state.schema.json
03 mutation.schema.json
04 mutation_result.schema.json
05 population.schema.json
06 generation.schema.json
07 run.schema.json
08 baseline.schema.json
09 project_manifest.schema.json
10 capability_contract.schema.json
11 objective.schema.json
12 metric_result.schema.json
13 oracle_result.schema.json
14 environment.schema.json
15 lineage_node.schema.json
16 lineage_edge.schema.json
17 selection_decision.schema.json
18 policy_snapshot.schema.json
19 provenance_certificate.schema.json
20 reproducibility_certificate.schema.json
21 checkpoint.schema.json
22 recovery_manifest.schema.json
23 release_gate.schema.json
24 quarantine_record.schema.json
25 memory_record.schema.json
26 engine_config.schema.json
```

Current status:

```text
Schema registry defined:                        YES
26 physical schema files present:               YES  schemas/01..26
Draft 2020-12 validity:                         YES  26/26 compile
Offline $ref resolution:                        YES  no network required
spec/schema_manifest.json with real SHA-256:    YES  REQ-S15-003
Valid fixtures pass:                            YES  52 fixtures
Invalid fixtures fail:                          YES  244 fixtures
Two validator implementations agree:            YES  jsonschema + jsonschema-rs
Therefore schema maturity: M3 CONDITIONS MET
```

ตรวจซ้ำได้ด้วย `python3 tools/validate_schemas.py` หรือ `pytest tests/schema`

M3 ในบันได Section 23.1 ยังต้องรอ gate อื่นของระดับเดียวกันด้วย สถานะนี้ยืนยันเฉพาะเงื่อนไข
schema package ตาม REQ-S15-001 ถึง REQ-S15-006 เท่านั้น

[REQ][REQ-S15-001] M3 requires exactly 26 files, no missing/extra canonical schema name, Draft 2020-12 validity, valid fixtures pass และ invalid fixtures fail

---

## 15.2 M3 First-Delivery Boundary [NORMATIVE]

M3 เป็น implementation deliverable แรกหลัง spec-linter bootstrap:

```text
schemas/
  01..26 canonical schema files only

spec/
  schema_manifest.json

tests/schema/fixtures/
  <schema-name>/valid/*.json
  <schema-name>/invalid/*.json

tools/
  validate_schemas.py
```

Suggested internal build order โดยยังไม่ claim M3 จนกว่าจะครบทั้งหมด:

```text
1 engine_config + command/config primitives
2 identifiers + candidate/mutation/population/generation/run
3 project/capability/objective/metric/oracle
4 environment/lineage/selection/policy
5 provenance/reproducibility/checkpoint/recovery/release/quarantine/memory
6 full registry + cross-schema + fixture validation
```

[REQ][REQ-S15-002] ทุก schema ต้องประกาศ Draft 2020-12, stable offline-resolvable `$id`, explicit required fields และ `additionalProperties: false` โดย default; extension points ต้องใช้ field ที่ตั้งชื่อและกำหนด schema ชัดเจน

[REQ][REQ-S15-003] `spec/schema_manifest.json` ต้องมี registry order, filename, schema `$id`, schema version และ SHA-256 จาก bytes จริงของทั้ง 26 files

[REQ][REQ-S15-004] ทุก schema ต้องมีอย่างน้อยหนึ่ง minimal valid fixture, one representative complete valid fixture และ invalid fixtures ต่อ required field/type/enum/range/reference invariant ที่สำคัญ

[REQ][REQ-S15-005] cross-schema `$ref` ต้อง resolve จาก local registry โดยไม่มี network และ validator อย่างน้อยสอง implementation ต้องให้ผลตรงกันสำหรับ corpus เดียวกันก่อน M3

[REQ][REQ-S15-006] CI job `schema_registry_exact_26` ต้องนับเฉพาะ canonical `*.schema.json`; helper/manifest files ห้ามวางปะปนจนถูกนับเป็น schema ลำดับที่ 27

[REQ][REQ-S15-007] ห้าม merge full protocol, persistence หรือ sandbox implementation เข้าสู่ canonical branch จน M3 gateผ่าน; ทำ exploratory spike แยกได้แต่ห้ามใช้เป็น maturity evidence

---

# 16. Golden Corpus [NORMATIVE]

## 16.1 Corpus Registry [NORMATIVE]

ไม่มี fabricated hashes ใน active contract

> Canonical source of this registry: `benchmarks/golden/manifest.yaml`

| ID | Purpose | Expected disposition | Maturity bucket |
|---|---|---|---|
| MVP-01 | Pure Function Optimization (`pure-function-opt`) | `SELECTED` @ `R4` | CORE |
| MVP-02 | Stateful Class & Cache Mutation (`stateful-cache-mod`) | `SELECTED` @ `R4` | CORE |
| MVP-03 | Multi-Objective Latency vs Memory (`multi-objective-pareto`) | `SELECTED` @ `R2` | CORE |
| MVP-04 | Asyncio Coroutines & Non-blocking (`async-io-pipeline`) | `SELECTED` @ `R2` | CORE |
| MVP-05 | Multi-file Project DAG (`multi-file-dag-project`) | `SELECTED` @ `R1` | CORE |
| MVP-06 | Quantum Qubit Rotation Operator (`quantum-rotation-suite`) | `SELECTED` @ `R2` | RESEARCH |
| MVP-07 | Python -> Rust Native Compilation (`polyglot-rust-kernel`) | `SELECTED` @ `R1` | RESEARCH |
| MVP-08 | Filesystem Traversal Attack Vector (`sec-fs-escape-probe`) | `QUARANTINED` @ `R0` | SECURITY |
| MVP-09 | Network Egress Attack Vector (`sec-net-socket-probe`) | `QUARANTINED` @ `R0` | SECURITY |
| MVP-10 | Fork Bomb PID Exhaustion Attack (`sec-forkbomb-cgroup`) | `REJECTED` @ `R0` | SECURITY |
| MVP-11 | Flaky Test Non-Gaming Verification (`flaky-test-isolation`) | `REJECTED` @ `R0` | RELIABILITY |
| MVP-12 | 2PC Crash Recovery Chaos Test (`crash-during-commit`) | `RESTORED_READY` @ `R1` | RELIABILITY |
| MVP-13 | Byzantine Malicious Peer Rejection (`p2p-swarm-byzantine`) | `QUARANTINED` @ `R0` | RESEARCH |
| MVP-14 | Engine Self-Evolution Protection (`self-evaluator-freeze`) | `QUARANTINED` @ `R0` | SELF_EVOLUTION |

[REQ][REQ-S16-001] `baseline_hash` ถูกคำนวณจาก fixture bytes จริงตอน corpus build เท่านั้น

[REQ][REQ-S16-002] ห้ามใส่ placeholder hash ใน release evidence

---

## 16.2 Corpus Artifact Contract [NORMATIVE]

ทุก corpus case ต้องมี:

```text
fixture source
fixture version
canonical baseline hash
config
seed
environment manifest
expected lifecycle disposition
expected reason code
expected metrics or metric bounds
expected security verdict
expected evidence records
```

---

# 17. Flaky Tests, Holdout & Anti-Gaming [NORMATIVE]

## 17.1 Flaky Tests [NORMATIVE]

Flaky detection:

```text
same immutable candidate + same declared environment
produces inconsistent required test verdict
```

Disposition:

```text
test = FLAKY
candidate release verdict = INCONCLUSIVE
retry result cannot erase prior flaky evidence
```

[REQ][REQ-S17-001] projectสามารถ quarantine flaky test สำหรับ future repair แต่ release gateที่ต้องพึ่ง test นั้นห้าม PASS

---

## 17.2 Holdout Boundary [NORMATIVE]

```text
Search workload: visible to evolution loop
Validation workload: evaluator controlled
Hidden holdout: release-gate only
```

[REQ][REQ-S17-002] hidden inputs/outputs ห้ามเข้าสู่ Evolution Memory

[REQ][REQ-S17-003] candidate workspace ห้าม mount hidden holdout source

---

# 18. Audit & Evidence [NORMATIVE]

## 18.1 Audit Hash Chain [NORMATIVE]

Genesis:

```text
sequence_no = 0
previous_event_hash = null
```

Subsequent event:

```text
event_hash = SHA256(previous_event_hash || canonical_event_payload)
```

[REQ][REQ-S18-001] sequence allocation ต้อง serialize ต่อ run

[REQ][REQ-S18-002] crash recovery ต้อง detect duplicate/gap

[REQ][REQ-S18-003] audit verifierต้องสามารถ validate full chainจาก genesisถึง latest durable event

---

## 18.2 Evidence Bundle [NORMATIVE]

Release evidence bundle ต้องมี:

```text
active contract version
schema bundle digest
protocol package digest
FSM digests
policy digest
environment digest
test report digest
golden corpus manifest digest
security profile digest
reproducibility certificate
migration status
audit chain head
release-gate decision
signatures where required
```

---

# 19. Deployment & Governance [NORMATIVE]

## 19.1 Deployment Modes [NORMATIVE]

```text
SAFE_EXPORT_ONLY
GOVERNED_CANARY
PRODUCTION_ACTIVE
SELF_EVOLUTION_SANDBOX
```

Permissions:

| Mode | Auto replace production | Human approval | Maturity |
|---|---:|---:|---|
| SAFE_EXPORT_ONLY | No | No for export | M11 or lower |
| GOVERNED_CANARY | No direct promotion | Yes | M12 |
| PRODUCTION_ACTIVE | Only governed transition | Yes | M12 |
| SELF_EVOLUTION_SANDBOX | No production effect | Yes | M13 |

---

## 19.2 Deployment FSM [NORMATIVE]

```text
EXPORT_PREPARED -> SIGNATURE_VERIFIED | ROLLED_BACK
SIGNATURE_VERIFIED -> PACKAGE_BUNDLED | ROLLED_BACK
PACKAGE_BUNDLED -> CANARY_PROVISIONED | ARCHIVED_PRODUCTION | ROLLED_BACK
CANARY_PROVISIONED -> CANARY_EVALUATING | ROLLED_BACK
CANARY_EVALUATING -> PROMOTED_FULL_TRAFFIC | ROLLED_BACK
PROMOTED_FULL_TRAFFIC -> ARCHIVED_PRODUCTION | ROLLED_BACK
```

`PACKAGE_BUNDLED -> ARCHIVED_PRODUCTION` เป็นเส้นทางของ mode `SAFE_EXPORT_ONLY` ซึ่งจบโดยไม่แตะ traffic จริง

Terminal states:

```text
ARCHIVED_PRODUCTION
ROLLED_BACK
```

[REQ][REQ-S19-001] threshold violation ระหว่าง `CANARY_EVALUATING` ต้อง transition เป็น `ROLLED_BACK` โดยตรงและสร้าง rollback evidence; ห้ามผ่าน `PROMOTED_FULL_TRAFFIC`

[REQ][REQ-S19-002] invalid Deployment transition ต้อง fail closed และบันทึก attempted transition โดยห้ามแก้ target environment

[REQ][REQ-S19-003] `spec/fsm/deployment.yaml` ต้อง encode state/transition/terminal sets ตรง section นี้และผ่าน reachability, rollback-path, illegal-transition และ terminal-state tests

---

## 19.3 Approval Digest [NORMATIVE]

Approval ต้อง bind:

```text
candidate_id
source_hash
evidence_digest
environment_hash
policy_hash
target_environment
deployment_config_hash
release_gate_version
crypto_profile_id
nonce
expiry
```

[REQ][REQ-S19-004] Multisig quorumเป็น **computed verification result** ห้าม trust boolean จาก input

[REQ][REQ-S19-005] Production approval default = 2-of-3 distinct authorized signer keys

[REQ][REQ-S19-006] duplicate signer, expired key, revoked key, invalid signature หรือ wrong proposal digest = quorum fail

---

## 19.4 Canary Rollback [NORMATIVE]

Canonical initial thresholds:

```text
error_rate > 1.0%
p99_latency_regression > 15%
crash_count > 0
```

เงื่อนไขใดเงื่อนไขหนึ่งเป็นจริง -> automatic rollback from canary

[REQ][REQ-S19-007] threshold unitต้องเก็บเป็น fractionใน machine config:

```yaml
error_rate_fraction_max_decimal: "0.01"
p99_latency_regression_fraction_max_decimal: "0.15"
crash_count_max: 0
```

[REQ][REQ-S19-008] threshold comparison ต้องใช้ validated Decimal/integer values, declared observation window และ minimum sample/event countที่ bind อยู่ใน deployment config hash

---

## 19.5 Stateful Migration Safety [NORMATIVE]

Core production policyจนกว่าจะมี reversible migration framework:

```text
irreversible stateful production migrations = FORBIDDEN
```

Project-level source evolutionสามารถเปลี่ยน migration filesได้เฉพาะใน governed branch แต่ deployment gateต้องพิสูจน์ backward/forward compatibilityก่อนใช้จริง

---

# 20. Self-Evolution Root of Trust [NORMATIVE]

## 20.1 M13 Boundary [NORMATIVE]

Engine self-evolutionไม่เป็น requirementของ M11/M12

M13 candidate engine ห้าม modify:

```text
immutable evaluator
root policy
trust store
golden self-evolution evaluator corpus
release-gate verification code
```

---

## 20.2 Root-of-Trust Verification [NORMATIVE]

Verification must checkทั้งหมด:

```text
trusted signer/key provenance
evaluator digest
policy digest
self-evolution corpus digest
candidate source digest
candidate signature
environment digest
expiry/revocation state
```

[REQ][REQ-S20-001] ไม่มี field เช่น `trusted=true` หรือ `quorum_satisfied=true` ที่ใช้แทน cryptographic verificationได้

---

## 20.3 Trust Bootstrap Ceremony [NORMATIVE]

ก่อน M13 ต้องมี:

1. create initial trusted evaluator artifact
2. compute and publish evaluator digest
3. provision trust-store keys
4. record policy digest
5. record corpus digest
6. create signed genesis trust manifest
7. store offline backup
8. define key rotation
9. define key compromise recovery
10. define evaluator upgrade process requiring old-root approval

---

# 21. CI & Conformance Matrix [NORMATIVE]

Required jobs:

```text
spec_utf8_control_char_lint
spec_heading_classification_lint
spec_single_active_version_lint
spec_no_historical_normative_freeze_lint
spec_archive_checksum_match
spec_requirement_id_unique_and_complete
spec_requirement_digest_change_guard
schema_registry_exact_26
schema_meta_validation
schema_valid_invalid_vectors
protocol_type_check
fsm_reachability_and_terminal_tests
config_argv_only_validation
config_resolution_precedence_validation
config_decimal_and_weight_semantics
vertical_slice_deterministic_replay
unit_tests
integration_tests
sandbox_profile_a_capability_probes
sandbox_profile_a_kernel_backend_matrix
sandbox_negative_security_corpus
crypto_profile_test_vectors
golden_core
golden_security
golden_reliability
replay_tests
db_migration_tests
db_foreign_key_and_state_constraints
db_index_query_plan_assertions
db_cas_crash_injection
audit_chain_verification
traceability_completeness
release_evidence_bundle_validation
golden_self_evolution
canary_traffic_validation
rollback_demonstration
immutable_evaluator_checksum_proof
root_of_trust_bootstrap_ceremony
```

5 job ท้าย (`golden_self_evolution` ถึง `root_of_trust_bootstrap_ceremony`) รองรับ `GATE_PRODUCTION`
และ `GATE_SELF_EVOLUTION` ซึ่งเดิมไม่มี job ใดผลิตหลักฐานให้เลย รวมทั้งหมด 38 required jobs

[REQ][REQ-S21-001] Active plan itself ต้องผ่าน spec linters ก่อน implementation release

[REQ][REQ-S21-002] ทุก `mandatory_checks` ใน `spec/release_gates.yaml` ต้องอ้างชื่อ job ที่อยู่ใน section นี้เท่านั้น; ชื่อที่ resolve ไม่ได้ = CI failure

---

# 22. Traceability [NORMATIVE]

Canonical chain:

```text
Requirement ID
-> Spec Section
-> Schema/Data Contract
-> Protocol
-> Implementation Symbol
-> Test
-> Evidence
-> Release Gate
```

[REQ][REQ-S22-001] `spec/traceability.yaml` ต้องมี entry ต่อ active normative requirementก่อน M11

[REQ][REQ-S22-002] traceability entry ต้องใช้ stable ID จาก Section 2.4 และตรวจ `text_digest` กับ Active Specification; การจับคู่ด้วยลำดับบรรทัดหรือข้อความคล้ายกันอย่างเดียวห้ามใช้

[REQ][REQ-S22-003] Dangling reference = CI failure

[REQ][REQ-S22-004] Requirement ที่ยังไม่มี implementation/test/evidenceต้องถูกแสดงสถานะจริง ไม่ใช่ auto-PASS

---

# 23. Maturity Ladder [NORMATIVE]

## 23.1 M0–M13 [NORMATIVE]

```text
M0 DRAFT
  document parses as UTF-8
  no malformed control characters

M1 ARCHITECTURE
  architecture boundaries defined
  core/research split defined

M2 REQUIREMENTS_CANONICAL
  one active contract
  one active version
  every active requirement has a stable unique ID
  no conflicting active FSM/CLI/SDK definitions
  THIS DOCUMENT TARGETS THIS LEVEL

M3 SCHEMAS
  26/26 physical schemas
  valid/invalid schema fixtures pass

M4 PROTOCOLS
  typed protocol package complete
  Python runtime/dependencies pinned

M5 FSM_AND_CONFIG
  candidate/run/deployment/recovery/governance FSM tests pass
  argv-only config and resolved-precedence contract pass
  trusted-fixture vertical slice replays deterministically

M6 SECURITY
  PROFILE_A executable on required kernel/backend matrix
  capability probes fail closed
  negative security corpus passes

M7 PERSISTENCE
  29-table migration installs from empty DB
  FK/state/polymorphic-owner/invariant tests pass
  required index/query-plan assertions pass

M8 RECOVERY
  DB+CAS crash matrix passes
  reconstruction and audit recovery pass

M9 CORE_GOLDEN
  CORE corpus passes

M10 SECURITY_RELIABILITY_GOLDEN
  SECURITY + RELIABILITY corpus passes

M11 EXECUTION_READY
  GATE_CORE passes
  complete traceability
  evidence bundle generated
  NO requirement for production promotion
  NO requirement for self-evolution

M12 PRODUCTION
  governed canary
  approval verification
  rollback evidence
  production gate passes

M13 SELF_EVOLUTION
  root-of-trust bootstrap
  immutable evaluator
  MVP-14/self-evolution corpus
  governed self-evolution gate passes
```

---

# 24. Release Gates [NORMATIVE]

```text
GATE_CORE
  maturity >= M10
  schemas/protocols/FSM/persistence/security/replay pass
  core traceability complete
  evidence bundle valid

GATE_PRODUCTION
  GATE_CORE pass
  maturity >= M12
  multisig approval valid
  canary/rollback tests pass
  target-environment evidence valid

GATE_SELF_EVOLUTION
  GATE_CORE pass
  maturity >= M13
  root-of-trust verification pass
  immutable evaluator pass
  self-evolution corpus pass

GATE_RESEARCH
  independent from M11
  must not weaken Core firewall
```

[REQ][REQ-S24-001] M11 ไม่ได้หมายถึง “all possible gates pass”

---

# 25. Definition of Done [NORMATIVE]

## 25.1 Evolution Engine v1 [NORMATIVE]

ทุกข้อเริ่มต้นเป็น `[REQ]`:

```text
[REQ][REQ-S25-001] Python source parsing
[REQ][REQ-S25-002] Function AST mutation
[REQ][REQ-S25-003] Population generation
[REQ][REQ-S25-004] Isolated execution
[REQ][REQ-S25-005] Capability preservation
[REQ][REQ-S25-006] Project-defined metrics
[REQ][REQ-S25-007] Direction-aware multi-objective optimization
[REQ][REQ-S25-008] Pareto selection
[REQ][REQ-S25-009] Evolution Memory
[REQ][REQ-S25-010] Lineage Graph
[REQ][REQ-S25-011] Adaptive mutation
[REQ][REQ-S25-012] Diversity preservation
[REQ][REQ-S25-013] Stagnation handling
[REQ][REQ-S25-014] Checkpoint/recovery
[REQ][REQ-S25-015] Reproducible runs
[REQ][REQ-S25-016] SAFE export
[REQ][REQ-S25-017] Candidate rollback lineage
```

Definition of Doneจริง:

```text
ทุก requirement ที่อยู่ใน v1 scope
ต้องถึงอย่างน้อย TEST
และ GATE_CORE ต้องมี EVID bundle
```

---

## 25.2 Self-Evolution Definition of Done [NORMATIVE]

Self-evolutionไม่ถือ doneจากการที่ engine mutate sourceตัวเองได้

ต้องถึง M13 และมี:

```text
[REQ][REQ-S25-018] immutable evaluator
[REQ][REQ-S25-019] trust bootstrap ceremony
[REQ][REQ-S25-020] evaluator/corpus/policy digests
[REQ][REQ-S25-021] engine candidate isolation
[REQ][REQ-S25-022] self-evolution test corpus
[REQ][REQ-S25-023] governed approval
[REQ][REQ-S25-024] recovery from rejected/broken engine candidate
[REQ][REQ-S25-025] signed evidence
```

---

# 26. Items Explicitly Deferred [RESEARCH]

หัวข้อต่อไปนี้เก็บไว้เป็น research backlog และ **ไม่เป็น dependency ของ Core/M11**:

- multi-language evolution
- CPython bytecode mutation
- PyPy/JIT-specific evolution
- Rust/Go/C++ mutation
- AST subtree crossover beyond core experiments
- advanced island-model evolution
- distributed/P2P evolutionary swarm
- artificial-life ecosystem simulation
- quantum-inspired optimization
- Qiskit integration
- GPU/hardware-specific evolutionary kernels
- automated production autonomy beyond governed canary
- recursive self-evolution beyond M13 baseline

Research feature ที่กลับเข้าสู่ Core ต้องผ่าน governed spec change และเพิ่ม explicit requirement/test/evidence

---

# 27. Governed Specification Change [NORMATIVE]

Change workflow:

```text
Change Proposal
-> Impact Analysis
-> Authority Check
-> Security/Safety Review
-> Traceability Impact
-> Human Approval
-> Version Bump
-> Update Active Contract
-> Invalidate Affected Evidence
-> Re-run Required Gates
```

[REQ][REQ-S27-001] ห้ามแก้ conflict ด้วยการเพิ่ม new “canonical” section โดยปล่อย old active definitionไว้

[REQ][REQ-S27-002] ถ้า definition ถูกแทน ต้องแก้ source definition หรือย้ายของเก่าออกจาก active contract

---

# 28. Current Truth — What Exists vs What Is Required [NORMATIVE]

จากไฟล์ Plan อย่างเดียว สิ่งที่พิสูจน์ได้มีเพียง specification text

ดังนั้นสถานะปัจจุบัน:

```yaml
current_evidence_status:
  active_contract_unique: true
  historical_append_only_freezes_removed_from_active_contract: true
  candidate_fsm_unique_in_this_document: true
  run_fsm_unique_in_this_document: true
  recovery_fsm_unique_in_this_document: true
  governance_fsm_unique_in_this_document: true
  cli_unique_in_this_document: true
  sdk_unique_in_this_document: true
  requirement_id_contract_defined: true
  active_requirement_ids_defined: 179
  generated_active_view_contract_defined: true
  db_ddl_count_defined_in_this_document: 29
  schema_registry_count_defined_in_this_document: 26
  golden_registry_count_defined_in_this_document: 14

  physical_schema_files_verified: false
  protocol_package_verified: false
  migrations_verified: false
  sandbox_profile_verified: false
  golden_fixture_hashes_verified: false
  CI_results_verified: false
  release_evidence_verified: false

  maturity_claim: "M2_REQUIREMENTS_CANONICAL"
```

[REQ][REQ-S28-001] ห้ามเปลี่ยน `maturity_claim` เป็น M11 จนกว่า required evidence ถูกสร้างและตรวจจริง

---

# 29. Implementation Order [NORMATIVE]

ลำดับ implementation ที่ลด rework:

```text
1  M2 closure: spec linters + Requirement IDs + Active-Spec View + authority/version artifacts
2  M3: exact 26-schema package + manifest + valid/invalid fixtures
3  M4: typed protocols + public SDK/CLI + pinned runtime/dependencies
4  M5: candidate/run/recovery/governance/deployment FSMs + resolved config/argv model
5  mandatory trusted-fixture vertical slice (Section 29.1)
6  M6: PROFILE_A capability probes + kernel/backend matrix + negative security corpus
7  M7: 29-table migrations + FK/state/index tests + CAS
8  M8: atomic generation commit + checkpoint/recovery/replay/audit
9  expand source analysis + mutation from vertical M01/M02 to Core M01-M08
10 tests/capability/oracle + flaky/holdout boundary
11 metrics/statistics/Pareto/diversity/preference semantics
12 lineage/memory/evidence/report/export
13 M9: CORE golden corpus
14 M10: SECURITY + RELIABILITY corpus
15 GATE_CORE -> M11
16 EE-CRYPTO-1 + governed production/canary -> M12
17 root-of-trust self-evolution -> M13
```

---

## 29.1 Mandatory Trusted-Fixture Vertical Slice [NORMATIVE]

ก่อนสร้างระบบเต็ม ต้องมี walking skeleton ที่วิ่ง end-to-end ผ่าน public protocols โดย scope ตายตัว:

```yaml
fixture: "MVP-01 trusted pure function only"
evolution_level: "function"
mutation_strategies: ["M01", "M02"]
population_size: 4
generations: 1
seed: 12345
capability_tests: 1
objectives: 1
persistence_adapter: "in_memory_non_evidence"
deployment: "SAFE_EXPORT_ONLY to temporary directory"
```

Required path:

```text
load validated config
-> parse trusted fixture
-> create baseline + mutated candidates
-> reject static-invalid candidate
-> execute trusted fixture evaluator
-> capability gate
-> one metric
-> deterministic selection
-> record in-memory lineage/events
-> export selected source
-> replay same seed and compare canonical identities
```

[REQ][REQ-S29-001] vertical slice ต้องใช้ schema models, typed protocols, Run/Candidate FSM และ canonical serializer จริง ห้ามสร้าง temporary API/data shape ที่ทิ้งภายหลัง

[REQ][REQ-S29-002] in-memory adapter ใช้ได้เฉพาะ slice และห้ามสร้าง M6-M11 evidence; full 29-table persistence ไม่เป็น prerequisite ของ slice

[REQ][REQ-S29-003] slice อนุญาตเฉพาะ repository-owned trusted fixture และ evaluator; ห้ามรับ arbitrary/untrusted project จน PROFILE_A ผ่าน M6

[REQ][REQ-S29-004] acceptance ต้องพิสูจน์ว่า invalid candidate ถูก reject, valid candidateถูกวัด/เลือก, export ตรง source hash และ replay สองครั้งให้ CandidateId/selection/lineage digest ตรงกัน

[REQ][REQ-S29-005] เมื่อ slice ผ่าน การขยาย persistence/sandbox/mutation ต้องเปลี่ยน implementation หลัง protocol boundary เดิม โดย conformance tests ของ slice ต้องยังผ่าน

---

# 30. Final Canonical Freeze Rule [NORMATIVE]

Plan 10.2.2 **ไม่ได้ประกาศว่า implementation เสร็จ** และ Appendix C ไม่ใช่ active implementation contract

สิ่งที่ freeze คือ:

```text
architecture direction
active authority hierarchy
scope boundaries
single CLI
single SDK
single Candidate FSM
single Run/Recovery/Governance FSM definitions
execution outcome semantics
argv-only command model
configuration ownership/precedence
canonical data model target
29-table relational design
26-schema registry
measurement protocol
Pareto/diversity/preference-weight semantics
security invariants
Linux/backend conformance matrix
EE-CRYPTO-1 profile
golden corpus taxonomy
maturity ladder
release-gate semantics
Requirement ID contract
generated Active-Spec View contract
```

สิ่งที่ยังต้องพิสูจน์ด้วย repository artifacts:

```text
schemas
protocols
migrations
sandbox profiles
test fixtures
golden hashes
CI results
signed evidence
```

### Canonical Status [NORMATIVE]

```text
SPEC CANONICALIZED: YES
DESIGN DOCUMENTATION SUFFICIENT TO START IMPLEMENTATION: YES
DOCUMENTATION CLOSED TO SPECULATIVE CORE EXPANSION: YES
EXECUTION READY: NOT YET
CURRENT MATURITY: M2
NEXT TARGET: M3
```

[REQ][REQ-S30-001] หลัง Plan 10.2.2 ห้ามเพิ่ม speculative Core section ก่อน M3; เอกสารแก้ได้เมื่อ implementation/test พบ ambiguity, contradiction, security defect หรือ falsified assumption และต้องผ่าน Section 27

[REQ][REQ-S30-002] feature idea ที่ไม่ block milestone ปัจจุบันต้องไป Research Backlog ไม่ใช่ active Core requirement

---

# Appendix A — Canonical Counts [INFORMATIVE]

```text
Active plan versions: 1
Canonical CLI executables: 1
Canonical SDK classes: 1
Canonical Candidate FSMs: 1
Canonical Run FSMs: 1
Canonical Recovery FSMs: 1
Canonical Governance FSMs: 1
Canonical deployment FSMs: 1
Active normative Requirement IDs: 179
Relational tables specified: 29
Schema registry entries: 26
Golden corpus cases: 14
Maturity levels: 14 (M0-M13)
```

---

# Appendix B — Why This Rewrite Stops the Previous Loop [INFORMATIVE]

ก่อน rewrite:

```text
old definition remains
+ new patch section
+ new freeze
= more sources of truth
```

หลัง rewrite:

```text
one active definition
+ explicit requirement status
+ no fake evidence
+ maturity tied to artifacts
= gaps become finite implementation tasks
```

เป้าหมายของ Plan ต่อจากนี้ไม่ใช่เพิ่ม section count แต่ทำให้แต่ละ `[REQ]` เลื่อนไป:

```text
REQ -> IMPL -> TEST -> EVID
```

โดยไม่สร้าง canonical definition ซ้ำ

<!-- ACTIVE_SPEC_END -->
