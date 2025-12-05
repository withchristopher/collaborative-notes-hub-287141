# Project Repository

This is the initial README file for the project.

## Backend (FastAPI)

- App path: backend/src/api/main.py
- Generate OpenAPI: `python -m src.api.generate_openapi` from backend root
- Environment:
  - DATABASE_URL (async): e.g. `postgresql+asyncpg://user:pass@host:port/db`
  - Or place `db_connection.txt` containing a line such as `psql postgresql://user:pass@host:port/db`
- Dependencies include async drivers for Postgres (asyncpg) and SQLite (aiosqlite).
- Startup auto-creates tables.

### Notes API highlights
- CRUD: `/notes` endpoints
- Pagination: `page`, `page_size`
- Search: `search` across title/content
- Tags filter: `tags` query can be repeated (?tags=a&tags=b)
- History: `/notes/{id}/history`