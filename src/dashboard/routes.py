"""
Dashboard routes for web UI.
"""
from typing import Optional
from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from supabase import Client

from src.config import get_supabase_client

router = APIRouter()
templates = Jinja2Templates(directory="src/dashboard/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    season: int = Query(default=2023, ge=1999, le=2030),
    week: int = Query(default=1, ge=1, le=18),
    scoring: str = Query(default="PPR (Point Per Reception)"),
    position: Optional[str] = Query(default=None),
    result_limit: int = Query(default=50, ge=1, le=200, alias="limit"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Main dashboard page showing projections.

    Args:
        request: FastAPI request object
        season: NFL season year
        week: Week number
        scoring: Scoring configuration name
        position: Optional position filter (QB, RB, WR, TE)
        limit: Number of results to display
        supabase: Supabase client

    Returns:
        HTML response with projections table
    """
    try:
        # Get scoring configurations for dropdown
        scoring_configs_response = supabase.table("scoring_configs").select("name").execute()
        scoring_options = [config["name"] for config in scoring_configs_response.data] if scoring_configs_response.data else ["PPR (Point Per Reception)", "Half-PPR", "Standard (No PPR)"]

        # Get projections from API logic (reuse existing API)
        from src.api.projections import get_projections

        projections = await get_projections(
            season=season,
            week=week,
            scoring=scoring,
            position=position,
            sort_by="fantasy_points",
            order="desc",
            limit=result_limit,
            supabase=supabase
        )

        # Convert to dict for template
        projections_data = [proj.model_dump() for proj in projections]

        return templates.TemplateResponse(
            "projections.html",
            {
                "request": request,
                "projections": projections_data,
                "season": season,
                "week": week,
                "scoring": scoring,
                "position": position or "ALL",
                "scoring_options": scoring_options,
                "positions": ["ALL", "QB", "RB", "WR", "TE"],
                "weeks": list(range(1, 19)),
                "seasons": list(range(2023, 2020, -1)),
            }
        )
    except HTTPException as e:
        # Handle API errors gracefully in the UI
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": str(e.detail),
                "error_code": e.status_code
            },
            status_code=e.status_code
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"An unexpected error occurred: {str(e)}",
                "error_code": 500
            },
            status_code=500
        )


@router.get("/player/{player_id}", response_class=HTMLResponse)
async def player_detail(
    request: Request,
    player_id: str,
    season: int = Query(default=2023, ge=1999, le=2030),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Player detail page showing stats and projections.

    Args:
        request: FastAPI request object
        player_id: UUID of the player
        season: NFL season year to display
        supabase: Supabase client

    Returns:
        HTML response with player details
    """
    try:
        # Get player info
        player_response = supabase.table("players").select("*").eq("id", player_id).execute()

        if not player_response.data:
            raise HTTPException(status_code=404, detail="Player not found")

        player = player_response.data[0]

        # Get all projections for this player in the season
        projections_response = supabase.table("projections").select(
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
            fumbles
            """
        ).eq("player_id", player_id).eq("season", season).order("week").execute()

        projections = projections_response.data if projections_response.data else []

        # Calculate fantasy points for each scoring format
        from src.scoring.calculator import ScoringCalculator
        from src.database.models import ScoringConfig, Projection
        from decimal import Decimal

        # Get scoring configs
        scoring_configs_response = supabase.table("scoring_configs").select("*").execute()
        scoring_configs = scoring_configs_response.data if scoring_configs_response.data else []

        # Calculate points for each projection and scoring format
        projections_with_points = []
        for proj_data in projections:
            proj_dict = {
                "week": proj_data["week"],
                "season": proj_data["season"],
                "source": proj_data["source"],
                "stats": proj_data,
                "fantasy_points": {}
            }

            # Create Projection model
            projection = Projection(
                id=proj_data["id"],
                player_id=player_id,
                week=proj_data["week"],
                season=proj_data["season"],
                source=proj_data["source"],
                pass_att=Decimal(str(proj_data["pass_att"])) if proj_data.get("pass_att") else None,
                pass_cmp=Decimal(str(proj_data["pass_cmp"])) if proj_data.get("pass_cmp") else None,
                pass_yds=Decimal(str(proj_data["pass_yds"])) if proj_data.get("pass_yds") else None,
                pass_tds=Decimal(str(proj_data["pass_tds"])) if proj_data.get("pass_tds") else None,
                pass_ints=Decimal(str(proj_data["pass_ints"])) if proj_data.get("pass_ints") else None,
                rush_att=Decimal(str(proj_data["rush_att"])) if proj_data.get("rush_att") else None,
                rush_yds=Decimal(str(proj_data["rush_yds"])) if proj_data.get("rush_yds") else None,
                rush_tds=Decimal(str(proj_data["rush_tds"])) if proj_data.get("rush_tds") else None,
                receptions=Decimal(str(proj_data["receptions"])) if proj_data.get("receptions") else None,
                rec_yds=Decimal(str(proj_data["rec_yds"])) if proj_data.get("rec_yds") else None,
                rec_tds=Decimal(str(proj_data["rec_tds"])) if proj_data.get("rec_tds") else None,
                targets=Decimal(str(proj_data["targets"])) if proj_data.get("targets") else None,
                fumbles=Decimal(str(proj_data["fumbles"])) if proj_data.get("fumbles") else None,
                created_at=proj_data.get("created_at"),
                updated_at=proj_data.get("updated_at")
            )

            # Calculate points for each scoring format
            for config_data in scoring_configs:
                config = ScoringConfig(**config_data)
                calculator = ScoringCalculator(config)
                points = calculator.calculate_points(projection)
                proj_dict["fantasy_points"][config.name] = float(points)

            projections_with_points.append(proj_dict)

        return templates.TemplateResponse(
            "player_detail.html",
            {
                "request": request,
                "player": player,
                "projections": projections_with_points,
                "season": season,
                "scoring_configs": [config["name"] for config in scoring_configs],
                "seasons": list(range(2023, 2020, -1)),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Failed to load player details: {str(e)}",
                "error_code": 500
            },
            status_code=500
        )
