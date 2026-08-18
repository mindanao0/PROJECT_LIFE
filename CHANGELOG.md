# Changelog

All notable changes to the **Evolution Engine Specification & Architecture** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to the Evolution Engine Canonical Versioning Policy.

---

## [10.2.2] - 2026-08-18 (Plan 10.2.2 Implementation-Start Canonical Release)

### Added
- **Sequential Requirement IDs:** 179 canonical machine-checkable Requirement IDs (`REQ-S00-001` through `REQ-S30-002`) across all active sections.
- **Relational Integrity in SQLite DDL:** Added unique natural key constraints to `test_definitions`, `capability_definitions`, `objective_definitions`, `oracle_results`, `policy_snapshots`, and `environment_manifests`.
- **Generated Active-Spec View:** Defined `build/spec/Evolution_Engine_Active_Spec_10_2_2.md` derived from canonical `ACTIVE_SPEC_BEGIN` and `ACTIVE_SPEC_END` markers.
- **Detailed FSMs:** Formalized Run FSM (11 states), Recovery FSM (9 states), Governance FSM (12 states), Candidate FSM (17 states), and Deployment FSM (8 states).
- **Mandatory Vertical Slice:** Defined concrete requirements for MVP-01 pure-function walking skeleton prior to full system assembly.
- **Linux Conformance Matrix:** Detailed kernel baseline lanes (A1 Linux 6.1 LTS through A4 Linux 6.18 LTS) with rootless OCI and native namespace backends.
- **EE-CRYPTO-1 Profile:** Formalized Ed25519 multisig verification rules, replay-resistant nonces, and offline revocation checks.

### Changed
- Resequenced Section 19 requirement identifiers to follow text flow monotonically (`REQ-S19-001` to `REQ-S19-008`).
- Clarified that Diversity Scoring ($[0,1]$ normalized AST, Token, Behavioral distances) operates prior to Preference Score tie-breaking.
- Clarified Pareto dominance mechanics to be direction-aware while ignoring metric preference weights during ranking.

### Removed
- Removed legacy patch sections, repeated boilerplate formulas, and fake example golden hashes from the active contract.
- Superseded and demoted historical content into **Appendix C — Full Historical & Design Archive**.

---

## [10.2.0] - Canonical Rewrite Baseline

### Added
- Single-File Canonical structure containing both Active Specification and non-normative Appendix C archive.
- Exact 26 JSON Schema Registry target and 29 SQLite tables definition.
- 14 Golden Corpus cases (`MVP-01` to `MVP-14`).
- Strict requirement lifecycle (`REQ` $\rightarrow$ `IMPL` $\rightarrow$ `TEST` $\rightarrow$ `EVID`).
- Argv-only command model (`shell=false` enforced across all subprocess executions).

---

## [10.1.0] - Historical

- Deprecated append-only patch sections.
- Consolidated multi-file draft specifications into initial master releases.

---

## [1.0.0 .. 10.0.0] - Historical (Archived in Appendix C)

- Initial evolution engine concepts, AST mutation operators, sandboxing explorations, and population lifecycle research.
