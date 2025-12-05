from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db_session
from .models import Note, NoteHistory
from .schemas import NoteCreate, NoteHistoryOut, NoteOut, NoteUpdate, PagedNotes

router = APIRouter(prefix="/notes", tags=["Notes"])


def _apply_search_filters(query, search: Optional[str], tags: Optional[List[str]]):
    conditions = []
    if search:
        pattern = f"%{search.lower()}%"
        conditions.append(
            or_(
                func.lower(Note.title).like(pattern),
                func.lower(Note.content).like(pattern),
            )
        )
    if tags:
        # Use a portable JSON array containment check.
        # For Postgres JSON/ARRAY: use overlap; For SQLite JSON: use contains semantics.
        # SQLAlchemy will translate "contains" for JSON-typed columns where supported.
        # We want notes that contain ANY of provided tags. Implement as OR of contains([tag]).
        tag_conds = [Note.tags.contains([t]) for t in tags]  # type: ignore[attr-defined]
        conditions.append(or_(*tag_conds))
    if conditions:
        query = query.where(and_(*conditions))
    return query


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=PagedNotes,
    summary="List notes with pagination",
    description="List notes filtered by optional search text and tags, with pagination.",
)
async def list_notes(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=200, description="Items per page"),
    search: Optional[str] = Query(None, description="Search text across title and content"),
    tags: Optional[List[str]] = Query(None, description="Filter notes containing any of the specified tags"),
    db: AsyncSession = Depends(get_db_session),
) -> PagedNotes:
    """List notes with pagination and optional search/tags filter."""
    base_q = select(Note)
    base_q = _apply_search_filters(base_q, search, tags)

    count_q = select(func.count()).select_from(Note)
    count_q = _apply_search_filters(count_q, search, tags)

    total = (await db.execute(count_q)).scalar_one()
    items_res = await db.execute(
        base_q.order_by(Note.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = items_res.scalars().all()
    return PagedNotes(items=items, total=total, page=page, page_size=page_size)


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=NoteOut,
    status_code=201,
    summary="Create a note",
    description="Create a new note and return it.",
)
async def create_note(payload: NoteCreate, db: AsyncSession = Depends(get_db_session)) -> NoteOut:
    """Create a new note."""
    note = Note(title=payload.title, content=payload.content, tags=payload.tags or [])
    db.add(note)
    await db.flush()  # Get note.id
    # store initial history snapshot
    hist = NoteHistory(note_id=note.id, title=note.title, content=note.content, tags=note.tags)
    db.add(hist)
    await db.commit()
    await db.refresh(note)
    return note


# PUBLIC_INTERFACE
@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get a note",
    description="Get a single note by its ID.",
)
async def get_note(note_id: int, db: AsyncSession = Depends(get_db_session)) -> NoteOut:
    """Get a note by ID."""
    res = await db.execute(select(Note).where(Note.id == note_id))
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update a note",
    description="Update fields of a note and record history before the change.",
)
async def update_note(note_id: int, payload: NoteUpdate, db: AsyncSession = Depends(get_db_session)) -> NoteOut:
    """Update a note and push previous snapshot to history."""
    res = await db.execute(select(Note).where(Note.id == note_id))
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Save snapshot BEFORE changes
    snapshot = NoteHistory(note_id=note.id, title=note.title, content=note.content, tags=note.tags)
    db.add(snapshot)

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.tags is not None:
        note.tags = payload.tags

    await db.flush()
    await db.commit()
    await db.refresh(note)
    return note


# PUBLIC_INTERFACE
@router.delete(
    "/{note_id}",
    status_code=204,
    response_model=None,  # Explicitly indicate no response model for 204 No Content
    summary="Delete a note",
    description="Delete the note by ID, removing its history as well.",
)
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db_session)) -> None:
    """Delete a note by ID.

    With status_code=204 this endpoint returns no content in the response body.
    """
    res = await db.execute(select(Note).where(Note.id == note_id))
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
    await db.commit()
    # For 204 No Content, return no body
    return


# PUBLIC_INTERFACE
@router.get(
    "/{note_id}/history",
    response_model=List[NoteHistoryOut],
    summary="List note history",
    description="List historical snapshots for a note.",
)
async def list_note_history(note_id: int, db: AsyncSession = Depends(get_db_session)) -> List[NoteHistoryOut]:
    """List the history snapshots for a note ordered by most recent first."""
    res = await db.execute(select(NoteHistory).where(NoteHistory.note_id == note_id).order_by(NoteHistory.changed_at.desc()))
    return res.scalars().all()
