# AI Production Incident Response Platform
## Development Guide

## 1. Purpose

This document describes the development environment, application configuration, local execution, database setup, automated testing, Docker workflow, CI/CD, and contribution practices for the AI Production Incident Response Platform.

The GitHub repository is the source of truth for application code:

https://github.com/frankierosa/ai-incident-response-platform

## 2. Technology Requirements

| Component | Technology |
|---|---|
| Programming language | Python 3.12 |
| API framework | FastAPI |
| Data validation | Pydantic |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Vector extension | pgvector |
| Embedding model | Sentence Transformers |
| AI integration | LangChain and OpenAI |
| Testing framework | pytest |
| Containerization | Docker |
| Local orchestration | Docker Compose |
| Source control | Git and GitHub |
| CI/CD | GitHub Actions |

Python 3.12 is recommended to match the project's Docker image and CI environment.

### Prerequisites

Install the following tools before starting:

- Git.
- Python 3.12.
- PostgreSQL with pgvector support, if running without Docker.
- Docker Desktop or Docker Engine with Docker Compose, if using containers.
- An OpenAI API key for live AI analysis.

## 3. Repository Structure

The main application structure is:

```text
ai-incident-response-platform/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── publish.yml
│
├── app/
│   ├── ai/
│   │   └── analyzer.py
│   ├── api/
│   │   └── routes/
│   │       └── incidents.py
│   ├── core/
│   │   ├── database.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── incident.py
│   │   ├── incident_analysis.py
│   │   └── knowledge_document.py
│   ├── schemas/
│   │   └── incident.py
│   ├── services/
│   │   ├── incident_service.py
│   │   ├── knowledge_search_service.py
│   │   └── knowledge_service.py
│   ├── init_db.py
│   └── main.py
│
├── data/
│   └── runbooks/
│
├── docker/
│   └── postgres-init/
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_incidents.py
│   ├── test_incident_analysis.py
│   └── test_knowledge_search.py
│
├── docs/
│   ├── PROJECT_GUIDE.md
│   └── DEVELOPMENT.md
│
├── .env.example
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── LICENSE
└── README.md
```

## 4. Clone the Repository

Clone the repository:

```bash
git clone https://github.com/frankierosa/ai-incident-response-platform.git
```

Move into the project directory:

```bash
cd ai-incident-response-platform
```

Confirm the current branch and working-tree status:

```bash
git status
git branch
```

## 5. Local Python Environment

Create a virtual environment:

```bash
python3.12 -m venv .venv
```

Activate the environment on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Verify the Python version:

```bash
python --version
```

## 6. Environment Configuration

The repository includes `.env.example`.

Create a local environment file:

```bash
cp .env.example .env
```

The example file defines the following variables:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy database connection URL for local development |
| `OPENAI_API_KEY` | API credential for live AI analysis |
| `POSTGRES_PASSWORD` | Password for the Docker Compose PostgreSQL service |

Example configuration:

```env
DATABASE_URL=postgresql+psycopg://sadmin:YOUR_PASSWORD@localhost:5432/incident_db
OPENAI_API_KEY=
POSTGRES_PASSWORD=YOUR_LOCAL_DATABASE_PASSWORD
```

Replace example values with valid local configuration.

**Security requirements:**

- Do not commit `.env` files.
- Do not store API keys in source code.
- Do not include database credentials in logs.
- Do not share raw connection strings containing passwords.
- Use separate credentials for development and production environments.

## 7. Database Configuration

The application uses PostgreSQL and the pgvector extension.

The Docker Compose configuration provides:

- PostgreSQL using the `pgvector/pgvector:pg16` image.
- Database name: `incident_db`.
- Database user: `sadmin`.
- A named volume for database persistence.
- An initialization script that enables the vector extension.

The application database connection inside Docker uses the Compose service name `db`.

The local development connection uses `localhost`.

### Database Initialization

The application includes:

```text
app/init_db.py
```

This module initializes tables using SQLAlchemy metadata:

```python
Base.metadata.create_all(bind=engine)
```

The Docker image executes database initialization before starting Uvicorn.

Versioned database migrations are not currently configured as the application's schema-management process.

## 8. Run the Application Locally

For local execution outside Docker, ensure PostgreSQL is running, the `incident_db` database exists, and the pgvector extension is enabled.

