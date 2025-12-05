from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from .db import get_engine
from .models import Base
from .routes_notes import router as notes_router

app = FastAPI(
    title="Collaborative Notes Hub API",
    description="Backend API for a self-hosted notetaking application supporting notes, tags, search, and history.",
    version="0.1.0",
    openapi_tags=[
        {"name": "Health", "description": "Health and utility endpoints"},
        {"name": "Notes", "description": "Create, read, update, delete notes; search and history"},
    ],
)

# Allow local frontend and generic origins; adjust as needed via env in future
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict via env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    """Create tables if they do not exist."""
    engine: AsyncEngine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """Health check endpoint to verify the service is running."""
    return {"message": "Healthy"}

# Include notes endpoints
app.include_router(notes_router)
