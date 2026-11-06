# Release v1.0.0 - Sovereign Release Gate (Frozen)

**Release Date:** 2026-11-06
**Commit:** `f1fa530`
**CI Status:** PASSED (GitHub Actions)

## Evidence
Full verification evidence is stored at:
`.verify/20261106T004731Z/summary.json`

## Verification Summary
- Total Checks: 11
- Passed: 11
- Failed: 0

## Key Changes
- Implemented strict Fail-Closed content gate and actor gate.
- Added Rego M1-M4 guardrails and strict type checks.
- Removed time-bomb (no `datetime.now` in runtime).
- Enforced global denied roles (AI/Copilot) before any_role check.
