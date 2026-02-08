"""
Service layer for data loading and database operations.

Orchestrates the process of loading data from sources, mapping to our schema,
and upserting into the database.
"""
from typing import Dict, List, Optional, Tuple
from uuid import UUID
import logging
from datetime import datetime

from supabase import Client

from src.database.models import PlayerCreate, ProjectionCreate
from src.loaders.nflverse import NFLVerseLoader
from src.loaders.ffdp import FFDPLoader
from src.loaders.mapper import DataMapper
from src.loaders.exceptions import DataNotAvailableError, LoaderError, MappingError

logger = logging.getLogger(__name__)


class ImportResult:
    """Result of a data import operation."""

    def __init__(self):
        self.success = False
        self.players_imported = 0
        self.players_updated = 0
        self.projections_imported = 0
        self.projections_updated = 0
        self.source = ""
        self.year = 0
        self.week = 0
        self.errors: List[str] = []
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "success": self.success,
            "players_imported": self.players_imported,
            "players_updated": self.players_updated,
            "projections_imported": self.projections_imported,
            "projections_updated": self.projections_updated,
            "source": self.source,
            "year": self.year,
            "week": self.week,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat(),
        }


class LoaderService:
    """
    Service for loading and importing data from various sources.
    """

    def __init__(self, supabase_client: Client):
        """
        Initialize the loader service.

        Args:
            supabase_client: Supabase client for database operations
        """
        self.supabase = supabase_client
        self.nflverse_loader = NFLVerseLoader()
        self.ffdp_loader = FFDPLoader()
        self.mapper = DataMapper()

    def import_weekly_data(
        self,
        year: int,
        week: int,
        source: str = "nflverse",
        use_fallback: bool = True
    ) -> ImportResult:
        """
        Import weekly player data from a source.

        Args:
            year: NFL season year
            week: Week number (1-18)
            source: Data source ('nflverse' or 'ffdp')
            use_fallback: Whether to fall back to FFDP if primary fails

        Returns:
            ImportResult with details of the import operation
        """
        result = ImportResult()
        result.year = year
        result.week = week
        result.source = source

        try:
            # Load data from source
            df = None
            actual_source = source

            try:
                if source == "nflverse":
                    df = self.nflverse_loader.load_weekly_data(year, week)
                elif source == "ffdp":
                    df = self.ffdp_loader.load_weekly_csv(year, week)
                else:
                    raise LoaderError(f"Unknown source: {source}")

            except (DataNotAvailableError, LoaderError) as e:
                logger.warning(f"Primary source {source} failed: {str(e)}")

                if use_fallback and source == "nflverse":
                    logger.info("Attempting fallback to FFDP...")
                    try:
                        df = self.ffdp_loader.load_weekly_csv(year, week)
                        actual_source = "ffdp"
                        result.source = "ffdp"
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed: {str(fallback_error)}")
                        raise LoaderError(f"Both primary and fallback sources failed") from e
                else:
                    raise

            if df is None or df.empty:
                raise DataNotAvailableError(f"No data loaded for {year} week {week}")

            logger.info(f"Loaded {len(df)} records from {actual_source}")

            # Map players
            players = self.mapper.map_to_player_schema(df, actual_source)
            logger.info(f"Mapped {len(players)} unique players")

            # Upsert players and get ID mappings
            player_id_map, new_count, updated_count = self.upsert_players(players)
            result.players_imported = new_count
            result.players_updated = updated_count

            logger.info(
                f"Upserted players: {new_count} new, {updated_count} updated"
            )

            # Map projections
            projections = self.mapper.map_to_projection_schema(
                df, actual_source, week, year, player_id_map
            )
            logger.info(f"Mapped {len(projections)} projections")

            # Upsert projections
            proj_new, proj_updated = self.upsert_projections(projections)
            result.projections_imported = proj_new
            result.projections_updated = proj_updated

            logger.info(
                f"Upserted projections: {proj_new} new, {proj_updated} updated"
            )

            result.success = True
            return result

        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            result.success = False
            result.errors.append(str(e))
            return result

    def upsert_players(
        self, players: List[PlayerCreate]
    ) -> Tuple[Dict[str, UUID], int, int]:
        """
        Upsert players into the database.

        Args:
            players: List of PlayerCreate models

        Returns:
            Tuple of (player_id_map, new_count, updated_count)
            where player_id_map is {name: UUID}
        """
        if not players:
            return {}, 0, 0

        player_id_map = {}
        new_count = 0
        updated_count = 0

        for player in players:
            try:
                # Check if player exists
                response = self.supabase.table("players").select("*").eq(
                    "name", player.name
                ).eq("position", player.position).execute()

                if response.data and len(response.data) > 0:
                    # Player exists, update if needed
                    existing = response.data[0]
                    player_id = UUID(existing["id"])

                    # Update team if changed
                    if player.team and player.team != existing.get("team"):
                        self.supabase.table("players").update({
                            "team": player.team,
                        }).eq("id", str(player_id)).execute()
                        updated_count += 1

                    player_id_map[player.name] = player_id
                    player_id_map[f"{player.name}_{player.position}"] = player_id

                else:
                    # Insert new player
                    insert_response = self.supabase.table("players").insert({
                        "name": player.name,
                        "team": player.team,
                        "position": player.position,
                        "status": player.status,
                        "espn_id": player.espn_id,
                    }).execute()

                    if insert_response.data and len(insert_response.data) > 0:
                        player_id = UUID(insert_response.data[0]["id"])
                        player_id_map[player.name] = player_id
                        player_id_map[f"{player.name}_{player.position}"] = player_id
                        new_count += 1

            except Exception as e:
                logger.error(f"Error upserting player {player.name}: {str(e)}")
                continue

        return player_id_map, new_count, updated_count

    def upsert_projections(
        self, projections: List[ProjectionCreate]
    ) -> Tuple[int, int]:
        """
        Upsert projections into the database.

        Args:
            projections: List of ProjectionCreate models

        Returns:
            Tuple of (new_count, updated_count)
        """
        if not projections:
            return 0, 0

        new_count = 0
        updated_count = 0

        for proj in projections:
            try:
                # Check if projection exists
                response = self.supabase.table("projections").select("id").eq(
                    "player_id", str(proj.player_id)
                ).eq("week", proj.week).eq("season", proj.season).eq(
                    "source", proj.source
                ).execute()

                projection_data = {
                    "player_id": str(proj.player_id),
                    "week": proj.week,
                    "season": proj.season,
                    "source": proj.source,
                    "pass_att": float(proj.pass_att) if proj.pass_att else None,
                    "pass_cmp": float(proj.pass_cmp) if proj.pass_cmp else None,
                    "pass_yds": float(proj.pass_yds) if proj.pass_yds else None,
                    "pass_tds": float(proj.pass_tds) if proj.pass_tds else None,
                    "pass_ints": float(proj.pass_ints) if proj.pass_ints else None,
                    "rush_att": float(proj.rush_att) if proj.rush_att else None,
                    "rush_yds": float(proj.rush_yds) if proj.rush_yds else None,
                    "rush_tds": float(proj.rush_tds) if proj.rush_tds else None,
                    "receptions": float(proj.receptions) if proj.receptions else None,
                    "rec_yds": float(proj.rec_yds) if proj.rec_yds else None,
                    "rec_tds": float(proj.rec_tds) if proj.rec_tds else None,
                    "targets": float(proj.targets) if proj.targets else None,
                    "fumbles": float(proj.fumbles) if proj.fumbles else None,
                }

                if response.data and len(response.data) > 0:
                    # Update existing
                    self.supabase.table("projections").update(
                        projection_data
                    ).eq("id", response.data[0]["id"]).execute()
                    updated_count += 1
                else:
                    # Insert new
                    self.supabase.table("projections").insert(
                        projection_data
                    ).execute()
                    new_count += 1

            except Exception as e:
                logger.error(f"Error upserting projection: {str(e)}")
                continue

        return new_count, updated_count

    def get_available_sources(self) -> List[Dict[str, str]]:
        """
        Get list of available data sources.

        Returns:
            List of source info dictionaries
        """
        sources = []

        # Test NFLVerse
        try:
            self.nflverse_loader.get_available_columns()
            sources.append({
                "name": "nflverse",
                "status": "available",
                "description": "NFLVerse historical player statistics"
            })
        except Exception:
            sources.append({
                "name": "nflverse",
                "status": "unavailable",
                "description": "NFLVerse historical player statistics"
            })

        # FFDP is always available (HTTP-based)
        sources.append({
            "name": "ffdp",
            "status": "available",
            "description": "Fantasy Football Data Pros CSV files"
        })

        return sources
