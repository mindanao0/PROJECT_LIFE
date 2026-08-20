"""In-memory adapters for the M5 vertical slice (Active Contract section 29.1).

REQ-S29-002 allows an in-memory persistence adapter for the slice only, and forbids it
producing M6-M11 evidence. REQ-S29-001 forbids inventing a temporary API: these classes
implement the protocols from section 7.2 as published, so REQ-S29-005's requirement
that later work change only the implementation behind the same boundary holds.

Nothing here is a sandbox. The slice executes a repository-owned trusted fixture
directly, which REQ-S29-003 permits and requires until PROFILE_A passes M6.
"""
from __future__ import annotations

import ast
import copy
import hashlib
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from evolution_engine.canonical import candidate_id as derive_candidate_id
from evolution_engine.canonical import sha256_hex

from evolution_engine.types import (
    ArtifactId,
    CandidateArtifact,
    CandidateDrafts,
    CandidateId,
    CandidateState,
    CapabilityVerdict,
    Decimal,
    LineageSnapshot,
    MutationContext,
    PolicyVerdict,
    ProgramRepresentation,
    Sha256,
    TestOutcome,
    TestPlan,
    TestSuiteResult,
    Verdict,
)

__all__ = [
    "InMemoryArtifactStore",
    "InMemoryLineageRepository",
    "MutationRecord",
    "SliceMutationEngine",
    "TrustedFixtureAnalyzer",
    "TrustedFixtureCapabilityVerifier",
    "TrustedFixtureMetricRunner",
    "TrustedFixtureTestRunner",
    "StaticPolicyEngine",
]


@dataclass(frozen=True, slots=True)
class MutationRecord:
    """What produced a candidate. Feeds MutationId, which feeds CandidateId."""

    strategy_id: str
    operator_name: str
    target_location: str
    rng_seed_hex: str

    @property
    def mutation_id(self) -> str:
        """Content-derived, per spec/reproducibility.yaml. A random id here would make
        CandidateId non-reproducible and REQ-S29-004 unverifiable."""
        digest: str = sha256_hex({
            "parent_candidate_id": None,
            "strategy_id": self.strategy_id,
            "operator_name": self.operator_name,
            "rng_seed_hex": self.rng_seed_hex,
            "target_location": self.target_location,
        })
        return digest


class InMemoryArtifactStore:
    """ArtifactStore. ArtifactId is SHA-256 of the bytes, so storage is idempotent."""

    def __init__(self) -> None:
        self._blobs: dict[str, bytes] = {}

    def put(self, data: bytes, media_type: str) -> ArtifactId:
        digest = sha256_hex_bytes(data)
        self._blobs[digest] = data
        return ArtifactId(digest)

    def get(self, artifact_id: ArtifactId) -> bytes:
        return self._blobs[str(artifact_id)]

    def __len__(self) -> int:
        return len(self._blobs)


def sha256_hex_bytes(data: bytes) -> str:
    digest: str = hashlib.sha256(data).hexdigest()
    return digest


class TrustedFixtureAnalyzer:
    """SourceAnalyzer, restricted to one repository-owned file (REQ-S29-003)."""

    def analyze(self, source_root: Path) -> ProgramRepresentation:
        source_bytes = source_root.read_bytes()
        return ProgramRepresentation(
            module_path=source_root.name,
            source_bytes=source_bytes,
            source_hash=Sha256(sha256_hex_bytes(source_bytes)),
            ast=ast.parse(source_bytes.decode("utf-8")),
        )


class _ConstantMutator(ast.NodeTransformer):
    """M01 constant mutation, applied to the first integer literal only."""

    def __init__(self, delta: int) -> None:
        self.delta = delta
        self.done = False

    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        if not self.done and isinstance(node.value, int) and not isinstance(node.value, bool):
            self.done = True
            return ast.Constant(value=node.value + self.delta)
        return node


class _OperatorMutator(ast.NodeTransformer):
    """M02 operator mutation on the first BinOp."""

    def __init__(self, replacement: ast.operator | ast.unaryop) -> None:
        self.replacement = replacement
        self.done = False

    def visit_BinOp(self, node: ast.BinOp) -> ast.BinOp:
        self.generic_visit(node)
        if not self.done:
            self.done = True
            node.op = self.replacement  # type: ignore[assignment]
        return node


class SliceMutationEngine:
    """MutationEngine, limited to M01 and M02 as section 29.1 fixes.

    Emits a fixed, fully enumerable set so the slice is deterministic by construction
    rather than by luck. One mutant is deliberately malformed: a real mutation engine
    produces invalid ASTs and the static gate exists to catch them, so the slice must
    exercise that path rather than pretend it never happens.
    """

    STRATEGIES = ("M01", "M02")

    def draft(
        self, baseline: ProgramRepresentation, context: MutationContext
    ) -> list[tuple[MutationRecord, ProgramRepresentation]]:
        drafts: list[tuple[MutationRecord, ProgramRepresentation]] = []

        # M01 — shift the first integer constant. Changes behaviour, so the capability
        # gate must reject it.
        drafts.append(self._apply(
            baseline, _ConstantMutator(delta=1),
            MutationRecord("M01", "constant_shift", "Constant[0]", context.rng_seed_hex)))

        # M02 — swap the first arithmetic operator. Also changes behaviour.
        drafts.append(self._apply(
            baseline, _OperatorMutator(ast.Sub()),
            MutationRecord("M02", "binop_add_to_sub", "BinOp[0]", context.rng_seed_hex)))

        # M02 — a swap that yields an AST the compiler rejects. The static gate's reason
        # to exist.
        drafts.append(self._apply(
            baseline, _OperatorMutator(ast.Not()),
            MutationRecord("M02", "binop_add_to_not", "BinOp[0]", context.rng_seed_hex)))

        return drafts

    @staticmethod
    def _apply(
        baseline: ProgramRepresentation,
        transformer: ast.NodeTransformer,
        record: MutationRecord,
    ) -> tuple[MutationRecord, ProgramRepresentation]:
        original = baseline.ast
        assert isinstance(original, ast.AST)
        tree = transformer.visit(copy.deepcopy(original))
        ast.fix_missing_locations(tree)
        try:
            source = ast.unparse(tree)
        except Exception:  # an AST too malformed even to render
            source = "<<unrenderable>>"
        data = source.encode("utf-8")
        return record, ProgramRepresentation(
            module_path=baseline.module_path,
            source_bytes=data,
            source_hash=Sha256(sha256_hex_bytes(data)),
            ast=tree,
        )


