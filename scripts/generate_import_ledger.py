#!/usr/bin/env python3
"""
Generate an import ledger showing which weeks have been imported and which are pending.

Usage:
    python scripts/generate_import_ledger.py

Output:
    - IMPORT_LEDGER.md (human-readable)
    - import_ledger.json (machine-readable)
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def get_imported_data():
    """Query database for imported weeks."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    client = create_client(url, key)

    # Get all unique season/week/source combinations
    response = client.table("projections").select(
        "season,week,source"
    ).execute()

    imported = {}
    for row in response.data:
        season = row["season"]
        week = row["week"]
        source = row["source"]

        if season not in imported:
            imported[season] = {}
        if week not in imported[season]:
            imported[season][week] = []
        if source not in imported[season][week]:
            imported[season][week].append(source)

    return imported


def get_player_projection_counts():
    """Get counts of players and projections."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    client = create_client(url, key)

    # Get total players
    players_response = client.table("players").select("id", count="exact").execute()
    total_players = players_response.count

    # Get total projections
    projections_response = client.table("projections").select("id", count="exact").execute()
    total_projections = projections_response.count

    return total_players, total_projections


def generate_markdown_ledger(imported_data, total_players, total_projections):
    """Generate human-readable markdown ledger."""
    content = ["# NFL Data Import Ledger\n"]
    content.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    content.append(f"**Total Players:** {total_players}")
    content.append(f"**Total Projections:** {total_projections}\n")

    # Define seasons and weeks to track
    seasons = [2023, 2024]  # Add more as needed
    weeks = list(range(1, 19))  # Weeks 1-18

    for season in sorted(seasons, reverse=True):
        content.append(f"\n## {season} Season\n")

        if season in imported_data:
            imported_weeks = imported_data[season]
            imported_count = len(imported_weeks)
            pending_count = len(weeks) - imported_count

            content.append(f"**Status:** {imported_count}/{len(weeks)} weeks imported ({pending_count} pending)\n")

            # Create status table
            content.append("| Week | Status | Source | Action |")
            content.append("|------|--------|--------|--------|")

            for week in weeks:
                if week in imported_weeks:
                    sources = ", ".join(imported_weeks[week])
                    status = "✅ Imported"
                    action = "Re-import to update"
                else:
                    sources = "-"
                    status = "⏳ Pending"
                    action = "**Import needed**"

                content.append(f"| {week:2d} | {status} | {sources} | {action} |")
        else:
            content.append(f"**Status:** 0/{len(weeks)} weeks imported (all pending)\n")
            content.append("⚠️ No data imported for this season yet.\n")
            content.append("**Action:** Run import for this season\n")

    content.append("\n## Import Commands\n")
    content.append("```bash")
    content.append("# Start the server")
    content.append("uvicorn src.main:app --reload")
    content.append("")
    content.append("# Import a single week")
    content.append('curl -X POST "http://localhost:8000/api/loaders/import/weekly" \\')
    content.append('  -H "Content-Type: application/json" \\')
    content.append('  -d \'{"year": 2023, "week": 5, "source": "nflverse"}\'')
    content.append("")
    content.append("# Import an entire season")
    content.append('curl -X POST "http://localhost:8000/api/loaders/import/season?year=2023&start_week=1&end_week=18"')
    content.append("```\n")

    content.append("\n## Data Sources\n")
    content.append("- **nflverse**: Primary source (nfl-data-py library)")
    content.append("- **ffdp**: Backup source (Fantasy Football Data Pros CSV)\n")

    return "\n".join(content)


def generate_json_ledger(imported_data, total_players, total_projections):
    """Generate machine-readable JSON ledger."""
    seasons = [2023, 2024]
    weeks = list(range(1, 19))

    ledger = {
        "last_updated": datetime.now().isoformat(),
        "summary": {
            "total_players": total_players,
            "total_projections": total_projections,
            "total_weeks_imported": sum(len(imported_data.get(s, {})) for s in seasons),
        },
        "seasons": {}
    }

    for season in seasons:
        imported_weeks = imported_data.get(season, {})

        ledger["seasons"][season] = {
            "weeks_imported": len(imported_weeks),
            "weeks_pending": len(weeks) - len(imported_weeks),
            "weeks": {}
        }

        for week in weeks:
            if week in imported_weeks:
                ledger["seasons"][season]["weeks"][week] = {
                    "status": "imported",
                    "sources": imported_weeks[week]
                }
            else:
                ledger["seasons"][season]["weeks"][week] = {
                    "status": "pending",
                    "sources": []
                }

    return ledger


def main():
    """Generate import ledgers."""
    print("🔍 Querying database for import status...")

    try:
        imported_data = get_imported_data()
        total_players, total_projections = get_player_projection_counts()

        print(f"✅ Found {total_players} players and {total_projections} projections")

        # Generate markdown ledger
        print("\n📝 Generating IMPORT_LEDGER.md...")
        markdown_content = generate_markdown_ledger(imported_data, total_players, total_projections)

        ledger_path = Path(__file__).parent.parent / "IMPORT_LEDGER.md"
        with open(ledger_path, "w") as f:
            f.write(markdown_content)

        print(f"✅ Created {ledger_path}")

        # Generate JSON ledger
        print("\n📊 Generating import_ledger.json...")
        json_ledger = generate_json_ledger(imported_data, total_players, total_projections)

        json_path = Path(__file__).parent.parent / "import_ledger.json"
        with open(json_path, "w") as f:
            json.dump(json_ledger, f, indent=2)

        print(f"✅ Created {json_path}")

        # Print summary
        print("\n" + "="*60)
        print("📊 IMPORT STATUS SUMMARY")
        print("="*60)

        for season in sorted(imported_data.keys(), reverse=True):
            imported_weeks = len(imported_data[season])
            pending_weeks = 18 - imported_weeks
            print(f"\n{season} Season:")
            print(f"  ✅ Imported: {imported_weeks} weeks")
            print(f"  ⏳ Pending:  {pending_weeks} weeks")

        print("\n" + "="*60)
        print("✅ Ledger generation complete!")
        print(f"\nView ledger: cat IMPORT_LEDGER.md")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
