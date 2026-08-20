# CR-0010 — Make every maturity rung as strong as the gate it claims to check

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-20
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** [CR-0009](CR-0009-close-the-regressions.md)

---

## 1. Change Proposal

CR-0009 rewrote `m4_protocols()` because it counted `.py` files, so nineteen empty
ones passed a gate reading "19 Typed Python Protocols with zero type errors". In the
same change it extended the ladder to M13 — **writing the new rungs with the exact
defect it was fixing.**

Measured directly: create an empty file at each path a predicate globs for, then call
the predicates.

```
m5_fsm_and_config                 empty files -> True
m6_security                       empty files -> True
m7_persistence                    empty files -> True
m8_recovery                       empty files -> True
m9_core_golden                    empty files -> True
m10_security_reliability_golden   empty files -> True
m12_production                    empty files -> True
m13_self_evolution                empty files -> True
```

Eight of thirteen. `touch` ten paths and the ladder reports M13 — and LINT-20, written
specifically to stop the maturity claim being asserted rather than earned, reports
nothing wrong, because it compares the declared value against a computation that is
itself trivially satisfiable.

## 2. Decision

A predicate must run the thing it claims to check. `_suite_passes(pattern, minimum)`
requires the matching tests to exist, to pass, and to collect at least `minimum`
tests — so an empty file, a file that errors, and a file with no assertions all fail.

Minimums come from the specification rather than being picked:

| Rung | Minimum | Why |
|---|---|---|
| M6 | 3 | MVP-08, MVP-09, MVP-10 are the SECURITY bucket |
| M8 | 2 | "DB and CAS crash matrix" is more than one crash point |
| M9 | 5 | the CORE bucket is MVP-01..MVP-05 after CR-0003 |
| M10 | 3 + 2 | SECURITY is MVP-08..10, RELIABILITY is MVP-11..12 |
| M13 | 1 + 1 | MVP-14 plus the root-of-trust proof |

`m11_execution_ready()` previously needed only a `build/evidence` directory to exist,
so `mkdir` satisfied it. It now requires a non-empty `evidence_bundle.json`.

The subprocess is scoped to directories holding no conformance test, so a predicate
cannot re-enter the linter that called it.

## 3. Guard

`tests/conformance/test_maturity_predicates.py` copies the repo, plants an empty file
at every path a predicate globs for, and asserts that not one rung is satisfied. It
also asserts every declared rung has a predicate, that no `_suite_passes` call allows
a zero minimum, and that M4 still checks mypy, the lock artifact and real `Protocol`
classes.

This is the difference between fixing an instance and fixing the class. CR-0009 fixed
the instance.

## 4. Impact Analysis

| Affected | Effect |
|---|---|
| `tools/compute_maturity.py` | nine predicates rewritten; `_suite_passes` added |
| `tests/conformance/test_maturity_predicates.py` | **new**, 12 tests |
| Computed maturity | unchanged at M3_SCHEMAS — the rungs were never legitimately reached |

## 5. Authority Check

No rank 1 data changes. This corrects a tool that reads it.

## 6. Traceability Impact

None added or withdrawn.

## 7. Re-run Required Gates

893 tests pass, 22 linters green, M3 gate passes.
