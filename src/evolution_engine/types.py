"""Types the protocol boundary needs (Active Contract sections 7.1 and 7.2).

Every name here is resolved in spec/protocol_types.yaml, which says for each one
whether it aliases a schema, lives only in process, or needs a schema of its own.
Sections 7.2 and 6.2 named 26 types and only three resolved to anything, so a protocol
written straight from the contract would have invented signatures and then rewritten
them. This module is the resolution made executable.

ALIAS types are named for their schema title, not for the second spelling section 7.2
used: PopulationManifest rather than PopulationSnapshot, OracleResult rather than
OracleVerdict. The aliases are kept at the bottom so contract-era names still import.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import NewType

# --- identifiers (section 7.1, derivation in spec/reproducibility.yaml) -------
# content-derived: SHA-256 rendered as 64 lowercase hex characters
CandidateId = NewType("CandidateId", str)
GenerationId = NewType("GenerationId", str)
MutationId = NewType("MutationId", str)
ArtifactId = NewType("ArtifactId", str)
# event-derived: UUIDv7, never compared across replays
RunId = NewType("RunId", str)
ProjectId = NewType("ProjectId", str)
EvaluationAttemptId = NewType("EvaluationAttemptId", str)
AuditEventId = NewType("AuditEventId", str)
# a canonical decimal string, never a float (REQ-S11-001)
Decimal = NewType("Decimal", str)
Sha256 = NewType("Sha256", str)


class CandidateState(StrEnum):
    """Section 8.1. Mirrors spec/fsm/candidate.yaml."""

    CREATED = "CREATED"
    MATERIALIZED = "MATERIALIZED"
    STATIC_VALIDATED = "STATIC_VALIDATED"
    POLICY_VALIDATED = "POLICY_VALIDATED"
    SECURITY_VALIDATED = "SECURITY_VALIDATED"
    SANDBOX_READY = "SANDBOX_READY"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    TESTING = "TESTING"
    ORACLE_VERIFIED = "ORACLE_VERIFIED"
    CAPABILITY_VERIFIED = "CAPABILITY_VERIFIED"
    METRIC_EVALUATED = "METRIC_EVALUATED"
    EVIDENCE_VERIFIED = "EVIDENCE_VERIFIED"
    ELIGIBLE = "ELIGIBLE"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"


class RunState(StrEnum):
    """Section 8.3. Mirrors spec/fsm/run.yaml."""

    INITIATED = "INITIATED"
    CONFIG_LOADED = "CONFIG_LOADED"
    PREFLIGHT_PASSED = "PREFLIGHT_PASSED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    GENERATION_COMMITTED = "GENERATION_COMMITTED"
    CHECKPOINTING = "CHECKPOINTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"
    RECOVERING = "RECOVERING"


class ExecutionStatus(StrEnum):
    """Section 8.1. Not a lifecycle state; the outcome of one execution.

    The mapping from a kernel-observed cause to one of these is total, and lives in
    spec/sandbox/profile-a-linux.yaml violation_detection.
    """

    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    CRASHED = "CRASHED"
    OOM = "OOM"
    RESOURCE_EXCEEDED = "RESOURCE_EXCEEDED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"


class Verdict(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


# --- IN_PROCESS structures ---------------------------------------------------
# These never cross a process boundary, so they have a dataclass and no schema. A
# schema would imply a wire form that does not exist. Where the value is persisted,
# the docstring names the table.


@dataclass(frozen=True, slots=True)
class ProgramRepresentation:
    """A parsed module. Holds live AST objects, so it has no serialised form."""

    module_path: str
    source_bytes: bytes
    source_hash: Sha256
    ast: object


@dataclass(frozen=True, slots=True)
class MutationContext:
    generation_index: int
    rng_seed_hex: str
    strategy_id: str
    policy_hash: Sha256


@dataclass(frozen=True, slots=True)
class CandidateArtifact:
    candidate_id: CandidateId
    source_artifact_id: ArtifactId
    source_hash: Sha256


@dataclass(frozen=True, slots=True)
class CandidateDrafts:
    """A batch produced before persistence; the element has schema 01."""

    drafts: tuple[CandidateArtifact, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class SandboxRequest:
    candidate_id: CandidateId
    command_argv: tuple[str, ...]
    timeout_seconds: int
    sandbox_profile: str


@dataclass(frozen=True, slots=True)
class SandboxExecutionResult:
    """Persisted as an evaluation_attempts row."""

    execution_status: ExecutionStatus
    exit_code: int | None
    duration_ms: int
    stdout_artifact_id: ArtifactId | None
    stderr_artifact_id: ArtifactId | None
    reason_code: str | None


@dataclass(frozen=True, slots=True)
class TestPlan:
    """holdout_excluded enforces the section 17.2 boundary at the call site."""

    test_ids: tuple[str, ...]
    holdout_excluded: bool


@dataclass(frozen=True, slots=True)
class TestOutcome:
    test_id: str
    result_value: str
    evidence_artifact_id: ArtifactId | None


@dataclass(frozen=True, slots=True)
class TestSuiteResult:
    """Persisted as test_results rows."""

    results: tuple[TestOutcome, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CapabilityVerdict:
    """Persisted as a capability_results row.

    Not schema 10 — that is CapabilityContract, the declaration being checked.
    """

    capability_id: str
    verdict: Verdict
    evidence_artifact_id: ArtifactId | None


@dataclass(frozen=True, slots=True)
class PolicyVerdict:
    """Not schema 18 — that is PolicySnapshot, the policy itself."""

    allowed: bool
    reason_code: str | None
    policy_hash: Sha256


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """Persisted as an evidence_records row."""

    evidence_id: str
    evidence_type: str
    evidence_digest: Sha256
    artifact_id: ArtifactId
    status: str


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    """Persisted as an artifact_refs row."""

    artifact_id: ArtifactId
    owner_type: str
    owner_id: str
    ref_role: str


@dataclass(frozen=True, slots=True)
class LineageSnapshot:
    """Assembled from lineage_nodes and lineage_edges; a query result, not a document."""

    nodes: tuple[CandidateId, ...] = field(default_factory=tuple)
    edges: tuple[tuple[CandidateId, CandidateId], ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class DeploymentResult:
    """Persisted as a deployments row."""

    deployment_id: str
    deployment_state: str
    deployment_mode: str


@dataclass(frozen=True, slots=True)
class AuditReceipt:
    """What AuditLog.append returns. event_hash follows section 18.1."""

    audit_event_id: AuditEventId
    sequence_no: int
    event_hash: Sha256


# --- ALIAS types -------------------------------------------------------------
# Named for their schema title. Modelled as opaque mappings until the schema models
# are generated; the schema is the contract, this is the reference to it.
SchemaDocument = dict[str, object]

ProjectManifest = SchemaDocument
MutationResult = SchemaDocument
PopulationManifest = SchemaDocument
OracleResult = SchemaDocument
MetricResult = SchemaDocument
SelectionDecision = SchemaDocument
CheckpointManifest = SchemaDocument
RecoveryManifest = SchemaDocument

# Section 7.2 spells several of these differently. The schema title is canonical;
# these exist so a reader following the contract still lands on the right type.
PopulationSnapshot = PopulationManifest
OracleVerdict = OracleResult
MetricMeasurement = MetricResult
CheckpointRef = CheckpointManifest
RecoveryResult = RecoveryManifest
