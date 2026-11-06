package baseline.policy
import rego.v1
default allow := false

required_fields := ["baseline_anchor","policy_decision","risk_status","seal_status","auditor_signoff","members","evidence_age_hours"]

deny contains "input is not an object" if { not is_object(input) }

present(k) if {
  is_object(input)
  k in object.keys(input)
  object.get(input, k, null) != null
}

deny contains sprintf("missing or null: %s", [k]) if {
  is_object(input)
  some k in required_fields
  not present(k)
}

valid_sha256(v) if {
  is_string(v)
  regex.match(`^[0-9a-fA-F]{64}$`, v)
}

is_signed(o) if { o.signed == true }

deny contains "baseline_anchor is not a valid sha256" if {
  present("baseline_anchor")
  not valid_sha256(input.baseline_anchor)
}

deny contains "policy_decision is not PASS" if {
  present("policy_decision")
  input.policy_decision != "PASS"
}

deny contains "risk_status is not ACCEPTABLE" if {
  present("risk_status")
  input.risk_status != "ACCEPTABLE"
}

deny contains "seal_status is not ACTIVE" if {
  present("seal_status")
  input.seal_status != "ACTIVE"
}

deny contains "auditor_signoff is not an object" if {
  present("auditor_signoff")
  not is_object(input.auditor_signoff)
}

deny contains "auditor_signoff is not signed" if {
  present("auditor_signoff")
  is_object(input.auditor_signoff)
  not is_signed(input.auditor_signoff)
}

deny contains "members is not an array" if {
  present("members")
  not is_array(input.members)
}

deny contains "members is empty" if {
  present("members")
  is_array(input.members)
  count(input.members) == 0
}

deny contains "evidence_age_hours is not a number" if {
  present("evidence_age_hours")
  not is_number(input.evidence_age_hours)
}

deny contains "evidence_age_hours is stale" if {
  present("evidence_age_hours")
  is_number(input.evidence_age_hours)
  input.evidence_age_hours > 120
}

allow if {
  is_object(input)
  count(deny) == 0
}
