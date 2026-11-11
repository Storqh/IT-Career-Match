"""Pytest configuration and fixtures."""
import sys
from pathlib import Path
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="session")
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def student_session(client):
    """Create session for regular student user."""
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["user_role"] = "student"
    return client


@pytest.fixture
def admin_session(client):
    """Create session for admin user."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_role"] = "admin"
    return client


@pytest.fixture
def app_context(app):
    """Provide app context."""
    with app.app_context():
        yield