# MASTER STANDARD — Sovereign V12 Blue Prince Repro Hub

Version: 1.0.0 · Status: DRAFT (not frozen, not certified, not production-authorized)

This standard is the normative root of the sovereign baseline package. Everything
else in `baseline/` derives from the axioms below.

## 1. Axioms

1. **Evidence-first.** Every claim (policy pass, risk acceptance, seal validity,
   release authorization) must cite verifiable evidence recorded in the evidence
   bundle. Claims without evidence are treated as absent.
2. **Fail-closed.** Any missing, malformed, expired, or unverifiable input denies
   the operation by default. There is no implicit allow.
3. **Immutable anchor.** A frozen baseline is identified by the SHA-256 digest of
   the git HEAD commit at freeze time (`audit/BOOTSTRAP_ANCHOR.txt`, Operator
   only). A frozen baseline is never rewritten; changes require a new freeze.
4. **Separation of duties.** Four roles, no overlap:
   | Role | May | May NOT |
   |---|---|---|
   | Policy Agent | evaluate evidence against policy | record, seal, authorize |
   | Ledger | record events/digests | evaluate, authorize |
   | Operator | freeze baseline, operate release gate execution | approve conditional risk |
   | Authorizing Officer (AO) | approve CONDITIONALLY_ACCEPTABLE risk | evaluate policy, freeze |
5. **Time-bound acceptance.** Conditional acceptance always carries a
   remediation SLA (≤ 120 hours) and an expiry. Expired acceptance reverts to
   UNACCEPTABLE until re-approved.
6. **No over-claim.** No claim of SLSA L3, production readiness, or compliance
   certification is made without a valid seal AND auditor signoff AND explicit
   Operator/AO authorization.

## 2. Non-goals

- This package does not certify anything. It defines how evidence is produced,
  evaluated, and gated.
- The Policy Agent and the release gate evaluate only; they never write state.

## 3. Precedence

If any derived document conflicts with this standard, this standard wins.
