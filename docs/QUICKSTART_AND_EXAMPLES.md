# 10 — Quickstart Guide & End-to-End Examples

> **Dimension:** Developer Experience & Practical Usage  
> **Target Audience:** Software Engineers, Researchers, and Operators

เอกสารฉบับนี้เป็นคู่มือเริ่มต้นใช้งานฉบับสมบูรณ์ (Quickstart Walkthrough) แสดงตัวอย่างโครงสร้างโปรเจกต์เป้าหมายจริง คำสั่ง CLI และผลลัพธ์ Machine-Readable JSON Envelope

---

## 1. Target Project Layout

ในการนำ Evolution Engine ไปใช้กับโปรเจกต์ Python ใดๆ โปรเจกต์นั้นควรมีโครงสร้างพื้นฐานดังนี้:

```text
my-target-project/
├── pyproject.toml
├── evolution.yaml               # ไฟล์คอนฟิกหลักสำหรับ Evolution Engine
├── src/
│   └── text_search.py           # โค้ดต้นฉบับที่ต้องการ optimize
├── tests/
│   └── test_correctness.py      # ชุดทดสอบ Unit Test / Capability Gates
└── benchmark/
    ├── benchmark_latency.py     # สคริปต์วัดความเร็ว (ms)
    └── benchmark_memory.py      # สคริปต์วัดการใช้ Memory (bytes)
```

---

## 2. Canonical `evolution.yaml` Example

```yaml
project:
  name: "text-search-optimizer"
  language: "python"
  version: "1.0.0"

evolution:
  level: "function"              # ขอบเขต: function | module | project
  population_size: 20            # จำนวน Candidate ต่อ Generation
  seed: 424242                   # Seed สำหรับ Deterministic Replay

# มาตรวัดประสิทธิภาพที่ต้องการปรับปรุง (Multi-Objective)
metrics:
  - name: "throughput_ops"
    direction: "maximize"
    unit: "ops/sec"
    valid_range:
      minimum_decimal: "0"
      maximum_decimal: "1000000"
    practical_margin_decimal: "100.0"
    failure_policy: "invalidate_candidate"
    preference_weight_decimal: "0.6"
    command:
      argv: ["python", "benchmark/benchmark_latency.py"]
      cwd: "."
      env: {}
      timeout_seconds: 15

  - name: "peak_memory_kb"
    direction: "minimize"
    unit: "kb"
    valid_range:
      minimum_decimal: "0"
      maximum_decimal: "500000"
    practical_margin_decimal: "10.0"
    failure_policy: "invalidate_candidate"
    preference_weight_decimal: "0.4"
    command:
      argv: ["python", "benchmark/benchmark_memory.py"]
      cwd: "."
      env: {}
      timeout_seconds: 15

# กฎการคัดเลือก (Pareto Selection)
selection:
  method: "pareto"
  preference_weights_usage: "same_front_tie_break_only"
  tie_break_order:
    - "pareto_rank"
    - "diversity_score"
    - "preference_score"
    - "canonical_candidate_id"

# เงื่อนไขการคงอยู่ของคุณสมบัติเดิม (Capability Constraints)
constraints:
  capability_commands:
    - argv: ["python", "-m", "pytest", "tests/test_correctness.py"]
      cwd: "."
      env: {}
      timeout_seconds: 30

# การตั้งค่าความปลอดภัยของ Sandbox
sandbox:
  profile: "PROFILE_A_LINUX"
  network: "deny"
  writable_tmp_bytes: 67108864   # 64 MB tmpfs

# โหมดการส่งออกผลลัพธ์
deployment:
  mode: "SAFE_EXPORT_ONLY"

# เงื่อนไขการหยุดทำงาน (Stopping Criteria)
stopping:
  max_generations: 50
  max_stagnation: 15
  max_runtime_seconds: 1800      # 30 minutes
```

---

## 3. End-to-End CLI Workflow

### Step 1: Preflight Validation
ตรวจสอบความถูกต้องของคอนฟิก โครงสร้างโปรเจกต์ และระบบ Sandbox:

```bash
evolve validate --project ./my-target-project --json
```

**ตัวอย่างผลลัพธ์ Output Envelope:**
```json
{
  "status": "VALID",
  "project_name": "text-search-optimizer",
  "config_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "sandbox_ready": true,
  "diagnostics": []
}
```

---

### Step 2: Start Evolution Run
เริ่มต้นการวิวัฒนาการโปรเจกต์:

```bash
evolve run --project ./my-target-project
```

**ตัวอย่างหน้าจอแสดงสถานะ (TUI / Terminal Log):**
```text
[INFO] Run started with ID: run-20260818-001
[INFO] Baseline established: through_put=1250 ops/sec, peak_mem=4200 kb
[GEN 01] Candidates: 20 | Valid: 18 | Rejected: 2 | Pareto Front: 3 | Best Gain: +12.4%
[GEN 05] Candidates: 20 | Valid: 19 | Rejected: 1 | Pareto Front: 5 | Best Gain: +28.7%
[GEN 10] Candidates: 20 | Valid: 20 | Rejected: 0 | Pareto Front: 6 | Best Gain: +45.2%
[INFO] Stopping condition reached: Pareto convergence achieved.
```

---

### Step 3: View Realtime Status
ตรวจสอบสถานะในขณะที่ Engine กำลังประมวลผลอยู่เบื้องหลัง:

```bash
evolve status --run-id run-20260818-001 --json
```

---

### Step 4: Generate Evolution Report
สร้างรายงานสรุปความก้าวหน้า Lineage Graph และ Pareto Frontier:

```bash
evolve report --run-id run-20260818-001 --format markdown --output report.md
```

---

### Step 5: Export Selected Candidate Code
ส่งออกโค้ดที่ได้รับการคัดเลือกไปยังไดเรกทอรีปลายทางอย่างปลอดภัย:

```bash
evolve export \
  --candidate-id cand-gen10-004 \
  --destination ./exported-solution \
  --mode SAFE_EXPORT_ONLY
```

---

## 4. Python SDK Integration Example

นอกจากการใช้งานผ่าน CLI คุณสามารถควบคุม Evolution Engine ผ่าน Python Script ได้โดยตรง:

```python
from evolution_engine import EvolutionEngine

# 1. Initialize Engine with project configuration
engine = EvolutionEngine.create(config_path="./my-target-project/evolution.yaml")

# 2. Run Preflight Validation
val_report = engine.validate_project("./my-target-project")
if not val_report.is_valid:
    print(f"Validation Error: {val_report.errors}")
    exit(1)

# 3. Start Evolution Run
run_id = engine.start_run("./my-target-project")
print(f"Started Run ID: {run_id}")

# 4. Wait & Get Final Report
status = engine.get_status(run_id)
report = engine.get_report(run_id)

print(f"Evolution Completed in {report.total_generations} generations")
print(f"Selected Candidate ID: {report.best_candidate_id}")
print(f"Improvements: {report.metric_improvements}")

# 5. Export Selected Candidate
engine.export_candidate(
    candidate_id=report.best_candidate_id,
    destination="./optimized_src"
)
```
