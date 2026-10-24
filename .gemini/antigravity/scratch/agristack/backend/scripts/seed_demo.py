"""
Idempotent demo seed for Farmer, Investor, Admin, Gov Officer.
Run: python -m scripts.seed_demo  (from backend/)
"""
from app.core.database import init_db, SessionLocal
from app.main import seed_defaults


def main():
    init_db()
    db = SessionLocal()
    try:
        seed_defaults(db)
        print("Demo accounts ready:")
        print("  admin@agristack.org / AgriStack@Admin2026")
        print("  farmer@agristack.org / AgriStack@Farmer2026")
        print("  investor@agristack.org / AgriStack@Investor2026")
        print("  gov@agristack.org / AgriStack@Gov2026")
    finally:
        db.close()


if __name__ == "__main__":
    main()
