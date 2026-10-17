# AI Production Incident Response Platform

An AI-assisted incident response backend built with **Python, FastAPI, PostgreSQL, and SQLAlchemy**. The project explores how AI analysis and operational knowledge retrieval can help engineers investigate production incidents and identify possible causes and next steps.

> **Portfolio project:** This is an actively developed learning project that connects my background in enterprise technical support and production troubleshooting with backend engineering and AI-assisted application development. The status below distinguishes implemented code from work that is still in progress.

## Overview

Production incidents often require engineers to examine incident details, application behavior, and historical troubleshooting knowledge before deciding what to investigate next. This project is being developed to provide a backend foundation for recording incidents and generating structured AI-assisted analysis.

Current development focuses on:

- Creating and retrieving incidents through REST endpoints.
- Persisting incident and analysis records in PostgreSQL.
- Returning structured incident analysis, including a summary, probable cause, impact, and recommended actions.
- Handling AI-service failures with a defined application error response.
- Building the knowledge-search foundation needed for a future retrieval-augmented generation (RAG) workflow.

The goal is to build these capabilities incrementally, with tests and clear development practices, rather than claim that the full AI/RAG or deployment architecture is already complete.

## Current implementation status

**Implemented in the codebase**

- FastAPI application and `GET /health` health-check endpoint.
- Incident API routing and Pydantic request/response schemas.
- SQLAlchemy models and database service logic for creating and retrieving incidents.
- PostgreSQL persistence for incidents.
- Incident-analysis service flow and a persisted incident-analysis model.
- Structured analysis fields: summary, probable cause, impact, and recommended actions.
- AI-service exception handling through an application-level service error.
- A knowledge-service/search integration scaffold.
- pytest tests for the incident-analysis success path and AI-service-unavailable path.

**In progress / needs verification**

- Stabilizing the incident-analysis test suite. In the latest reported run, one test passed and one failed because the expected service-unavailable message did not match the returned message. The test checks for HTTP 503 and the `AI_SERVICE_UNAVAILABLE` error code as well.
- Completing and verifying the knowledge-document ingestion and retrieval workflow.
- Resolving the current embedding/retrieval mismatch before describing semantic search as fully working.
- Verifying a repeatable local database startup and test setup with Docker.
- Expanding database integration tests and documenting the exact environment configuration.

**Planned — not yet represented as completed**

- A complete, validated RAG pipeline with embedding generation and vector similarity search.
- Reliable context injection from retrieved knowledge into AI analysis.
- Dockerized application and a reproducible Docker Compose deployment.
- GitHub Actions CI, automated container builds, and publishing versioned images to GitHub Container Registry (GHCR).
- Semantic-versioned releases and GitHub Releases.
- Kubernetes deployment, cloud deployment, and production observability.

Project status will change as these capabilities are implemented and tested.

## Architecture

### Current application flow

```text
API Client (browser / curl / Postman)
                 |
                 v
             FastAPI
                 |
        +--------+---------+
        |                  |
        v                  v
 Incident API       Incident Analysis API
        |                  |
        v                  +------> AI analysis service
 SQLAlchemy                     |
        |                       +------> Knowledge search
        v
    PostgreSQL
        |
        +--> Incident records
        +--> Incident-analysis records
        +--> Knowledge data (as implemented)
```

This diagram describes the current application flow at a high level. The full vector-retrieval and RAG path remains under development; it should not be interpreted as proof that end-to-end semantic retrieval is already complete.

### Intended AI/RAG flow

```text
Knowledge documents
        |
        v
Ingestion and text processing
        |
        v
Chunking and embedding generation
        |
        v
Vector storage / pgvector
        |
        v
Similarity search for incident context
        |
        v
Context-aware LLM analysis
        |
        v
Summary, probable cause, impact, recommended actions
```

The intended RAG workflow will retrieve relevant knowledge and supply it as context to the model. The current implementation still needs validation of the embedding and retrieval path before this flow can be marked complete.

## Technology stack

| Area | Technology | Status |
|---|---|---|
| Language | Python | In use |
| Backend framework | FastAPI | Implemented |
| API style | REST | Implemented |
| Request/response validation | Pydantic | In use |
| ORM | SQLAlchemy | In use |
| Relational database | PostgreSQL | Integrated; local environment setup is being stabilized |
| Testing | pytest | In use; tests being refined |
| AI analysis | LLM-backed analysis service | Analysis flow implemented; provider behavior depends on configuration and availability |
| Knowledge retrieval / RAG | Knowledge service, planned embeddings and retrieval | In progress |
| Vector database extension | pgvector | Intended for vector search; end-to-end retrieval needs verification |
| Containers | Docker / Docker Compose | Planned reproducible application deployment |
| CI/CD | GitHub Actions | Planned |
| Image registry | GitHub Container Registry | Planned |
| Orchestration | Kubernetes | Future milestone |
| Version control | Git / GitHub | In use |

## API

The application currently defines the health endpoint and incident routes. The intended/current route set is:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check application health |
| POST | `/incidents` | Create an incident |
| GET | `/incidents` | List incidents |
| GET | `/incidents/{id}` | Retrieve an incident by ID |
| POST | `/incidents/{id}/analyze` | Request AI-assisted analysis for an incident |

