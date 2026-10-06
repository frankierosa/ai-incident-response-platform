from unittest.mock import patch

from app.ai.analyzer import IncidentAnalysis

# Test the analyze_incident endpoint
def test_analyze_incident(client):
    mock_analysis = IncidentAnalysis(
        summary="Payment service is returning HTTP 500 errors.",
        probable_cause=(
            "The payment service may be experiencing an application "
            "or dependency failure."
        ),
        impact=(
            "Customers may be unable to complete payment transactions."
        ),
        recommended_actions=[
            "Review payment service logs.",
            "Check recent deployments.",
            "Verify database connectivity.",
        ],
    )

    # Patch the analyze_incident function to return the mock analysis
    with patch(
        "app.services.incident_service.analyze_incident",
        return_value=mock_analysis,
    ):
        create_response = client.post(
            "/incidents",
            json={
                "title": "Payment service HTTP 500 errors",
                "severity": "HIGH",
                "status": "OPEN",
                "service": "payment-service",
                "description": (
                    "Customers are receiving HTTP 500 responses "
                    "when attempting to make payments."
                ),
            },
        )

        assert create_response.status_code == 201

        incident_id = create_response.json()["id"]

        response = client.post(
            f"/incidents/{incident_id}/analyze"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["summary"] == (
        "Payment service is returning HTTP 500 errors."
    )

    assert data["probable_cause"] == (
        "The payment service may be experiencing an application "
        "or dependency failure."
    )

    assert data["impact"] == (
        "Customers may be unable to complete payment transactions."
    )

    assert data["recommended_actions"] == [
        "Review payment service logs.",
        "Check recent deployments.",
        "Verify database connectivity.",
    ]
    