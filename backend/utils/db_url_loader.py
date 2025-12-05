"""
Utility to load DATABASE_URL from environment or parse a db_connection.txt file.

PUBLIC_INTERFACE
"""
import os
from typing import Optional


def _read_db_connection_txt() -> Optional[str]:
    """
    Attempt to read a db_connection.txt file from common locations and build a
    PostgreSQL URL string. The file format is expected to contain lines like:
      HOST=localhost
      PORT=5001
      DB=notesdb
      USER=postgres
      PASSWORD=postgres
    Returns a postgresql:// URL if successful, otherwise None.
    """
    candidate_paths = [
        # Same workspace as backend
        os.path.join(os.getcwd(), "db_connection.txt"),
        # Sibling database workspace (typical project layout)
        os.path.abspath(
            os.path.join(
                os.getcwd(),
                "..",
                "collaborative-notes-hub-287142",
                "database",
                "db_connection.txt",
            )
        ),
    ]
    for path in candidate_paths:
        try:
            if not os.path.exists(path):
                continue
            data = {}
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    data[k.strip().upper()] = v.strip()
            host = data.get("HOST", "localhost")
            port = data.get("PORT", "5001")
            db = data.get("DB") or data.get("DATABASE") or "postgres"
            user = data.get("USER", "postgres")
            pwd = data.get("PASSWORD", "")
            return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
        except Exception:
            # ignore parse errors and try next
            continue
    return None


# PUBLIC_INTERFACE
def get_database_url() -> Optional[str]:
    """
    Returns the DATABASE_URL from environment, or tries to derive one by
    parsing db_connection.txt if present. This is intended for local/dev only.
    """
    env_val = os.getenv("DATABASE_URL")
    if env_val:
        return env_val
    return _read_db_connection_txt()
