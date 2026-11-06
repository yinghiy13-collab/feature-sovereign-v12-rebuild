#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --quiet pytest jsonschema
echo "Sovereign V12 baseline environment ready."
echo "Reminder: Policy Agent evaluates only. Operator freezes. AO approves conditional risk."
