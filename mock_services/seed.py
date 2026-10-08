import os
import sys

# add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine, SessionLocal
from app.db import models
from datetime import datetime, date, timedelta

def seed_db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(models.Customer).count() > 0:
        print("Database already seeded.")
        db.close()
        return

    # Seed Customers
    c1 = models.Customer(
        customer_id="CUST1",
        name="Rohit Sharma",
        phone_hash="hash1",
        preferred_language="hinglish"
    )
    c2 = models.Customer(
        customer_id="CUST2",
        name="Sunita Gupta",
        phone_hash="hash2",
        preferred_language="hi"
    )
    db.add_all([c1, c2])
    db.commit()

    # Seed Policies
    p1 = models.Policy(
        policy_no="POL123456",
        customer_id="CUST1",
        type="car",
        start_date=date(2025, 11, 15),
        expiry_date=date(2026, 11, 15),
        status="ACTIVE",
        premium=11200.00
    )
    p2 = models.Policy(
        policy_no="POL654321",
        customer_id="CUST2",
        type="health",
        start_date=date(2025, 1, 10),
        expiry_date=date(2026, 1, 10),
        status="ACTIVE",
        premium=15000.00
    )
    db.add_all([p1, p2])
    db.commit()
    
    print("Database seeded with sample customers and policies.")
    db.close()

if __name__ == "__main__":
    seed_db()
