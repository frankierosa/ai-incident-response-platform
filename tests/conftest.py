import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Set up the test database URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure that the DATABASE_URL environment variable is set
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

# Create a test database URL by appending a test database name to the original DATABASE_URL 
TEST_DATABASE_URL = DATABASE_URL.rsplit("/", 1)[0] + "/test_incident_db"

# Create a test engine and sessionmaker for the test database
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
)

# Create a sessionmaker for the test database
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

# Create the test database if it doesn't exist
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    # Drop the test database tables after the tests are done
    #Base.metadata.drop_all(bind=test_engine)

# Override the get_db dependency to use the test database session
@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()