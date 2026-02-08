"""
Pytest configuration and fixtures for testing.
"""
import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables before any tests run."""
    # Set dummy Supabase credentials for testing
    # In a real scenario, you'd use a test database
    os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_KEY"] = "test-key"
    os.environ["ENVIRONMENT"] = "test"

    # Clear any cached settings from src.config
    from src.config import get_settings, get_supabase_client

    get_settings.cache_clear()
    get_supabase_client.cache_clear()

    yield

    # Cleanup
    get_settings.cache_clear()
    get_supabase_client.cache_clear()
