# CR-0005 — Give PROFILE_A_LINUX real numbers, one rootfs model and a closed environment

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-19
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** [CR-0001](CR-0001-active-contract-becomes-source.md)

---

## 1. Change Proposal

Section 12 listed seventeen sandbox invariants and no numbers. Three consequences:

**Limits had no values.** `memory.max`, `cpu.max`, `pids.max`, `RLIMIT_NOFILE` and
`RLIMIT_FSIZE` appeared nowhere in the contract. Only `timeout_seconds` and
`writable_tmp_bytes` had values. The execution outcomes `OOM` and
`RESOURCE_EXCEEDED` therefore had no mechanism that could produce them, and
`SECURITY_VIOLATION` had no detection channel at all — while `REQ-S12-003` forbids
treating a Python monkeypatch as the boundary.

**Two rootfs models were implied at once.** A denied list containing `~/.ssh` and
`/var/run/docker.sock` only means something when the host root is visible; "แยก Root
Filesystem" means those paths never existed. Nothing chose. Nothing mounted the
CPython interpreter the candidate must run, though `REQ-S12-006` requires the profile
to be built and tested against CPython 3.12.

**The environment leaked the host import path.** The only allowlist in the repo was
`{PATH, PYTHONPATH, LANG}` in a rank 4 document. Passing the host `PYTHONPATH` in
lets the host choose which modules the candidate loads, which defeats a minimal
rootfs entirely.

## 2. Decision

Three rank 1 files, all declared in the section 4 layout and none of which existed.

**`spec/sandbox/profile-a-linux.yaml`** — concrete limits promoted from the rank 4
document and completed: memory 512 MiB hard / 384 MiB soft, swap 0, 1.0 CPU,
`pids.max` 64, `RLIMIT_NOFILE` 256, `RLIMIT_FSIZE` matching the tmpfs, no core dumps.
A project may lower a limit and never raise it; the engine takes the minimum and
records it in the environment manifest so replay compares like with like.

It also adds the **violation mapping**, which is total: seccomp kill →
`SECURITY_VIOLATION`, cgroup `oom_kill` → `OOM`, `pids.events max` → `RESOURCE_EXCEEDED`,
wall clock → `TIMEOUT`, anything else non-zero → `CRASHED`. No abnormal termination
can fall through to `SUCCESS`.

**`spec/sandbox/mounts.yaml`** — **minimal rootfs**. It is the stronger of the two
models: a path that was never mounted cannot be reached by a bug in a deny rule.
`/usr`, `/lib` and `/lib64` are read-only so CPython exists; `/workspace` is
read-only; `/tmp` is the only writable surface; `/proc` gets `hidepid=2`,
`subset=pid` and named masked and readonly paths instead of the word "restricted";
`/sys` is not mounted at all. The old denied list becomes
`assertions_after_setup.must_not_exist`, which is what MVP-08 can actually assert.

**`spec/sandbox/env-allowlist.yaml`** — deny by default, nine pinned variables, and
`PYTHONPATH`, `PYTHONSTARTUP`, `LD_PRELOAD` and `LD_LIBRARY_PATH` explicitly removed
with the reason. `PYTHONHASHSEED=0`, `LC_ALL=C.UTF-8` and `TZ=UTC` are pinned because
hash order, collation and time formatting are all hash-critical.

## 3. Impact Analysis

| Affected | Effect |
|---|---|
| `spec/sandbox/*.yaml` | three new rank 1 files |
| Section 12.2 | gains `REQ-S12-021`, `REQ-S12-022` |
| Section 12.3 | gains `REQ-S12-023`, `REQ-S12-024` |
| `SECCOMP_BPF_FILTERING.md` | `clone/fork/vfork` and `socket(AF_UNIX)` were `SECCOMP_RET_ALLOW`, contradicting section 12.5 `candidate subprocess = DENY`; both are now kill-by-default |
| `spec/authority.yaml` | rank 1 glob was `spec/*.yaml`, which did not cover `spec/fsm/` or `spec/sandbox/`; now `spec/**/*.yaml` |
| Requirement total | 179 → 183 |

## 4. Authority Check

Values move from rank 4 to rank 1. The authority glob fix is a correction: the
existing `spec/fsm/*.yaml` files were already outside the literal rank 1 pattern.

## 5. Security / Safety Review

This change only tightens. The rootfs shrinks, the environment shrinks, subprocess
creation moves from allowed to killed, and every abnormal exit now has a named
outcome instead of possibly reading as success.

## 6. Traceability Impact

Four requirements added, none withdrawn.

## 7. Version Bump

None.

## 8. Update Active Contract

Sections 12.2 and 12.3 point at the three files.

## 9. Invalidate Affected Evidence

None exists.

## 10. Re-run Required Gates

`tests/security/test_sandbox_profile.py` asserts every limit has a value, the
violation mapping is total, the rootfs model is chosen, the interpreter is mounted,
only `/tmp` and `/dev` are writable, and `PYTHONPATH` is not passed through.
