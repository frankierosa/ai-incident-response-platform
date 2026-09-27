from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# Test cases for the /incidents endpoint
def test_create_incident():
    response = client.post(
        "/incidents",
        json={
            "title": "Database connection failure",
            "severity": "CRITICAL",
            "status": "OPEN",
            "service": "payment-service",
            "description": "Payment service cannot connect to database",
        },
    )
    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Database connection failure"
    assert data["severity"] == "CRITICAL"
    assert data["status"] == "OPEN"
    assert data["service"] == "payment-service"
    assert data["description"] == (
        "Payment service cannot connect to database"
    )

    assert "id" in data
    assert "created_at" in data


# Test cases for the /incidents/{id} endpoint
def test_get_incidents():
    response = client.get("/incidents")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# Test cases for getting an incident by ID
def test_get_incident_by_id():
    create_response = client.post(
        "/incidents",
        json={
            "title": "API timeout",
            "severity": "HIGH",
            "status": "OPEN",
            "service": "order-service",
            "description": "Order API is timing out",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    response = client.get(f"/incidents/{incident_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == incident_id
    assert data["title"] == "API timeout"


# Test cases for getting a nonexistent incident
def test_get_nonexistent_incident():
    response = client.get("/incidents/999999")

    assert response.status_code == 404