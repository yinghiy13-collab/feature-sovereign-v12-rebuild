#!/usr/bin/env python3
"""Generate honest dashboard.html from the latest .verify/summary.json"""
import json
import glob
import subprocess
from pathlib import Path

def get_git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"

# 1. Find latest evidence
reports = sorted(glob.glob('.verify/*/summary.json'))
if not reports:
    print("❌ No .verify/*/summary.json found. Run verify_all.sh first.")
    exit(1)

latest_report = reports[-1]
with open(latest_report) as f:
    data = json.load(f)

# 2. Build HTML rows
rows = ""
for check, status in data["checks"].items():
    color = "text-emerald-600" if status == "PASS" else "text-red-600"
    icon = "✓" if status == "PASS" else "✗"
    rows += f"""
    <tr class="border-b border-slate-200 hover:bg-slate-50">
        <td class="p-3 font-mono text-sm">{check}</td>
        <td class="p-3 text-center {color} font-bold">{icon} {status}</td>
    </tr>"""

# 3. Build HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sovereign Gate Dashboard - v1.0.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 text-slate-800 p-8">
    <div class="max-w-4xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
        <div class="bg-slate-900 text-white p-6 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold">Sovereign Release Gate</h1>
                <p class="text-slate-400 text-sm">Verification Evidence</p>
            </div>
            <div class="text-right">
                <span class="bg-emerald-500 text-white px-3 py-1 rounded-full text-sm font-bold">FROZEN v1.0.0</span>
            </div>
        </div>
        
        <div class="p-6 grid grid-cols-3 gap-4 border-b border-slate-200">
            <div class="bg-slate-50 p-4 rounded-lg text-center">
                <div class="text-sm text-slate-500">Commit Hash</div>
                <div class="font-mono font-bold">{get_git_hash()}</div>
            </div>
            <div class="bg-slate-50 p-4 rounded-lg text-center">
                <div class="text-sm text-slate-500">Evidence Source</div>
                <div class="font-mono font-bold text-xs pt-1">{latest_report}</div>
            </div>
            <div class="bg-slate-50 p-4 rounded-lg text-center">
                <div class="text-sm text-slate-500">Result</div>
                <div class="font-bold text-emerald-600 text-lg">{data['passed']} / {data['total']} PASSED</div>
            </div>
        </div>

        <div class="p-6">
            <h2 class="text-lg font-bold mb-4">Verification Checks</h2>
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-slate-100 text-slate-600 text-sm">
                        <th class="p-3">Check Name</th>
                        <th class="p-3 text-center">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        
        <div class="bg-slate-50 p-4 text-center text-xs text-slate-500">
            This dashboard is auto-generated from actual test evidence. No mock data.
        </div>
    </div>
</body>
</html>"""

Path("dashboard.html").write_text(html)
print(f"✅ Generated dashboard.html from {latest_report}")
