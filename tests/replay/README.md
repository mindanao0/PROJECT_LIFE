# tests/replay

Deterministic replay against the declared R-level per corpus case.

**Not written yet.** This directory is declared in the Canonical Repository
Layout (Active Contract section 4) and is created so the layout is real rather
than aspirational. It holds no tests because the code under test does not exist.

- **Gated by:** M5 vertical slice, then M11. Drives MVP-12 reproducibility.
- **CI jobs that will run it:** `replay_tests, vertical_slice_deterministic_replay`

Adding a placeholder test that always passes here would be worse than an empty
directory: `REQ-S22-004` forbids reporting a requirement as satisfied when it is
not, and a green tick with no assertions is exactly that.
