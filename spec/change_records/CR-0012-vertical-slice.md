# CR-0012 — The mandatory trusted-fixture vertical slice (M5)

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-20
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** [CR-0004](CR-0004-canonical-bytes-and-reproducibility.md), [CR-0011](CR-0011-protocol-package.md)

---

## 1. Change Proposal

Section 29.1 fixes the slice's scope exactly — MVP-01, function level, strategies M01
and M02, population 4, one generation, seed 12345, one capability test, one objective,
in-memory persistence, `SAFE_EXPORT_ONLY`. It could not be built, for two reasons.

**The fixture was empty.** `benchmarks/golden/mvp01_pure_function/` held a
`project.yaml` and a README. Section 16.2 requires eleven things of every corpus case —
fixture source, version, canonical baseline hash, config, seed, environment manifest,
expected disposition, reason code, metric bounds, security verdict, evidence records —
and the directory supplied none of them. There was nothing to hash, nothing to run and
no expected outcome.

**The acceptance criterion was unverifiable.** REQ-S29-004 requires two replays to
agree on the CandidateId, selection and lineage digests. Until CR-0004 made CandidateId
content-derived and CR-0009 closed MutationId inside its envelope, two replays produced
different ids by construction, so no test could have asserted it.

The fixture also declared `sandbox_profile: PROFILE_A_LINUX`, which REQ-S29-003
forbids: the slice may not enter PROFILE_A before M6.

## 2. What was built

**The fixture** — `src/math_kernel.py` with one integer constant and one arithmetic
operator, so M01 and M02 each have exactly one site and the candidate set is fully
enumerable. One capability test. An `evolution.yaml` that validates against schema 26
with zero errors. A `fixture_manifest.yaml` carrying all eleven section 16.2 items,
with `canonical_baseline_hash` computed from real bytes as REQ-S16-001 demands and
REQ-S16-002 requires of every hash in the corpus.

**The adapters** — `src/evolution_engine/adapters/in_memory.py`, implementing the
published protocols rather than a temporary API, which REQ-S29-001 requires so that
REQ-S29-005 holds when persistence and sandboxing arrive behind the same boundary.

The mutation engine emits three candidates and **one of them is deliberately
malformed**: an operator swap producing an AST the compiler rejects. A real mutation
engine produces invalid ASTs, and the static gate exists to catch them, so a slice that
never generated one would leave that path untested.

**The slice** — `src/evolution_engine/slice.py` walks section 29.1's required path one
stage at a time, using the real Run and Candidate FSM vocabularies and the canonical
serializer.

Observed: 4 candidates, 1 rejected by the static gate, 2 rejected by the capability
gate, the baseline selected, exported under `SAFE_EXPORT_ONLY`.

## 3. Acceptance

`tests/replay/test_vertical_slice.py`, 21 tests, covering each REQ-S29-004 condition:
the static-invalid candidate is rejected, a behaviour-breaking candidate is caught by
the capability gate rather than the static one, rejected candidates never receive a
metric (REQ-S08-002), the export hash matches the manifest's baseline hash, and two
replays agree on candidate ids, the selected candidate, the selection digest and the
lineage digest.

It also asserts the run's state sequence is a legal path through `spec/fsm/run.yaml`
rather than merely a set of valid names, and that every CandidateId is 64 hex
characters rather than a UUID.

## 4. What mypy caught

`mypy --strict` found a real defect the tests did not: the slice reused one variable
for both a `PolicyVerdict` and a `CapabilityVerdict`, so a capability decision was
being read through a policy type. It passed at runtime because both have the fields
used. This is the value CR-0011 predicted from checking the specification against a
compiler instead of against another document.

The canonical serializer moved from `tools/canonical_bytes.py` to
`src/evolution_engine/canonical.py` — it is engine code that the protocols and the
slice depend on, not a build tool. `tools/canonical_bytes.py` remains as a re-export so
existing imports keep working.

## 5. A predicate bug found while landing this

`_suite_passes` passed `-q` to pytest while `pytest.ini` already sets it. Two `-q`
collapse to `-qq`, which suppresses the summary line the function reads, so it reported
"not yet" for a suite that had just passed. It now omits the flag, and raises rather
than returning False when pytest exits 0 with unreadable output — a predicate that
cannot count is broken, not failing.

## 6. Maturity

**M4_PROTOCOLS → M5_FSM_AND_CONFIG**, computed. `m5_fsm_and_config()` requires the
engine package and a passing `tests/replay` suite; CR-0010's decoy test proves it
rejects an empty file, and that test was updated to remove real suites before planting
decoys, since a genuinely earned rung would otherwise make the decoy prove nothing.

## 7. Re-run Required Gates

960 tests pass, 22 linters green, M3 gate passes, `mypy --strict` clean over 22 files.
