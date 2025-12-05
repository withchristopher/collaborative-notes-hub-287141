# Project Repository

This is the initial README file for the project.

## Backend Container Notes

- The backend container has been initialized with a minimal FastAPI app.
- Any previous references to a non-existent database/db_visualizer path have been removed. The backend build does not attempt to cd into or depend on that path.
- See backend/ for Dockerfile, docker-compose.yml, and Makefile that build and run the service independently.
- Future integration with the database container should use proper service discovery and environment variables, not file path dependencies. When using docker compose, rely on service healthchecks and a DATABASE_URL env var, never a cd into database/db_visualizer.