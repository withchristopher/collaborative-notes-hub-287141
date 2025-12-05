import os
import re
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# PUBLIC_INTERFACE
def get_database_url() -> str:
    """Return the database URL to connect to.

    Order of precedence:
    1) DATABASE_URL environment variable
    2) Parse db_connection.txt (if present) which typically contains a psql command like:
       'psql postgresql://user:pass@host:port/dbname'
    """
    # Prefer explicit env var
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return _ensure_async_driver(env_url)

    # Fallback to db_connection.txt in project root or backend root
    candidates = [
        os.path.join(os.getcwd(), "db_connection.txt"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db_connection.txt"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "db_connection.txt"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            # Look for postgresql://... URL
            m = re.search(r"(postgresql://[^\s]+)", content)
            if m:
                return _ensure_async_driver(m.group(1))
            # Sometimes psql "postgres://..." exists as well
            m = re.search(r"(postgres://[^\s]+)", content)
            if m:
                return _ensure_async_driver(m.group(1).replace("postgres://", "postgresql://"))

    # Default to a local ephemeral SQLite DB for development if nothing set.
    # Using aiosqlite driver for async.
    return "sqlite+aiosqlite:///./notes_dev.db"


def _ensure_async_driver(url: str) -> str:
    """Ensure the URL uses an async driver if PostgreSQL is used."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url and "+psycopg" not in url:
        # Prefer asyncpg
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


# Lazily initialized engine/sessionmaker singletons
_engine = None
_sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None

# PUBLIC_INTERFACE
def get_engine():
    """Get or create the global async engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_database_url(), future=True, pool_pre_ping=True)
    return _engine

# PUBLIC_INTERFACE
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Get or create the global async sessionmaker."""
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _sessionmaker

# PUBLIC_INTERFACE
async def get_db_session() -> AsyncSession:
    """FastAPI dependency that yields an async DB session."""
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        await session.close()
