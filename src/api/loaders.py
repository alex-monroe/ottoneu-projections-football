"""
API endpoints for data loading operations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
import logging

from src.config import get_supabase_client
from src.database.models import ImportRequest, ImportResultModel, DataSourceInfo
from src.loaders.service import LoaderService
from src.loaders.exceptions import DataNotAvailableError, LoaderError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["loaders"])


def get_loader_service(
    supabase: Client = Depends(get_supabase_client)
) -> LoaderService:
    """Dependency for getting loader service."""
    return LoaderService(supabase)


@router.post("/loaders/import/weekly", response_model=ImportResultModel)
async def import_weekly_data(
    request: ImportRequest,
    service: LoaderService = Depends(get_loader_service)
):
    """
    Import weekly player data from a data source.

    Args:
        request: Import request with year, week, and source

    Returns:
        Import result with statistics

    Raises:
        HTTPException: If import fails
    """
    try:
        logger.info(f"Importing {request.source} data for {request.year} week {request.week}")

        result = service.import_weekly_data(
            year=request.year,
            week=request.week,
            source=request.source,
            use_fallback=True
        )

        if not result.success:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Import failed",
                    "errors": result.errors
                }
            )

        return ImportResultModel(**result.to_dict())

    except DataNotAvailableError as e:
        logger.warning(f"Data not available: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Data not available: {str(e)}"
        )
    except LoaderError as e:
        logger.error(f"Loader error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Loader error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during import: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/loaders/import/season", response_model=List[ImportResultModel])
async def import_season_data(
    year: int = Query(..., ge=1999, le=2030, description="NFL season year"),
    source: str = Query(default="nflverse", description="Data source name"),
    start_week: int = Query(default=1, ge=1, le=18, description="Starting week"),
    end_week: int = Query(default=18, ge=1, le=18, description="Ending week"),
    service: LoaderService = Depends(get_loader_service)
):
    """
    Import multiple weeks of data for a season.

    Args:
        year: NFL season year
        source: Data source name
        start_week: First week to import (default: 1)
        end_week: Last week to import (default: 18)

    Returns:
        List of import results for each week

    Raises:
        HTTPException: If validation fails
    """
    if start_week > end_week:
        raise HTTPException(
            status_code=400,
            detail="start_week must be less than or equal to end_week"
        )

    results = []
    for week in range(start_week, end_week + 1):
        try:
            logger.info(f"Importing week {week} of {year}")

            result = service.import_weekly_data(
                year=year,
                week=week,
                source=source,
                use_fallback=True
            )

            results.append(ImportResultModel(**result.to_dict()))

            # Continue even if one week fails
            if not result.success:
                logger.warning(f"Week {week} import failed: {result.errors}")

        except Exception as e:
            logger.error(f"Error importing week {week}: {str(e)}")
            # Create a failed result for this week
            from datetime import datetime
            failed_result = ImportResultModel(
                success=False,
                players_imported=0,
                players_updated=0,
                projections_imported=0,
                projections_updated=0,
                source=source,
                year=year,
                week=week,
                errors=[str(e)],
                timestamp=datetime.utcnow()
            )
            results.append(failed_result)

    return results


@router.get("/loaders/sources", response_model=List[DataSourceInfo])
async def get_data_sources(
    service: LoaderService = Depends(get_loader_service)
):
    """
    Get list of available data sources.

    Returns:
        List of data source information
    """
    try:
        sources = service.get_available_sources()
        return [DataSourceInfo(**source) for source in sources]
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve data sources: {str(e)}"
        )


@router.get("/loaders/available-data")
async def get_available_data(
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get summary of what data exists in the database.

    Returns:
        Summary of available data by year/week/source
    """
    try:
        # Query distinct year/week/source combinations
        response = supabase.table("projections").select(
            "season,week,source"
        ).execute()

        if not response.data:
            return {
                "total_weeks": 0,
                "seasons": [],
                "sources": []
            }

        # Organize data
        data_map = {}
        sources = set()

        for row in response.data:
            season = row["season"]
            week = row["week"]
            source = row["source"]

            sources.add(source)

            if season not in data_map:
                data_map[season] = {}

            if week not in data_map[season]:
                data_map[season][week] = []

            if source not in data_map[season][week]:
                data_map[season][week].append(source)

        # Format response
        seasons = []
        for season in sorted(data_map.keys()):
            weeks = []
            for week in sorted(data_map[season].keys()):
                weeks.append({
                    "week": week,
                    "sources": data_map[season][week]
                })

            seasons.append({
                "season": season,
                "weeks": weeks,
                "week_count": len(weeks)
            })

        return {
            "total_weeks": sum(s["week_count"] for s in seasons),
            "seasons": seasons,
            "sources": sorted(list(sources))
        }

    except Exception as e:
        logger.error(f"Error getting available data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve available data: {str(e)}"
        )
