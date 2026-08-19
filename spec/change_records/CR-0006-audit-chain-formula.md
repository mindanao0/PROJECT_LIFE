# CR-0006 — Complete the audit hash chain formula

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-19
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** [CR-0004](CR-0004-canonical-bytes-and-reproducibility.md)

---

## 1. Change Proposal

Section 18.1 gave the shape and left three things open:

```text
event_hash = SHA256(previous_event_hash || canonical_event_payload)
```

**`canonical_event_payload` was never defined.** The phrase appeared twice in the
whole repository and nowhere said what it contains. If it were the bytes of the
artifact that `payload_artifact_id` points at, the chain would not bind `run_id` or
`sequence_no` at all, and reordering two events would be undetectable.

**`||` had no encoding.** Concatenating the raw 32-byte digest, the 64-character
lowercase hex, or a `sha256:`-prefixed string all read naturally and all produce
different hashes. Two correct implementations would disagree.

**Genesis contradicted itself.** Section 18.1 said `previous_event_hash = null`
while `RELEASE_EVIDENCE_BUNDLE.md` recorded
`"genesis_hash": "sha256:000…0"`. A verifier following one would compute a head
that the other's bundle does not declare.

`audit_chain_verification` is a `GATE_CORE` mandatory check, so none of this was
implementable.

## 2. Decision

- **Payload** is the canonical bytes of exactly six fields: `run_id`,
  `sequence_no`, `actor`, `event_type`, `payload_artifact_id`, `created_at_utc`.
  Including `sequence_no` and `run_id` is what binds the chain to order and scope.
  Key order follows `spec/reproducibility.yaml`, so it is lexicographic and fixed.
- **`||` is raw byte concatenation**: the 32-byte digest followed by the payload
  bytes. Hex and prefixed forms are explicitly forbidden.
- **Genesis** uses 32 zero bytes as `previous_digest_bytes` while the database
  column `previous_event_hash` stores `NULL`. Both statements are now true and
  they no longer contradict each other. The evidence bundle field is renamed
  `genesis_previous_digest` and carries the 64-hex rendering of those zero bytes
  without a prefix.
- **Scope**: one `run_id` is one chain, and `run_id IS NULL` is the engine chain,
  which starts at its own sequence 0.

## 3. Impact Analysis

| Affected | Effect |
|---|---|
| Section 18.1 | payload fields, concatenation and genesis all pinned |
| `REQ-S18-004`, `REQ-S18-005` | **new** |
| `tools/canonical_bytes.py` | gains the reference chain implementation and verifier |
| `RELEASE_EVIDENCE_BUNDLE.md` | `genesis_hash` → `genesis_previous_digest`, prefix removed |
| Requirement total | 183 → 185 |

## 4. Authority Check

The formula sits in the contract at rank 2, resting on the canonical byte rules at
rank 1. The evidence bundle document is rank 4 and yields.

## 5. Security / Safety Review

This is the tamper-evidence mechanism, so pinning it is the whole point. The tests
prove the chain now detects field tampering, reordering, a gap and a forged link —
none of which could be asserted while the formula was ambiguous.

## 6. Traceability Impact

Two requirements added, none withdrawn.

## 7. Version Bump

None.

## 8. Update Active Contract

Section 18.1 rewritten.

## 9. Invalidate Affected Evidence

None exists.

## 10. Re-run Required Gates

`tests/conformance/test_audit_chain.py` covers both scopes with three events each
as `REQ-S18-005` requires, and asserts that the raw-byte form differs from the hex
and prefixed forms, so a future implementation cannot quietly pick the wrong one.
