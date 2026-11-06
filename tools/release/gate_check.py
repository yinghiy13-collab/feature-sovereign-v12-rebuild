#!/usr/bin/env python3
import json, sys, argparse, re

REQUIRED = ["baseline_anchor","policy_decision","risk_status","seal_status","auditor_signoff","members","evidence_age_hours"]

def check(path, as_json=False):
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        out = {"decision":"DENY","denies":[f"invalid input: {e}"],"count":1}
        print(json.dumps(out) if as_json else f"DENY: invalid input ({e})")
        return 1

    denies = []
    if not isinstance(data, dict):
        denies.append("input is not an object")
    else:
        for k in REQUIRED:
            if k not in data or data[k] is None:
                denies.append(f"missing or null: {k}")

        ba = data.get("baseline_anchor")
        if ba is not None:
            if not isinstance(ba, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", ba):
                denies.append("baseline_anchor is not a valid sha256")

        pd = data.get("policy_decision")
        if pd is not None and pd != "PASS":
            denies.append("policy_decision is not PASS")

        rs = data.get("risk_status")
        if rs is not None and rs != "ACCEPTABLE":
            denies.append("risk_status is not ACCEPTABLE")

        ss = data.get("seal_status")
        if ss is not None and ss != "ACTIVE":
            denies.append("seal_status is not ACTIVE")

        aso = data.get("auditor_signoff")
        if aso is not None:
            if not isinstance(aso, dict):
                denies.append("auditor_signoff is not an object")
            elif aso.get("signed") is not True:
                denies.append("auditor_signoff is not signed")

        m = data.get("members")
        if m is not None:
            if not isinstance(m, list):
                denies.append("members is not an array")
            elif len(m) == 0:
                denies.append("members is empty")

        age = data.get("evidence_age_hours")
        if age is not None:
            if isinstance(age, bool) or not isinstance(age, (int, float)):
                denies.append("evidence_age_hours is not a number")
            elif age > 120:
                denies.append("evidence_age_hours is stale")

    denies.sort()
    if denies:
        out = {"decision":"DENY","denies":denies,"count":len(denies)}
        print(json.dumps(out) if as_json else "DENY: " + "; ".join(denies))
        return 1
    out = {"decision":"PASS","denies":[],"count":0}
    print(json.dumps(out) if as_json else "PASS")
    return 0

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("bundle")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    sys.exit(check(a.bundle, a.json))
