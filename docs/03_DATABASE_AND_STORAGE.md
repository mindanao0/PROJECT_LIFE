# 03 — Database Schema (31 Tables), Integrity Triggers & CAS Persistence

> **Active Requirements Covered:** `REQ-S13-001` .. `REQ-S13-009`, `REQ-S14-001` .. `REQ-S14-002`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Not normative.    
> **Integrity triggers ตัวจริงอยู่ที่** [`spec/ACTIVE_CONTRACT.md`](../spec/ACTIVE_CONTRACT.md) section 13.2 ระหว่าง marker `INTEGRITY_TRIGGERS_BEGIN`/`END`  
> SQL ที่เคยอยู่ในไฟล์นี้เป็นร่างคู่ขนานที่ขัดกับอีกฉบับ จึงถูกถอดออกที่ CR-0002
> **Canonical source:** [`docs/03_storage_and_database/`](./03_storage_and_database/) — เมื่อขัดกัน ให้ยึดฝั่งนั้น

สถาปัตยกรรมการจัดเก็บข้อมูลของ Evolution Engine แบ่งหน้าที่ออกเป็น 2 ชั้นอย่างชัดเจน:
1. **SQLite Database (Relational Engine):** เก็บโครงสร้าง Metadata, สถานะของกระบวนการ, ผลการประเมิน, ความสัมพันธ์ Lineage และ Index สำหรับ Audit
2. **Content-Addressed Storage (CAS):** เก็บ Immutable Blobs/Artifacts เช่น Source snapshots, Output logs, Checkpoint payloads, และ Evidence envelopes โดยอ้างอิงผ่าน SHA-256

---

## 1. Storage Responsibilities & Commit Semantics

### Generation Commit FSM (7 States)
```text
PREPARING 
 -> CAS_OBJECTS_DURABLE 
  -> DB_TRANSACTION_OPEN 
   -> DB_ROWS_WRITTEN 
    -> DB_COMMITTED 
     -> GENERATION_MANIFEST_DURABLE 
      -> COMMITTED
```

- **[REQ-S14-001]** การเขียน CAS ต้องเป็น Atomic: `temp file` $\rightarrow$ `fsync file` $\rightarrow$ `atomic rename` $\rightarrow$ `fsync parent directory`
- **[REQ-S13-001]** ทุก Generation ต้องมี Durable Generation Manifest ใน CAS เพื่อให้สามารถ Reconstruct ฐานข้อมูลได้แม้ไฟล์ SQLite เสียหาย

---

## 2. Canonical 31-table SQLite DDL

