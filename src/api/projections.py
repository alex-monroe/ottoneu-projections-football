"""
API endpoints for fantasy projections with calculated points.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from decimal import Decimal
import logging

from src.config import get_supabase_client
from src.database.models import PlayerProjection
from src.scoring.calculator import ScoringCalculator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["projections"])


@router.get("/projections", response_model=List[PlayerProjection])
async def get_projections(
    season: int = Query(..., ge=1999, le=2030, description="NFL season year"),
    week: int = Query(..., ge=1, le=18, description="Week number"),
    scoring: str = Query(default="PPR", description="Scoring configuration name"),
    position: Optional[str] = Query(
        default=None, description="Filter by position (QB, RB, WR, TE)"
    ),
    team: Optional[str] = Query(default=None, description="Filter by team"),
    min_points: Optional[float] = Query(
        default=None, description="Minimum fantasy points"
    ),
    sort_by: str = Query(
        default="fantasy_points", description="Sort field (fantasy_points, player_name)"
    ),
    order: str = Query(default="desc", description="Sort order (asc, desc)"),
    limit: int = Query(default=50, ge=1, le=500, description="Number of results"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Get fantasy projections with calculated points.

    Args:
        season: NFL season year
        week: Week number
        scoring: Scoring configuration name (PPR, Half-PPR, Standard)
        position: Optional position filter
        team: Optional team filter
        min_points: Optional minimum fantasy points threshold
        sort_by: Field to sort by
        order: Sort order (asc/desc)
        limit: Number of results to return
        offset: Offset for pagination

    Returns:
        List of PlayerProjection objects with calculated fantasy points

    Raises:
        HTTPException: If scoring config not found or query fails
    """
    try:
        # Get scoring configuration
        scoring_response = (
            supabase.table("scoring_configs").select("*").eq("name", scoring).execute()
        )

        if not scoring_response.data or len(scoring_response.data) == 0:
            raise HTTPException(
                status_code=404, detail=f"Scoring configuration '{scoring}' not found"
            )

        scoring_config_data = scoring_response.data[0]

        # Build query for projections with player data
        query = (
            supabase.table("projections")
            .select(
                """
            id,
            week,
            season,
            source,
            pass_att,
            pass_cmp,
            pass_yds,
            pass_tds,
            pass_ints,
            rush_att,
            rush_yds,
            rush_tds,
            receptions,
            rec_yds,
            rec_tds,
            targets,
            fumbles,
            player_id,
            created_at,
            updated_at,
            players(id, name, team, position)
            """
            )
            .eq("season", season)
            .eq("week", week)
        )

        # Apply filters
        if position:
            # Can't filter on joined table directly, will filter after
            pass

        if team:
            # Can't filter on joined table directly, will filter after
            pass

        # Execute query
        response = query.execute()

        if not response.data:
            return []

        # Calculate fantasy points and build results
        from src.database.models import ScoringConfig, Projection

        # Create scoring config model
        scoring_config = ScoringConfig(**scoring_config_data)
        calculator = ScoringCalculator(scoring_config)

        projections_list = []

        for row in response.data:
            # Get player data
            player_data = row.get("players")
            if not player_data:
                continue

            # Apply position filter
            if position and player_data.get("position") != position:
                continue

            # Apply team filter
            if team and player_data.get("team") != team:
                continue

            # Create Projection model for calculation
            projection = Projection(
                id=row["id"],
                player_id=row["player_id"],
                week=row["week"],
                season=row["season"],
                source=row["source"],
                pass_att=Decimal(str(row["pass_att"])) if row.get("pass_att") else None,
                pass_cmp=Decimal(str(row["pass_cmp"])) if row.get("pass_cmp") else None,
                pass_yds=Decimal(str(row["pass_yds"])) if row.get("pass_yds") else None,
                pass_tds=Decimal(str(row["pass_tds"])) if row.get("pass_tds") else None,
                pass_ints=Decimal(str(row["pass_ints"]))
                if row.get("pass_ints")
                else None,
                rush_att=Decimal(str(row["rush_att"])) if row.get("rush_att") else None,
                rush_yds=Decimal(str(row["rush_yds"])) if row.get("rush_yds") else None,
                rush_tds=Decimal(str(row["rush_tds"])) if row.get("rush_tds") else None,
                receptions=Decimal(str(row["receptions"]))
                if row.get("receptions")
                else None,
                rec_yds=Decimal(str(row["rec_yds"])) if row.get("rec_yds") else None,
                rec_tds=Decimal(str(row["rec_tds"])) if row.get("rec_tds") else None,
                targets=Decimal(str(row["targets"])) if row.get("targets") else None,
                fumbles=Decimal(str(row["fumbles"])) if row.get("fumbles") else None,
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at"),
            )

            # Calculate fantasy points
            fantasy_points = calculator.calculate_points(projection)

            # Apply minimum points filter
            if min_points and float(fantasy_points) < min_points:
                continue

            # Build PlayerProjection
            player_projection = PlayerProjection(
                player_id=row["player_id"],
                player_name=player_data["name"],
                team=player_data.get("team"),
                position=player_data["position"],
                week=row["week"],
                season=row["season"],
                source=row["source"],
                fantasy_points=fantasy_points,
                pass_yds=projection.pass_yds,
                pass_tds=projection.pass_tds,
                rush_yds=projection.rush_yds,
                rush_tds=projection.rush_tds,
                receptions=projection.receptions,
                rec_yds=projection.rec_yds,
                rec_tds=projection.rec_tds,
            )

            projections_list.append(player_projection)

        # Sort results
        if sort_by == "fantasy_points":
            reverse = order == "desc"
            projections_list.sort(
                key=lambda x: float(x.fantasy_points), reverse=reverse
            )
        elif sort_by == "player_name":
            reverse = order == "desc"
            projections_list.sort(key=lambda x: x.player_name, reverse=reverse)

        # Apply pagination
        start = offset
        end = offset + limit
        paginated = projections_list[start:end]

        logger.info(
            f"Returning {len(paginated)} projections for {season} week {week} "
            f"(total: {len(projections_list)}, scoring: {scoring})"
        )

        return paginated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting projections: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve projections: {str(e)}"
        )


@router.get("/projections/top/{position}")
async def get_top_players_by_position(
    position: str,
    season: int = Query(..., ge=1999, le=2030),
    week: int = Query(..., ge=1, le=18),
    scoring: str = Query(default="PPR"),
    limit: int = Query(default=20, ge=1, le=100),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Get top players by position for a given week.

    Args:
        position: Position (QB, RB, WR, TE)
        season: NFL season year
        week: Week number
        scoring: Scoring configuration
        limit: Number of top players to return

    Returns:
        List of top players at the position
    """
    # Reuse the main endpoint with position filter
    return await get_projections(
        season=season,
        week=week,
        scoring=scoring,
        position=position.upper(),
        sort_by="fantasy_points",
        order="desc",
        limit=limit,
        supabase=supabase,
    )
