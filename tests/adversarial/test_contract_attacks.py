import json
import subprocess
import sys
import pytest
from pathlib import Path

# Path ไปยัง Validator ของเรา
VALIDATOR = "governance/validate_contract.py"

def run_validator(spec_data):
    """เขียน JSON ลงไฟล์ชั่วคราวแล้วรัน Validator"""
    tmp_path = Path("/tmp/adversarial_spec.json")
    tmp_path.write_text(json.dumps(spec_data))
    
    result = subprocess.run(
        [sys.executable, VALIDATOR, str(tmp_path)],
        capture_output=True, text=True
    )
    return result

def get_valid_base_spec():
    return {
        "spec_id": "SPEC-0001",
        "domain": "Security",
        "version": "v1.0.0",
        "artifacts": [
            {
                "artifact_id": "opa_policy",
                "sha256": "f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0e1"
            }
        ],
        "authority_boundary": {
            "can_release": False,
            "can_freeze": False
        }
    }

# ─── ATTACK 1: พยายามแหกกฎเรื่องสิทธิ์ (Authority Override) ───
def test_attack_can_release_true():
    spec = get_valid_base_spec()
    spec["authority_boundary"]["can_release"] = True  # โจมตี! AI พยายามปล่อย Release
    
    result = run_validator(spec)
    assert result.returncode == 1, "ระบบต้อง FAIL ถ้า can_release เป็น true"
    assert "Schema violation" in result.stdout or "FAIL" in result.stdout

# ─── ATTACK 2: ปลอมแปลง Domain ที่ไม่มีอยู่จริง ───
def test_attack_invalid_domain():
    spec = get_valid_base_spec()
    spec["domain"] = "HackerDomain"  # โจมตี!
    
    result = run_validator(spec)
    assert result.returncode == 1
    assert "Schema violation" in result.stdout

# ─── ATTACK 3: ใส่ Hash ปลอม (ไม่ใช่ SHA256) ───
def test_attack_invalid_hash():
    spec = get_valid_base_spec()
    spec["artifacts"][0]["sha256"] = "not-a-real-hash"  # โจมตี!
    
    result = run_validator(spec)
    assert result.returncode == 1
    assert "Schema violation" in result.stdout

# ─── ATTACK 4: ลบ Field ที่สำคัญที่สุดออก (Authority Boundary หายไป) ───
def test_attack_missing_authority():
    spec = get_valid_base_spec()
    del spec["authority_boundary"]  # โจมตี!
    
    result = run_validator(spec)
    assert result.returncode == 1
    assert "Schema violation" in result.stdout

# ─── HAPPY PATH: ตรวจสอบว่าไฟล์ที่ถูกต้อง ผ่านจริง ───
def test_valid_spec_passes():
    spec = get_valid_base_spec()
    result = run_validator(spec)
    assert result.returncode == 0
    assert "PASS" in result.stdout
