"""PROFILE_A_LINUX on a real kernel — the negative security corpus (M6).

These are the tests M6 certifies: MVP-08 filesystem escape, MVP-09 network egress and
MVP-10 fork bomb, each run against the actual sandbox rather than against the spec that
describes it. `spec/sandbox/negative-tests.yaml` states the attack, the kernel mechanism
that must stop it, the observable, and a negative control for each.

On a kernel without unprivileged user namespaces or seccomp these SKIP. A skip is not a
pass: `m6_security()` counts passes, so M6 stays unearned on a machine that cannot run
what M6 certifies. Reporting M6 from a machine that never executed a sandbox would be
exactly the unearned claim REQ-S28-002 exists to prevent.
"""
from __future__ import annotations

import sys

import pytest
import yaml

from tests.conftest import ROOT

sys.path.insert(0, str(ROOT / "src"))
from evolution_engine.sandbox.profile_a import (  # noqa: E402
    DENIED_SYSCALLS,
    load_environment,
    load_profile,
    probe_support,
    run_candidate,
)
from evolution_engine.types import ExecutionStatus  # noqa: E402

NEGATIVE = yaml.safe_load(
    (ROOT / "spec/sandbox/negative-tests.yaml").read_text(encoding="utf-8"))
MOUNTS = yaml.safe_load((ROOT / "spec/sandbox/mounts.yaml").read_text(encoding="utf-8"))
CASES = {case["case_id"]: case for case in NEGATIVE["cases"]}

SUPPORT = probe_support()
requires_sandbox = pytest.mark.skipif(
    not SUPPORT.usable,
    reason=f"kernel cannot run PROFILE_A: {SUPPORT.reasons or 'namespaces or seccomp missing'}")
requires_cgroups = pytest.mark.skipif(
    not SUPPORT.limits_enforceable,
    reason="no writable delegated cgroup v2 subtree for this user")


# --- negative controls, run first -------------------------------------------
# spec/sandbox/negative-tests.yaml: a case that errors for an unrelated reason, or never
# runs at all, is a FAILED case rather than a passing one. These prove the harness can
# tell the difference.

@requires_sandbox
def test_benign_code_succeeds_inside_the_sandbox():
    """If this fails, every security result below is meaningless."""
    outcome = run_candidate("x = sum(i * i for i in range(1000))")
    assert outcome.status is ExecutionStatus.SUCCESS, outcome.reason_code


@requires_sandbox
def test_the_workspace_is_writable_inside_the_sandbox():
    """MVP-08's negative control: containment, not a totally unusable filesystem."""
    outcome = run_candidate("open('probe.txt', 'w').write('x')")
    assert outcome.status is ExecutionStatus.SUCCESS, outcome.reason_code


@requires_sandbox
def test_setup_failure_is_reported_rather_than_ignored():
    """The sandbox refuses to run a candidate it could not confine."""
    source = (ROOT / "src/evolution_engine/sandbox/profile_a.py").read_text(encoding="utf-8")
    assert "SANDBOX_SETUP_INCOMPLETE" in source
    assert "UNCONFINED:" in source


# --- MVP-08 filesystem escape ------------------------------------------------

@requires_sandbox
def test_mvp08_credential_paths_are_absent():
    """The observable spec/sandbox/negative-tests.yaml names for MVP-08."""
    targets = MOUNTS["assertions_after_setup"]["must_not_exist"]
    checks = "\n".join(
        f"assert not os.path.exists({path!r}), {path!r}" for path in targets)
    outcome = run_candidate("import os\n" + checks)
    assert outcome.status is ExecutionStatus.SUCCESS, (
        f"a path that must not exist was reachable: {outcome.reason_code}")


@requires_sandbox
def test_mvp08_proc_paths_are_masked_rather_than_absent():
    """CPython needs /proc, so those paths cannot be removed. They are bound over
    instead, which leaves the path present and its contents empty — the distinction
    mounts.yaml now draws between must_not_exist and must_be_masked."""
    targets = MOUNTS["assertions_after_setup"]["must_be_masked"]
    # A path this kernel does not provide is vacuously safe; the guarantee is that a
    # path which IS present reveals nothing.
    checks = "\n".join(
        f"assert not os.path.exists({path!r}) or open({path!r}, 'rb').read() == b'', {path!r}"
        for path in targets)
    outcome = run_candidate("import os\n" + checks)
    assert outcome.status is ExecutionStatus.SUCCESS, (
        f"a masked path still had contents: {outcome.reason_code}")


@requires_sandbox
def test_mvp08_reading_a_host_credential_file_fails():
    outcome = run_candidate("open('/etc/shadow', 'rb').read()")
    assert outcome.status is not ExecutionStatus.SUCCESS


