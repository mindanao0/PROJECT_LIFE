"""Sandbox profile conformance (REQ-S12-021 .. REQ-S12-024).

These check the profile is *specified* well enough to build and to test against.
They do not create a sandbox — that needs the engine and lands at M6. What they do
catch is the failure that made M6 unstartable: limits with no value, a violation
that maps to no outcome, and an environment that leaks the host import path.
"""
from __future__ import annotations

import pytest
import yaml

from tests.conftest import ROOT

SANDBOX = ROOT / "spec/sandbox"
EXECUTION_OUTCOMES = {"SUCCESS", "TIMEOUT", "CRASHED", "OOM", "RESOURCE_EXCEEDED", "SECURITY_VIOLATION"}


@pytest.fixture(scope="module")
def profile() -> dict:
    return yaml.safe_load((SANDBOX / "profile-a-linux.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def mounts() -> dict:
    return yaml.safe_load((SANDBOX / "mounts.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def env() -> dict:
    return yaml.safe_load((SANDBOX / "env-allowlist.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("key", [
    "memory_max_bytes", "memory_high_bytes", "memory_swap_max_bytes",
    "cpu_max", "pids_max", "rlimit_nofile", "rlimit_fsize_bytes", "rlimit_core_bytes",
])
def test_every_resource_limit_has_a_value(profile, key):
    """The gap that made OOM and RESOURCE_EXCEEDED unreachable outcomes."""
    limits = profile["resource_limits"]
    assert key in limits, f"{key} is not declared"
    assert limits[key] is not None and limits[key] != "", f"{key} has no value"


def test_memory_high_is_below_memory_max(profile):
    limits = profile["resource_limits"]
    assert limits["memory_high_bytes"] < limits["memory_max_bytes"]


def test_swap_is_disabled(profile):
    """Swapping would make every timing metric meaningless."""
    assert profile["resource_limits"]["memory_swap_max_bytes"] == 0


def test_limits_have_a_resolution_rule(profile):
    """A project lowering a limit must be unambiguous."""
    rule = profile["resource_limits"]["resolution_rule"]
    assert "never raise" in rule and "min(" in rule


def test_violation_mapping_is_total(profile):
    """Every abnormal termination must land on exactly one execution outcome."""
    mapped = {entry["outcome"] for entry in profile["violation_detection"]["mapping"]}
    assert mapped == EXECUTION_OUTCOMES, f"unmapped outcomes: {EXECUTION_OUTCOMES - mapped}"


def test_security_violation_has_a_kernel_mechanism(profile):
    """REQ-S12-003 forbids treating a Python monkeypatch as the boundary."""
    entry = next(e for e in profile["violation_detection"]["mapping"]
                 if e["outcome"] == "SECURITY_VIOLATION")
    assert "seccomp" in entry["cause"].lower()


def test_timeout_kills_the_whole_process_tree(profile):
    assert "cgroup.kill" in profile["violation_detection"]["process_tree_kill"]


def test_every_probe_names_the_invariant_it_checks(profile):
    for probe in profile["conformance_probes"]:
        assert probe["asserts"] and probe["invariant"], probe["id"]


def test_security_corpus_has_a_probe_behind_it(profile):
    """MVP-08, MVP-09 and MVP-10 each need a mechanism that can detect them."""
    ids = {p["id"] for p in profile["conformance_probes"]}
    assert {"PROBE-FS-ESCAPE", "PROBE-NET", "PROBE-FORK"} <= ids


def test_rootfs_model_is_chosen(mounts):
    """Section 12.3 implied two incompatible models at once."""
    assert mounts["model"] == "minimal_rootfs"


def test_interpreter_is_mounted(mounts):
    """Nothing previously mounted the CPython the candidate has to run."""
    targets = {m["target"] for m in mounts["mounts"]}
    assert "/usr" in targets, "CPython and stdlib are not reachable"
    assert "/workspace" in targets and "/tmp" in targets


def test_only_declared_writable_mounts_are_writable(mounts):
    writable = {m["target"] for m in mounts["mounts"] if m.get("access") == "read-write"}
    assert writable <= {"/tmp", "/dev"}, f"unexpected writable mount: {writable}"


def test_proc_restrictions_are_named_not_implied(mounts):
    """mode: "restricted" meant nothing an implementer could act on."""
    proc = next(m for m in mounts["mounts"] if m["target"] == "/proc")
    assert proc["hidepid"] == "2"
    assert proc["masked_paths"] and proc["readonly_paths"]


def test_sys_is_not_mounted(mounts):
    assert "/sys" in mounts["not_mounted"]
    assert "/sys" not in {m["target"] for m in mounts["mounts"]}


def test_credential_paths_are_asserted_absent(mounts):
    absent = set(mounts["assertions_after_setup"]["must_not_exist"])
    assert "/var/run/docker.sock" in absent
    assert any(p.endswith(".ssh") for p in absent)


def test_environment_is_deny_by_default(env):
    assert env["model"] == "deny by default"
    assert "empty environment" in env["rule"]


def test_pythonpath_is_not_passed_through(env):
    """Injecting the host import path defeats the minimal rootfs."""
    allowed = {v["name"] for v in env["variables"]}
    removed = {v["name"] for v in env["explicitly_removed"]}
    assert "PYTHONPATH" not in allowed
    assert {"PYTHONPATH", "LD_PRELOAD", "LD_LIBRARY_PATH"} <= removed


def test_determinism_variables_are_pinned(env):
    values = {v["name"]: v["value"] for v in env["variables"]}
    assert values["PYTHONHASHSEED"] == "0"
    assert values["LC_ALL"] == "C.UTF-8"
    assert values["TZ"] == "UTC"


def test_profile_and_env_agree_on_determinism(profile, env):
    values = {v["name"]: v["value"] for v in env["variables"]}
    determinism = profile["determinism"]
    assert values["PYTHONHASHSEED"] == determinism["pythonhashseed"]
    assert values["TZ"] == determinism["tz"]
    assert values["LC_ALL"] == determinism["lc_all"]
