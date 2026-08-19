# CR-0003 — Restore the Core / Research firewall in the golden corpus

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-19
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** [CR-0001](CR-0001-active-contract-becomes-source.md)

---

## 1. Change Proposal

Section 3.1 excludes from Core v1: cross-language mutation, P2P swarm,
quantum-inspired search and artificial-life infrastructure. Section 26 repeats it
and states those items are **not a dependency of Core/M11**.

The golden corpus contradicted both. Section 16.1 placed MVP-06
`quantum-rotation-suite` and MVP-07 `polyglot-rust-kernel` in the **CORE** bucket,
and `spec/maturity.yaml` defined M9 as "Golden Corpus cases MVP-01 to MVP-07 pass".
Since GATE_CORE requires M10, which sits above M9, **Core v1 could not be reached
without a working quantum rotation operator and a Python-to-Rust compiler.**

MVP-13 `p2p-swarm-byzantine` sat in a `SWARM` bucket that no gate recognised, and
no case carried a machine-readable bucket at all — the assignment existed only as a
column in a markdown table.

## 2. Decision

Follow section 3.1. The contract already made this decision; the corpus never
implemented it.

| Case | Was | Now | Why |
|---|---|---|---|
| MVP-06 `quantum-rotation-suite` | CORE | **RESEARCH** | 3.1 excludes quantum-inspired search |
| MVP-07 `polyglot-rust-kernel` | CORE | **RESEARCH** | 3.1 excludes cross-language mutation |
| MVP-13 `p2p-swarm-byzantine` | SWARM | **RESEARCH** | 3.1 excludes P2P swarm |

Resulting buckets: CORE 5, SECURITY 3, RELIABILITY 2, RESEARCH 3, SELF_EVOLUTION 1.
Still 14 cases.

This is the difference between a Core v1 that needs a Python mutation engine and one
that needs a quantum optimiser and a compiler backend. The contract asked for the
first.

## 3. Impact Analysis

| Affected | Effect |
|---|---|
| `benchmarks/golden/manifest.yaml` | every case gains `maturity_bucket`; the three moved cases gain `out_of_core_reason` |
| Section 16.1 | bucket column follows the manifest |
| `spec/maturity.yaml` M9 | "MVP-01 to MVP-07" → "CORE bucket (MVP-01..MVP-05)" |
| `spec/maturity.yaml` M10 | now names the SECURITY and RELIABILITY buckets, not a raw range |
| `spec/maturity.yaml` M13 | now names MVP-14 explicitly, which nothing did before |
| GATE_CORE | unchanged in text; it already required only `golden_core`, `golden_security`, `golden_reliability` |
| derived doc tables | regenerated with the bucket column |

RESEARCH cases are **not deleted**. They stay in the corpus and may be run; they
simply cannot gate a Core rung.

## 4. Authority Check

Sections 3.1 and 26 are rank 2 normative. The corpus bucket assignment is derived
data. Derived data yielding to the contract is the correct direction.

## 5. Security / Safety Review

The SECURITY bucket is untouched: MVP-08, MVP-09 and MVP-10 remain Core-gating, so
M6 and M10 still require the sandbox to defeat filesystem escape, network egress and
fork-bomb attacks.

## 6. Traceability Impact

No requirement added or withdrawn.

## 7. Version Bump

None; this corrects a contradiction rather than changing intent.

## 8. Update Active Contract

Section 16.1's Maturity bucket column now matches the manifest.

## 9. Invalidate Affected Evidence

None exists.

## 10. Re-run Required Gates

LINT-19 is added to keep the firewall shut: every case must declare a bucket, and
neither GATE_CORE nor a Core maturity rung may name a RESEARCH case. Verified by
pulling MVP-06 back into the M9 gate on a copy.
