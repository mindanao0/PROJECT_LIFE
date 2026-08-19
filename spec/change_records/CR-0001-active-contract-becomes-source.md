# CR-0001 — Active Contract becomes its own canonical source

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-19
> **Workflow:** Section 27 Governed Specification Change
> **Governance FSM:** `spec/fsm/governance.yaml`

---

## 1. Change Proposal

Section 0.5 defined the requirements file as a *generated* view:

```text
source:    Evolution_Engine_Plan_10_2_2_Complete_Single_File_Canonical_Release.md
generated: build/spec/Evolution_Engine_Active_Spec_10_2_2.md
generator: tools/render_active_spec.py
```

and `REQ-S00-007` declared it "read-only build artifact … ห้ามแก้ด้วยมือ".

Neither the source master nor the generator exists in the repository. The master
was deleted at commit `cac1d52`; `tools/render_active_spec.py` was never written.
The consequence is that there was **no lawful way to change the specification at
all**, while `REQ-S30-001` explicitly anticipates that implementation will surface
ambiguities requiring specification changes.

Proposal: promote the file to canonical source, move it out of `build/`, restore
the historical archive, and withdraw the four requirements that only make sense
under the generator model.

## 2. Impact Analysis

| Affected | Effect |
|---|---|
| `REQ-S00-005` marker rules for the generator | withdrawn — no generator exists |
| `REQ-S00-006` byte-preserving extraction | withdrawn — nothing is extracted |
| `REQ-S00-007` read-only build artifact | withdrawn — the file is now the source |
| `REQ-S00-008` CI regenerate + byte compare | withdrawn — nothing to regenerate |
| `REQ-S00-009` archive manifest SHA-256 | **retained**, retargeted at the recovered archive |
| `REQ-S00-010` | **new** — changes now require a record in `spec/change_records/` |
| CI job `spec_active_view_byte_match` | removed; 39 required jobs become 38 |
| CI job `spec_archive_checksum_match` | retained, now checks `spec/archive/manifest.json` |
| Requirement total | 179 → 176 |
| File path | `build/spec/Evolution_Engine_Active_Spec_10_2_2.md` → `spec/ACTIVE_CONTRACT.md` |

## 3. Authority Check

`spec/authority.yaml` rank 2 already names the Active Contract as the sole home of
the `[REQ]` declarations. This change removes the contradiction between that rank
and `REQ-S00-007`, which called the same file a non-authority. Rank 1 keeps
precedence over the contract; nothing in the hierarchy is reordered.

## 4. Security / Safety Review

No L0–L2 content changes. No sandbox, crypto or FSM rule is touched. The archive
is restored as `NON-NORMATIVE / SUPERSEDED` and cannot grant authority to anything
it contains.

## 5. Traceability Impact

Four IDs are withdrawn. Per Section 2.4 they are **immutable and permanently
reserved**; they must never be reissued. They are recorded under
`retired_requirements` in `spec/requirements.yaml` with a pointer to this record.
`REQ-S00-010` takes the next free number in section 00.

## 6. Human Approval

Requested by the repository owner and applied in the same session. This record is
the durable evidence required by Section 27.

## 7. Version Bump

Contract content version stays `10.2.2`; this is a governance-model correction,
not a semantic change to any engine requirement.

## 8. Update Active Contract

Section 0.5 rewritten. See the diff for commit that carries this record.

## 9. Invalidate Affected Evidence

No evidence bundle exists yet, so none is invalidated.

## 10. Re-run Required Gates

`tools/lint_state_vocabulary.py`, `tools/validate_schemas.py` and the full pytest
suite must pass in the same commit.

---

## Archive recovery

The Appendix C archive was not lost, only unreachable. It is recovered from commit
`26493b3` into `spec/archive/Plan_10_2_0_Historical_Archive.md` with
`spec/archive/manifest.json` recording its SHA-256, so `REQ-S00-009` becomes
satisfiable rather than being withdrawn with the others.

```text
recovered_from_commit  26493b3
deleted_at_commit      cac1d52
span_line_count        11845
```

Absolute `file:///Users/...` links inside the recovered text were flattened to
plain text; they pointed at the original author's machine and resolved nowhere.
