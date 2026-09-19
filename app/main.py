from fastapi import FastAPI

from app.api.routes.incidents import router as incident_router


# Create a FastAPI application instance with a title and version.
app = FastAPI(
    title="AI Production Incident Response Platform",
    version="0.1.0",
)

# Define a health check endpoint that returns a simple JSON response indicating the service is operational.
@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


# Import the incident router from the incidents module and include it in the FastAPI application instance. This allows the application to handle requests related to incidents using the defined endpoints in the incident router.
app.include_router(incident_router)