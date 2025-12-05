# Collaborative Notes Hub - Backend

This backend service is implemented with FastAPI.

Key points:
- No dependency on database/db_visualizer path. Previous references have been removed.
- Use docker-compose at the root of each container or the provided Makefile to build and run.

## Local Development

### Python (no Docker)
- Create virtualenv and install:
  pip install -e .
- Run:
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

### Docker
- Build:
  docker build -t collaborative-notes-hub-backend:dev .
- Run:
  docker run -p 8000:8000 collaborative-notes-hub-backend:dev

### Compose (backend only)
- docker compose up --build

Health check: http://localhost:8000/health
