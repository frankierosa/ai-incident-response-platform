from fastapi import FastAPI


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
