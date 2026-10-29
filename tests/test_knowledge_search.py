from app.models.knowledge_document import KnowledgeDocument
from app.services.knowledge_service import knowledge_service

# Define a test function to verify the functionality of the search_knowledge method in the KnowledgeService class. This test creates sample knowledge documents, adds them to the database, and then performs a search query to ensure that the most relevant document is returned based on the query's content.
def test_search_knowledge(client, db_session):
    documents = [
        KnowledgeDocument(
            title="Payment Service HTTP 500",
            content=(
                "Investigate HTTP 500 errors by checking application logs "
                "and database connectivity."
            ),
            source="test-payment-runbook.md",
            document_type="runbook",
            chunk_index=0,
            embedding=knowledge_service.embedding_model.encode(
                "Investigate HTTP 500 errors by checking application logs "
                "and database connectivity.",
                normalize_embeddings=True,
                show_progress_bar=False,
            ).tolist(),
        ),

        # Define a second KnowledgeDocument instance representing an unrelated runbook, which provides instructions for restarting a background worker. This document is also added to the database to test the search functionality of the KnowledgeService class.
        KnowledgeDocument(
            title="Unrelated Runbook",
            content="Instructions for restarting a background worker.",
            source="test-worker-runbook.md",
            document_type="runbook",
            chunk_index=0,
            embedding=knowledge_service.embedding_model.encode(
                "Instructions for restarting a background worker.",
                normalize_embeddings=True,
                show_progress_bar=False,
            ).tolist(),
        ),
    ]

    db_session.add_all(documents)
    db_session.commit()

    results = knowledge_service.search_knowledge(
        db_session,
        "Payment API is returning HTTP 500 errors",
        limit=1,
    )
    
    result = results[0]
    
    assert result.document.title == "Payment Service HTTP 500"
    assert 0.0 <= result.distance <= 2