Configure `DATABASE_URL` in `.env` to point to the local database.

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The application is available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## 9. Run with Docker Compose

Docker Compose is the recommended reproducible environment for running the API and PostgreSQL together.

Create and configure `.env`:

```bash
cp .env.example .env
```

Set a non-empty `POSTGRES_PASSWORD` before starting the services. Set `OPENAI_API_KEY` for live AI analysis; it may remain empty when testing API functionality that does not invoke the live AI provider.

Start the containers:

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

Review API logs:

```bash
docker compose logs -f api
```

Review database logs:

```bash
docker compose logs -f db
```

Verify the API:

```bash
curl http://localhost:8000/health
```

Open:

```text
http://localhost:8000/docs
```

Stop the services:

```bash
docker compose down
```

To remove the database volume as well:

```bash
docker compose down -v
```

**Warning:** Removing the volume deletes the persisted local PostgreSQL data. Use this command only when that data is no longer required.

## 10. Knowledge Base Development

Markdown runbooks are maintained in:

```text
data/runbooks/
```

The knowledge service uses the following processing stages:

1. Read Markdown files.
2. Split document content into chunks.
3. Generate normalized embeddings.
4. Store document chunks and embeddings in PostgreSQL.
5. Search stored embeddings using cosine distance.

The current text-splitting configuration uses:

- Chunk size: 800 characters.
- Chunk overlap: 120 characters.
- Markdown-aware separators.

The embedding model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The vector column is configured for 384 dimensions.

### Trigger Knowledge Ingestion

The API endpoint is:

```http
POST /incidents/knowledge/ingest
```

The endpoint invokes the runbook ingestion service and returns the number of chunks ingested when successful.

Knowledge ingestion and retrieval should be tested against a database containing the expected runbook data.

## 11. Incident Analysis Development

The analysis endpoint is:

```http
POST /incidents/{incident_id}/analyze
```

The current workflow:

1. Retrieves the incident.
2. Searches the knowledge base using the incident description.
3. Retrieves up to three matching knowledge chunks.
4. Passes incident details and optional knowledge context to the AI analyzer.
5. Validates the structured AI response.
6. Persists the analysis and knowledge-source metadata.
7. Returns the response to the API client.

The AI analyzer uses LangChain's OpenAI integration and a Pydantic structured-output model.

The application requires a valid `OPENAI_API_KEY` for live AI analysis.

If the AI provider is unavailable, the application maps the failure to HTTP `503 Service Unavailable` with the code `AI_SERVICE_UNAVAILABLE`.

## 12. Automated Testing

The project uses pytest.

Run the complete suite:

```bash
pytest -v
```

Run individual test modules:

```bash
pytest -v tests/test_health.py
pytest -v tests/test_incidents.py
pytest -v tests/test_incident_analysis.py
pytest -v tests/test_knowledge_search.py
```

### Test Database

The test configuration is defined in:

```text
tests/conftest.py
```

The test configuration derives a separate database name, `test_incident_db`, from the configured `DATABASE_URL`.

The test database must already exist and be accessible. The pgvector extension must be available in that database.

For a local PostgreSQL instance, create the test database and enable the extension using an account with the required privileges. For example:

