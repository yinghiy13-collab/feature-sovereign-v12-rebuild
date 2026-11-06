# MASTER ARTIFACT — Sovereign V12 Blue Prince Repro Hub

Digest-based artifact registry and lifecycle definitions. Digests below are
placeholders (`<sha256:...>`) and are filled ONLY by the Operator at freeze
time. Never insert a digest you have not computed from the artifact itself.

## Artifact registry

| artifact | digest | evidence ref | lifecycle state |
|---|---|---|---|
| baseline/MASTER_STANDARD.md | `<sha256:pending-freeze>` | — | DRAFT |
| baseline/BASELINE_PIPELINE.md | `<sha256:pending-freeze>` | — | DRAFT |
| baseline/RISK_MANAGEMENT_PLAYBOOK.md | `<sha256:pending-freeze>` | — | DRAFT |
| baseline/memory.yaml | `<sha256:pending-freeze>` | — | DRAFT |
| policy/baseline.rego | `<sha256:pending-freeze>` | opa test output | DRAFT |
| schemas/evidence_bundle.schema.json | `<sha256:pending-freeze>` | pytest output | DRAFT |

## Lifecycle states

DRAFT → FROZEN → SEALED → RELEASED → RECERTIFIED

- **DRAFT**: editable; no evidentiary value.
- **FROZEN**: anchor recorded by Operator; content immutable.
- **SEALED**: seal over bundle digest; ledger entry present.
- **RELEASED**: gate ALLOW with auditor signoff + Operator/AO authorization.
- **RECERTIFIED**: post-recertification re-anchor; returns to SEALED.

Any digest mismatch from FROZEN onward invalidates the artifact (fail-closed).
