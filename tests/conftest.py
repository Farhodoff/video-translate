
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import os
import shutil

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    return client

@pytest.fixture(scope="session", autouse=True)
def cleanup_uploads():
    """Ensure uploads directory exists and cleanup after tests"""
    os.makedirs("uploads", exist_ok=True)
    yield
    # Optional: cleanup files created during tests
    # shutil.rmtree("uploads") 
    # Re-create mostly to not delete user data if running locally, 
    # but for pure test env it's good to clean. 
    # For now, let's just leave it or clean specific test artifacts if needed.
