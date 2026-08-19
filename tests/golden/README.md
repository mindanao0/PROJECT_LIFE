# tests/golden

End-to-end runs of the 14 golden corpus cases.

**Not written yet.** This directory is declared in the Canonical Repository
Layout (Active Contract section 4) and is created so the layout is real rather
than aspirational. It holds no tests because the code under test does not exist.

- **Gated by:** M9 CORE_GOLDEN, M10, M13.
- **CI jobs that will run it:** `golden_core, golden_security, golden_reliability, golden_self_evolution`

Adding a placeholder test that always passes here would be worse than an empty
directory: `REQ-S22-004` forbids reporting a requirement as satisfied when it is
not, and a green tick with no assertions is exactly that.
