import sys
sys.path.insert(0, ".")
from app.core.logging import setup_logging; setup_logging()
from app.services.file_service import store, load_all_files
from app.services.model_service import load_model
load_all_files(); load_model()
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app, raise_server_exceptions=False)

tests = [
    ("/hotspots?risk_category=CRITICAL", 153),
    ("/hotspots?risk_category=MODERATE", 150),
    ("/hotspots?risk_category=HIGH", 151),
    ("/hotspots?risk_category=LOW", 152),
    ("/hotspots?stability_class=Volatile", 432),
    ("/hotspots?stability_class=Persistent", 155),
    ("/hotspots?stability_class=Declining", 2),    # patrol table: 2 Declining
    ("/hotspots?stability_class=Emerging", 17),    # patrol table: 17 Emerging
    ("/risk-zones?category=CRITICAL", 153),
    ("/stability?stability_class=Emerging", 60),   # stability table: 60 Emerging
    ("/patrol-recommendations?stability_class=Persistent", 18),  # top20 Persistent
]
all_ok = True
for ep, expected in tests:
    limit_override = "&limit=200" if "patrol-recommendations" in ep else "&limit=1000"
    r = client.get(ep + limit_override)
    total = r.json().get("meta", {}).get("total", -1)
    ok = total == expected
    if not ok:
        all_ok = False
    status = "OK  " if ok else "FAIL"
    print(f"{status}  total={total}  expected={expected}  {ep}")
print("ALL OK:", all_ok)
