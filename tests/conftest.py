import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db

# Define the TEST_DATABASE_URL environment variable, which specifies the connection URL for the test database. If the environment variable is not set, it defaults to a PostgreSQL database running locally with the specified credentials and database name.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://sadmin:sadmin@localhost:5432/test_incident_db",
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

# Define a pytest fixture that sets up the test database before running tests and tears it down afterward. This fixture creates all tables defined in the SQLAlchemy models before yielding control to the tests, and drops all tables after the tests have completed.
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)

# Define a pytest fixture that provides a TestClient instance for testing the FastAPI application. This fixture overrides the get_db dependency to use the test database session, allowing tests to interact with the application using the test database.
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