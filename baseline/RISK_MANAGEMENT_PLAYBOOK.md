# RISK MANAGEMENT PLAYBOOK — Sovereign V12 Blue Prince Repro Hub

Normative reference for risk classification, compensating controls, SLAs, and
escalation. Referenced by `baseline/BASELINE_PIPELINE.md` and `policy/baseline.rego`.

## 1. Classifications

| Classification | Meaning | Gate effect |
|---|---|---|
| ACCEPTABLE | Residual risk within tolerance; no extra conditions | May pass with valid evidence |
| CONDITIONALLY_ACCEPTABLE | Tolerable only with AO approval + compensating controls + SLA + expiry | Passes only with all five required elements (see §2) |
| UNACCEPTABLE | Outside tolerance | Always denies; stop work and escalate |

## 2. Conditional acceptance — required elements (all five)

1. `ao_approval`: explicit AO approval recorded (boolean true in the bundle).
2. `compensating_controls`: non-empty array of applied controls (schema §3).
3. `remediation_sla_hours`: positive number, ≤ 120.
4. `expiry`: RFC 3339 timestamp after which acceptance is void.
5. `ledger_anchor`: sha256 digest of the ledger entry recording the approval.

Missing any element → treated as UNACCEPTABLE (fail-closed).

## 3. Compensating control schema

Each control: `control_id` (string, unique), `description` (string),
`verifier` (role that checks it), optional `evidence_ref` (digest of proof).
Controls are claims until their `evidence_ref` is verified.

## 4. Canonical risk register (placeholder rows — classifications pending AO review)

| risk_id | title | classification | sla_hours | owner | status |
|---|---|---|---|---|---|
| RISK-0001 | Unpinned build dependency | PENDING_REVIEW | — | Operator | OPEN |
| RISK-0002 | Evidence staleness between audits | PENDING_REVIEW | — | Operator | OPEN |
| RISK-0003 | Legacy witness machinery in tree (legacy `dist/`, `evidence/`) | PENDING_REVIEW | — | AO | OPEN |

> Placeholder only. Live classification requires AO action recorded in the
> ledger; this file is not an approval.

## 5. SLA and staleness

- Remediation SLA: 120 hours from acceptance. `policy/baseline.rego` denies
  evidence older than 120 hours unless a recorded exemption applies.
- Expired conditional acceptance reverts to UNACCEPTABLE automatically.

## 6. Escalation

Policy Agent detects → reports to Operator → Operator routes to AO → AO decides
(classify / impose controls / reject). The Policy Agent never classifies live
risk and never authorizes release.