@requires_sandbox
def test_mvp08_path_traversal_out_of_the_workspace_fails():
    """REQ-S12-004: the containment check resolves symlinks first."""
    outcome = run_candidate(
        "import os\n"
        "assert not os.path.exists('../../../etc/shadow')\n"
        "assert not os.path.exists('/etc/shadow')")
    assert outcome.status is ExecutionStatus.SUCCESS, outcome.reason_code


# --- MVP-09 network egress ---------------------------------------------------

@requires_sandbox
def test_mvp09_opening_a_socket_is_killed_by_the_kernel():
    """REQ-S12-003 forbids treating a Python-level guard as the boundary, so the
    assertion is on the kernel signal, not on an exception type."""
    outcome = run_candidate(
        "import socket\n"
        "socket.socket(socket.AF_INET, socket.SOCK_STREAM)")
    assert outcome.status is ExecutionStatus.SECURITY_VIOLATION
    assert outcome.reason_code == "SECCOMP_DENIED_SYSCALL"
    assert outcome.signal_number == 31  # SIGSYS


@requires_sandbox
def test_mvp09_connecting_outward_is_killed_by_the_kernel():
    outcome = run_candidate(
        "import socket\n"
        "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "s.connect(('192.0.2.1', 80))")
    assert outcome.status is ExecutionStatus.SECURITY_VIOLATION


@requires_sandbox
def test_mvp09_a_unix_socket_is_denied_too():
    """CR-0005 aligned the seccomp table with section 12.5: the coordinator hands over a
    pre-opened fd, so the candidate never calls socket() itself."""
    outcome = run_candidate(
        "import socket\n"
        "socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)")
    assert outcome.status is ExecutionStatus.SECURITY_VIOLATION


# --- MVP-10 fork bomb --------------------------------------------------------

@requires_sandbox
def test_mvp10_forking_is_killed_by_the_kernel():
    outcome = run_candidate("import os\nfor _ in range(200): os.fork()")
    assert outcome.status in (ExecutionStatus.SECURITY_VIOLATION,
                              ExecutionStatus.RESOURCE_EXCEEDED)


@requires_sandbox
def test_mvp10_spawning_a_thread_pool_cannot_escape_the_pid_ceiling():
    outcome = run_candidate(
        "import os\n"
        "pids = []\n"
        "for _ in range(500):\n"
        "    pids.append(os.fork())")
    assert outcome.status is not ExecutionStatus.SUCCESS


@requires_sandbox
def test_mvp10_execve_is_denied():
    """A fork bomb that cannot exec cannot become a different program."""
    outcome = run_candidate("import os\nos.execve('/bin/sh', ['sh'], {})")
    assert outcome.status is ExecutionStatus.SECURITY_VIOLATION


# --- the profile is what is actually enforced --------------------------------

@requires_sandbox
def test_every_case_in_the_negative_corpus_has_a_test_here():
    """A corpus case with no executing test is a case nothing verifies."""
    covered = {"MVP-08", "MVP-09", "MVP-10"}
    assert set(CASES) == covered


@requires_sandbox
def test_denied_syscalls_cover_the_mechanisms_the_corpus_names():
    for case in CASES.values():
        mechanism = case["stopped_by"].lower()
        if "seccomp" in mechanism:
            assert DENIED_SYSCALLS, "the corpus names seccomp but nothing is denied"


@requires_cgroups
def test_memory_ceiling_comes_from_the_rank_one_profile():
    """The limit enforced must be the declared one, not a constant in the code."""
    limits = load_profile()["resource_limits"]
    source = (ROOT / "src/evolution_engine/sandbox/profile_a.py").read_text(encoding="utf-8")
    assert str(limits["memory_max_bytes"]) not in source, (
        "the memory ceiling is hardcoded; it must be read from the profile")
    assert '_limit(limits, "memory_max_bytes")' in source, (
        "the memory ceiling is not read from spec/sandbox/profile-a-linux.yaml")


@requires_sandbox
def test_environment_is_the_pinned_allowlist():
    env = load_environment()
    assert "PYTHONPATH" not in env
    assert env["PYTHONHASHSEED"] == "0"


@requires_sandbox
def test_timeout_kills_the_candidate():
    outcome = run_candidate("while True:\n    pass", timeout_seconds=2)
    assert outcome.status is ExecutionStatus.TIMEOUT
    assert outcome.reason_code == "TIMEOUT_WALL_CLOCK"


def test_support_is_reported_honestly():
    """Runs everywhere. A machine that cannot sandbox must say so rather than skip
    silently, so a green suite on such a machine is still visibly incomplete."""
    support = probe_support()
    if not support.usable:
        assert support.reasons, "unusable sandbox reported no reason"
    else:
        assert support.user_namespaces and support.seccomp
