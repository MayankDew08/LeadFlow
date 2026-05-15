import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.core.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.lead import Lead
from app.models.discussion import Discussion

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Dummy Data Configuration
USER_NAME = "Mayank Dewangan"
USER_EMAIL = "mayank24102@iiitnr.edu.in"
USER_PASSWORD = hash_password("Mayank@123")

LEGIT_LEADS = [
    {"name": "Satya Nadella", "company": "Microsoft", "phone": "+1-425-882-8080", "status": "Won"},
    {"name": "Sundar Pichai", "company": "Google", "phone": "+1-650-253-0000", "status": "Qualified"},
    {"name": "Tim Cook", "company": "Apple", "phone": "+1-408-996-1010", "status": "Proposal Sent"},
    {"name": "Elon Musk", "company": "Tesla", "phone": "+1-650-681-5000", "status": "Contacted"},
    {"name": "Jeff Bezos", "company": "Amazon", "phone": "+1-206-266-1000", "status": "New"},
    {"name": "Mark Zuckerberg", "company": "Meta", "phone": "+1-650-543-4800", "status": "Lost"},
    {"name": "Jensen Huang", "company": "NVIDIA", "phone": "+1-408-486-2000", "status": "Qualified"},
    {"name": "Larry Ellison", "company": "Oracle", "phone": "+1-650-506-7000", "status": "Proposal Sent"},
    {"name": "Marc Benioff", "company": "Salesforce", "phone": "+1-415-901-7000", "status": "Contacted"},
    {"name": "Arvind Krishna", "company": "IBM", "phone": "+1-914-499-1900", "status": "New"},
]

DUMMY_NOTES = [
    "Initial discovery call completed. Very interested in AI integration.",
    "Sent follow-up email with product deck. Awaiting response.",
    "Discussion about enterprise pricing and security compliance.",
    "Requested a demo for the engineering team next Tuesday.",
    "Negotiating terms for a multi-year contract.",
    "Budget constraints identified. May need to revisit next quarter.",
    "Technical deep dive scheduled with their CTO.",
    "Interested in the lead scoring feature. Wants to see a pilot.",
    "Competitive analysis provided. They liked our transparency.",
    "Checking back in after the previous quarter's rejection.",
]

async def seed_data():
    async with AsyncSessionLocal() as db:
        # 1. Ensure User exists
        result = await db.execute(select(User).where(User.email == USER_EMAIL))
        user = result.scalar_one_or_none()

        if not user:
            print(f"Creating user: {USER_NAME}...")
            user = User(
                name=USER_NAME,
                email=USER_EMAIL,
                password=USER_PASSWORD
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            print(f"User {USER_EMAIL} already exists.")

        # 2. Add Leads and Discussions
        print(f"Adding {len(LEGIT_LEADS)} leads...")
        for i, lead_data in enumerate(LEGIT_LEADS):
            # Check if lead already exists by company to avoid duplicates on multiple runs
            res = await db.execute(select(Lead).where(Lead.company == lead_data["company"], Lead.sales_rep_id == user.id))
            existing_lead = res.scalar_one_or_none()
            
            if not existing_lead:
                lead = Lead(
                    name=lead_data["name"],
                    company=lead_data["company"],
                    phone=lead_data["phone"],
                    status=lead_data["status"],
                    sales_rep_id=user.id,
                    follow_up_at=datetime.now(timezone.utc) + timedelta(days=i+1)
                )
                db.add(lead)
                await db.flush() # Get lead.id
                
                # Add a discussion for this lead
                discussion = Discussion(
                    lead_id=lead.id,
                    note=DUMMY_NOTES[i % len(DUMMY_NOTES)],
                    follow_up_at=lead.follow_up_at
                )
                db.add(discussion)
            else:
                print(f"Lead for {lead_data['company']} already exists. Skipping.")

        await db.commit()
        print("Seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
