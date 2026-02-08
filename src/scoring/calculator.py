"""
Fantasy points calculator for NFL player projections.

Calculates fantasy points based on raw statistics and scoring configurations.
"""
from decimal import Decimal
from typing import Dict, Optional
import logging

from src.database.models import ScoringConfig, Projection

logger = logging.getLogger(__name__)


class ScoringCalculator:
    """
    Calculates fantasy points from player statistics using scoring configurations.
    """

    def __init__(self, scoring_config: ScoringConfig):
        """
        Initialize calculator with a scoring configuration.

        Args:
            scoring_config: ScoringConfig model with point values
        """
        self.config = scoring_config

    def calculate_points(self, projection: Projection) -> Decimal:
        """
        Calculate total fantasy points for a projection.

        Args:
            projection: Projection with raw stats

        Returns:
            Total fantasy points as Decimal
        """
        points = Decimal("0")

        # Passing points
        points += self._calculate_passing_points(projection)

        # Rushing points
        points += self._calculate_rushing_points(projection)

        # Receiving points
        points += self._calculate_receiving_points(projection)

        # Fumble points (negative)
        points += self._calculate_fumble_points(projection)

        return points.quantize(Decimal("0.01"))  # Round to 2 decimal places

    def calculate_points_from_stats(
        self,
        pass_yds: Optional[Decimal] = None,
        pass_tds: Optional[Decimal] = None,
        pass_ints: Optional[Decimal] = None,
        rush_yds: Optional[Decimal] = None,
        rush_tds: Optional[Decimal] = None,
        receptions: Optional[Decimal] = None,
        rec_yds: Optional[Decimal] = None,
        rec_tds: Optional[Decimal] = None,
        fumbles: Optional[Decimal] = None,
    ) -> Decimal:
        """
        Calculate fantasy points from individual stat values.

        Useful for quick calculations without a Projection model.

        Args:
            pass_yds: Passing yards
            pass_tds: Passing touchdowns
            pass_ints: Interceptions thrown
            rush_yds: Rushing yards
            rush_tds: Rushing touchdowns
            receptions: Number of receptions
            rec_yds: Receiving yards
            rec_tds: Receiving touchdowns
            fumbles: Fumbles lost

        Returns:
            Total fantasy points
        """
        points = Decimal("0")

        # Passing
        if pass_yds:
            points += pass_yds / self.config.pass_yds_per_point
        if pass_tds:
            points += pass_tds * self.config.pass_td_points
        if pass_ints:
            points += pass_ints * self.config.pass_int_points  # Negative

        # Rushing
        if rush_yds:
            points += rush_yds / self.config.rush_yds_per_point
        if rush_tds:
            points += rush_tds * self.config.rush_td_points

        # Receiving
        if receptions:
            points += receptions * self.config.rec_points  # PPR bonus
        if rec_yds:
            points += rec_yds / self.config.rec_yds_per_point
        if rec_tds:
            points += rec_tds * self.config.rec_td_points

        # Fumbles
        if fumbles:
            points += fumbles * self.config.fumble_points  # Negative

        return points.quantize(Decimal("0.01"))

    def calculate_breakdown(self, projection: Projection) -> Dict[str, Decimal]:
        """
        Calculate fantasy points with category breakdown.

        Args:
            projection: Projection with raw stats

        Returns:
            Dictionary with points by category:
            {
                'passing': Decimal,
                'rushing': Decimal,
                'receiving': Decimal,
                'fumbles': Decimal,
                'total': Decimal
            }
        """
        passing = self._calculate_passing_points(projection)
        rushing = self._calculate_rushing_points(projection)
        receiving = self._calculate_receiving_points(projection)
        fumbles = self._calculate_fumble_points(projection)

        return {
            'passing': passing.quantize(Decimal("0.01")),
            'rushing': rushing.quantize(Decimal("0.01")),
            'receiving': receiving.quantize(Decimal("0.01")),
            'fumbles': fumbles.quantize(Decimal("0.01")),
            'total': (passing + rushing + receiving + fumbles).quantize(Decimal("0.01"))
        }

    def _calculate_passing_points(self, projection: Projection) -> Decimal:
        """Calculate points from passing stats."""
        points = Decimal("0")

        if projection.pass_yds:
            points += projection.pass_yds / self.config.pass_yds_per_point

        if projection.pass_tds:
            points += projection.pass_tds * self.config.pass_td_points

        if projection.pass_ints:
            points += projection.pass_ints * self.config.pass_int_points

        return points

    def _calculate_rushing_points(self, projection: Projection) -> Decimal:
        """Calculate points from rushing stats."""
        points = Decimal("0")

        if projection.rush_yds:
            points += projection.rush_yds / self.config.rush_yds_per_point

        if projection.rush_tds:
            points += projection.rush_tds * self.config.rush_td_points

        return points

    def _calculate_receiving_points(self, projection: Projection) -> Decimal:
        """Calculate points from receiving stats."""
        points = Decimal("0")

        # PPR bonus
        if projection.receptions:
            points += projection.receptions * self.config.rec_points

        if projection.rec_yds:
            points += projection.rec_yds / self.config.rec_yds_per_point

        if projection.rec_tds:
            points += projection.rec_tds * self.config.rec_td_points

        return points

    def _calculate_fumble_points(self, projection: Projection) -> Decimal:
        """Calculate points from fumbles (typically negative)."""
        if projection.fumbles:
            return projection.fumbles * self.config.fumble_points
        return Decimal("0")


def get_standard_scoring_configs() -> Dict[str, Dict[str, Decimal]]:
    """
    Get standard fantasy scoring configurations.

    Returns:
        Dictionary of scoring config names to their point values
    """
    return {
        "PPR": {
            "name": "PPR (Point Per Reception)",
            "pass_yds_per_point": Decimal("25.0"),
            "pass_td_points": Decimal("4.0"),
            "pass_int_points": Decimal("-2.0"),
            "rush_yds_per_point": Decimal("10.0"),
            "rush_td_points": Decimal("6.0"),
            "rec_yds_per_point": Decimal("10.0"),
            "rec_td_points": Decimal("6.0"),
            "rec_points": Decimal("1.0"),  # 1 point per reception
            "fumble_points": Decimal("-2.0"),
            "is_default": True,
        },
        "Half-PPR": {
            "name": "Half-PPR",
            "pass_yds_per_point": Decimal("25.0"),
            "pass_td_points": Decimal("4.0"),
            "pass_int_points": Decimal("-2.0"),
            "rush_yds_per_point": Decimal("10.0"),
            "rush_td_points": Decimal("6.0"),
            "rec_yds_per_point": Decimal("10.0"),
            "rec_td_points": Decimal("6.0"),
            "rec_points": Decimal("0.5"),  # 0.5 points per reception
            "fumble_points": Decimal("-2.0"),
            "is_default": False,
        },
        "Standard": {
            "name": "Standard (No PPR)",
            "pass_yds_per_point": Decimal("25.0"),
            "pass_td_points": Decimal("4.0"),
            "pass_int_points": Decimal("-2.0"),
            "rush_yds_per_point": Decimal("10.0"),
            "rush_td_points": Decimal("6.0"),
            "rec_yds_per_point": Decimal("10.0"),
            "rec_td_points": Decimal("6.0"),
            "rec_points": Decimal("0.0"),  # No PPR
            "fumble_points": Decimal("-2.0"),
            "is_default": False,
        },
    }
