"""
Tests for scoring calculator.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from src.scoring.calculator import ScoringCalculator, get_standard_scoring_configs
from src.database.models import ScoringConfig, Projection


@pytest.fixture
def ppr_config():
    """Create a PPR scoring configuration."""
    return ScoringConfig(
        id=uuid4(),
        name="PPR",
        pass_yds_per_point=Decimal("25"),
        pass_td_points=Decimal("4"),
        pass_int_points=Decimal("-2"),
        rush_yds_per_point=Decimal("10"),
        rush_td_points=Decimal("6"),
        rec_yds_per_point=Decimal("10"),
        rec_td_points=Decimal("6"),
        rec_points=Decimal("1"),  # PPR
        fumble_points=Decimal("-2"),
        is_default=True,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def standard_config():
    """Create a Standard (non-PPR) scoring configuration."""
    return ScoringConfig(
        id=uuid4(),
        name="Standard",
        pass_yds_per_point=Decimal("25"),
        pass_td_points=Decimal("4"),
        pass_int_points=Decimal("-2"),
        rush_yds_per_point=Decimal("10"),
        rush_td_points=Decimal("6"),
        rec_yds_per_point=Decimal("10"),
        rec_td_points=Decimal("6"),
        rec_points=Decimal("0"),  # No PPR
        fumble_points=Decimal("-2"),
        is_default=False,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def qb_projection():
    """Create a QB projection."""
    return Projection(
        id=uuid4(),
        player_id=uuid4(),
        week=1,
        season=2023,
        source="nflverse",
        pass_yds=Decimal("300"),
        pass_tds=Decimal("3"),
        pass_ints=Decimal("1"),
        rush_yds=Decimal("20"),
        rush_tds=Decimal("0"),
        receptions=None,
        rec_yds=None,
        rec_tds=None,
        fumbles=Decimal("0"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def rb_projection():
    """Create an RB projection."""
    return Projection(
        id=uuid4(),
        player_id=uuid4(),
        week=1,
        season=2023,
        source="nflverse",
        pass_yds=None,
        pass_tds=None,
        pass_ints=None,
        rush_yds=Decimal("100"),
        rush_tds=Decimal("1"),
        receptions=Decimal("5"),
        rec_yds=Decimal("50"),
        rec_tds=Decimal("0"),
        fumbles=Decimal("1"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def wr_projection():
    """Create a WR projection."""
    return Projection(
        id=uuid4(),
        player_id=uuid4(),
        week=1,
        season=2023,
        source="nflverse",
        pass_yds=None,
        pass_tds=None,
        pass_ints=None,
        rush_yds=Decimal("10"),
        rush_tds=Decimal("0"),
        receptions=Decimal("8"),
        rec_yds=Decimal("120"),
        rec_tds=Decimal("1"),
        fumbles=Decimal("0"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def test_calculate_qb_points_ppr(ppr_config, qb_projection):
    """Test QB fantasy points calculation with PPR scoring."""
    calculator = ScoringCalculator(ppr_config)

    points = calculator.calculate_points(qb_projection)

    # 300 yards / 25 = 12
    # 3 TDs * 4 = 12
    # 1 INT * -2 = -2
    # 20 rush yards / 10 = 2
    # Total = 24.00
    assert points == Decimal("24.00")


def test_calculate_rb_points_ppr(ppr_config, rb_projection):
    """Test RB fantasy points calculation with PPR scoring."""
    calculator = ScoringCalculator(ppr_config)

    points = calculator.calculate_points(rb_projection)

    # 100 rush yards / 10 = 10
    # 1 rush TD * 6 = 6
    # 5 receptions * 1 (PPR) = 5
    # 50 rec yards / 10 = 5
    # 1 fumble * -2 = -2
    # Total = 24.00
    assert points == Decimal("24.00")


def test_calculate_rb_points_standard(standard_config, rb_projection):
    """Test RB fantasy points calculation with Standard (non-PPR) scoring."""
    calculator = ScoringCalculator(standard_config)

    points = calculator.calculate_points(rb_projection)

    # 100 rush yards / 10 = 10
    # 1 rush TD * 6 = 6
    # 5 receptions * 0 (no PPR) = 0
    # 50 rec yards / 10 = 5
    # 1 fumble * -2 = -2
    # Total = 19.00
    assert points == Decimal("19.00")


def test_calculate_wr_points_ppr(ppr_config, wr_projection):
    """Test WR fantasy points calculation with PPR scoring."""
    calculator = ScoringCalculator(ppr_config)

    points = calculator.calculate_points(wr_projection)

    # 10 rush yards / 10 = 1
    # 8 receptions * 1 (PPR) = 8
    # 120 rec yards / 10 = 12
    # 1 rec TD * 6 = 6
    # Total = 27.00
    assert points == Decimal("27.00")


def test_calculate_points_from_stats(ppr_config):
    """Test calculating points directly from stat values."""
    calculator = ScoringCalculator(ppr_config)

    points = calculator.calculate_points_from_stats(
        pass_yds=Decimal("250"),
        pass_tds=Decimal("2"),
        rush_yds=Decimal("30"),
        receptions=Decimal("6"),
        rec_yds=Decimal("80"),
    )

    # 250 / 25 = 10
    # 2 * 4 = 8
    # 30 / 10 = 3
    # 6 * 1 = 6 (PPR)
    # 80 / 10 = 8
    # Total = 35.00
    assert points == Decimal("35.00")


def test_calculate_breakdown(ppr_config, rb_projection):
    """Test calculating points with category breakdown."""
    calculator = ScoringCalculator(ppr_config)

    breakdown = calculator.calculate_breakdown(rb_projection)

    assert breakdown["passing"] == Decimal("0.00")
    assert breakdown["rushing"] == Decimal("16.00")  # 100/10 + 1*6
    assert breakdown["receiving"] == Decimal("10.00")  # 5*1 + 50/10
    assert breakdown["fumbles"] == Decimal("-2.00")  # 1*-2
    assert breakdown["total"] == Decimal("24.00")


def test_get_standard_scoring_configs():
    """Test getting standard scoring configurations."""
    configs = get_standard_scoring_configs()

    assert "PPR" in configs
    assert "Half-PPR" in configs
    assert "Standard" in configs

    # Check PPR config
    ppr = configs["PPR"]
    assert ppr["rec_points"] == Decimal("1.0")

    # Check Half-PPR config
    half_ppr = configs["Half-PPR"]
    assert half_ppr["rec_points"] == Decimal("0.5")

    # Check Standard config
    standard = configs["Standard"]
    assert standard["rec_points"] == Decimal("0.0")


def test_calculator_with_none_values(ppr_config):
    """Test calculator handles None values gracefully."""
    projection = Projection(
        id=uuid4(),
        player_id=uuid4(),
        week=1,
        season=2023,
        source="nflverse",
        pass_yds=None,
        pass_tds=None,
        pass_ints=None,
        rush_yds=Decimal("50"),
        rush_tds=None,
        receptions=None,
        rec_yds=None,
        rec_tds=None,
        fumbles=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    calculator = ScoringCalculator(ppr_config)
    points = calculator.calculate_points(projection)

    # Only 50 rush yards / 10 = 5.00
    assert points == Decimal("5.00")


def test_calculator_with_zero_points(ppr_config):
    """Test calculator with projection that scores zero points."""
    projection = Projection(
        id=uuid4(),
        player_id=uuid4(),
        week=1,
        season=2023,
        source="nflverse",
        pass_yds=Decimal("0"),
        pass_tds=Decimal("0"),
        pass_ints=Decimal("0"),
        rush_yds=Decimal("0"),
        rush_tds=Decimal("0"),
        receptions=Decimal("0"),
        rec_yds=Decimal("0"),
        rec_tds=Decimal("0"),
        fumbles=Decimal("0"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    calculator = ScoringCalculator(ppr_config)
    points = calculator.calculate_points(projection)

    assert points == Decimal("0.00")


def test_negative_points_from_turnovers(ppr_config):
    """Test that interceptions and fumbles result in negative points."""
    projection = Projection(
        id=uuid4(),
        player_id=uuid4(),
        week=1,
        season=2023,
        source="nflverse",
        pass_yds=Decimal("100"),  # 4 points
        pass_tds=Decimal("0"),
        pass_ints=Decimal("3"),  # -6 points
        rush_yds=None,
        rush_tds=None,
        receptions=None,
        rec_yds=None,
        rec_tds=None,
        fumbles=Decimal("2"),  # -4 points
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    calculator = ScoringCalculator(ppr_config)
    points = calculator.calculate_points(projection)

    # 100/25 + 0 + 3*-2 + 2*-2 = 4 - 6 - 4 = -6.00
    assert points == Decimal("-6.00")
