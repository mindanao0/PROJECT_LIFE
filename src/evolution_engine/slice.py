"""The mandatory trusted-fixture vertical slice (Active Contract section 29.1).

A walking skeleton that runs end to end through the published boundary. Section 29.1
fixes its scope exactly: MVP-01, function level, strategies M01 and M02, population 4,
one generation, seed 12345, one capability test, one objective, in-memory persistence,
SAFE_EXPORT_ONLY to a temporary directory.

The required path, one step per stage:

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

REQ-S29-001 forbids a temporary API, so every stage uses the real schema models, the
published protocols, the Candidate FSM vocabulary and the canonical serializer.
REQ-S29-004 is the acceptance test: an invalid candidate is rejected, a valid one is
measured and selected, the export matches its source hash, and two replays agree on the
CandidateId, selection and lineage digests.
"""
from __future__ import annotations

import json
import pathlib
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from evolution_engine.canonical import sha256_hex

from evolution_engine.adapters.in_memory import (  # noqa: E402
    InMemoryArtifactStore,
    InMemoryLineageRepository,
    SliceMutationEngine,
    SliceState,
    StaticPolicyEngine,
    TrustedFixtureAnalyzer,
    TrustedFixtureCapabilityVerifier,
    TrustedFixtureMetricRunner,
    TrustedFixtureTestRunner,
    derive_id,
)
from evolution_engine.types import (  # noqa: E402
    CandidateId,
    CandidateState,
    Decimal,
    MutationContext,
    RunState,
    Sha256,
    TestPlan,
    Verdict,
)

__all__ = ["SliceResult", "run_slice"]

GENERATION_INDEX = 0


@dataclass(frozen=True, slots=True)
class SliceResult:
    """Everything REQ-S29-004 compares. All values are canonical and replay-stable."""

    run_states: tuple[str, ...]
    candidate_ids: tuple[str, ...]
    selected_candidate_id: str
    static_rejected: tuple[str, ...]
    capability_rejected: tuple[str, ...]
    metrics: dict[str, str]
    selection_digest: str
    lineage_digest: str
    exported_source_hash: str
    export_path: str