class StaticPolicyEngine:
    """PolicyEngine. The static gate of section 8.2 step 3.

    A candidate whose source will not compile can never be executed, so it is refused
    here rather than crashing the evaluator later.
    """

    def evaluate(self, artifact: CandidateArtifact) -> PolicyVerdict:
        raise NotImplementedError("use evaluate_source; the slice has no artifact store lookup")

    def evaluate_source(self, source: bytes, policy_hash: Sha256) -> PolicyVerdict:
        text = source.decode("utf-8", errors="replace")
        if text == "<<unrenderable>>":
            return PolicyVerdict(False, "STATIC_UNRENDERABLE_AST", policy_hash)
        try:
            compile(text, "<candidate>", "exec")
        except SyntaxError:
            return PolicyVerdict(False, "STATIC_SYNTAX_ERROR", policy_hash)
        return PolicyVerdict(True, None, policy_hash)


class TrustedFixtureTestRunner:
    """TestRunner. Executes the trusted capability test against candidate source.

    The fixture and its test are repository-owned, so direct execution is what
    REQ-S29-003 requires until PROFILE_A passes M6.
    """

    def run(self, source: bytes, plan: TestPlan) -> TestSuiteResult:
        namespace: dict[str, object] = {}
        outcomes: list[TestOutcome] = []
        try:
            exec(compile(source.decode("utf-8"), "<candidate>", "exec"), namespace)
            compute = namespace["compute_series"]
            passed = compute(5) == 30  # type: ignore[operator]
            outcomes.append(TestOutcome("test_sum_of_squares_below_five",
                                        "PASS" if passed else "FAIL", None))
        except Exception:
            outcomes.append(TestOutcome("test_sum_of_squares_below_five", "ERROR", None))
        return TestSuiteResult(results=tuple(outcomes))


class TrustedFixtureCapabilityVerifier:
    """CapabilityVerifier. One declared capability, as section 29.1 fixes."""

    def verify(self, results: TestSuiteResult, capability_id: str) -> CapabilityVerdict:
        ok = all(outcome.result_value == "PASS" for outcome in results.results)
        return CapabilityVerdict(capability_id, Verdict.PASS if ok else Verdict.FAIL, None)


class TrustedFixtureMetricRunner:
    """MetricRunner. One objective, as section 29.1 fixes.

    The value is a canonical decimal string, never a float (REQ-S11-001).
    """

    def measure(self, results: TestSuiteResult) -> Decimal:
        total = len(results.results)
        if total == 0:
            return Decimal("0")
        passed = sum(1 for o in results.results if o.result_value == "PASS")
        return Decimal("1" if passed == total else "0")


class InMemoryLineageRepository:
    """LineageRepository. Holds the graph for the slice and nothing beyond it."""

    def __init__(self) -> None:
        self._nodes: list[CandidateId] = []
        self._edges: list[tuple[CandidateId, CandidateId]] = []

    def add_node(self, candidate_id: CandidateId) -> None:
        self._nodes.append(candidate_id)

    def add_edge(self, parent: CandidateId, child: CandidateId) -> None:
        self._edges.append((parent, child))

    def snapshot(self) -> LineageSnapshot:
        return LineageSnapshot(nodes=tuple(self._nodes), edges=tuple(self._edges))

    def digest(self) -> str:
        """Part of what REQ-S29-004 compares across two replays."""
        snap = self.snapshot()
        digest: str = sha256_hex({
            "nodes": list(snap.nodes),
            "edges": [list(edge) for edge in snap.edges],
        })
        return digest


def derive_id(
    generation_index: int, source_hash: str, parent: str | None, mutation: str | None
) -> CandidateId:
    """CandidateId exactly as spec/reproducibility.yaml defines it."""
    return CandidateId(derive_candidate_id(generation_index, source_hash, parent, mutation))


@dataclass
class SliceState:
    """The in-memory stand-in for the 31 tables. REQ-S29-002 keeps it to the slice."""

    candidates: dict[CandidateId, CandidateState] = field(default_factory=dict)
    reasons: dict[CandidateId, str] = field(default_factory=dict)
    metrics: dict[CandidateId, Decimal] = field(default_factory=dict)
    events: list[tuple[str, str]] = field(default_factory=list)

    def transition(self, candidate_id: CandidateId, state: CandidateState,
                   reason: str | None = None) -> None:
        self.candidates[candidate_id] = state
        if reason is not None:
            self.reasons[candidate_id] = reason
        self.events.append((str(candidate_id), state.value))

    def in_state(self, state: CandidateState) -> Sequence[CandidateId]:
        return [c for c, s in self.candidates.items() if s is state]
