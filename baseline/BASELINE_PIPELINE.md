# BASELINE PIPELINE — Sovereign V12 Blue Prince Repro Hub

Ten-phase lifecycle from bootstrap to recertification. Each phase lists inputs,
the responsible role, and exit criteria. Formal semantics follow the phase list.

## Phases

| # | Phase | Responsible | Exit criteria |
|---|-------|-------------|---------------|
| 1 | Bootstrap | Operator | `baseline/` package complete; repo initialized; no anchor yet |
| 2 | Intermediate Representation (IR) | Policy Agent | Source artifacts normalized into verifiable IR with sha256 digests |
| 3 | Policy | Policy Agent | `policy/baseline.rego` evaluates bundles; all OPA tests pass |
| 4 | Risk | AO + Operator | Every risk classified per `baseline/RISK_MANAGEMENT_PLAYBOOK.md` |
| 5 | Evidence Bundle | Operator | Bundle assembled per `schemas/evidence_bundle.schema.json`; digest computed |
| 6 | Seal | Operator | Seal created over bundle digest; recorded in ledger; status ACTIVE |
| 7 | Auditor | External auditor | Independent audit; signoff recorded in bundle |
| 8 | Attestation | Ledger | Attestation statement recorded (digest-only, no secrets) |
| 9 | Release | Operator + AO | Release gate (`tools/release/gate_check.py`) outputs ALLOW |
| 10 | Recertification | Operator + auditor | Cycle repeats; stale evidence (>120h, no exemption) blocks re-release |

## Formal Semantics

- **Freeze(B)**: `git rev-parse HEAD` over immutable commit set; anchor = sha256(HEAD).
- **Anchor(x)**: sha256 digest hex of artifact x; must match `^[0-9a-f]{64}$`.
- **Decision(e)**: `policy/baseline.rego` evaluated over evidence e; result ∈ {allow, deny}.
- **Classification(r)**: per `baseline/RISK_MANAGEMENT_PLAYBOOK.md`, result ∈
  {ACCEPTABLE, CONDITIONALLY_ACCEPTABLE, UNACCEPTABLE}.
- **Stale(e)**: `now - evidence_timestamp > 120h` ∧ no recorded exemption.
- **Release(B)**: allowed iff
  `Anchor(B) valid ∧ Decision(bundle(B)) = allow ∧ Seal = ACTIVE ∧
   Signoff(auditor) present ∧ Authorization(Operator) ∧ Authorization(AO)`.
  Any conjunct missing → deny (fail-closed).

## Prohibited

- The pipeline never mints approvals, seals, or attestations automatically.
- No phase downgrades a risk classification without AO action recorded in the ledger.
