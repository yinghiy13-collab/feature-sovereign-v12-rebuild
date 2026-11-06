#!/usr/bin/env bash
# Evidence generator for release gate verification.
# Exit 0 = all passed. Exit 1 = any failed.
set -uo pipefail

REPORT_DIR="${REPORT_DIR:-.verify/$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$REPORT_DIR"
PASS=0
FAIL=0

run() {
  local name="$1"; shift
  local out="$REPORT_DIR/$name.out" err="$REPORT_DIR/$name.err"
  printf "▶ %-45s " "$name"
  if "$@" > "$out" 2> "$err"; then
    echo "✓ PASS"
    echo "PASS" > "$REPORT_DIR/$name.status"
    PASS=$((PASS + 1))
  else
    local rc=$?
    echo "✗ FAIL (rc=$rc)"
    echo "FAIL rc=$rc" > "$REPORT_DIR/$name.status"
    head -10 "$err" | sed 's/^/    /'
    FAIL=$((FAIL + 1))
  fi
}

# ═══════ fixtures ═══════
cat > /tmp/empty_role_spec.yaml <<'YEOF'
state_machine:
  initial: A
  states: [A, B]
  transitions:
    - from: A
      to: B
      when: "always"
      role_allowed: []
YEOF

cat > /tmp/anyrole.yaml <<'YEOF'
state_machine:
  initial: A
  states: [A, B]
  transitions:
    - from: A
      to: B
      when: "test"
      any_role: true
metadata:
  global_denied_roles: [AI, Copilot]
YEOF

# ═══════ 01-03: OPA + pytest ═══════
run "01-opa-check-strict" opa check --strict policy/
run "02-opa-unit-tests"   opa test policy/ -v
run "03-pytest"           python3 -m pytest tests/ -v

# ═══════ 04-05: gate smoke (2 directions) ═══════
cat > /tmp/check_ph.py <<'PYEOF'
import json
d = json.load(open("/tmp/ph.json"))
assert d["decision"] == "DENY", d
assert d["count"] > 0, d
print(f"  placeholder: DENY count={d['count']}")
PYEOF

cat > /tmp/check_real.py <<'PYEOF'
import json
d = json.load(open("/tmp/real.json"))
assert d["decision"] == "PASS", d
assert d["count"] == 0, d
print("  real: PASS count=0")
PYEOF

run "04-placeholder-deny" bash -c '
python3 tools/release/gate_check.py examples/placeholder_evidence_bundle.json --json | tee /tmp/ph.json
python3 /tmp/check_ph.py
'

run "05-real-pass" bash -c '
python3 tools/release/gate_check.py examples/real_evidence_bundle.PASS.json --json | tee /tmp/real.json
python3 /tmp/check_real.py
'

# ═══════ 06: Rego M1-M4 markers (multiline-safe) ═══════
cat > /tmp/check_markers.sh <<'SEOF'
declare -a markers=(
  "is_signed(o) if {"
  "o.signed == true"
  "risk_status is not ACCEPTABLE"
  "valid_sha256"
  "auditor_signoff is not an object"
)
missing=0
for m in "${markers[@]}"; do
  if ! grep -qF "$m" policy/baseline.rego; then
    echo "MISSING marker: $m"
    missing=$((missing + 1))
  fi
done
[ "$missing" -eq 0 ] || exit 1
echo "all ${#markers[@]} markers found"
SEOF
run "06-rego-markers-m1-m4" bash /tmp/check_markers.sh

# ═══════ 07: state-machine validate (happy) ═══════
run "07-state-machine-validate" python3 tools/release/state_machine.py validate schemas/state-machine.yaml

# ═══════ 08: empty role_allowed → exit 1, isolated ═══════
cat > /tmp/check_empty_role.sh <<'SEOF'
out=$(python3 tools/release/state_machine.py validate /tmp/empty_role_spec.yaml 2>&1)
rc=$?
echo "$out"
[ $rc -eq 1 ] || { echo "expected exit 1, got $rc"; exit 1; }
echo "$out" | grep -q "role_allowed must be non-empty" || { echo "wrong message"; exit 1; }
err_count=$(echo "$out" | grep -c '^  - ')
[ "$err_count" -eq 1 ] || { echo "expected exactly 1 error (isolated), got $err_count"; exit 1; }
echo "isolated empty-role error confirmed"
SEOF
run "08-state-machine-empty-role-deny" bash /tmp/check_empty_role.sh

# ═══════ 09-10: operator allow / AI deny ═══════
run "09-state-machine-operator-allow" bash -c '
python3 tools/release/state_machine.py check \
  --spec schemas/state-machine.yaml \
  --from PENDING_AO_REVIEW --to FROZEN --actor Operator \
  | tee /tmp/sm_allow.txt
grep -q "^\[ALLOW\]" /tmp/sm_allow.txt
'

run "10-state-machine-ai-deny" bash -c '
python3 tools/release/state_machine.py check \
  --spec schemas/state-machine.yaml \
  --from PENDING_AO_REVIEW --to FROZEN --actor AI \
  | tee /tmp/sm_deny.txt
grep -q "^\[DENY\]" /tmp/sm_deny.txt
'

# ═══════ 11: global_denied blocks even any_role ═══════
cat > /tmp/check_global_deny.sh <<'SEOF'
out=$(python3 tools/release/state_machine.py check \
      --spec /tmp/anyrole.yaml \
      --from A --to B --actor AI 2>&1)
echo "$out"
echo "$out" | grep -q "^\[DENY\]" || { echo "AI ต้อง DENY แม้ any_role:true"; exit 1; }
echo "$out" | grep -q "global_denied_roles" || { echo "reason ต้องอ้าง global_denied_roles"; exit 1; }
echo "global_denied enforced before any_role"
SEOF
run "11-global-denied-blocks-anyrole" bash /tmp/check_global_deny.sh

# ═══════ summary ═══════
echo
echo "═══════════ VERIFY SUMMARY ═══════════"
echo "Report dir: $REPORT_DIR"
echo
for f in "$REPORT_DIR"/*.status; do
  name=$(basename "$f" .status)
  status=$(cat "$f")
  if [ "$status" = "PASS" ]; then
    printf "  ✓ %-45s %s\n" "$name" "$status"
  else
    printf "  ✗ %-45s %s\n" "$name" "$status"
  fi
done
echo
echo "Passed: $PASS    Failed: $FAIL    Total: $((PASS + FAIL))"
echo

python3 - "$REPORT_DIR" "$PASS" "$FAIL" <<'PYEOF'
import json, sys
from pathlib import Path
d = Path(sys.argv[1])
summary = {
    "report_dir": str(d),
    "total": int(sys.argv[2]) + int(sys.argv[3]),
    "passed": int(sys.argv[2]),
    "failed": int(sys.argv[3]),
    "checks": {
        f.stem: f.read_text().strip()
        for f in sorted(d.glob("*.status"))
    },
}
(d / "summary.json").write_text(json.dumps(summary, indent=2))
print(f"Machine summary: {d}/summary.json")
PYEOF

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
