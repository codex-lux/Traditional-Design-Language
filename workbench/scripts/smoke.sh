#!/usr/bin/env bash
# End-to-end smoke: start the server, prove the HTTP results match the CLI's own,
# run one compose job to completion, stop the server. Exits non-zero on any drift.
set -euo pipefail
cd "$(dirname "$0")/../.."

python3 -m uvicorn workbench.server.app:app --host 127.0.0.1 --port 8178 --log-level error &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true' EXIT
for i in $(seq 1 40); do
  curl -sf http://127.0.0.1:8178/api/health >/dev/null && break
  sleep 0.5
done

echo "— health"
curl -sf http://127.0.0.1:8178/api/health | python3 -c "import json,sys; h=json.load(sys.stdin); assert h['ok'], h; print('ok · styles', h['counts']['styles'])"

echo "— evaluate parity vs build/plan_check.py --json"
python3 - <<'EOF'
import json, subprocess, urllib.request

plan = json.load(open("plans/tidewater-georgian-careful.json"))
req = urllib.request.Request("http://127.0.0.1:8178/api/plan/evaluate",
    data=json.dumps({"plan": plan, "place": False}).encode(),
    headers={"content-type": "application/json"})
http = json.load(urllib.request.urlopen(req))["check"]
cli = json.loads(subprocess.check_output(
    ["python3", "build/plan_check.py", "plans/tidewater-georgian-careful.json", "--json"]))
assert http["counts"] == cli["counts"], (http["counts"], cli["counts"])
assert [f["statement"] for f in http["findings"]] == [f["statement"] for f in cli["findings"]]
print("counts", http["counts"], "· identical to the CLI")
EOF

echo "— compose job"
python3 - <<'EOF'
import json, time, urllib.request

brief = json.load(open("briefs/family-georgian.json"))
req = urllib.request.Request("http://127.0.0.1:8178/api/compose",
    data=json.dumps({"brief": brief, "candidates": 4}).encode(),
    headers={"content-type": "application/json"})
job = json.load(urllib.request.urlopen(req))["job_id"]
for _ in range(120):
    j = json.load(urllib.request.urlopen(f"http://127.0.0.1:8178/api/jobs/{job}"))
    if j["status"] in ("done", "error"):
        break
    time.sleep(0.5)
assert j["status"] == "done", j
cands = j["result"]["candidates"]
print(f"{len(cands)} candidates ·", " · ".join(f"{c['parti']} {c['score']}" for c in cands))
plan = json.load(urllib.request.urlopen(f"http://127.0.0.1:8178/api/jobs/{job}/candidates/0/plan"))
assert plan["levels"], "candidate plan is fetchable"
print("candidate 0 plan:", plan["id"])
EOF

echo "SMOKE GREEN"
