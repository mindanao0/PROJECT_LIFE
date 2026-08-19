# CR-0008 — Discover test coverage instead of declaring it, and specify the negative corpus

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-20
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** [CR-0005](CR-0005-sandbox-profile-mounts-and-env.md)

---

## 1. Change Proposal

**Coverage was hand-declared.** `tools/generate_requirements.py` carried a literal
`VERIFIED_BY` map naming which requirements a test exercised. Tests were then written
covering sixteen more requirements — the audit chain, the canonical serializer, the
sandbox profile, the requirement register itself — and the map was never updated, so
all sixteen stayed `PENDING` while being covered.

This is the same defect the repository has been correcting everywhere else: a fact
asserted by hand instead of derived. It happened to fail safe this time, understating
coverage rather than overstating it, but nothing made that the likely direction.

**The negative security corpus was three names.** MVP-08, MVP-09 and MVP-10 are
Core-gating — M6 requires the negative security corpus and M10 requires the SECURITY
bucket — yet each case had only a name and an expected disposition. Nothing said what
the attack does or what proves the sandbox stopped it, so a fixture that never
attacked anything would pass identically to one that was correctly contained.

**Three layout entries were stale.** Section 4 still listed
`tools/render_active_spec.py`, withdrawn by CR-0001; `spec/measurement/protocol.yaml`
next to a `reproducibility.yaml` that CR-0004 put at the `spec/` root; and no entry
for `spec/protocols.yaml`, `spec/archive/` or `spec/change_records/`, all of which now
exist.

## 2. Decision

**Coverage is discovered.** A test claims a requirement by naming its id in its own
source, usually the module docstring, and `discover_test_refs()` scans for that. The
claim is not free: `tests/conformance/test_requirement_register.py` asserts every
referenced file exists, and the referencing test has to pass for the suite to be
green. Coverage moves from 18 to 35 of 189 requirements, all of which were already
covered — the number changed, the reality did not.

**`spec/sandbox/negative-tests.yaml`** specifies each Core-gating security case with
four things: the attack, the kernel mechanism that must stop it, the observable that
proves it, and a **negative control** that fails the case if the attack silently did
nothing. The corpus also has to prove it is testing the sandbox rather than the
fixture: running the same fixture without PROFILE_A must produce a different
disposition.

**Section 4** now matches the repository.

## 3. Impact Analysis

| Affected | Effect |
|---|---|
| `tools/generate_requirements.py` | `VERIFIED_BY` map replaced by `discover_test_refs()` |
| `spec/requirements.yaml` | AUTOMATED_TEST 18 → 35 |
| `spec/sandbox/negative-tests.yaml` | **new**, rank 1 |
| `REQ-S12-025` | **new** |
| Section 4 layout | stale entries removed, real ones added |
| Requirement total | 188 → 189 |

## 4. Authority Check

The negative corpus lands at rank 1 beside the other sandbox files. Discovery reads
the repository rather than a declaration, which is the direction every other fix in
this series has taken.

## 5. Security / Safety Review

The negative control is the substantive part. Without it a security case cannot
distinguish "the sandbox held" from "the attack was never attempted", which is the
failure mode that makes a green security suite worthless.

## 6. Traceability Impact

One requirement added. `REQ-S22-004` still holds: a requirement with no test remains
PENDING, and discovery cannot mark one verified without a test that names it and passes.

## 7. Version Bump

None.

## 8. Update Active Contract

Section 4 corrected; section 12.3 gains `REQ-S12-025`.

## 9. Invalidate Affected Evidence

None exists.

## 10. Re-run Required Gates

873 tests pass; all twenty linters and the M3 gate are green.