```sql
PRAGMA foreign_keys = ON;

-- 1. Projects
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    project_version TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

-- 2. Runs
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

-- 3. Generations
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

-- 4. Candidates
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

-- 5. Candidate Parents
CREATE TABLE candidate_parents (
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    parent_candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    parent_order INTEGER NOT NULL CHECK(parent_order >= 0),
    PRIMARY KEY(candidate_id, parent_candidate_id),
    UNIQUE(candidate_id, parent_order),
    CHECK(candidate_id <> parent_candidate_id)
);

-- 6. Population Memberships
CREATE TABLE population_memberships (
    generation_id TEXT NOT NULL REFERENCES generations(generation_id) ON DELETE CASCADE,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('PARENT','OFFSPRING','ELITE','SURVIVOR')),
    PRIMARY KEY(generation_id, candidate_id)
);

-- 7. Mutation Strategies
CREATE TABLE mutation_strategies (
    strategy_id TEXT PRIMARY KEY,
    strategy_version TEXT NOT NULL,
    risk_level TEXT NOT NULL CHECK(risk_level IN ('LOW','MEDIUM','HIGH')),
    enabled INTEGER NOT NULL CHECK(enabled IN (0,1)),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count >= 0),
    improvement_count INTEGER NOT NULL DEFAULT 0 CHECK(improvement_count >= 0)
);

-- 8. Mutation Attempts
CREATE TABLE mutation_attempts (
    mutation_attempt_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    strategy_id TEXT NOT NULL REFERENCES mutation_strategies(strategy_id) ON DELETE RESTRICT,
    parent_candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    rng_seed_hex TEXT NOT NULL,
    parameters_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    status TEXT NOT NULL CHECK(status IN ('CREATED','APPLIED','INVALID','FAILED'))
);

-- 9. Evaluation Attempts
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

-- 10. Test Definitions
CREATE TABLE test_definitions (
    test_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    test_version TEXT NOT NULL,
    test_kind TEXT NOT NULL,
    definition_hash TEXT NOT NULL,
    UNIQUE(project_id, test_version)
);

-- 11. Test Results
CREATE TABLE test_results (
    test_result_id TEXT PRIMARY KEY,
    evaluation_attempt_id TEXT NOT NULL REFERENCES evaluation_attempts(evaluation_attempt_id) ON DELETE CASCADE,
    test_id TEXT NOT NULL REFERENCES test_definitions(test_id) ON DELETE RESTRICT,
    result_value TEXT NOT NULL CHECK(result_value IN ('PASS','FAIL','ERROR','FLAKY','SKIPPED','INCONCLUSIVE')),
    duration_ns INTEGER CHECK(duration_ns IS NULL OR duration_ns >= 0),
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(evaluation_attempt_id, test_id)
);

-- 12. Capability Definitions
CREATE TABLE capability_definitions (
    capability_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    capability_version TEXT NOT NULL,
    required INTEGER NOT NULL CHECK(required IN (0,1)),
    definition_hash TEXT NOT NULL,
    UNIQUE(project_id, capability_version)
);

-- 13. Capability Results
CREATE TABLE capability_results (
    capability_result_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    capability_id TEXT NOT NULL REFERENCES capability_definitions(capability_id) ON DELETE RESTRICT,
    verdict TEXT NOT NULL CHECK(verdict IN ('PASS','FAIL','INCONCLUSIVE')),
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(candidate_id, capability_id)
);

-- 14. Objective Definitions
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

-- 15. Metric Results
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

-- 16. Oracle Results
CREATE TABLE oracle_results (
    oracle_result_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    oracle_version TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('PASS','FAIL','INCONCLUSIVE','NOT_REQUIRED')),
    oracle_digest TEXT NOT NULL,
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(candidate_id, oracle_version)
);

-- 17. Selection Decisions
CREATE TABLE selection_decisions (
    selection_decision_id TEXT PRIMARY KEY,
    generation_id TEXT NOT NULL REFERENCES generations(generation_id) ON DELETE CASCADE,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    decision TEXT NOT NULL CHECK(decision IN ('SELECTED','RETAINED','REJECTED')),
    reason_code TEXT NOT NULL,
    rank_index INTEGER CHECK(rank_index IS NULL OR rank_index >= 0),
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT
);

-- 18. Policy Snapshots
CREATE TABLE policy_snapshots (
    policy_snapshot_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    policy_version TEXT NOT NULL,
    policy_hash TEXT NOT NULL,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(run_id, policy_version)
);

-- 19. Environment Manifests
CREATE TABLE environment_manifests (
    environment_manifest_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    environment_hash TEXT NOT NULL,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    UNIQUE(run_id, environment_hash)
);

-- 20. Artifacts
CREATE TABLE artifacts (
    artifact_id TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL UNIQUE,
    size_bytes INTEGER NOT NULL CHECK(size_bytes >= 0),
    media_type TEXT NOT NULL,
    cas_relative_path TEXT NOT NULL UNIQUE,
    created_at_utc TEXT NOT NULL
);

-- 21. Artifact Refs
CREATE TABLE artifact_refs (
    artifact_ref_id TEXT PRIMARY KEY,
    owner_type TEXT NOT NULL CHECK(owner_type IN (
        'PROJECT','RUN','GENERATION','CANDIDATE','MUTATION_ATTEMPT','EVALUATION_ATTEMPT',
        'TEST_RESULT','CAPABILITY_RESULT','METRIC_RESULT','ORACLE_RESULT',
        'SELECTION_DECISION','CHECKPOINT','RECOVERY','EVIDENCE','AUDIT','DEPLOYMENT',
        'MEMORY_RECORD','BASELINE'
    )),
    owner_id TEXT NOT NULL,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    ref_role TEXT NOT NULL,
    UNIQUE(owner_type, owner_id, artifact_id, ref_role)
);

-- 22. Lineage Edges
CREATE TABLE lineage_edges (
    lineage_edge_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    parent_candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    child_candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    mutation_attempt_id TEXT REFERENCES mutation_attempts(mutation_attempt_id) ON DELETE SET NULL,
    relationship TEXT NOT NULL CHECK(relationship IN ('MUTATION','CROSSOVER','CLONE','ROLLBACK')),
    UNIQUE(parent_candidate_id, child_candidate_id, relationship)
);

-- 23. Checkpoints
CREATE TABLE checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    generation_id TEXT NOT NULL REFERENCES generations(generation_id) ON DELETE CASCADE,
    manifest_artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    random_state_artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    created_at_utc TEXT NOT NULL
);

-- 24. Recovery Records
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

-- 25. Evidence Records
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

-- 26. Audit Events
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

-- 27. Quarantine Records
CREATE TABLE quarantine_records (
    quarantine_record_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE RESTRICT,
    reason_code TEXT NOT NULL,
    security_profile_version TEXT NOT NULL,
    evidence_artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    created_at_utc TEXT NOT NULL
);

-- 28. Deployments
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

-- 29. Approval Certificates
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


CREATE TABLE memory_records (
    memory_record_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE RESTRICT,
    run_id TEXT REFERENCES runs(run_id) ON DELETE RESTRICT,
    ast_pattern_hash TEXT NOT NULL,
    reward_score_decimal TEXT NOT NULL,
    access_count INTEGER NOT NULL DEFAULT 0 CHECK(access_count >= 0),
    holdout_tainted INTEGER NOT NULL DEFAULT 0 CHECK(holdout_tainted IN (0,1)),
    embedding_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL,
    UNIQUE(project_id, ast_pattern_hash)
);

CREATE TABLE baselines (
    baseline_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE RESTRICT,
    source_hash TEXT NOT NULL,
    environment_hash TEXT NOT NULL,
    measurement_artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    created_at_utc TEXT NOT NULL,
    UNIQUE(project_id, source_hash, environment_hash)
);

-- Indices (56 Indices for Query Performance & Invariant Verification)
CREATE INDEX idx_runs_project ON runs(project_id);
CREATE INDEX idx_memory_records_project ON memory_records(project_id);
CREATE INDEX idx_memory_records_run ON memory_records(run_id);
CREATE INDEX idx_memory_records_embedding_artifact_id ON memory_records(embedding_artifact_id);
CREATE INDEX idx_baselines_project ON baselines(project_id);
CREATE INDEX idx_baselines_measurement_artifact_id ON baselines(measurement_artifact_id);
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

---

## 3. Relational Integrity Triggers (Polymorphic Validation)

ตามข้อกำหนด `[REQ-S13-003]` ตาราง `artifact_refs` มี Foreign Key แบบ Polymorphic (`owner_type`, `owner_id`) ระบบต้องสร้าง SQLite Triggers เพื่อป้องกัน Dangling References:


