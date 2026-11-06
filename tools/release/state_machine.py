#!/usr/bin/env python3
"""Actor gate — validate spec + check transition authorization.
Fail-closed: global_denied_roles blocks any transition before any_role.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required → pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ──────────────────── load (merge metadata) ────────────────────
def load_spec(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"spec not found: {p}")
    with p.open() as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict):
        raise ValueError("spec root must be a mapping")

    if "state_machine" in raw:
        sm = raw["state_machine"]
        if not isinstance(sm, dict):
            raise ValueError("'state_machine' must be a mapping")
        # merge metadata so can_transition() sees global_denied_roles
        sm = dict(sm)  # copy
        sm["metadata"] = raw.get("metadata", {})
        return sm

    # flat spec: assume metadata already present at top level
    return raw


# ──────────────────── validate ────────────────────
def validate_spec(spec: dict[str, Any]) -> list[str]:
    """Return list of error strings. Empty list = valid."""
    errors: list[str] = []

    states = set(spec.get("states", []))
    if not states:
        errors.append("states must be non-empty")

    initial = spec.get("initial")
    if not initial:
        errors.append("initial is required")
    elif initial not in states:
        errors.append(f"initial '{initial}' not in states")

    transitions = spec.get("transitions")
    if not isinstance(transitions, list) or not transitions:
        errors.append("transitions must be a non-empty list")
        return errors

    seen: set[tuple[str, str]] = set()
    for i, t in enumerate(transitions):
        if not isinstance(t, dict):
            errors.append(f"transitions[{i}] is not a mapping")
            continue
        frm, to = t.get("from"), t.get("to")
        ctx = f"{frm}->{to}"

        if not frm:
            errors.append(f"transitions[{i}].from is required")
        elif frm not in states:
            errors.append(f"{ctx}.from not in states")

        if not to:
            errors.append(f"transitions[{i}].to is required")
        elif to not in states:
            errors.append(f"{ctx}.to not in states")

        if not t.get("when"):
            errors.append(f"{ctx}.when is required")

        if frm and frm == to:
            errors.append(f"{ctx}.self_transition forbidden")

        if frm and to:
            key = (frm, to)
            if key in seen:
                errors.append(f"duplicate transition {key}")
            seen.add(key)

        # role semantics: role_allowed:[] without any_role/automatic = ERROR
        has_explicit_mode = t.get("any_role") or t.get("automatic")
        if "role_allowed" in t and not t["role_allowed"] and not has_explicit_mode:
            errors.append(
                f"{ctx}.role_allowed must be non-empty "
                "(use any_role:true or automatic:true if intentional)"
            )

        # overlap allowed ∩ denied
        allowed = set(t.get("role_allowed") or [])
        denied = set(t.get("role_denied") or [])
        overlap = allowed & denied
        if overlap:
            errors.append(f"{ctx}: roles both allowed and denied: {sorted(overlap)}")

    # unreachable states
    incoming = {to for (_, to) in seen}
    if initial:
        orphan = states - incoming - {initial}
        if orphan:
            errors.append(f"unreachable state(s): {sorted(orphan)}")

    return errors


# ──────────────────── transition check ────────────────────
def can_transition(
    spec: dict[str, Any], frm: str, to: str, actor: str
) -> tuple[bool, str]:
    """Fail-closed. Order matters: global_denied > automatic > any_role > role_allowed."""
    global_denied = (spec.get("metadata") or {}).get("global_denied_roles") or []
    if actor in global_denied:
        return False, f"actor '{actor}' in global_denied_roles {global_denied}"

    for t in spec.get("transitions", []):
        if t.get("from") == frm and t.get("to") == to:
            if t.get("automatic"):
                return False, f"{frm}->{to} is automatic; CLI actor cannot trigger"
            if t.get("any_role"):
                return True, f"allowed (any_role): {frm}->{to} by {actor}"
            allowed = t.get("role_allowed") or []
            if not allowed:
                return False, f"{frm}->{to} has empty role_allowed and no any_role/automatic"
            if actor in allowed:
                return True, f"allowed: {frm}->{to} by {actor} (role_allowed={allowed})"
            return False, f"actor '{actor}' not in role_allowed {allowed} for {frm}->{to}"
    return False, f"no transition {frm}->{to} in spec"


# ──────────────────── CLI ────────────────────
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="state_machine")
    ap.add_argument("command", choices=["validate", "check"])
    ap.add_argument("spec_pos", nargs="?", metavar="SPEC")
    ap.add_argument("--spec", dest="spec_opt")
    ap.add_argument("--from", dest="frm")
    ap.add_argument("--to", dest="to")
    ap.add_argument("--actor")
    a = ap.parse_args(argv)

    path = a.spec_opt or a.spec_pos
    if not path:
        ap.print_help(sys.stderr)
        return 2

    try:
        spec = load_spec(path)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if a.command == "validate":
        errors = validate_spec(spec)
        if errors:
            print(f"SPEC INVALID: {len(errors)} error(s)")
            for e in errors:
                print(f"  - {e}")
            return 1
        print("SPEC VALID")
        return 0

    # check
    if not (a.frm and a.to and a.actor):
        print("ERROR: check requires --from --to --actor", file=sys.stderr)
        return 2
    ok, msg = can_transition(spec, a.frm, a.to, a.actor)
    print(f"[{'ALLOW' if ok else 'DENY'}] {msg}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
