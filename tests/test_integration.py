"""Integration: freeze authorized iff content_gate PASS AND actor_gate ALLOW."""
import json
import subprocess
import sys

REAL = "examples/real_evidence_bundle.PASS.json"
PLACEHOLDER = "examples/placeholder_evidence_bundle.json"
SPEC = "schemas/state-machine.yaml"


def _gate(bundle):
    r = subprocess.run(
        [sys.executable, "tools/release/gate_check.py", bundle, "--json"],
        capture_output=True, text=True,
    )
    return r.returncode, json.loads(r.stdout)


def _actor(frm, to, actor):
    r = subprocess.run(
        [sys.executable, "tools/release/state_machine.py", "check",
         "--spec", SPEC, "--from", frm, "--to", to, "--actor", actor],
        capture_output=True, text=True,
    )
    return r.returncode, r.stdout.strip()


def freeze_authorized(bundle, actor):
    content_rc, content = _gate(bundle)
    actor_rc, actor_out = _actor("PENDING_AO_REVIEW", "FROZEN", actor)
    ok = content_rc == 0 and actor_rc == 0
    return ok, {"content": content, "actor": actor_out,
                "content_rc": content_rc, "actor_rc": actor_rc}


def test_freeze_authorized_real_operator():
    ok, d = freeze_authorized(REAL, "Operator")
    assert ok, d

def test_freeze_denied_placeholder_operator():
    ok, d = freeze_authorized(PLACEHOLDER, "Operator")
    assert not ok
    assert d["content_rc"] == 1
    assert d["actor_rc"] == 0

def test_freeze_denied_real_ai():
    ok, d = freeze_authorized(REAL, "AI")
    assert not ok
    assert d["content_rc"] == 0
    assert d["actor_rc"] == 1

def test_freeze_denied_real_copilot():
    ok, _ = freeze_authorized(REAL, "Copilot")
    assert not ok

def test_freeze_denied_real_policy_agent():
    ok, _ = freeze_authorized(REAL, "Policy Agent")
    assert not ok

def test_freeze_denied_placeholder_ai():
    ok, d = freeze_authorized(PLACEHOLDER, "AI")
    assert not ok
    assert d["content_rc"] == 1
    assert d["actor_rc"] == 1

def test_freeze_denied_unknown_actor():
    ok, _ = freeze_authorized(REAL, "Random Bot")
    assert not ok

def test_gates_independent_content_ok_actor_deny():
    content_rc, _ = _gate(REAL)
    actor_rc, _ = _actor("PENDING_AO_REVIEW", "FROZEN", "AI")
    assert content_rc == 0
    assert actor_rc == 1

def test_gates_independent_content_deny_actor_ok():
    content_rc, _ = _gate(PLACEHOLDER)
    actor_rc, _ = _actor("PENDING_AO_REVIEW", "FROZEN", "Operator")
    assert content_rc == 1
    assert actor_rc == 0
