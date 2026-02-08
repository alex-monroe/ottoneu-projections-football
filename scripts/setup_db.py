"""
Database setup script.
Initializes Supabase tables and creates default scoring configurations.
"""
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_supabase_client


def setup_database():
    """Initialize database tables and default data."""
    client = get_supabase_client()

    print("Setting up database...")
    print("\nIMPORTANT: Please run the schema.sql file in your Supabase SQL editor first!")
    print("Location: src/database/schema.sql")
    print("\nThis script will now insert default scoring configurations...\n")

    # Default scoring configurations
    scoring_configs = [
        {
            "name": "PPR",
            "pass_yds_per_point": 25.0,
            "pass_td_points": 4.0,
            "pass_int_points": -2.0,
            "rush_yds_per_point": 10.0,
            "rush_td_points": 6.0,
            "rec_yds_per_point": 10.0,
            "rec_td_points": 6.0,
            "rec_points": 1.0,  # Full PPR
            "fumble_points": -2.0,
            "is_default": True
        },
        {
            "name": "Half-PPR",
            "pass_yds_per_point": 25.0,
            "pass_td_points": 4.0,
            "pass_int_points": -2.0,
            "rush_yds_per_point": 10.0,
            "rush_td_points": 6.0,
            "rec_yds_per_point": 10.0,
            "rec_td_points": 6.0,
            "rec_points": 0.5,  # Half PPR
            "fumble_points": -2.0,
            "is_default": False
        },
        {
            "name": "Standard",
            "pass_yds_per_point": 25.0,
            "pass_td_points": 4.0,
            "pass_int_points": -2.0,
            "rush_yds_per_point": 10.0,
            "rush_td_points": 6.0,
            "rec_yds_per_point": 10.0,
            "rec_td_points": 6.0,
            "rec_points": 0.0,  # No PPR
            "fumble_points": -2.0,
            "is_default": False
        }
    ]

    # Insert scoring configurations
    for config in scoring_configs:
        try:
            result = client.table("scoring_configs").upsert(
                config,
                on_conflict="name"
            ).execute()
            print(f"✓ Created/updated scoring config: {config['name']}")
        except Exception as e:
            print(f"✗ Error creating scoring config {config['name']}: {e}")

    print("\n✓ Database setup complete!")
    print("\nNext steps:")
    print("1. Create a .env file with your Supabase credentials (see .env.example)")
    print("2. Run the application: uvicorn src.main:app --reload")
    print("3. Visit http://localhost:8000/docs for API documentation")


if __name__ == "__main__":
    setup_database()
