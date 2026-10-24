import sys, os
# Add the project root to PYTHONPATH so "backend" can be imported when running this script directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import SessionLocal, init_db
from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole
from backend.app.models.farm import Farm
from backend.app.models.project import Project
from backend.app.models.marketplace import MarketplaceListing
from backend.app.models.settlement import SettlementRecord
from backend.app.core.config import settings
from sqlalchemy.orm import Session

def seed_demo_data():
    """Populate the database with a minimal demo dataset.
    Creates:
    - One farm owned by the demo farmer
    - One project linked to that farm
    - A marketplace listing for a share of the project
    - A settlement record for a completed transaction
    """
    init_db()
    db: Session = SessionLocal()
    try:
        # Ensure demo farmer exists (created by backend seed_defaults)
        farmer = db.query(User).filter(User.email == "farmer@agristack.org").first()
        if not farmer:
            raise RuntimeError("Demo farmer not found – ensure backend seed runs first.")

        # Create a farm if not present
        farm = db.query(Farm).filter(Farm.name == "Demo Farm").first()
        if not farm:
            farm = Farm(
                name="Demo Farm",
                location="Maharashtra, India",
                owner_id=farmer.id,
                description="A small family-owned mango orchard used for demo purposes.",
            )
            db.add(farm)
            db.commit()
            db.refresh(farm)

        # Create a project linked to the farm
        project = db.query(Project).filter(Project.title == "Mango Harvest 2026").first()
        if not project:
            project = Project(
                title="Mango Harvest 2026",
                description="Harvest season for the demo mango orchard.",
                farm_id=farm.id,
                target_amount=5000.0,  # currency units
                share_price=10.0,
                total_shares=500,
                status="open",
            )
            db.add(project)
            db.commit()
            db.refresh(project)

        # Marketplace listing for the project
        listing = db.query(MarketplaceListing).filter(
            MarketplaceListing.project_id == project.id
        ).first()
        if not listing:
            listing = MarketplaceListing(
                project_id=project.id,
                price_per_share=project.share_price,
                available_shares=project.total_shares,
                description="Buy shares of the mango harvest.",
            )
            db.add(listing)
            db.commit()
            db.refresh(listing)

        # Settlement record (pretend a purchase of 10 shares)
        settlement = db.query(SettlementRecord).filter(
            SettlementRecord.project_id == project.id
        ).first()
        if not settlement:
            settlement = SettlementRecord(
                project_id=project.id,
                buyer_id=farmer.id,
                shares=10,
                amount=10 * project.share_price,
                status="completed",
            )
            db.add(settlement)
            db.commit()

        print("✅ Demo data seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()
