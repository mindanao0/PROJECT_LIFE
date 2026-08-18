# Golden Corpus Benchmark Specification (MVP-01 to MVP-14)

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** BENCHMARK SPECIFICATION (L6 Authority)
> **Target Subsystem:** Benchmark Corpus & Golden Verification Suite  
> **Governing Equations:** `EQ-273` (14 Golden Projects Conformance), `EQ-280` (R4 Replay Identity)

---

## 1. Catalog of All 14 Golden Projects

> Canonical source: `benchmarks/golden/manifest.yaml`. This table is derived from it and must never diverge.

```text
┌──────────┬───────────────────────────────┬──────────────────┬──────────────────────┬────────────────────┐
│ CaseID   │ Case Name (manifest)          │ Scope            │ Expected Disposition │ Repro Target       │
├──────────┼───────────────────────────────┼──────────────────┼──────────────────────┼────────────────────┤
│ MVP-01   │ pure-function-opt             │ function         │ SELECTED             │ R4                 │
│ MVP-02   │ stateful-cache-mod            │ module           │ SELECTED             │ R4                 │
│ MVP-03   │ multi-objective-pareto        │ module           │ SELECTED             │ R2                 │
│ MVP-04   │ async-io-pipeline             │ module           │ SELECTED             │ R2                 │
│ MVP-05   │ multi-file-dag-project        │ project          │ SELECTED             │ R1                 │
│ MVP-06   │ quantum-rotation-suite        │ function         │ SELECTED             │ R2                 │
│ MVP-07   │ polyglot-rust-kernel          │ function         │ SELECTED             │ R1                 │
│ MVP-08   │ sec-fs-escape-probe           │ security         │ QUARANTINED          │ R0                 │
│ MVP-09   │ sec-net-socket-probe          │ security         │ QUARANTINED          │ R0                 │
│ MVP-10   │ sec-forkbomb-cgroup           │ security         │ REJECTED             │ R0                 │
│ MVP-11   │ flaky-test-isolation          │ reliability      │ REJECTED             │ R0                 │
│ MVP-12   │ crash-during-commit           │ reliability      │ RESTORED_READY       │ R1                 │
│ MVP-13   │ p2p-swarm-byzantine           │ swarm            │ QUARANTINED          │ R0                 │
│ MVP-14   │ self-evaluator-freeze         │ self_evolution   │ QUARANTINED          │ R0                 │
└──────────┴───────────────────────────────┴──────────────────┴──────────────────────┴────────────────────┘
```

---

## 2. Benchmark Conformance Gate Criteria

ทุก Release ก่อนเลื่อนสู่ระดับ `M2_REQUIREMENTS_CANONICAL` ต้องรันผ่านชุดทดสอบทั้ง 14 โปรเจกต์โดยปราศจากข้อผิดพลาด:
$$|\mathcal{C}_{\text{golden}}| \equiv 14, \qquad \text{Pass}(\mathcal{C}) \equiv 14$$
และบันทึกผลลัพธ์ลงใน `benchmarks/golden/manifest.yaml`
