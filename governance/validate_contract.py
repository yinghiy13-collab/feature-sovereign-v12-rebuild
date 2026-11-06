#!/usr/bin/env python3
import json, sys, yaml
from jsonschema import Draft202012Validator, ValidationError

def validate_spec(spec_path, schema_path, registry_path):
    spec = json.load(open(spec_path))
    schema = json.load(open(schema_path))
    registry = yaml.safe_load(open(registry_path))

    try:
        Draft202012Validator(schema).validate(spec)
    except ValidationError as e:
        print(f"FAIL: Schema violation -> {e.message}")
        return 1

    if spec["domain"] not in registry["domains"]:
        print(f"FAIL: Unknown domain '{spec['domain']}'")
        return 1

    if spec["authority_boundary"]["can_release"] is not False:
        print("FAIL: Authority violation — AI cannot release")
        return 1

    print(f"PASS: Contract valid for {spec['spec_id']} ({spec['domain']})")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(2)
    sys.exit(validate_spec(sys.argv[1], "schemas/canonical_spec.schema.json", "schemas/domain_registry.yaml"))
