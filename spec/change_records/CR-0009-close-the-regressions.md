# CR-0009 — Close the regressions CR-0002..CR-0007 introduced

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-20
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** CR-0002, CR-0003, CR-0004, CR-0007

---

## 1. Change Proposal

An adversarial audit of the seven preceding change records found thirteen
regressions they caused. Four mattered, and all four share one cause: **a rule was
declared at rank 1 and applied in only one place.**

**Identifier split-brain (CR-0004).** CR-0004 declared `CandidateId`, `GenerationId`
and `ArtifactId` content-derived 64-hex, then changed one schema. Eleven others kept
`format: uuid` for the same fields, so `generation_id` was a UUID in
`17_selection_decision/valid/minimal.json` and 64-hex in
`01_candidate/valid/minimal.json` — both shipped as *valid* fixtures.

The M3 gate could not see it: `tools/validate_schemas.py` built validators without a
`FormatChecker`, which makes `format` a comment. The one deliverable declared
complete was certifying a corpus that contradicts rank 1.

**`MutationId` had no derivation (CR-0004).** It sits inside `CandidateId`'s envelope
while being a random UUID everywhere it appears, so `CandidateId` was never actually
content-derived and two replays still produced different ids — the precise defect
CR-0004 was written to close. `REQ-S29-004` stayed unsatisfiable.

**Maturity ceiling (CR-0007).** `compute_maturity.py`'s ladder stopped at M9 while
`GATE_CORE` requires M10. Since LINT-20 demands declared equals computed, **no
release gate could ever be entered.** Before CR-0007 the value was hardcoded and
therefore declarable though wrong; after it, it became undeclarable.

**`m4_protocols()` counted files (CR-0007).** Nineteen empty `.py` files passed a
gate that reads "19 Typed Python Protocols with zero type errors", and the predicate
never touched mypy or the pinned-dependency clause.

**The root cause of half the rest:** every linter read `spec/` and none read `docs/`.
`docs/09_MATURITY_GATES_AND_ROADMAP.md` — the file whose name most invites opening
when asking what M4 needs — still said 22 protocols and put MVP-06 quantum and
MVP-07 Rust on the M9 Core rung, three change records after both were corrected at
rank 1. `docs/07_SCHEMAS_AND_PROTOCOLS.md` and `docs/API_REFERENCE.md` still offered
`connect_swarm` and `evolve swarm join`, which section 3.1 excludes from Core v1.

## 2. Decision

| Fix | Effect |
|---|---|
| `MutationId` is content-derived | `SHA-256` of parent, strategy, operator, seed and target; `CandidateId`'s envelope finally closes |
| `identifier_rules` in `spec/reproducibility.yaml` | names all 18 content-derived properties, so the rule is data rather than prose |
| `tools/sync_identifier_formats.py` | rewrites every schema from that list; 20 properties across 13 schemas aligned |
| `FormatChecker` enabled in both validators | `format` is evaluated instead of ignored; invalid fixtures 244 → 248 |
| Ladder extended M10–M13 | a release gate can be reached |
| `m4_protocols()` rewritten | requires the named `Protocol` classes, full annotation, `mypy --strict` clean and the lock artifact; verified to return False on nineteen empty files |
| `requirements.lock` | REQ-S03-004's lock artifact, with the pyproject digest it was resolved from |
| docs corrected | the two maturity tables are regenerated from `spec/maturity.yaml`; swarm surface removed; counts fixed |
| **LINT-21** | content-derived properties must carry the 64-hex pattern, every identifier needs a formula, anything in `CandidateId`'s envelope must itself be content-derived, and the M3 validator must check formats |
| **LINT-22** | `docs/` may not contradict rank 1 counts, may not place a RESEARCH case on a Core rung, and may not offer a CLI verb section 6.1 does not declare |

## 3. Authority Check

Every fix moves a declaration into data at rank 1 and derives the rest. LINT-22 is
the structural correction: rank 4 was never being checked against rank 1 at all.

## 4. Security / Safety Review

Removing `connect_swarm` from the public surface closes an out-of-scope network
capability that the Core sandbox spec never accounted for.

## 5. Traceability Impact

No requirement added or withdrawn.

## 6. Version Bump

None.

## 7. Re-run Required Gates

881 tests pass, 22 linters green, M3 gate passes with format checking on.
LINT-21 verified by reverting one schema to `format: uuid`; LINT-22 verified by
adding a RESEARCH case to a Core rung and an undeclared `evolve teleport` verb.

---

## What this says about the process

Seven of the nine change records were correct in intent and incomplete in reach. The
pattern is consistent: declare at rank 1, apply at one site, and let the derived
copies drift. The two linters added here exist because the previous eight change
records could not see their own blast radius.
