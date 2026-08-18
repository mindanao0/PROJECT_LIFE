# Python SDK Reference Specification

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.    
> **Canonical surface:** [`build/spec/Evolution_Engine_Active_Spec_10_2_2.md`](../../build/spec/Evolution_Engine_Active_Spec_10_2_2.md) §6.2 — synchronous, 12 operations.  
> เมธอด async ในไฟล์นี้เป็น **ข้อเสนอ** ที่ยังไม่อยู่ใน Active Contract ต้องผ่าน Section 27 governed spec change ก่อนจึงจะบังคับใช้ได้
> **Scope:** PUBLIC SDK SPECIFICATION (L4 Authority)
> **Target Subsystem:** Public Client Interface (`evolution_engine.sdk`)  
> **Governing Equations:** `EQ-046` (SDK Idempotency), `EQ-050` (Asyncio Scaling)

---

## 1. Class `EvolutionEngine` Signature & Methods

```python
from decimal import Decimal
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional
from uuid import UUID

class EvolutionEngine:
    """Master Client SDK for Evolution Engine Orchestration."""

    def __init__(
        self,
        config_path: Path,
        work_dir: Optional[Path] = None,
        master_seed: Optional[int] = None,
    ) -> None:
        """Initialize Engine instance with configuration and optional seed."""
        ...

    async def initialize(self) -> UUID:
        """Run preflight checks, create DB, and return initialized run_id."""
        ...

    async def run(self, max_generations: Optional[int] = None) -> RunSummary:
        """Execute evolutionary loop until max_generations or convergence."""
        ...

    async def step(self) -> GenerationSummary:
        """Execute a single generation step and commit results."""
        ...

    async def pause(self) -> RunState:
        """Pause running execution gracefully after in-flight tasks finish."""
        ...

    async def resume(self) -> RunState:
        """Resume paused execution."""
        ...

    async def abort(self) -> RunState:
        """Abort execution immediately and trigger cleanup."""
        ...

    async def get_pareto_front(self, generation_index: Optional[int] = None) -> List[CandidateManifest]:
        """Retrieve non-dominated Pareto front candidates."""
        ...

    async def export_candidate(
        self,
        candidate_id: UUID,
        output_dir: Path,
        mode: ExportMode = ExportMode.SAFE_STANDALONE,
    ) -> Path:
        """Export optimized candidate code with full provenance bundle."""
        ...

    async def stream_events(self) -> AsyncIterator[AuditEvent]:
        """Stream real-time audit and lifecycle events."""
        ...
```

---

## 2. SDK Invariants & Error Handling

1. **Deterministic Execution:** หากส่ง `master_seed` ค่าเดียวกันบนสภาพแวดล้อมเดิม ผลลัพธ์ต้องตรงกัน 100%
2. **State Idempotency:** การเรียก `pause()` ซ้ำบนสถานะ `PAUSED` จะคืนค่า `PAUSED` เสมอโดยไม่เกิด Error:
   $$\text{SDK}.\text{pause}(R) = \text{PAUSED} \implies \text{SDK}.\text{pause}(R) = \text{PAUSED}$$
3. **Safe Export Default:** การ Export โค้ดจะใช้โหมด `SAFE_EXPORT_ONLY` โดยไม่เขียนทับโค้ดต้นฉบับใน Source Directory
