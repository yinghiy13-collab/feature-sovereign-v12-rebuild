import subprocess, json, pytest

REAL = "examples/real_evidence_bundle.PASS.json"
PLACEHOLDER = "examples/placeholder_evidence_bundle.json"

def run(path, extra=[]):
    return subprocess.run(["python3","tools/release/gate_check.py",path]+extra, capture_output=True, text=True)

def run_json(path):
    r = run(path, ["--json"])
    assert r.stdout, f"empty stdout, stderr={r.stderr}"
    return r, json.loads(r.stdout)

def load_real():
    return json.load(open(REAL))

def dump(tmp_path, name, bundle):
    p = tmp_path / name
    p.write_text(json.dumps(bundle))
    return str(p)

def test_placeholder_denies():
    r, data = run_json(PLACEHOLDER)
    assert data["decision"] == "DENY"
    assert data["count"] >= 3

def test_real_bundle_allows():
    r, data = run_json(REAL)
    assert data["decision"] == "PASS"
    assert data["count"] == 0

def test_no_datetime_runtime_usage():
    src = open("tools/release/gate_check.py").read()
    runtime_lines = [ln.strip() for ln in src.splitlines() if "datetime.now" in ln and not ln.strip().startswith("#")]
    assert runtime_lines == [], "v1 ต้องไม่มี datetime.now runtime"

def test_evidence_age_hours_is_only_staleness_source():
    src = open("tools/release/gate_check.py").read()
    assert "collected_at" not in src, "v1 ต้องไม่อ่าน collected_at"

def test_auditor_signoff_string_denies_exact(tmp_path):
    b = load_real(); b["auditor_signoff"] = "yes"
    r, data = run_json(dump(tmp_path, "aso_str.json", b))
    assert data["count"] == 1
    assert data["denies"] == ["auditor_signoff is not an object"]

def test_baseline_anchor_number_denies_exact(tmp_path):
    b = load_real(); b["baseline_anchor"] = 12345
    r, data = run_json(dump(tmp_path, "ba_num.json", b))
    assert data["count"] == 1
    assert data["denies"] == ["baseline_anchor is not a valid sha256"]

def test_risk_status_unknown_denies(tmp_path):
    b = load_real(); b["risk_status"] = "PENDING"
    r = run(dump(tmp_path, "rs_pending.json", b))
    assert r.returncode == 1

def test_signed_string_denies(tmp_path):
    b = load_real(); b["auditor_signoff"]["signed"] = "yes"
    r = run(dump(tmp_path, "signed_str.json", b))
    assert r.returncode == 1

def test_string_age_denies_exact(tmp_path):
    b = load_real(); b["evidence_age_hours"] = "999"
    r, data = run_json(dump(tmp_path, "str_age.json", b))
    assert data["count"] == 1
    assert data["denies"] == ["evidence_age_hours is not a number"]

@pytest.mark.parametrize("field,expected", [
    ("auditor_signoff", "missing or null: auditor_signoff"),
    ("evidence_age_hours", "missing or null: evidence_age_hours"),
    ("policy_decision", "missing or null: policy_decision"),
])
def test_missing_no_double_fire(tmp_path, field, expected):
    b = load_real(); del b[field]
    r, data = run_json(dump(tmp_path, f"m_{field}.json", b))
    assert data["count"] == 1
    assert data["denies"] == [expected]

def test_null_auditor_signoff_exact(tmp_path):
    b = load_real(); b["auditor_signoff"] = None
    r, data = run_json(dump(tmp_path, "null_aso.json", b))
    assert data["count"] == 1
    assert data["denies"] == ["missing or null: auditor_signoff"]