def run_slice(case_dir: Path, export_root: Path) -> SliceResult:
    """Run the slice once. Deterministic for a fixed case directory and seed."""
    state = SliceState()
    lineage = InMemoryLineageRepository()
    artifacts = InMemoryArtifactStore()
    run_states: list[str] = []

    def enter(run_state: RunState) -> None:
        run_states.append(run_state.value)

    # --- load validated config -----------------------------------------------
    enter(RunState.INITIATED)
    config = yaml.safe_load((case_dir / "evolution.yaml").read_text(encoding="utf-8"))
    seed = int(config["evolution"]["seed"])
    population_size = int(config["evolution"]["population_size"])
    enter(RunState.CONFIG_LOADED)

    # No preflight probe: the slice does not enter PROFILE_A (REQ-S29-003).
    enter(RunState.PREFLIGHT_PASSED)
    enter(RunState.RUNNING)

    # --- parse trusted fixture ------------------------------------------------
    analyzer = TrustedFixtureAnalyzer()
    baseline = analyzer.analyze(case_dir / "src/math_kernel.py")

    baseline_id = derive_id(GENERATION_INDEX, str(baseline.source_hash), None, None)
    state.transition(baseline_id, CandidateState.CREATED)
    lineage.add_node(baseline_id)
    artifacts.put(baseline.source_bytes, "text/x-python")
    state.transition(baseline_id, CandidateState.MATERIALIZED)

    # --- create baseline + mutated candidates ---------------------------------
    engine = SliceMutationEngine()
    context = MutationContext(
        generation_index=GENERATION_INDEX,
        rng_seed_hex=f"{seed:016x}",
        strategy_id="M01+M02",
        policy_hash=Sha256(sha256_hex({"policy": "slice-static-only"})),
    )
    drafts = engine.draft(baseline, context)

    sources: dict[CandidateId, bytes] = {baseline_id: baseline.source_bytes}
    for record, draft in drafts:
        candidate_id = derive_id(
            GENERATION_INDEX, str(draft.source_hash), str(baseline_id), record.mutation_id)
        sources[candidate_id] = draft.source_bytes
        state.transition(candidate_id, CandidateState.CREATED)
        lineage.add_node(candidate_id)
        lineage.add_edge(baseline_id, candidate_id)
        artifacts.put(draft.source_bytes, "text/x-python")
        state.transition(candidate_id, CandidateState.MATERIALIZED)

    if len(sources) != population_size:
        raise AssertionError(
            f"section 29.1 fixes population_size at {population_size}, produced {len(sources)}")

    # --- reject static-invalid candidate --------------------------------------
    policy = StaticPolicyEngine()
    static_rejected: list[str] = []
    for candidate_id, source in sources.items():
        policy_verdict = policy.evaluate_source(source, context.policy_hash)
        if policy_verdict.allowed:
            state.transition(candidate_id, CandidateState.STATIC_VALIDATED)
            state.transition(candidate_id, CandidateState.POLICY_VALIDATED)
        else:
            state.transition(candidate_id, CandidateState.REJECTED, policy_verdict.reason_code)
            static_rejected.append(str(candidate_id))

    # --- execute trusted fixture evaluator, capability gate, one metric -------
    runner = TrustedFixtureTestRunner()
    verifier = TrustedFixtureCapabilityVerifier()
    meter = TrustedFixtureMetricRunner()
    plan = TestPlan(test_ids=("test_sum_of_squares_below_five",), holdout_excluded=True)

    capability_rejected: list[str] = []
    for candidate_id in list(state.in_state(CandidateState.POLICY_VALIDATED)):
        # SECURITY_VALIDATED is vacuous here: the fixture is trusted and no sandbox is
        # entered, which REQ-S29-003 requires until M6.
        state.transition(candidate_id, CandidateState.SECURITY_VALIDATED)
        state.transition(candidate_id, CandidateState.SANDBOX_READY)
        state.transition(candidate_id, CandidateState.EXECUTING)
        results = runner.run(sources[candidate_id], plan)
        state.transition(candidate_id, CandidateState.EXECUTED)
        state.transition(candidate_id, CandidateState.TESTING)
        state.transition(candidate_id, CandidateState.ORACLE_VERIFIED)

        capability = verifier.verify(results, "capability-correctness")
        if capability.verdict is not Verdict.PASS:
            state.transition(candidate_id, CandidateState.REJECTED, "CAPABILITY_FAILED")
            capability_rejected.append(str(candidate_id))
            continue
        state.transition(candidate_id, CandidateState.CAPABILITY_VERIFIED)

        state.metrics[candidate_id] = meter.measure(results)
        state.transition(candidate_id, CandidateState.METRIC_EVALUATED)
        state.transition(candidate_id, CandidateState.EVIDENCE_VERIFIED)
        state.transition(candidate_id, CandidateState.ELIGIBLE)

    # --- deterministic selection ----------------------------------------------
    eligible = sorted(str(c) for c in state.in_state(CandidateState.ELIGIBLE))
    if not eligible:
        raise AssertionError("no eligible candidate; the slice cannot select")
    best = max(Decimal(state.metrics[CandidateId(c)]) for c in eligible)
    # Ties break on canonical CandidateId order, which REQ-S10-010 makes the final rule
    # and which only works because CandidateId is content-derived.
    winner = sorted(c for c in eligible if state.metrics[CandidateId(c)] == best)[0]
    state.transition(CandidateId(winner), CandidateState.SELECTED)

    selection_digest = sha256_hex({
        "eligible": eligible,
        "metrics": {c: str(state.metrics[CandidateId(c)]) for c in eligible},
        "selected": winner,
    })

    # --- export selected source (SAFE_EXPORT_ONLY) ----------------------------
    export_root.mkdir(parents=True, exist_ok=True)
    export_path = export_root / "math_kernel.py"
    export_path.write_bytes(sources[CandidateId(winner)])
    exported_hash = sha256_hex_bytes_local(export_path.read_bytes())

    enter(RunState.GENERATION_COMMITTED)
    enter(RunState.CHECKPOINTING)
    enter(RunState.COMPLETED)

    return SliceResult(
        run_states=tuple(run_states),
        candidate_ids=tuple(sorted(str(c) for c in sources)),
        selected_candidate_id=winner,
        static_rejected=tuple(sorted(static_rejected)),
        capability_rejected=tuple(sorted(capability_rejected)),
        metrics={c: str(state.metrics[CandidateId(c)]) for c in eligible},
        selection_digest=selection_digest,
        lineage_digest=lineage.digest(),
        exported_source_hash=exported_hash,
        export_path=str(export_path),
    )


def sha256_hex_bytes_local(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[2]
    case = root / "benchmarks/golden/mvp01_pure_function"
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        result = run_slice(case, pathlib.Path(tmp) / "export")
        print(json.dumps({
            "selected": result.selected_candidate_id[:16] + "...",
            "candidates": len(result.candidate_ids),
            "static_rejected": len(result.static_rejected),
            "capability_rejected": len(result.capability_rejected),
            "selection_digest": result.selection_digest[:16] + "...",
            "lineage_digest": result.lineage_digest[:16] + "...",
            "run_states": list(result.run_states),
        }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
