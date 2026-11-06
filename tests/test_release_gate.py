import subprocess, json, os, tempfile
from pathlib import Path

def run(p): 
    return subprocess.run(["python3","tools/release/gate_check.py",p], capture_output=True, text=True)

def tmp_bundle(mod):
    with open("examples/real_evidence_bundle.PASS.json") as f:
        d = json.load(f)
    mod(d)
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, 'w') as f:
        json.dump(d, f)
    return path

def test_01_placeholder_denies(): 
    assert run("examples/placeholder_evidence_bundle.json").returncode == 1

def test_02_real_allows(): 
    assert run("examples/real_evidence_bundle.PASS.json").returncode == 0

# แก้ไขบั๊ก: เอา or True ออก และเช็ค datetime.now ให้ถูกต้อง
def test_03_no_time_bomb(): 
    src = open("tools/release/gate_check.py").read()
    assert "parse_rfc3339" not in src
    assert "datetime.now" not in src

def test_04_empty_members_deny(): 
    assert run(tmp_bundle(lambda d: d.__setitem__("members", []))).returncode == 1

def test_05_stale_deny(): 
    assert run(tmp_bundle(lambda d: d.__setitem__("evidence_age_hours", 999))).returncode == 1

def test_06_policy_fail_deny(): 
    assert run(tmp_bundle(lambda d: d.__setitem__("policy_decision", "FAIL"))).returncode == 1

def test_07_risk_unacceptable_deny(): 
    assert run(tmp_bundle(lambda d: d.__setitem__("risk_status", "UNACCEPTABLE"))).returncode == 1

def test_08_seal_revoked_deny(): 
    assert run(tmp_bundle(lambda d: d.__setitem__("seal_status", "REVOKED"))).returncode == 1

def test_09_auditor_not_signed_deny(): 
    assert run(tmp_bundle(lambda d: d["auditor_signoff"].__setitem__("signed", False))).returncode == 1

def test_10_invalid_anchor_deny(): 
    assert run(tmp_bundle(lambda d: d.__setitem__("baseline_anchor", "INVALID"))).returncode == 1

def test_11_members_nonempty_allow(): 
    assert len(json.load(open("examples/real_evidence_bundle.PASS.json"))["members"]) > 0
