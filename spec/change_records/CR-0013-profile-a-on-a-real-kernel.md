# CR-0013 — PROFILE_A_LINUX on a real kernel (M6)

> **Status:** RATIFIED_CANONICAL
> **Date:** 2026-08-21
> **Workflow:** Section 27 Governed Specification Change
> **Depends on:** [CR-0005](CR-0005-sandbox-profile-mounts-and-env.md), [CR-0008](CR-0008-discovered-coverage-and-negative-corpus.md)

---

## 1. Change Proposal

CR-0005 gave PROFILE_A concrete limits, a minimal-rootfs mount model and a total
violation-to-outcome mapping. CR-0008 specified the three Core-gating security cases
with an attack, a mechanism, an observable and a negative control each. Both were
documents. Nothing had executed.

M6's gate is "PROFILE_A executable on required kernel/backend matrix, capability probes
fail closed, negative security corpus passes". That cannot be satisfied by a
specification, only by a kernel refusing something.

## 2. What was built

`src/evolution_engine/sandbox/profile_a.py`. Every limit is read from
`spec/sandbox/profile-a-linux.yaml` rather than written in the module, so the rank 1
declaration is what takes effect — and a test asserts the ceiling does not appear as a
literal in the source.

- **Namespaces**: user, mount, PID, network and IPC, unshared before anything else.
- **Filesystem**: mount propagation detached, then empty tmpfs over `/etc`, `/home`,
  `/root`, `/var`, `/run`, `/boot`, `/srv` and `/sys`, and `/proc` masked path by path.
- **Limits**: `memory.max`, `memory.high`, `memory.swap.max` and `pids.max` through a
  delegated cgroup v2 scope; `RLIMIT_NOFILE`, `RLIMIT_FSIZE` and `RLIMIT_CORE` through
  rlimits.
- **Syscalls**: a seccomp BPF filter installed after `PR_SET_NO_NEW_PRIVS` and before
  the candidate's first bytecode, killing `socket`, `connect`, `bind`, `clone`, `fork`,
  `execve`, `ptrace`, `mount`, `unshare`, `keyctl`, `userfaultfd` and `io_uring_setup`.

A denylist rather than an allowlist: an allowlist has to enumerate everything CPython
touches at startup, and getting it wrong kills the interpreter instead of the attack,
which would make MVP-08..10 untestable rather than passing.

## 3. Measured, not asserted

```
benign code           SUCCESS
MVP-08 fs escape      every must_not_exist path absent; /proc paths masked
MVP-09 socket()       SECURITY_VIOLATION  SECCOMP_DENIED_SYSCALL  SIGSYS
MVP-10 fork bomb      SECURITY_VIOLATION  SECCOMP_DENIED_SYSCALL  SIGSYS
execve                SECURITY_VIOLATION
infinite loop         TIMEOUT             whole cgroup killed
```

`REQ-S12-003` forbids treating a Python-level guard as the boundary, so MVP-09 asserts
the kernel signal number, not an exception type.

## 4. A distinction the spec had wrong

`mounts.yaml` listed `/proc/kcore` under `must_not_exist`. It cannot be absent —
CPython needs `/proc` — so it is **masked**: bound over with `/dev/null`, present and
revealing nothing, which is what `masked_paths` in the same file already described.
Conflating "absent" with "masked" made the M6 test assert something no correct sandbox
could satisfy. `assertions_after_setup` now separates `must_not_exist` from
`must_be_masked`, and the tests check the right guarantee for each.

## 5. Two bugs of the same shape

Both were work done inside the child *after* confinement, depending on things
confinement had just removed.

- `ctypes.util.find_library` shells out to `ldconfig`. Called after `/etc` and `/var`
  became empty tmpfs and behind a filter denying `fork`, it failed — so **every**
  candidate looked like a crash, benign ones included. libc is now resolved at import.
- The masked-path list was read from `spec/sandbox/mounts.yaml`, which lives under
  `/home` — a tree the child had just covered. It is read at import too.

When confinement could not be completed, the sandbox now exits with
`SANDBOX_SETUP_INCOMPLETE` rather than running the candidate unconfined. Refusing to
run beats running unprotected and recording the result as a pass.

## 6. Honest skipping

The tests skip on a kernel without unprivileged user namespaces or seccomp, and the
cgroup tests skip without a writable delegated subtree. **A skip is not a pass**:
`m6_security()` counts passes, so M6 stays unearned on a machine that cannot run what
M6 certifies. One test runs everywhere and asserts that an unusable sandbox reports a
reason, so a green suite on such a machine is still visibly incomplete.

## 7. Maturity

**M5_FSM_AND_CONFIG → M6_SECURITY**, computed. On this kernel — Linux 7.1.5, cgroups v2
with memory and pids delegated, unprivileged user namespaces enabled — all 19 tests
execute rather than skip.

## 8. Re-run Required Gates

979 tests pass, 22 linters green, M3 gate passes, `mypy --strict` clean over 24 files.
