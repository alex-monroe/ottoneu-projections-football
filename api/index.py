"""
Vercel serverless entry point.

NOTE: Vercel is NOT recommended for this FastAPI app.
See DEPLOYMENT.md for better alternatives (Render, Railway, Fly.io).

This file exists for users who still want to try Vercel deployment.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mangum import Mangum
    from src.main import app

    # Wrap FastAPI app for serverless with Mangum
    handler = Mangum(app, lifespan="off")

except ImportError as e:
    print(f"Error: {e}")
    print("Make sure to install: pip install mangum")
    raise
