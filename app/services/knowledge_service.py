
from datetime import datetime, timezone
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument

# Define the project root and the directory where runbooks are stored. Also, specify the embedding model name to be used for generating embeddings of the runbook content.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNBOOKS_DIR = PROJECT_ROOT / "data" / "runbooks"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Define the KnowledgeService class, which is responsible for managing and retrieving knowledge related to incidents. This service includes methods for ingesting runbooks, splitting their content into chunks, generating embeddings, and storing them in the database.
class KnowledgeService:
    # Initialize the KnowledgeService class, which sets up a text splitter for chunking runbook content and loads the embedding model for generating embeddings of the text chunks.
    def __init__(self) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )
        # Load the model once and reuse it.
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    
    # Define the ingest_runbooks method, which loads Markdown runbooks from the specified directory, splits their content into chunks, generates embeddings for each chunk, and stores them in the database. The method returns the number of inserted documents.
    def ingest_runbooks(self, db: Session) -> int:
        """Load Markdown runbooks, split them, and store their embeddings."""
        if not RUNBOOKS_DIR.exists():
            raise FileNotFoundError(
                f"Runbooks directory not found: {RUNBOOKS_DIR}"
            )

        files = sorted(RUNBOOKS_DIR.glob("*.md"))
        if not files:
            raise FileNotFoundError(
                f"No Markdown runbooks found in {RUNBOOKS_DIR}"
            )

        inserted_count = 0

        try:
            for file_path in files:
                content = file_path.read_text(encoding="utf-8").strip()
                if not content:
                    continue

                existing = db.scalars(
                    select(KnowledgeDocument).where(
                        KnowledgeDocument.source == str(file_path)
                    )
                ).all()

                for document in existing:
                    db.delete(document)

                chunks = self.text_splitter.split_text(content)

                if not chunks:
                    continue

                embeddings = self.embedding_model.encode(
                    chunks,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )

                for chunk_index, chunk in enumerate(chunks):
                    document = KnowledgeDocument(
                        title=file_path.stem.replace("-", " ").title(),
                        content=chunk,
                        source=str(file_path),
                        document_type="runbook",
                        chunk_index=chunk_index,
                        embedding=embeddings[chunk_index].tolist(),
                        created_at=datetime.now(timezone.utc).replace(
                            tzinfo=None
                        ),
                    )
                    db.add(document)
                    inserted_count += 1

            db.commit()
            return inserted_count

        except Exception:
            db.rollback()
            raise



    # Define the search_knowledge method, which takes a query string and searches for the most relevant knowledge chunks in the database based on their embeddings. The method returns a list of KnowledgeDocument instances that are most similar to the query. 
    def search_knowledge(
            self,
            db: Session,
            query: str,
            limit: int = 3,
            ) -> list[KnowledgeDocument]:
        
        """Find the most relevant knowledge chunks for a query."""
        
        query_embedding = self.embedding_model.encode(
            query,
            normalize_embeddings=True,
            show_progress_bar=False,
            ).tolist()
        
        distance = KnowledgeDocument.embedding.cosine_distance(
            query_embedding
            )
        
        statement = (
            select(KnowledgeDocument)
            .where(KnowledgeDocument.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
            )
        
        return list(db.scalars(statement).all())


knowledge_service = KnowledgeService()
