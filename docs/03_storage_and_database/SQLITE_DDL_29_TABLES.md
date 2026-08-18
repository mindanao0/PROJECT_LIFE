# SQLite Relational Architecture: Complete 29 Tables DDL

> **Subsystem:** Relational Metadata Store  
> **Authority:** NORMATIVE (`REQ-S13-001` .. `REQ-S13-009`)

---

## 1. Complete DDL Script (29 Tables & 33 Indices)

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
        'CREATED','VALIDATING','READY','RUNNING','PAUSING','PAUSED',
        'STOPPING','STOPPED','COMPLETED','FAILED','RECOVERING'
    )),
    seed_hex TEXT NOT NULL,
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
        'SELECTION_DECISION','CHECKPOINT','RECOVERY','EVIDENCE','AUDIT','DEPLOYMENT'
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
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    checkpoint_id TEXT REFERENCES checkpoints(checkpoint_id) ON DELETE SET NULL,
    started_at_utc TEXT NOT NULL,
    finished_at_utc TEXT,
    recovery_status TEXT NOT NULL CHECK(recovery_status IN (
        'REQUESTED','VALIDATING_INPUTS','RECONSTRUCTING_CAS','RECONCILING_DB',
        'VERIFYING_AUDIT','REPLAYING_GENERATION','RECOVERED','FAILED','QUARANTINED'
    )),
    evidence_artifact_id TEXT REFERENCES artifacts(artifact_id) ON DELETE RESTRICT
);

-- 25. Evidence Records
CREATE TABLE evidence_records (
    evidence_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    candidate_id TEXT REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    evidence_type TEXT NOT NULL,
    evidence_digest TEXT NOT NULL,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id) ON DELETE RESTRICT,
    status TEXT NOT NULL CHECK(status IN ('CREATED','VERIFIED','INVALID','REVOKED')),
    created_at_utc TEXT NOT NULL
);

-- 26. Audit Events
CREATE TABLE audit_events (
    audit_event_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES runs(run_id) ON DELETE CASCADE,
    sequence_no INTEGER NOT NULL CHECK(sequence_no >= 0),
    previous_event_hash TEXT,
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
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
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
        'ARCHIVED','STAGED','CANARY','VALIDATED','APPROVED','ACTIVE',
        'SUPERSEDED','ROLLED_BACK'
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
```
