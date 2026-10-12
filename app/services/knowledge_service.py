
from datetime import datetime, timezone
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNBOOKS_DIR = PROJECT_ROOT / "data" / "runbooks"

# This service is responsible for ingesting knowledge documents, specifically Markdown runbooks, 
# into the database. It reads the files from a specified directory, splits their content into manageable chunks, 
# and stores each chunk as a separate entry in the `knowledge_documents` table. 
# The service ensures that repeated ingestion of the same source file is idempotent by deleting any existing 
# entries for that source before adding new ones.
class KnowledgeService:
    def __init__(self) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )

    def ingest_runbooks(self, db: Session) -> int:
        """Load Markdown runbooks, split them, and store their chunks."""

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

                # Make repeated ingestion idempotent for each source file.
                existing = db.scalars(
                    select(KnowledgeDocument).where(
                        KnowledgeDocument.source == str(file_path)
                    )
                ).all()

                for document in existing:
                    db.delete(document)

                chunks = self.text_splitter.split_text(content)

                for chunk_index, chunk in enumerate(chunks):
                    document = KnowledgeDocument(
                        title=file_path.stem.replace("-", " ").title(),
                        content=chunk,
                        source=str(file_path),
                        document_type="runbook",
                        chunk_index=chunk_index,
                        embedding=None,
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


knowledge_service = KnowledgeService()