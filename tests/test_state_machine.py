import subprocess, pytest, yaml, sys

SPEC = "schemas/state-machine.yaml"

def test_role_allowed_empty_denies(tmp_path):
    spec = {
        "state_machine": {
            "initial": "A",
            "states": ["A", "B"],
            "transitions": [{"from": "A", "to": "B", "when": "always", "role_allowed": []}],
        }
    }
    p = tmp_path / "spec.yaml"
    p.write_text(yaml.dump(spec))
    r = subprocess.run(["python3","tools/release/state_machine.py","validate",str(p)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "role_allowed must be non-empty" in r.stdout
