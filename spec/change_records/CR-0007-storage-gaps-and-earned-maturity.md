# CR-0007 — Tables for what v1 must persist, and a maturity level that is computed

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-19
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** [CR-0001](CR-0001-active-contract-becomes-source.md)

---

## 1. Change Proposal

**Three things v1 requires had nowhere to live.** Searching the whole DDL for
memory, baseline, reproducibility and holdout returned nothing.

- `REQ-S25-009` puts Evolution Memory in v1 scope and `memory_record.schema.json`
  is schema 25, but no table existed. Its `access_count` field makes the record
  mutable, so it cannot be an immutable CAS blob either. `REQ-S17-002` forbids the
  hidden holdout from reaching Evolution Memory — a rule with nothing to check.
- Section 10.4's better-rule compares against a `baseline`, and `baseline.schema.json`
  is schema 8, but no table existed.
- The achieved reproducibility level had no column, though MVP-12 and the evidence
  bundle both certify it.

Even the escape hatch was shut: `artifact_refs.owner_type` had no `MEMORY_RECORD` or
`BASELINE` value.

**The maturity claim was the one number nobody checked.** Every count in this repo
is derived and linted. `maturity_claim` was hardcoded in five places and verified by
nothing, which is how it read `M2_REQUIREMENTS_CANONICAL` after M3 was finished,
fixtured and gate-verified.

## 2. Decision

**Storage.** Two tables, taking the count from 29 to 31.

- `memory_records` — mutable, scoped by `project_id` and optionally `run_id`,
  unique on `(project_id, ast_pattern_hash)`, carrying `holdout_tainted` so
  `REQ-S17-002` becomes a checkable flag rather than a hope.
- `baselines` — unique on `(project_id, source_hash, environment_hash)`, because a
  baseline measured in a different environment is not comparable.
- `runs` gained `reproducibility_target` and `reproducibility_level` in CR-0004.
- `owner_type` gains `MEMORY_RECORD` and `BASELINE`, and the generated triggers
  cover all 18 owner types.

`SQLITE_DDL_29_TABLES.md` is renamed `SQLITE_DDL_TABLES.md` so the filename cannot
go stale again, and all 21 files that said "29-table" now say 31.

**Maturity.** `tools/compute_maturity.py` derives the level from artifacts: M0 is
UTF-8 integrity, M1 is the authority and protocol registries, M2 is unique
requirement IDs plus a clean linter run, M3 is the schema gate passing, and M4
onward look for the packages and test suites that do not exist yet. The computed
answer today is **M3_SCHEMAS**, and the five hardcoded claims are updated to match.

LINT-20 fails the build whenever the declared level and the computed level differ.
`compute_maturity.py` invokes the linter for M2, so the linter skips LINT-20 when
called that way; without that guard the two call each other forever.

## 3. Impact Analysis

| Affected | Effect |
|---|---|
| DDL, all three copies | 29 → 31 tables, 57 → 62 indices |
| `owner_type` | 16 → 18 values, triggers regenerated |
| `REQ-S13-011`, `REQ-S13-012`, `REQ-S28-002` | **new** |
| Section 28 | rewritten to report what the tools verify, claim `M3_SCHEMAS` |
| `EQ-251` | "29 SQLite Tables" → 31 |
| Requirement total | 185 → 188 |

## 4. Authority Check

The tables land in the contract at rank 2 alongside the rest of the DDL. The
maturity computation reads rank 1 `spec/maturity.yaml` and never invents a rung.

## 5. Security / Safety Review

`holdout_tainted` gives `REQ-S17-002` an enforcement point it never had. Both new
tables use `ON DELETE RESTRICT`, consistent with the evidence retention rule.

## 6. Traceability Impact

Three requirements added, none withdrawn.

## 7. Version Bump

None.

## 8. Update Active Contract

Section 13.2 gains both tables and the regenerated triggers; section 28 is rewritten.

## 9. Invalidate Affected Evidence

None exists.

## 10. Re-run Required Gates

All linters, the M3 gate and 864 tests pass. LINT-20 was verified by declaring
M9_CORE_GOLDEN on a copy; it reports the mismatch against the computed M3.
