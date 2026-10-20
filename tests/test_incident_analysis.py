from unittest.mock import patch
from app.models.knowledge_document import KnowledgeDocument
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

    # Patch the run_ai_analysis function to return the mock_analysis when called. This allows us to simulate the behavior of the AI analysis without actually invoking the AI service.
    with patch(
        "app.services.incident_service.run_ai_analysis",
        return_value=mock_analysis,
        ) as mock_run_ai_analysis:
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



# Test the analyze_incident endpoint when the AI service is unavailable
def test_analyze_incident_ai_service_unavailable(client):
    with patch(
        "app.services.incident_service.run_ai_analysis",
        side_effect=Exception("429: You have no credits remaining"),
    ):
         
        mock_knowledge = KnowledgeDocument(
            title="Payment Service Runbook",
            content=(
                "For HTTP 500 errors, review application logs, "
                "recent deployments, and database connectivity."
            ),
            source="payment-service.md",
            document_type="runbook",
            chunk_index=0,
        )
        
        with patch(
            "app.services.incident_service.knowledge_service.search_knowledge",
            return_value=[mock_knowledge],
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

    assert response.status_code == 503

    data = response.json()

    assert data["detail"]["code"] == "AI_SERVICE_UNAVAILABLE"

    assert data["detail"]["message"] == (
    "AI analysis is temporarily unavailable. "
    "Please try again later. "
    "Please contact your system administrator if the issue persists."
)


    
# Test that the knowledge context is passed to the AI analysis function
def test_analyze_incident_passes_knowledge_to_ai(client):
    mock_analysis = IncidentAnalysis(
        summary="Payment service is returning HTTP 500 errors.",
        probable_cause="Database connectivity may be contributing to the failure.",
        impact="Customers may be unable to complete payment transactions.",
        recommended_actions=[
            "Review database connectivity.",
            "Review payment service logs.",
        ],
    )

    # Patch the knowledge_service.search_knowledge function to return a mock knowledge document when called. This allows us to simulate the behavior of the knowledge search without actually querying the knowledge base.
    mock_knowledge = KnowledgeDocument(
                id=1,
                title="Payment Service Runbook",
                content=(
                    "For HTTP 500 errors, review application logs, "
                    "recent deployments, and database connectivity."
                ),
                source="payment-service.md",
                document_type="runbook",
                chunk_index=0,
            )

    with patch(
        "app.services.incident_service.knowledge_service.search_knowledge",
        return_value=[mock_knowledge],
    ), patch(
        "app.services.incident_service.run_ai_analysis",
        return_value=mock_analysis,
    ) as mock_run_ai_analysis:

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

    mock_run_ai_analysis.assert_called_once()

    call_args = mock_run_ai_analysis.call_args

    assert call_args.kwargs["knowledge_context"] == [
        mock_knowledge.content
    ]