The incident-analysis route returns structured fields such as `summary`, `probable_cause`, `impact`, and `recommended_actions` on the success path. If the AI service is unavailable, the application is intended to return HTTP 503 with the `AI_SERVICE_UNAVAILABLE` error code.

When the application is running locally, FastAPI's interactive API documentation is normally available at:

```text
http://localhost:8000/docs
```

## Database

PostgreSQL stores application data through SQLAlchemy models and service methods. The current code includes incident records and incident-analysis records. The knowledge-search and vector-retrieval capabilities are being developed and must be validated separately.

Database work includes verifying that the database container is running, the configured host and port are reachable, and the application's connection settings match the local environment. Do not assume the database is available simply because a container was previously created.

## Testing

Run the test suite from the project root after activating the project's virtual environment and configuring a reachable test database:

```bash
pytest -v
```

To run the incident-analysis tests specifically:

```bash
pytest -v tests/test_incident_analysis.py
```

Current test focus:

- Incident-analysis success response and structured fields.
- Behavior when the AI service is unavailable.
- Incident creation and persistence required by the analysis flow.
- Database integration and retrieval behavior.

**Known follow-up:** The latest reported incident-analysis test run had one passing test and one failing test. The failure concerned an expected-versus-actual error-message mismatch. The next step is to align the assertion with the intended public error response and rerun the tests. Test results should be updated here only after a fresh run confirms them.

## Local development

The repository is the source of truth for application code. Docker images are build artifacts and should not be committed to the Git repository.

Typical setup:

```bash
git clone https://github.com/frankierosa/ai-incident-response-platform.git
cd ai-incident-response-platform

python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Then configure the database and any required AI-provider settings using the project's actual configuration files and environment variables. Start the API using the entry point configured by the project; for the standard FastAPI development setup:

```bash
uvicorn app.main:app --reload
```

The database must be running and reachable before testing database-backed endpoints. Docker Compose instructions will be added once the repository's compose configuration and environment-variable requirements are finalized. Do not commit secrets or API keys.

## Development workflow

Development uses feature branches and pull requests instead of making feature changes directly on `main`.

Example:

```bash
git checkout main
git pull origin main
git checkout -b feature/incident-analysis-improvements
```

After making a focused change, run the relevant tests, commit the work, push the branch, and open a pull request for review.

Suggested future feature branches include:

- `feature/knowledge-ingestion`
- `feature/vector-retrieval`
- `feature/rag-analysis`
- `feature/docker`
- `feature/ci-cd`
- `feature/kubernetes`

## Roadmap

### Phase 1 — Backend and persistence
- [x] FastAPI application and health endpoint
- [x] Incident API and schemas
- [x] SQLAlchemy incident persistence
- [x] Incident-analysis data model and service flow
- [ ] Finish stabilizing tests and local database setup

### Phase 2 — Knowledge retrieval and RAG
- [x] Initial knowledge-service/search integration
- [ ] Verify knowledge-document ingestion
- [ ] Resolve embedding/retrieval mismatch
- [ ] Validate vector similarity search end to end
- [ ] Pass retrieved context into AI analysis and test it

### Phase 3 — AI analysis quality
- [x] Structured analysis response
- [x] AI-service-unavailable error handling path
- [ ] Improve failure-path test assertions
- [ ] Add tests for missing incidents and knowledge retrieval failures
- [ ] Evaluate analysis quality and remediation recommendations

### Phase 4 — Reproducible deployment
- [ ] Finalize Dockerfile and Docker Compose configuration
- [ ] Document environment variables and local startup
- [ ] Validate clean startup and shutdown

### Phase 5 — CI/CD and releases
- [ ] GitHub Actions test workflow
- [ ] Automated container build and validation
- [ ] Publish versioned images to GHCR
- [ ] Adopt semantic versioning and GitHub Releases

### Phase 6 — Kubernetes and operations
- [ ] Kubernetes manifests and configuration
- [ ] Readiness and liveness probes
- [ ] Resource configuration and scaling
- [ ] Logging, metrics, and observability
- [ ] Evaluate cloud deployment

## Versioning and container distribution

The project intends to use Semantic Versioning (`MAJOR.MINOR.PATCH`) and Git tags/GitHub Releases to mark stable milestones. These practices and GHCR publishing are planned; no release or published image should be assumed until one exists.

The intended distribution flow is:

```text
Feature branch -> Pull request -> Tests -> Merge
                                      |
                                      v
                              Build container image
                                      |
                                      v
                              Publish versioned image
                                      |
                                      v
                                  GHCR
```

## Portfolio goals

This project is an incremental demonstration of backend engineering and production problem-solving:

- Python application development
- REST API design with FastAPI
- Relational data persistence with PostgreSQL and SQLAlchemy
- Automated testing with pytest
- Structured AI analysis and error handling
- Knowledge retrieval and planned RAG capabilities
- Professional Git branching and pull-request workflow
- Planned containerization, CI/CD, release management, and Kubernetes deployment

The project is being built around a realistic operational problem: helping engineers investigate production incidents with structured data and, eventually, relevant historical knowledge.

## License

A formal open-source license has not yet been added. Until a license is included in the repository, reuse and redistribution are subject to the default copyright rules.
