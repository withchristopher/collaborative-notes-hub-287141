from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _now_utc():
    return datetime.utcnow()


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), default=_now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), default=_now_utc)

    history: Mapped[list[NoteHistory]] = relationship("NoteHistory", back_populates="note", cascade="all, delete-orphan")


class NoteHistory(Base):
    __tablename__ = "note_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), default=_now_utc)

    note: Mapped[Note] = relationship("Note", back_populates="history")
