# Backend (FastAPI)

This service provides the REST API for the Collaborative Notes application.

## Environment

Copy `.env.example` to `.env` and set:

```
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db>
ALLOWED_ORIGINS=http://localhost:3000
```

Notes:
- For local development, ensure `ALLOWED_ORIGINS` includes `http://localhost:3000`.
- If `DATABASE_URL` is not set, the service may attempt to parse a `db_connection.txt` found in the database workspace to construct a fallback connection string. If that file shows a port other than `5001`, prefer the listed port.

## Running

- Ensure Postgres is running and reachable using `DATABASE_URL`.
- Start the API server (e.g., on port `3001`).
- The frontend will call this service using `NEXT_PUBLIC_API_BASE` (default `http://localhost:3001`).

## E2E Smoke Checklist (see repo root README)
- Create note -> Edit -> Search -> View “Last edited” timestamp updates.
