# AI Incident Response Platform

AI-powered production incident response platform using Python, FastAPI, PostgreSQL, Docker, LangChain/LLM, AI Agents, and Kubernetes.


app/
├── ai/
│   └── analyzer.py              ← already working
│
├── api/
│   └── routes/
│       └── incidents.py         ← HTTP/API layer
│
├── models/
│   └── incident.py              ← PostgreSQL model
│
├── schemas/
│   └── incident.py              ← API request/response schemas
│
├── services/
│   └── incident_service.py      ← business logic
│
└── core/
    └── database.py
