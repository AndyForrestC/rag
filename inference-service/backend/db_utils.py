"""
Database initialization and migration utilities
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_database, engine
from app.models.db_models import Base


async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")


async def drop_tables():
    """Drop all database tables (use with caution!)"""
    print("Dropping all database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("✅ Database tables dropped successfully!")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")


async def reset_database():
    """Drop and recreate all database tables"""
    print("Resetting database...")
    await drop_tables()
    await create_tables()
    print("✅ Database reset completed!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management utilities")
    parser.add_argument("action", choices=["create", "drop", "reset"], 
                       help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "create":
        asyncio.run(create_tables())
    elif args.action == "drop":
        asyncio.run(drop_tables())
    elif args.action == "reset":
        asyncio.run(reset_database())
