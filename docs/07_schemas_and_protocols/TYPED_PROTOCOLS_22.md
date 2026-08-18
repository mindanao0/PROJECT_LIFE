# The 22 Core Architecture Protocols Specification

> **Subsystem:** Subsystem Interface Protocols  
> **Authority Level:** NORMATIVE (`REQ-S07-001` .. `REQ-S07-003`)

---

## 1. Complete Typed Python Protocol Definitions

```python
from typing import Protocol, runtime_checkable
from pathlib import Path

@runtime_checkable
class ProjectAdapter(Protocol):
    def load_project(self, project_path: Path) -> dict: ...
    def parse_entry_points(self, project_manifest: dict) -> list[str]: ...

@runtime_checkable
class SourceAnalyzer(Protocol):
    def parse_ast(self, source_bytes: bytes) -> object: ...
    def extract_cfg(self, ast_tree: object) -> object: ...

@runtime_checkable
class MutationStrategy(Protocol):
    def apply_mutation(self, parent_ast: object, rng_seed: int, params: dict) -> tuple[object, dict]: ...

@runtime_checkable
class MutationEngine(Protocol):
    def mutate_population(self, parents: list, registry: dict) -> list: ...
    def update_ucb1_rewards(self, strategy_id: str, reward: float) -> None: ...

@runtime_checkable
class QuantumSearchAdapter(Protocol):
    def rotate_qubit_vector(self, q_vector: list, best_solution: list, delta_theta: float) -> list: ...
    def collapse_state(self, q_vector: list, seed: int) -> list[int]: ...

@runtime_checkable
class PolyglotBridge(Protocol):
    def translate_to_native(self, ast_subtree: object, target_lang: str) -> str: ...
    def compile_in_sandbox(self, native_source: str, output_path: Path) -> Path: ...

@runtime_checkable
class PopulationManager(Protocol):
    def form_generation(self, candidates: list, generation_index: int) -> dict: ...

@runtime_checkable
class EcosystemManager(Protocol):
    def evaluate_coevolution(self, prey_pop: list, predator_pop: list) -> dict: ...

@runtime_checkable
class SwarmCoordinator(Protocol):
    def gossip_pareto_elites(self, local_front: list) -> list: ...
    def verify_peer_candidate(self, peer_candidate: dict) -> bool: ...

@runtime_checkable
class SandboxManager(Protocol):
    def provision_sandbox(self, candidate_id: str, tmpfs_bytes: int) -> Path: ...
    def execute_in_sandbox(self, argv: list[str], cwd: Path, timeout: float) -> dict: ...

@runtime_checkable
class TestRunner(Protocol):
    def run_tests(self, test_plan: dict, sandbox_path: Path) -> dict: ...

@runtime_checkable
class CapabilityVerifier(Protocol):
    def verify_capabilities(self, test_results: dict, contract: dict) -> bool: ...

@runtime_checkable
class OracleRunner(Protocol):
    def compare_oracle(self, candidate_out: bytes, oracle_out: bytes) -> str: ...

@runtime_checkable
class MetricRunner(Protocol):
    def measure_metric(self, candidate_id: str, objective: dict) -> dict: ...

@runtime_checkable
class ParetoSelector(Protocol):
    def rank_and_select(self, population: list, objectives: list, count: int) -> list: ...

@runtime_checkable
class EvidenceStore(Protocol):
    def store_evidence(self, evidence_data: dict, sign_key_id: str) -> str: ...

@runtime_checkable
class ArtifactStore(Protocol):
    def put_bytes(self, data: bytes) -> str: ...
    def get_bytes(self, sha256_digest: str) -> bytes: ...

@runtime_checkable
class LineageRepository(Protocol):
    def record_edge(self, parent_id: str, child_id: str, rel_type: str) -> None: ...

@runtime_checkable
class CheckpointManager(Protocol):
    def save_checkpoint(self, run_id: str, generation_id: str) -> str: ...

@runtime_checkable
class RecoveryManager(Protocol):
    def reconcile_state(self, run_id: str) -> bool: ...

@runtime_checkable
class PolicyEngine(Protocol):
    def check_policy(self, candidate_ast: object) -> tuple[bool, list[str]]: ...

@runtime_checkable
class DeploymentManager(Protocol):
    def export_candidate(self, candidate_id: str, destination: Path, mode: str) -> dict: ...
```
