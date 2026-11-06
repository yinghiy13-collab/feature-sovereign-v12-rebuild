import json, subprocess, sys, pytest
from pathlib import Path

VALIDATOR = "governance/validate_contract.py"

def run_validator(spec_data):
    tmp_path = Path("/tmp/adversarial_spec.json")
    tmp_path.write_text(json.dumps(spec_data))
    result = subprocess.run([sys.executable, VALIDATOR, str(tmp_path)], capture_output=True, text=True)
    return result

def get_valid_base_spec():
    return {
        "spec_id": "SPEC-0001", "domain": "Security", "version": "v1.0.0",
        "artifacts": [{"artifact_id": "opa_policy", "sha256": "f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0e1"}],
        "authority_boundary": {"can_release": False, "can_freeze": False}
    }

def test_attack_can_release_true():
    spec = get_valid_base_spec()
    spec["authority_boundary"]["can_release"] = True
    result = run_validator(spec)
    assert result.returncode == 1

def test_attack_invalid_domain():
    spec = get_valid_base_spec()
    spec["domain"] = "HackerDomain"
    result = run_validator(spec)
    assert result.returncode == 1

def test_attack_invalid_hash():
    spec = get_valid_base_spec()
    spec["artifacts"][0]["sha256"] = "not-a-real-hash"
    result = run_validator(spec)
    assert result.returncode == 1

def test_attack_missing_authority():
    spec = get_valid_base_spec()
    del spec["authority_boundary"]
    result = run_validator(spec)
    assert result.returncode == 1

def test_valid_spec_passes():
    spec = get_valid_base_spec()
    result = run_validator(spec)
    assert result.returncode == 0
