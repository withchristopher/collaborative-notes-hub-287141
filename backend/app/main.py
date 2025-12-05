import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """Create and configure the FastAPI application with metadata and tags."""
    app = FastAPI(
        title="Collaborative Notes Hub Backend",
        description="Backend API for the Collaborative Notes Hub application.",
        version="0.1.0",
        openapi_tags=[
            {"name": "health", "description": "Service health and readiness checks."},
        ],
    )

    @app.get("/health", tags=["health"], summary="Health check", description="Returns service health status.")
    def health():
        return JSONResponse(content={"status": "ok"})

    return app


app = create_app()
