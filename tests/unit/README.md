# tests/unit

Unit tests for individual engine components.

**Not written yet.** This directory is declared in the Canonical Repository
Layout (Active Contract section 4) and is created so the layout is real rather
than aspirational. It holds no tests because the code under test does not exist.

- **Gated by:** M5 FSM_AND_CONFIG onward. Requires src/evolution_engine to exist.
- **CI jobs that will run it:** `unit_tests`

Adding a placeholder test that always passes here would be worse than an empty
directory: `REQ-S22-004` forbids reporting a requirement as satisfied when it is
not, and a green tick with no assertions is exactly that.
