-- NFL Fantasy Football Projections Database Schema
-- Run this in your Supabase SQL editor to set up the database

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Players table
CREATE TABLE IF NOT EXISTS players (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  espn_id INTEGER UNIQUE,
  name TEXT NOT NULL,
  team TEXT,
  position TEXT NOT NULL,  -- QB, RB, WR, TE, K, DST
  status TEXT,             -- Active, Injured, etc.
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);
CREATE INDEX IF NOT EXISTS idx_players_team ON players(team);
CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);

-- Projections table
CREATE TABLE IF NOT EXISTS projections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID REFERENCES players(id) ON DELETE CASCADE,
  week INTEGER NOT NULL,
  season INTEGER NOT NULL,
  source TEXT NOT NULL,    -- 'espn', 'fantasypros', 'aggregate'

  -- Passing stats
  pass_att DECIMAL(6,2),
  pass_cmp DECIMAL(6,2),
  pass_yds DECIMAL(7,2),
  pass_tds DECIMAL(5,2),
  pass_ints DECIMAL(5,2),

  -- Rushing stats
  rush_att DECIMAL(6,2),
  rush_yds DECIMAL(7,2),
  rush_tds DECIMAL(5,2),

  -- Receiving stats
  receptions DECIMAL(6,2),
  rec_yds DECIMAL(7,2),
  rec_tds DECIMAL(5,2),
  targets DECIMAL(6,2),

  -- Other
  fumbles DECIMAL(5,2),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(player_id, week, season, source)
);

CREATE INDEX IF NOT EXISTS idx_projections_week_season ON projections(week, season);
CREATE INDEX IF NOT EXISTS idx_projections_player ON projections(player_id);
CREATE INDEX IF NOT EXISTS idx_projections_source ON projections(source);

-- Scoring configurations table
CREATE TABLE IF NOT EXISTS scoring_configs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,  -- 'PPR', 'Half-PPR', 'Standard', 'Ottoneu'

  -- Passing scoring
  pass_yds_per_point DECIMAL(6,2) DEFAULT 25,  -- yards per 1 point
  pass_td_points DECIMAL(4,2) DEFAULT 4,
  pass_int_points DECIMAL(4,2) DEFAULT -2,

  -- Rushing scoring
  rush_yds_per_point DECIMAL(6,2) DEFAULT 10,
  rush_td_points DECIMAL(4,2) DEFAULT 6,

  -- Receiving scoring
  rec_yds_per_point DECIMAL(6,2) DEFAULT 10,
  rec_td_points DECIMAL(4,2) DEFAULT 6,
  rec_points DECIMAL(4,2) DEFAULT 0,  -- PPR bonus (0, 0.5, or 1)

  -- Other
  fumble_points DECIMAL(4,2) DEFAULT -2,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_default BOOLEAN DEFAULT FALSE
);

-- Calculated points table (optional - can calculate on-the-fly instead)
CREATE TABLE IF NOT EXISTS calculated_points (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  projection_id UUID REFERENCES projections(id) ON DELETE CASCADE,
  scoring_config_id UUID REFERENCES scoring_configs(id) ON DELETE CASCADE,
  fantasy_points DECIMAL(6,2) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(projection_id, scoring_config_id)
);

CREATE INDEX IF NOT EXISTS idx_calculated_points_projection ON calculated_points(projection_id);
CREATE INDEX IF NOT EXISTS idx_calculated_points_config ON calculated_points(scoring_config_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to automatically update updated_at
CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projections_updated_at BEFORE UPDATE ON projections
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Job executions table for tracking scheduled job runs
CREATE TABLE IF NOT EXISTS job_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT NOT NULL,        -- 'weekly_import', 'manual_import', etc.
  status TEXT NOT NULL,         -- 'success', 'failed', 'error'
  executed_at TIMESTAMP WITH TIME ZONE NOT NULL,
  result JSONB,                 -- Job execution details (counts, errors, etc.)
  season INTEGER,               -- NFL season (optional)
  week INTEGER,                 -- NFL week (optional)
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_job_executions_job_id ON job_executions(job_id);
CREATE INDEX IF NOT EXISTS idx_job_executions_status ON job_executions(status);
CREATE INDEX IF NOT EXISTS idx_job_executions_executed_at ON job_executions(executed_at);
CREATE INDEX IF NOT EXISTS idx_job_executions_season_week ON job_executions(season, week);
