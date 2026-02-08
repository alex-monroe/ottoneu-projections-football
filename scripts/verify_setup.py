"""
Verification script to check if the project is set up correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def verify_environment():
    """Verify environment variables are set."""
    print("🔍 Checking environment variables...")
    try:
        from src.config import get_settings
        settings = get_settings()

        if settings.supabase_url == "your-project-url-here":
            print("  ⚠️  WARNING: Using placeholder Supabase URL")
            print("     Please update your .env file with real credentials")
            return False

        print(f"  ✓ Supabase URL: {settings.supabase_url}")
        print(f"  ✓ Environment: {settings.environment}")
        return True
    except Exception as e:
        print(f"  ✗ Error loading settings: {e}")
        print("  Make sure you have a .env file with SUPABASE_URL and SUPABASE_KEY")
        return False


def verify_dependencies():
    """Verify all required packages are installed."""
    print("\n🔍 Checking dependencies...")
    required_packages = [
        "fastapi",
        "uvicorn",
        "supabase",
        "pydantic",
        "pydantic_settings",
        "espn_api",
        "jinja2",
        "pytest"
    ]

    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} not installed")
            all_installed = False

    return all_installed


def verify_database_schema():
    """Check if database schema file exists."""
    print("\n🔍 Checking database schema...")
    schema_file = Path(__file__).parent.parent / "src" / "database" / "schema.sql"

    if schema_file.exists():
        print(f"  ✓ Schema file found: {schema_file}")
        print("  ℹ️  Remember to run this SQL in your Supabase SQL editor!")
        return True
    else:
        print(f"  ✗ Schema file not found: {schema_file}")
        return False


def verify_tests():
    """Run basic tests."""
    print("\n🔍 Running tests...")
    import subprocess

    try:
        result = subprocess.run(
            ["pytest", "tests/test_api.py", "-v"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("  ✓ All tests passed")
            return True
        else:
            print("  ✗ Some tests failed")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"  ✗ Error running tests: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("NFL Fantasy Football Projections - Setup Verification")
    print("=" * 60)

    checks = [
        ("Dependencies", verify_dependencies),
        ("Environment Variables", verify_environment),
        ("Database Schema", verify_database_schema),
        ("Tests", verify_tests),
    ]

    results = {}
    for name, check_func in checks:
        results[name] = check_func()

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Make sure you've run schema.sql in Supabase SQL editor")
        print("2. Run: python scripts/setup_db.py")
        print("3. Start the server: ./run.sh")
        print("4. Visit: http://localhost:8000/docs")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
