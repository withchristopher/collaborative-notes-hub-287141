from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, TypeDecorator


class Base(DeclarativeBase):
    pass


def _now_utc():
    return datetime.utcnow()


class JSONEncodedList(TypeDecorator):
    """
    Cross-dialect list-of-strings column.

    - Uses native JSON when available (e.g., PostgreSQL, SQLite new versions).
    - Falls back to TEXT storing JSON-serialized content for other dialects.

    Ensures compatibility when the app falls back to SQLite, which doesn't support
    PostgreSQL ARRAY(String) type.
    """
    impl = JSON

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        # Ensure list of strings
        if not isinstance(value, list):
            raise ValueError("tags must be a list of strings or None")
        return value

    def process_result_value(self, value, dialect):
        return value


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    # Use JSONEncodedList to support both Postgres and SQLite
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONEncodedList, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), default=_now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), default=_now_utc)

    history: Mapped[list[NoteHistory]] = relationship("NoteHistory", back_populates="note", cascade="all, delete-orphan")


class NoteHistory(Base):
    __tablename__ = "note_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    # Use JSONEncodedList to support both Postgres and SQLite
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONEncodedList, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), default=_now_utc)

    note: Mapped[Note] = relationship("Note", back_populates="history")
