#!/usr/bin/env python3
"""
Seed the database with standard fantasy scoring configurations.

Usage:
    python scripts/seed_scoring_configs.py
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from supabase import create_client

from src.scoring.calculator import get_standard_scoring_configs

load_dotenv()


def seed_scoring_configs():
    """Seed standard scoring configurations into the database."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    client = create_client(url, key)

    configs = get_standard_scoring_configs()

    print("🏈 Seeding Standard Fantasy Scoring Configurations\n")
    print("="*60)

    for config_name, config_data in configs.items():
        print(f"\n📊 {config_name}")
        print(f"   {config_data['name']}")

        try:
            # Check if config already exists
            response = client.table("scoring_configs").select("*").eq(
                "name", config_data["name"]
            ).execute()

            if response.data and len(response.data) > 0:
                # Update existing
                existing_id = response.data[0]["id"]

                update_data = {k: float(v) if isinstance(v, type(config_data["pass_yds_per_point"])) else v
                              for k, v in config_data.items() if k != "name"}

                client.table("scoring_configs").update(
                    update_data
                ).eq("id", existing_id).execute()

                print(f"   ✅ Updated existing configuration")
            else:
                # Insert new
                insert_data = {k: float(v) if isinstance(v, type(config_data["pass_yds_per_point"])) else v
                              for k, v in config_data.items()}

                client.table("scoring_configs").insert(insert_data).execute()

                print(f"   ✅ Created new configuration")

            # Print scoring details
            print(f"\n   Passing:")
            print(f"      • {config_data['pass_yds_per_point']} yards per point")
            print(f"      • {config_data['pass_td_points']} points per TD")
            print(f"      • {config_data['pass_int_points']} points per INT")

            print(f"\n   Rushing:")
            print(f"      • {config_data['rush_yds_per_point']} yards per point")
            print(f"      • {config_data['rush_td_points']} points per TD")

            print(f"\n   Receiving:")
            print(f"      • {config_data['rec_points']} points per reception (PPR)")
            print(f"      • {config_data['rec_yds_per_point']} yards per point")
            print(f"      • {config_data['rec_td_points']} points per TD")

            print(f"\n   Other:")
            print(f"      • {config_data['fumble_points']} points per fumble lost")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    print("\n" + "="*60)
    print("✅ Scoring configurations seeded successfully!")
    print("\nYou can now use these in the projections API:")
    print("  - PPR (Point Per Reception)")
    print("  - Half-PPR")
    print("  - Standard (No PPR)")


def main():
    """Main entry point."""
    try:
        seed_scoring_configs()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
