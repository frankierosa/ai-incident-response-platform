from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument

# Define the embedding model name to be used for generating embeddings of the query and knowledge chunks.
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Define the KnowledgeSearchService class, which is responsible for searching the knowledge base for relevant documents based on a query. This service includes methods for generating embeddings of the query and retrieving the most relevant knowledge chunks from the database.
class KnowledgeSearchService:
    def __init__(self) -> None:
        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )

    # Define the search method, which takes a database session, a query string, and an optional top_k parameter to specify the number of relevant documents to retrieve. The method generates an embedding for the query, retrieves knowledge documents with embeddings from the database, and orders them by cosine distance to find the most relevant chunks.
    def search(
        self,
        db: Session,
        query: str,
        top_k: int = 3,
    ) -> list[KnowledgeDocument]:
        """Find the most relevant knowledge chunks for a query."""

        query_embedding = self.embedding_model.encode(
            query,
            normalize_embeddings=True,
        ).tolist()

        statement = (
            select(KnowledgeDocument)
            .where(KnowledgeDocument.embedding.is_not(None))
            .order_by(
                KnowledgeDocument.embedding.cosine_distance(
                    query_embedding
                )
            )
            .limit(top_k)
        )

        return list(db.scalars(statement).all())


knowledge_search_service = KnowledgeSearchService()