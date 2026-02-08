#!/bin/bash
# Quick start script for development server

# Activate virtual environment
source venv/bin/activate

# Run FastAPI development server
uvicorn src.main:app --reload --port 8000
