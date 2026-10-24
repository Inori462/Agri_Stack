import sys
sys.path.append("backend")

modules_to_test = [
    "app.services.payment_service",
    "app.api.v1.payments",
    "app.services.marketplace_service",
    "app.api.v1.marketplace",
    "app.services.settlement_service",
    "app.api.v1.settlements",
    "app.services.dispute_service",
    "app.api.v1.disputes",
]

for mod in modules_to_test:
    try:
        __import__(mod)
        print(f"[OK] {mod}")
    except Exception as e:
        print(f"[FAIL] {mod}: {type(e).__name__}: {e}")
