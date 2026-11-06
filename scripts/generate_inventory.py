#!/usr/bin/env python3
import os, json, hashlib, csv
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT_DIR = ROOT / "inventory_reports"
PROTECTED_FILES = ["memory.yaml", "MASTER_STANDARD.md", "BASELINE_PIPELINE.md", "MASTER_ARTIFACT.md"]

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def scan_repo():
    inventory = {"scan_timestamp": datetime.now(timezone.utc).isoformat(), "files": [], "skills": [], "protected_baseline": []}
    skill_matrix = []
    for root, dirs, files in os.walk(ROOT):
        if any(ignored in root for ignored in [".git", ".verify", "__pycache__", "node_modules"]):
            continue
        for file in files:
            full_path = Path(root) / file
            rel_path = full_path.relative_to(ROOT)
            file_hash = sha256_file(full_path)
            file_meta = {"path": str(rel_path), "size_bytes": full_path.stat().st_size, "sha256": file_hash}
            inventory["files"].append(file_meta)
            if file == "SKILL.md": inventory["skills"].append(file_meta); skill_matrix.append([str(rel_path), "PROPOSED", "NOT_TESTED", file_hash])
            if str(rel_path) in PROTECTED_FILES: inventory["protected_baseline"].append(file_meta)
    with open(OUT_DIR / "REPOSITORY_INVENTORY.json", "w") as f: json.dump(inventory, f, indent=2)
    with open(OUT_DIR / "CAPABILITY_COVERAGE_MATRIX.csv", "w", newline="") as f:
        writer = csv.writer(f); writer.writerow(["Path", "Status", "Verification", "SHA256"]); writer.writerows(skill_matrix)
    with open(OUT_DIR / "PROTECTED_BASELINE_REPORT.md", "w") as f:
        f.write("# Protected Baseline Integrity Report\n\n")
        f.write(f"**Scan Date:** {inventory['scan_timestamp']}\n\n| File | Size (bytes) | SHA-256 |\n|---|---|---|\n")
        for p in inventory["protected_baseline"]: f.write(f"| {p['path']} | {p['size_bytes']} | `{p['sha256']}` |\n")
    print(f"✅ G0 Scan Complete. Found {len(inventory['files'])} files.")

if __name__ == "__main__": scan_repo()
