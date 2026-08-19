# CR-0004 — Pin the canonical bytes, derive CandidateId, define R0–R4

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-19
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** [CR-0001](CR-0001-active-contract-becomes-source.md)

---

## 1. Change Proposal

Three gaps sat on the critical path to M5 and M11.

**The canonical bytes were not pinned.** Section 11.1 fixed eight rules but left
four degrees of freedom, each enough to make two correct implementations disagree
on a hash: whether an absent field and an explicit `null` are the same bytes, what
range an integer may occupy, which characters are escaped and how, and what a
canonical decimal looks like. A fifth, the trailing newline, was never mentioned.

**CandidateId had no derivation.** `REQ-S10-010` makes its order the final
tie-break and `REQ-S29-004` makes the vertical slice compare it across two replays,
yet `schemas/01_candidate.schema.json` declared it `format: uuid` — a random value.
Two replays of the same run would produce different ids, so the acceptance criterion
of the slice could never be evaluated.

**R0–R4 were five labels.** Section 11.3 named them and described the scope of R4.
No level had an operational definition or a verification procedure, and no column
anywhere recorded which level a run achieved, though `MVP-12` and the evidence
bundle both require the level to be certified.

## 2. Decision

`spec/reproducibility.yaml` becomes the rank 1 home for all three.

- **Canonical bytes**: the eight existing rules plus the five that were open. An
  absent field and a `null` are different bytes; integers are signed 64-bit and an
  out-of-range value is an error rather than a float; escaping is minimal and
  non-ASCII stays literal UTF-8 so NFC is what fixes the bytes; decimals follow the
  `REQ-S05-011` pattern with half-even rounding to the declared scale; and canonical
  bytes carry no trailing newline.
- **Identifiers**: each is declared content-derived or event-derived.
  `CandidateId` is `SHA-256` over `{generation_index, source_hash,
  parent_candidate_id, mutation_id}`, rendered as 64 lowercase hex characters,
  which gives `REQ-S10-010` a total and machine-independent order.
  `ArtifactId` and `GenerationId` are likewise content-derived. `RunId` and the
  attempt ids stay event-derived UUIDv7 and are never part of a compared digest —
  a replay is a new run and gets a new `RunId`.
- **R0–R4**: each level gets a definition and a verification procedure, plus the
  implication order. R4 implies R2 implies R1 implies R0; R3 implies R1; R3 and R2
  are not ordered.

## 3. Impact Analysis

| Affected | Effect |
|---|---|
| `spec/reproducibility.yaml` | **new**, rank 1 |
| `tools/canonical_bytes.py` | **new** reference serializer |
| `tests/golden/canonical_bytes_vectors.json` | **new**, satisfies `REQ-S11-002` |
| `schemas/01_candidate.schema.json` | `candidate_id`, `generation_id`, `parent_candidate_id` become 64-hex, not UUID |
| `runs` table | gains `reproducibility_target` and `reproducibility_level` |
| Section 11 | gains `REQ-S11-003`, `REQ-S11-004`, `REQ-S11-005` |
| Requirement total | 176 → 179 |

## 4. Authority Check

All three additions land at rank 1 with the contract pointing at them, which is the
direction `spec/authority.yaml` requires.

## 5. Security / Safety Review

Content-derived ids remove a source of non-determinism from selection, which
strengthens the audit trail. No sandbox or crypto rule is touched.

## 6. Traceability Impact

Three requirements added. None withdrawn.

## 7. Version Bump

None; these close gaps rather than change intent.

## 8. Update Active Contract

Sections 11.1, 11.2 and 11.3 now point at `spec/reproducibility.yaml` and carry the
three new requirements.

## 9. Invalidate Affected Evidence

None exists.

## 10. Re-run Required Gates

The fixture corpus and schema manifest were regenerated for the changed schema and
the added `runs` columns; the M3 gate, all linters and the full suite pass.

---

## Adversarial vectors

Two of the fourteen golden vectors exist to catch a serializer that looks right:

- `nfc_normalization` and `nfc_precomposed` are two spellings of `é` and **must**
  hash identically.
- `null_present_vs_absent_a` and `_b` differ only by an explicit `null` and **must**
  hash differently.

`tools/generate_golden_vectors.py` refuses to write the file if either fails, so a
broken serializer cannot regenerate vectors that agree with it.
