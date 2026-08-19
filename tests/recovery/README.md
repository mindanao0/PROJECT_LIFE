# tests/recovery

Crash injection across DB and CAS, and the recovery FSM.

**Not written yet.** This directory is declared in the Canonical Repository
Layout (Active Contract section 4) and is created so the layout is real rather
than aspirational. It holds no tests because the code under test does not exist.

- **Gated by:** M8 RECOVERY. Drives MVP-12.
- **CI jobs that will run it:** `db_cas_crash_injection`

Adding a placeholder test that always passes here would be worse than an empty
directory: `REQ-S22-004` forbids reporting a requirement as satisfied when it is
not, and a green tick with no assertions is exactly that.
