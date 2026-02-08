"""
Fixtures for loader tests.
"""
import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock
from uuid import uuid4


@pytest.fixture
def sample_nflverse_data():
    """Create sample NFLVerse-style data."""
    return pd.DataFrame({
        'player_name': ['Patrick Mahomes', 'Christian McCaffrey', 'Justin Jefferson'],
        'player_display_name': ['Patrick Mahomes', 'Christian McCaffrey', 'Justin Jefferson'],
        'position': ['QB', 'RB', 'WR'],
        'recent_team': ['KC', 'SF', 'MIN'],
        'week': [1, 1, 1],
        'season': [2023, 2023, 2023],

        # Passing stats
        'passing_yards': [320.0, 0.0, 0.0],
        'completions': [25.0, 0.0, 0.0],
        'attempts': [35.0, 0.0, 0.0],
        'passing_tds': [3.0, 0.0, 0.0],
        'interceptions': [1.0, 0.0, 0.0],

        # Rushing stats
        'rushing_yards': [15.0, 125.0, 0.0],
        'carries': [3.0, 22.0, 0.0],
        'rushing_tds': [0.0, 2.0, 0.0],

        # Receiving stats
        'receptions': [0.0, 5.0, 8.0],
        'receiving_yards': [0.0, 45.0, 115.0],
        'receiving_tds': [0.0, 0.0, 1.0],
        'targets': [0.0, 7.0, 12.0],

        # Other
        'fumbles_lost': [0.0, 0.0, 0.0],
    })


@pytest.fixture
def sample_ffdp_data():
    """Create sample FFDP-style CSV data."""
    return pd.DataFrame({
        'Player': ['Patrick Mahomes', 'Christian McCaffrey', 'Justin Jefferson'],
        'Pos': ['QB', 'RB', 'WR'],
        'Tm': ['KC', 'SF', 'MIN'],

        # Passing
        'PassYds': [320.0, 0.0, 0.0],
        'PassCmp': [25.0, 0.0, 0.0],
        'PassAtt': [35.0, 0.0, 0.0],
        'PassTD': [3.0, 0.0, 0.0],
        'Int': [1.0, 0.0, 0.0],

        # Rushing
        'RushYds': [15.0, 125.0, 0.0],
        'RushAtt': [3.0, 22.0, 0.0],
        'RushTD': [0.0, 2.0, 0.0],

        # Receiving
        'Rec': [0.0, 5.0, 8.0],
        'RecYds': [0.0, 45.0, 115.0],
        'RecTD': [0.0, 0.0, 1.0],
        'Tgt': [0.0, 7.0, 12.0],

        # Other
        'FL': [0.0, 0.0, 0.0],
    })


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    mock_client = MagicMock()

    # Mock table operations
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table

    # Mock select query
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select

    # Mock eq filters
    mock_eq = MagicMock()
    mock_select.eq.return_value = mock_eq
    mock_eq.eq.return_value = mock_eq

    # Mock execute with empty response by default
    mock_response = MagicMock()
    mock_response.data = []
    mock_eq.execute.return_value = mock_response

    # Mock insert
    mock_insert = MagicMock()
    mock_table.insert.return_value = mock_insert

    insert_response = MagicMock()
    insert_response.data = [{"id": str(uuid4())}]
    mock_insert.execute.return_value = insert_response

    # Mock update
    mock_update = MagicMock()
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_update

    update_response = MagicMock()
    update_response.data = [{"id": str(uuid4())}]
    mock_update.execute.return_value = update_response

    return mock_client


@pytest.fixture
def sample_player_ids():
    """Create sample player ID mappings."""
    return {
        'Patrick Mahomes': uuid4(),
        'Patrick Mahomes_QB': uuid4(),
        'Christian McCaffrey': uuid4(),
        'Christian McCaffrey_RB': uuid4(),
        'Justin Jefferson': uuid4(),
        'Justin Jefferson_WR': uuid4(),
    }
