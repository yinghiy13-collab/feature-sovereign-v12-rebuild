# Release v1.0.1 - Sovereign Release Gate (CI Patch)

**Release Date:** 2026-11-06
**Base Version:** v1.0.0
**Status:** PATCHED & FROZEN

## Changes in this Patch
- **CI Fix:** Added `include-hidden-files: true` to the GitHub Actions `upload-artifact` step. This ensures the `.verify/` directory (containing all test evidence) is successfully uploaded and downloadable as an artifact on GitHub.
- No changes to the core gate logic (`gate_check.py`, `baseline.rego`, or `state_machine.py`).

## Evidence
All 11 checks passed successfully in GitHub Actions.
