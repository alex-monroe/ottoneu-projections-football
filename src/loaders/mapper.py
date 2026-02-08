"""
Data mapper for transforming data from various sources to our database schema.
"""
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional
from uuid import UUID
import pandas as pd
import logging

from src.database.models import PlayerCreate, ProjectionCreate
from src.loaders.exceptions import MappingError

logger = logging.getLogger(__name__)


class DataMapper:
    """
    Maps data from various sources to our database schema.
    """

    # Column mappings for different data sources
    NFLVERSE_PLAYER_MAP = {
        'player_name': 'name',
        'player_display_name': 'name',
        'recent_team': 'team',
        'position': 'position',
        'player_id': 'espn_id',
    }

    NFLVERSE_PROJECTION_MAP = {
        # Passing
        'passing_yards': 'pass_yds',
        'completions': 'pass_cmp',
        'attempts': 'pass_att',
        'passing_tds': 'pass_tds',
        'interceptions': 'pass_ints',

        # Rushing
        'rushing_yards': 'rush_yds',
        'carries': 'rush_att',
        'rushing_tds': 'rush_tds',

        # Receiving
        'receptions': 'receptions',
        'receiving_yards': 'rec_yds',
        'receiving_tds': 'rec_tds',
        'targets': 'targets',

        # Other
        'fumbles_lost': 'fumbles',
    }

    FFDP_PLAYER_MAP = {
        'Player': 'name',
        'player': 'name',
        'Tm': 'team',
        'team': 'team',
        'Pos': 'position',
        'pos': 'position',
    }

    FFDP_PROJECTION_MAP = {
        # Passing
        'PassYds': 'pass_yds',
        'pass_yds': 'pass_yds',
        'PassAtt': 'pass_att',
        'pass_att': 'pass_att',
        'PassCmp': 'pass_cmp',
        'pass_cmp': 'pass_cmp',
        'PassTD': 'pass_tds',
        'pass_td': 'pass_tds',
        'Int': 'pass_ints',
        'pass_int': 'pass_ints',

        # Rushing
        'RushYds': 'rush_yds',
        'rush_yds': 'rush_yds',
        'RushAtt': 'rush_att',
        'rush_att': 'rush_att',
        'RushTD': 'rush_tds',
        'rush_td': 'rush_tds',

        # Receiving
        'Rec': 'receptions',
        'rec': 'receptions',
        'RecYds': 'rec_yds',
        'rec_yds': 'rec_yds',
        'RecTD': 'rec_tds',
        'rec_td': 'rec_tds',
        'Tgt': 'targets',
        'targets': 'targets',

        # Other
        'FL': 'fumbles',
        'fumbles': 'fumbles',
        'fumbles_lost': 'fumbles',
    }

    def __init__(self):
        """Initialize the data mapper."""
        self.source_maps = {
            'nflverse': (self.NFLVERSE_PLAYER_MAP, self.NFLVERSE_PROJECTION_MAP),
            'ffdp': (self.FFDP_PLAYER_MAP, self.FFDP_PROJECTION_MAP),
        }

    def map_to_player_schema(self, df: pd.DataFrame, source: str) -> List[PlayerCreate]:
        """
        Map DataFrame to PlayerCreate models.

        Args:
            df: DataFrame with player data
            source: Data source name ('nflverse', 'ffdp', etc.)

        Returns:
            List of PlayerCreate models

        Raises:
            MappingError: If mapping fails
        """
        if df.empty:
            return []

        try:
            player_map, _ = self._get_source_maps(source)

            players = []
            # Group by player to avoid duplicates
            player_cols = list(player_map.values())

            # Get the columns we need to map
            mapped_df = self._map_columns(df, player_map)

            # Remove duplicates based on name and position
            if 'name' in mapped_df.columns and 'position' in mapped_df.columns:
                unique_players = mapped_df.drop_duplicates(subset=['name', 'position'])

                for _, row in unique_players.iterrows():
                    # Try to convert espn_id to int, but skip if it's not a valid integer
                    espn_id = None
                    if pd.notna(row.get('espn_id')):
                        try:
                            espn_id = int(row.get('espn_id'))
                        except (ValueError, TypeError):
                            # espn_id is not a valid integer, skip it
                            pass

                    player_data = {
                        'name': str(row.get('name', '')),
                        'position': str(row.get('position', '')),
                        'team': str(row.get('team', '')) if pd.notna(row.get('team')) else None,
                        'espn_id': espn_id,
                    }

                    # Only add if we have minimum required fields
                    if player_data['name'] and player_data['position']:
                        players.append(PlayerCreate(**player_data))

            logger.info(f"Mapped {len(players)} players from {source}")
            return players

        except Exception as e:
            raise MappingError(f"Failed to map players: {str(e)}")

    def map_to_projection_schema(
        self,
        df: pd.DataFrame,
        source: str,
        week: int,
        season: int,
        player_id_map: Optional[Dict[str, UUID]] = None
    ) -> List[ProjectionCreate]:
        """
        Map DataFrame to ProjectionCreate models.

        Args:
            df: DataFrame with projection data
            source: Data source name
            week: NFL week number
            season: NFL season year
            player_id_map: Optional mapping of player name -> UUID

        Returns:
            List of ProjectionCreate models

        Raises:
            MappingError: If mapping fails
        """
        if df.empty:
            return []

        try:
            player_map, projection_map = self._get_source_maps(source)

            # Map columns
            mapped_df = self._map_columns(df, {**player_map, **projection_map})

            projections = []
            for _, row in mapped_df.iterrows():
                player_name = str(row.get('name', ''))
                player_position = str(row.get('position', ''))

                # Skip if no player identifier
                if not player_name or not player_position:
                    continue

                # Get player_id if map provided
                player_id = None
                if player_id_map:
                    # Try name lookup
                    player_id = player_id_map.get(player_name)
                    if not player_id:
                        # Try name + position lookup
                        key = f"{player_name}_{player_position}"
                        player_id = player_id_map.get(key)

                # If we don't have a player_id, we'll need to handle this at the service layer
                # For now, skip entries without player_id
                if not player_id:
                    continue

                projection_data = {
                    'player_id': player_id,
                    'week': week,
                    'season': season,
                    'source': source,

                    # Passing
                    'pass_att': self._to_decimal(row.get('pass_att')),
                    'pass_cmp': self._to_decimal(row.get('pass_cmp')),
                    'pass_yds': self._to_decimal(row.get('pass_yds')),
                    'pass_tds': self._to_decimal(row.get('pass_tds')),
                    'pass_ints': self._to_decimal(row.get('pass_ints')),

                    # Rushing
                    'rush_att': self._to_decimal(row.get('rush_att')),
                    'rush_yds': self._to_decimal(row.get('rush_yds')),
                    'rush_tds': self._to_decimal(row.get('rush_tds')),

                    # Receiving
                    'receptions': self._to_decimal(row.get('receptions')),
                    'rec_yds': self._to_decimal(row.get('rec_yds')),
                    'rec_tds': self._to_decimal(row.get('rec_tds')),
                    'targets': self._to_decimal(row.get('targets')),

                    # Other
                    'fumbles': self._to_decimal(row.get('fumbles')),
                }

                projections.append(ProjectionCreate(**projection_data))

            logger.info(f"Mapped {len(projections)} projections from {source}")
            return projections

        except Exception as e:
            raise MappingError(f"Failed to map projections: {str(e)}")

    def _get_source_maps(self, source: str) -> tuple:
        """Get column mapping for a source."""
        if source not in self.source_maps:
            raise MappingError(f"Unknown data source: {source}")
        return self.source_maps[source]

    def _map_columns(self, df: pd.DataFrame, column_map: Dict[str, str]) -> pd.DataFrame:
        """
        Map DataFrame columns using provided mapping.

        Args:
            df: Input DataFrame
            column_map: Mapping of source columns to target columns

        Returns:
            DataFrame with renamed columns
        """
        # Create a new DataFrame with mapped columns
        mapped_data = {}

        for source_col, target_col in column_map.items():
            if source_col in df.columns:
                mapped_data[target_col] = df[source_col]

        return pd.DataFrame(mapped_data)

    def _to_decimal(self, value) -> Optional[Decimal]:
        """
        Convert value to Decimal, handling NaN and None.

        Args:
            value: Value to convert

        Returns:
            Decimal or None
        """
        if pd.isna(value) or value is None:
            return None

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
