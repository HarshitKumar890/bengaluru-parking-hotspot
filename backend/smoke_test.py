"""Quick smoke test — run from the backend/ directory."""
import sys
sys.path.insert(0, ".")

from app.core.logging import setup_logging
setup_logging()

from app.services.file_service import store, load_all_files
from app.services.model_service import load_model

load_all_files()
load_model()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

ENDPOINTS = [
    "/health",
    "/summary",
    "/hotspots?limit=5",
    "/forecast?limit=5",
    "/patrol-recommendations?limit=5",
    "/risk-zones?limit=5",
    "/feature-importance?limit=5",
    "/stations?limit=5",
    "/junctions?limit=5",
    "/stability?limit=5",
    "/download",
    "/download/feature_importance.csv",
]

all_ok = True
for ep in ENDPOINTS:
    r = client.get(ep)
    ok = r.status_code in (200,)
    if not ok:
        all_ok = False
        print(f"FAIL {r.status_code}  {ep}  -> {r.text[:150]}")
    else:
        ct = r.headers.get("content-type", "")
        if "json" in ct:
            data = r.json()
            if isinstance(data, dict) and "meta" in data:
                meta = data["meta"]
                print(f"OK   {r.status_code}  {ep}  total={meta['total']}  returned={meta['returned']}")
            elif isinstance(data, dict):
                print(f"OK   {r.status_code}  {ep}  keys={list(data.keys())[:6]}")
            else:
                print(f"OK   {r.status_code}  {ep}  (json list/other)")
        else:
            print(f"OK   {r.status_code}  {ep}  content-type={ct[:40]}")

print()
print("Result:", "ALL PASSED" if all_ok else "SOME FAILED")
sys.exit(0 if all_ok else 1)
