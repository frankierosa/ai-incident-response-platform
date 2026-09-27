from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

# Define a test function that checks the health check endpoint of the FastAPI application. This function sends a GET request to the "/health" endpoint and asserts that the response status code is 200 (indicating success) and that the response JSON matches the expected output {"status": "ok"}.
def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}