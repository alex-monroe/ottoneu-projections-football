"""
Pydantic models for API request/response validation.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PlayerBase(BaseModel):
    """Base player model."""

    name: str
    team: Optional[str] = None
    position: str  # QB, RB, WR, TE, K, DST
    status: Optional[str] = None


class PlayerCreate(PlayerBase):
    """Model for creating a new player."""

    espn_id: Optional[int] = None


class Player(PlayerBase):
    """Full player model with database fields."""

    id: UUID
    espn_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectionBase(BaseModel):
    """Base projection model."""

    week: int = Field(..., ge=1, le=18)
    season: int = Field(..., ge=2020, le=2030)
    source: str = "espn"

    # Passing stats
    pass_att: Optional[Decimal] = None
    pass_cmp: Optional[Decimal] = None
    pass_yds: Optional[Decimal] = None
    pass_tds: Optional[Decimal] = None
    pass_ints: Optional[Decimal] = None

    # Rushing stats
    rush_att: Optional[Decimal] = None
    rush_yds: Optional[Decimal] = None
    rush_tds: Optional[Decimal] = None

    # Receiving stats
    receptions: Optional[Decimal] = None
    rec_yds: Optional[Decimal] = None
    rec_tds: Optional[Decimal] = None
    targets: Optional[Decimal] = None

    # Other
    fumbles: Optional[Decimal] = None


class ProjectionCreate(ProjectionBase):
    """Model for creating a new projection."""

    player_id: UUID


class Projection(ProjectionBase):
    """Full projection model with database fields."""

    id: UUID
    player_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectionWithPlayer(Projection):
    """Projection with nested player data."""

    player: Player


class ScoringConfigBase(BaseModel):
    """Base scoring configuration model."""

    name: str

    # Passing scoring
    pass_yds_per_point: Decimal = Decimal("25.0")
    pass_td_points: Decimal = Decimal("4.0")
    pass_int_points: Decimal = Decimal("-2.0")

    # Rushing scoring
    rush_yds_per_point: Decimal = Decimal("10.0")
    rush_td_points: Decimal = Decimal("6.0")

    # Receiving scoring
    rec_yds_per_point: Decimal = Decimal("10.0")
    rec_td_points: Decimal = Decimal("6.0")
    rec_points: Decimal = Decimal("0.0")  # PPR bonus

    # Other
    fumble_points: Decimal = Decimal("-2.0")

    is_default: bool = False


class ScoringConfigCreate(ScoringConfigBase):
    """Model for creating a new scoring configuration."""

    pass


class ScoringConfig(ScoringConfigBase):
    """Full scoring configuration model with database fields."""

    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class PlayerProjection(BaseModel):
    """Combined model with player, projection, and calculated points."""

    player_id: UUID
    player_name: str
    team: Optional[str] = None
    position: str
    week: int
    season: int
    source: str
    fantasy_points: Decimal

    # Include raw stats for reference
    pass_yds: Optional[Decimal] = None
    pass_tds: Optional[Decimal] = None
    rush_yds: Optional[Decimal] = None
    rush_tds: Optional[Decimal] = None
    receptions: Optional[Decimal] = None
    rec_yds: Optional[Decimal] = None
    rec_tds: Optional[Decimal] = None


class HealthCheck(BaseModel):
    """Health check response model."""

    status: str
    environment: str
    timestamp: datetime


class ImportRequest(BaseModel):
    """Request model for importing data."""

    year: int = Field(..., ge=1999, le=2030, description="NFL season year")
    week: int = Field(..., ge=1, le=18, description="Week number")
    source: str = Field(default="nflverse", description="Data source name")


class ImportResultModel(BaseModel):
    """Result of a data import operation."""

    success: bool
    players_imported: int
    players_updated: int
    projections_imported: int
    projections_updated: int
    source: str
    year: int
    week: int
    errors: list[str]
    timestamp: datetime


class DataSourceInfo(BaseModel):
    """Information about a data source."""

    name: str
    status: str  # 'available' or 'unavailable'
    description: str


class JobExecutionBase(BaseModel):
    """Base job execution model."""

    job_id: str
    status: str  # 'success', 'failed', 'error'
    executed_at: datetime
    result: Optional[dict] = None
    season: Optional[int] = None
    week: Optional[int] = None


class JobExecution(JobExecutionBase):
    """Full job execution model with database fields."""

    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class JobStatus(BaseModel):
    """Status of a scheduled job."""

    job_id: str
    name: str
    next_run: Optional[datetime] = None
    trigger: str
    last_execution: Optional[JobExecution] = None


class JobTriggerRequest(BaseModel):
    """Request to manually trigger a job."""

    year: int = Field(..., ge=1999, le=2030)
    week: int = Field(..., ge=1, le=18)
    source: str = Field(default="nflverse")