```bash
createdb -h localhost -U sadmin test_incident_db
psql -h localhost -U sadmin -d test_incident_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

The test fixture creates the SQLAlchemy tables at the beginning of the test session and drops those tables when the session completes.

**Important:** The tests use a separate database and remove its application tables after the test session. Do not point the test configuration at a database containing data that must be preserved.

The GitHub Actions workflow provisions a PostgreSQL pgvector service for CI testing.

### Testing Practices

For each implementation change:

1. Identify the behavior being changed.
2. Inspect the existing implementation and tests.
3. Add or update a focused test.
4. Run the relevant test module.
5. Run the full test suite.
6. Review the final changes.
7. Confirm the working tree contains only intended modifications.

A passing test result should be recorded only after the relevant command has completed successfully.

## 13. Continuous Integration

The repository includes:

```text
.github/workflows/ci.yml
```

The workflow runs on pushes and pull requests targeting `main`.

The CI workflow:

1. Checks out the repository.
2. Configures Python 3.12.
3. Starts a PostgreSQL pgvector service.
4. Installs project dependencies.
5. Enables the PostgreSQL vector extension.
6. Runs pytest.
7. Builds the API Docker image without publishing it.

The workflow provides automated validation of the application test suite and Docker build.

## 14. Container Publishing

The repository includes:

```text
.github/workflows/publish.yml
```

The publishing workflow is configured to run when a Git tag matching the following pattern is pushed:

```text
v*.*.*
```

The workflow:

- Authenticates to GitHub Container Registry.
- Extracts version metadata.
- Builds multi-platform Docker images for `linux/amd64` and `linux/arm64`.
- Publishes the images to GHCR.

The configured image repository is:

```text
ghcr.io/frankierosa/ai-incident-response-platform
```

A published image should be verified in the GitHub Packages interface after a version tag triggers the workflow.

## 15. Git Development Workflow

The repository uses feature branches and pull requests.

The `main` branch should contain reviewed and validated changes.

### Start a Feature Branch

Update the local `main` branch:

```bash
git checkout main
git pull origin main
```

Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

### Review Changes

Before committing:

```bash
git status
git diff
```

Review the changes and confirm that only the intended files have been modified.

### Run Tests

```bash
pytest -v
```

### Commit Changes

Use descriptive commit messages:

```bash
git add path/to/changed-file
git commit -m "feat: describe the implemented change"
```

### Push the Branch

```bash
git push -u origin feature/your-feature-name
```

Open a pull request targeting `main`.

### Pull Request Expectations

A pull request should include:

- A clear description of the change.
- The reason for the change.
- Relevant test coverage.
- Test results.
- Any configuration or documentation updates.
- Known limitations or follow-up work.

Do not merge changes until review and validation are complete.

## 16. Versioning and Releases

The project uses Semantic Versioning as its intended release convention:

```text
MAJOR.MINOR.PATCH
```

Example:

```text
v0.1.0
```

Version tags are used by the GHCR publishing workflow.

Before creating a release:

1. Confirm the intended changes are merged into `main`.
2. Run the complete automated test suite.
3. Verify the Docker build.
4. Create the version tag.
5. Push the tag.
6. Verify the publishing workflow.
7. Confirm the image is available in GHCR.

## 17. Troubleshooting

### Database Connection Errors

Verify:

- PostgreSQL is running.
- The database exists.
- The username and password are correct.
- The database connection URL uses the correct hostname and port.
- The pgvector extension is available.

For Docker Compose, inspect:

```bash
docker compose ps
docker compose logs -f db
```

### Missing Environment Variables

Verify that `.env` exists and contains the required configuration.

Do not commit secrets or paste unredacted credentials into support requests.

### AI Analysis Unavailable

Verify:

- `OPENAI_API_KEY` is configured.
- The key is valid.
- The account has access to the configured model.
- The provider service is available.

The API may return `AI_SERVICE_UNAVAILABLE` when the analysis operation cannot be completed.

### Knowledge Search Returns No Results

Verify:

- Markdown runbook files exist under `data/runbooks/`.
- Knowledge ingestion completed successfully.
- The database contains knowledge documents.
- The documents have generated embeddings.
- The vector extension is enabled.

## 18. Development Principles

The following principles guide ongoing development:

- Preserve existing working functionality.
- Prefer small, focused changes.
- Inspect the implementation before proposing modifications.
- Add tests for new behavior.
- Avoid introducing unnecessary dependencies.
- Keep secrets out of source control.
- Use GitHub as the source of truth.
- Use Docker for reproducible deployment environments.
- Keep container images separate from application source code.
- Use feature branches and pull requests.
- Document implemented functionality accurately.
- Distinguish verified capabilities from planned enhancements.

## 19. Future Engineering Improvements

Potential engineering improvements include:

- More comprehensive retrieval evaluation.
- Incident-aware retrieval-query construction.
- Configurable retrieval limits and similarity thresholds.
- Improved ingestion lifecycle management.
- Versioned database migrations.
- Expanded integration testing.
- Improved logging and diagnostics.
- Authentication and authorization.
- Operational metrics and observability.
- Kubernetes deployment.
- Production deployment validation.

These improvements should be introduced incrementally and supported by tests.

## 20. Related Documentation

- [README.md](../README.md) — Project overview, capabilities, architecture summary, and setup.
- [PROJECT_GUIDE.md](PROJECT_GUIDE.md) — Project purpose, architecture, workflow, and portfolio explanation.
- [LICENSE](../LICENSE) — MIT License.
