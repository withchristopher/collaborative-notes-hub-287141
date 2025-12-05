# Utils

- db_url_loader.py: helper to obtain `DATABASE_URL` from environment or derive it from a `db_connection.txt` file during local development.

Integration reminder (for maintainers):
- Import and use `get_database_url()` during app startup (e.g., when configuring your database engine) to enable the optional fallback behavior.
