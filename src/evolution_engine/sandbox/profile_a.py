"""PROFILE_A_LINUX — the real sandbox (M6, Active Contract section 12).

Everything here is enforced by the kernel. REQ-S12-003 says a Python-level socket
monkeypatch is not a security boundary, so nothing in this module pretends otherwise:
isolation comes from namespaces, limits come from cgroups v2 and rlimits, and syscall
denial comes from a seccomp BPF filter installed before the candidate's code runs.

Values are read from spec/sandbox/profile-a-linux.yaml rather than written here, so the
rank 1 declaration is what actually takes effect.

The sandbox is unavailable on a kernel without unprivileged user namespaces, cgroups v2
or seccomp. `probe_support()` reports that, and the M6 tests skip on it. A skipped test
is not a passing one: `m6_security()` requires passes, so M6 stays unearned on a machine
that cannot run the thing M6 certifies.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import errno
import os
import pathlib
import resource
import signal
import struct
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Final

import yaml

from evolution_engine.types import ExecutionStatus

__all__ = [
    "SandboxSupport",
    "SandboxOutcome",
    "probe_support",
    "load_profile",
    "run_candidate",
]

ROOT: Final = pathlib.Path(__file__).resolve().parents[3]
PROFILE_PATH: Final = ROOT / "spec/sandbox/profile-a-linux.yaml"
ENV_PATH: Final = ROOT / "spec/sandbox/env-allowlist.yaml"
MOUNTS_PATH: Final = ROOT / "spec/sandbox/mounts.yaml"


def _load_masked_proc_paths() -> tuple[str, ...]:
    """Read at import, for the same reason libc is resolved at import.

    _confine_filesystem covers /home with an empty tmpfs, and this repository lives
    under /home. Reading the spec file inside the child after that mount means reading a
    path the child just made unreachable — which failed every candidate, benign ones
    included.
    """
    doc = yaml.safe_load(MOUNTS_PATH.read_text(encoding="utf-8"))
    proc = next(m for m in doc["mounts"] if m["target"] == "/proc")
    return tuple(proc.get("masked_paths", []))


_MASKED_PROC_PATHS: Final = _load_masked_proc_paths()

CLONE_NEWNS: Final = 0x00020000
CLONE_NEWIPC: Final = 0x08000000
CLONE_NEWUSER: Final = 0x10000000
CLONE_NEWPID: Final = 0x20000000
CLONE_NEWNET: Final = 0x40000000
ALL_NAMESPACES: Final = CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWIPC

PR_SET_NO_NEW_PRIVS: Final = 38
PR_GET_SECCOMP: Final = 21
SECCOMP_SET_MODE_FILTER: Final = 1
SECCOMP_RET_KILL_PROCESS: Final = 0x80000000
SECCOMP_RET_ALLOW: Final = 0x7FFF0000
AUDIT_ARCH_X86_64: Final = 0xC000003E
SYS_seccomp: Final = 317

MS_BIND: Final = 1 << 12
MS_REC: Final = 1 << 14
MS_PRIVATE: Final = 1 << 18

# BPF opcodes, just enough for a syscall-number allowlist.
BPF_LD: Final = 0x00
BPF_W: Final = 0x00
BPF_ABS: Final = 0x20
BPF_JMP: Final = 0x05
BPF_JEQ: Final = 0x10
BPF_K: Final = 0x00
BPF_RET: Final = 0x06

# Syscalls the candidate must never make. Each maps to SECURITY_VIOLATION through the
# mapping in spec/sandbox/profile-a-linux.yaml.
DENIED_SYSCALLS: Final[dict[str, int]] = {
    "socket": 41,
    "connect": 42,
    "accept": 43,
    "bind": 49,
    "listen": 50,
    "clone": 56,
    "fork": 57,
    "vfork": 58,
    "execve": 59,
    "ptrace": 101,
    "mount": 165,
    "umount2": 166,
    "unshare": 272,
    "clone3": 435,
    "keyctl": 250,
    "userfaultfd": 323,
    "io_uring_setup": 425,
}


@dataclass(frozen=True, slots=True)
class SandboxSupport:
    """What this kernel can actually do. Reported honestly, never assumed."""

    user_namespaces: bool
    cgroup_v2: bool
    cgroup_delegated_path: str | None
    seccomp: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)

    @property
    def usable(self) -> bool:
        return self.user_namespaces and self.seccomp

    @property
    def limits_enforceable(self) -> bool:
        """cgroups are needed for memory and pid ceilings; rlimits cover the rest."""
        return self.cgroup_v2 and self.cgroup_delegated_path is not None


@dataclass(frozen=True, slots=True)
class SandboxOutcome:
    """The kernel-observed result, mapped to one execution status."""

    status: ExecutionStatus
    exit_code: int | None
    signal_number: int | None
    reason_code: str | None
    stdout: bytes = b""


def _resolve_libc() -> ctypes.CDLL:
    """Resolved once, at import.

    ctypes.util.find_library shells out to ldconfig. Calling it inside the child after
    unshare means spawning a process in a namespace whose /etc and /var have just been
    replaced by empty tmpfs, and later behind a seccomp filter that denies fork — so it
    fails, and every candidate looks like a crash including the benign ones. Binding the
    handle before any fork removes the subprocess from the sandboxed path entirely.
    """
    name = ctypes.util.find_library("c") or "libc.so.6"
    return ctypes.CDLL(name, use_errno=True)


_LIBC: Final = _resolve_libc()


def _libc() -> ctypes.CDLL:
    return _LIBC


def probe_support() -> SandboxSupport:
    """Check the kernel rather than trusting the platform string."""
    reasons: list[str] = []

    if sys.platform != "linux":
        return SandboxSupport(False, False, None, False, ("not Linux",))

    read, write = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read)
        try:
            os.unshare(ALL_NAMESPACES)
            os.write(write, b"1")
        except OSError as exc:
            os.write(write, f"0:{exc.strerror}".encode())
        os._exit(0)
    os.close(write)
    raw = os.read(read, 128).decode()
    os.waitpid(pid, 0)
    namespaces = raw.startswith("1")
    if not namespaces:
        reasons.append(f"unprivileged user namespaces unavailable ({raw})")

    cgroup_root = pathlib.Path("/sys/fs/cgroup")
    cgroup_v2 = (cgroup_root / "cgroup.controllers").is_file()
    if not cgroup_v2:
        reasons.append("cgroups v2 not mounted")

    delegated: str | None = None
    candidate = cgroup_root / f"user.slice/user-{os.getuid()}.slice/user@{os.getuid()}.service"
    if cgroup_v2 and candidate.is_dir() and os.access(candidate, os.W_OK):
        controllers = (candidate / "cgroup.controllers").read_text().split()
        if {"memory", "pids"} <= set(controllers):
            delegated = str(candidate)
        else:
            reasons.append(f"delegated cgroup lacks memory/pids: {controllers}")
    elif cgroup_v2:
        reasons.append("no writable delegated cgroup for this user")

    # PR_SET_NO_NEW_PRIVS is one-way, so probing it by setting 0 returns EINVAL on a
    # kernel that supports it perfectly well. PR_GET_SECCOMP reports the current mode
    # without changing anything, and the /proc line only exists when CONFIG_SECCOMP is on.
    seccomp = False
    try:
        libc = _libc()
        seccomp = libc.prctl(PR_GET_SECCOMP, 0, 0, 0, 0) != -1
    except Exception as exc:  # pragma: no cover - libc missing is not a normal path
        reasons.append(f"seccomp probe failed: {exc}")
    if not seccomp:
        status = pathlib.Path("/proc/self/status")
        seccomp = status.is_file() and "Seccomp:" in status.read_text()
    if not seccomp:
        reasons.append("kernel reports no seccomp support")

    return SandboxSupport(namespaces, cgroup_v2, delegated, seccomp, tuple(reasons))


def load_profile() -> dict[str, object]:
    """Limits come from rank 1, not from constants in this file."""
    loaded: dict[str, object] = yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))
    return loaded


def load_environment() -> dict[str, str]:
    """The deny-by-default allowlist. Values are pinned, never inherited."""
    doc = yaml.safe_load(ENV_PATH.read_text(encoding="utf-8"))
    return {entry["name"]: entry["value"] for entry in doc["variables"]}


def _bpf_filter(denied: dict[str, int]) -> bytes:
    """A seccomp program that kills the process on any denied syscall number.

    Denylist rather than allowlist: an allowlist would have to enumerate everything
    CPython needs at startup, and getting that wrong kills the interpreter instead of
    the attack, which makes MVP-08..10 untestable. The syscalls that matter for the
    three security corpus cases are all here.
    """
    instructions: list[bytes] = []

    def stmt(code: int, k: int) -> bytes:
        return struct.pack("HBBI", code, 0, 0, k)

    def jump(code: int, k: int, jt: int, jf: int) -> bytes:
        return struct.pack("HBBI", code, jt, jf, k)

    # reject the program outright if the architecture is not what the numbers mean
    instructions.append(stmt(BPF_LD | BPF_W | BPF_ABS, 4))          # arch
    instructions.append(jump(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0))
    instructions.append(stmt(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS))
    instructions.append(stmt(BPF_LD | BPF_W | BPF_ABS, 0))          # syscall number

    for number in sorted(set(denied.values())):
        instructions.append(jump(BPF_JMP | BPF_JEQ | BPF_K, number, 0, 1))
        instructions.append(stmt(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS))

    instructions.append(stmt(BPF_RET | BPF_K, SECCOMP_RET_ALLOW))
    return b"".join(instructions)


def _install_seccomp(denied: dict[str, int]) -> None:
    """Install the filter in the current process. Irreversible, as it must be."""
    libc = _libc()
    if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "prctl(PR_SET_NO_NEW_PRIVS) failed")

    program = _bpf_filter(denied)
    buffer = ctypes.create_string_buffer(program, len(program))

    class SockFprog(ctypes.Structure):
        _fields_ = [("len", ctypes.c_ushort), ("filter", ctypes.c_void_p)]

    fprog = SockFprog(len(program) // 8, ctypes.cast(buffer, ctypes.c_void_p))
    if libc.syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, ctypes.byref(fprog)) != 0:
        raise OSError(ctypes.get_errno(), "seccomp(SECCOMP_SET_MODE_FILTER) failed")


def _confine_filesystem() -> list[str]:
    """Make the paths spec/sandbox/mounts.yaml says must be absent actually absent.

    Section 12.3 chose a minimal rootfs in CR-0005 precisely so a path that was never
    mounted cannot be reached by a bug in a deny rule. Inside the mount namespace this
    covers the host trees the candidate has no business seeing with an empty tmpfs, so
    an escape attempt gets ENOENT rather than a permission error — which is what
    spec/sandbox/negative-tests.yaml names as the MVP-08 observable.

    Returns the paths it could not cover, so containment is reported rather than assumed.
    """
    libc = _libc()
    uncovered: list[str] = []
    if libc.mount(b"none", b"/", None, MS_REC | MS_PRIVATE, None) != 0:
        return ["/"]  # cannot detach propagation; nothing below would be safe
    for target in (b"/etc", b"/home", b"/root", b"/var", b"/run", b"/boot", b"/srv"):
        if not os.path.isdir(target.decode()):
            continue
        if libc.mount(b"tmpfs", target, b"tmpfs", 0, b"size=4k,mode=0555") != 0:
            uncovered.append(target.decode())

    # /sys is not mounted at all in spec/sandbox/mounts.yaml, so cover it whole.
    if os.path.isdir("/sys") and libc.mount(b"tmpfs", b"/sys", b"tmpfs", 0,
                                            b"size=4k,mode=0555") != 0:
        uncovered.append("/sys")

    # /proc stays, because CPython needs it, so its masked_paths are covered
    # individually — bind /dev/null over each, which is how a path is masked without
    # unmounting the filesystem underneath it.
    for masked in _MASKED_PROC_PATHS:
        if not os.path.exists(masked):
            continue
        # /dev/null binds over a file; a directory needs an empty tmpfs instead, or the
        # mount fails with ENOTDIR. /proc/scsi is a directory on most kernels.
        if os.path.isdir(masked):
            failed = libc.mount(b"tmpfs", masked.encode(), b"tmpfs", 0,
                                b"size=4k,mode=0555") != 0
        else:
            failed = libc.mount(b"/dev/null", masked.encode(), None, MS_BIND, None) != 0
        if failed:
            uncovered.append(masked)
    return uncovered


def _limit(limits: dict[str, object], key: str) -> int:
    """Read one numeric limit from the rank 1 profile."""
    value = limits[key]
    if not isinstance(value, int):
        raise TypeError(f"{key} must be an integer in spec/sandbox/profile-a-linux.yaml")
    return value


def _apply_rlimits(limits: dict[str, object]) -> None:
    """The ceilings cgroups do not cover."""
    nofile = _limit(limits, "rlimit_nofile")
    fsize = _limit(limits, "rlimit_fsize_bytes")
    core = _limit(limits, "rlimit_core_bytes")
    resource.setrlimit(resource.RLIMIT_NOFILE, (nofile, nofile))
    resource.setrlimit(resource.RLIMIT_FSIZE, (fsize, fsize))
    resource.setrlimit(resource.RLIMIT_CORE, (core, core))


class CgroupScope:
    """A cgroup v2 scope carrying the memory and pid ceilings from rank 1.

    Falls back to no cgroup when the kernel gives this user no delegated subtree; the
    caller sees that through SandboxSupport and the tests skip rather than pretend.
    """

    def __init__(self, delegated: str | None, limits: dict[str, object]) -> None:
        self.path: pathlib.Path | None = None
        if delegated is None:
            return
        base = pathlib.Path(delegated)
        scope = base / f"evolution-{os.getpid()}-{os.urandom(4).hex()}"
        try:
            scope.mkdir()
            (scope / "memory.max").write_text(str(_limit(limits, "memory_max_bytes")))
            (scope / "memory.high").write_text(str(_limit(limits, "memory_high_bytes")))
            (scope / "memory.swap.max").write_text(
                str(_limit(limits, "memory_swap_max_bytes")))
            (scope / "pids.max").write_text(str(_limit(limits, "pids_max")))
            self.path = scope
        except OSError:
            self.path = None

    def attach(self, pid: int) -> None:
        if self.path is not None:
            (self.path / "cgroup.procs").write_text(str(pid))

    def oom_kills(self) -> int:
        if self.path is None:
            return 0
        for line in (self.path / "memory.events").read_text().splitlines():
            if line.startswith("oom_kill "):
                return int(line.split()[1])
        return 0

    def pids_max_events(self) -> int:
        if self.path is None:
            return 0
        events = self.path / "pids.events"
        if not events.is_file():
            return 0
        for line in events.read_text().splitlines():
            if line.startswith("max "):
                return int(line.split()[1])
        return 0

    def kill(self) -> None:
        """cgroup.kill takes the whole tree, so no grandchild outlives the evaluation."""
        if self.path is not None:
            killer = self.path / "cgroup.kill"
            if killer.is_file():
                try:
                    killer.write_text("1")
                except OSError:
                    pass

    def close(self) -> None:
        if self.path is not None:
            try:
                self.path.rmdir()
            except OSError:
                pass


def run_candidate(source: str, timeout_seconds: int = 10) -> SandboxOutcome:
    """Execute candidate source under PROFILE_A_LINUX and map the outcome.

    The child enters the namespaces, joins the cgroup, drops rlimits, installs the
    seccomp filter and only then runs the candidate. Every step happens before the
    candidate's first bytecode, so nothing it does can undo them.
    """
    profile = load_profile()
    raw_limits = profile["resource_limits"]
    if not isinstance(raw_limits, dict):
        raise TypeError("resource_limits missing from spec/sandbox/profile-a-linux.yaml")
    limits: dict[str, object] = raw_limits
    support = probe_support()
    scope = CgroupScope(support.cgroup_delegated_path if support.limits_enforceable else None,
                        limits)

    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:  # pragma: no cover - the child never returns
        os.close(read_fd)
        try:
            os.unshare(ALL_NAMESPACES)
            uncovered = _confine_filesystem()
            if uncovered:
                os.write(write_fd, b"UNCONFINED:" + ",".join(uncovered).encode())
                os._exit(3)
            _apply_rlimits(limits)
            with tempfile.TemporaryDirectory() as workspace:
                os.chdir(workspace)
                _install_seccomp(DENIED_SYSCALLS)
                namespace: dict[str, object] = {"__name__": "__candidate__"}
                exec(compile(source, "<candidate>", "exec"), namespace)
            os.write(write_fd, b"OK")
            os._exit(0)
        except MemoryError:
            os._exit(9)
        except BaseException:
            os._exit(1)

    os.close(write_fd)
    scope.attach(pid)

    status = _wait_with_timeout(pid, timeout_seconds, scope)
    try:
        payload = os.read(read_fd, 4096)
    except OSError:
        payload = b""
    os.close(read_fd)

    outcome = _map_outcome(status, scope, payload)
    scope.close()
    return outcome


def _wait_with_timeout(pid: int, timeout_seconds: int, scope: CgroupScope) -> int:
    """Wait, and on expiry kill the whole cgroup rather than only the direct child."""
    def on_alarm(_signum: int, _frame: object) -> None:
        raise TimeoutError

    previous = signal.signal(signal.SIGALRM, on_alarm)
    signal.alarm(timeout_seconds)
    try:
        _, status = os.waitpid(pid, 0)
        return status
    except TimeoutError:
        scope.kill()
        try:
            os.kill(pid, signal.SIGKILL)
            _, status = os.waitpid(pid, 0)
        except ChildProcessError:
            status = -1
        return -2  # sentinel: timed out
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def _map_outcome(status: int, scope: CgroupScope, payload: bytes) -> SandboxOutcome:
    """The total mapping from spec/sandbox/profile-a-linux.yaml violation_detection.

    Order matters: a seccomp kill and an OOM kill both surface as SIGKILL-adjacent
    terminations, so the cgroup counters are consulted before falling back to CRASHED.
    """
    if status == -2:
        return SandboxOutcome(ExecutionStatus.TIMEOUT, None, None, "TIMEOUT_WALL_CLOCK")

    if os.WIFSIGNALED(status):
        signal_number = os.WTERMSIG(status)
        if signal_number == signal.SIGSYS:
            return SandboxOutcome(ExecutionStatus.SECURITY_VIOLATION, None, signal_number,
                                  "SECCOMP_DENIED_SYSCALL")
        if scope.oom_kills() > 0:
            return SandboxOutcome(ExecutionStatus.OOM, None, signal_number, "CGROUP_OOM_KILL")
        return SandboxOutcome(ExecutionStatus.CRASHED, None, signal_number, "FATAL_SIGNAL")

    exit_code = os.WEXITSTATUS(status)
    if scope.oom_kills() > 0:
        return SandboxOutcome(ExecutionStatus.OOM, exit_code, None, "CGROUP_OOM_KILL")
    if scope.pids_max_events() > 0:
        return SandboxOutcome(ExecutionStatus.RESOURCE_EXCEEDED, exit_code, None,
                              "CGROUP_PIDS_MAX")
    if exit_code == 0 and payload == b"OK":
        return SandboxOutcome(ExecutionStatus.SUCCESS, 0, None, None, payload)
    if exit_code == 9:
        return SandboxOutcome(ExecutionStatus.OOM, exit_code, None, "PYTHON_MEMORY_ERROR")
    if exit_code == 3 and payload.startswith(b"UNCONFINED:"):
        # Refusing to run beats running unconfined and calling the result a pass.
        return SandboxOutcome(ExecutionStatus.CRASHED, exit_code, None,
                              "SANDBOX_SETUP_INCOMPLETE", payload)
    return SandboxOutcome(ExecutionStatus.CRASHED, exit_code, None, "NONZERO_EXIT")


def errno_name(number: int) -> str:
    return errno.errorcode.get(number, str(number))
