from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# PUBLIC_INTERFACE
class Pagination(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(20, ge=1, le=200, description="Number of items per page")


class NoteBase(BaseModel):
    """Base note fields shared by input and output schemas."""
    title: str = Field(..., min_length=1, max_length=255, description="Note title")
    content: str = Field(..., description="Note content as markdown or rich text")
    # Accept None on input but normalize to [] on output via model serializer hooks
    tags: Optional[List[str]] = Field(None, description="List of tags for the note")


# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Payload model to create a new note.

    Fields:
    - title: required
    - content: required
    - tags: optional list of strings
    """


# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Payload model to update an existing note.

    Only provided fields are updated; omitted fields remain unchanged.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated note title")
    content: Optional[str] = Field(None, description="Updated note content")
    tags: Optional[List[str]] = Field(None, description="Updated list of tags for the note (replaces all tags)")


# PUBLIC_INTERFACE
class NoteOut(NoteBase):
    """Response model representing a note entity with server-managed fields."""
    id: int = Field(..., description="Note identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        """Ensure tags are always returned as a list (never null)."""
        data = super().model_dump(*args, **kwargs)
        # Normalize tags to [] for response
        if data.get("tags") is None:
            data["tags"] = []
        return data


# PUBLIC_INTERFACE
class NoteHistoryOut(BaseModel):
    """Response model for a historical snapshot of a note prior to an update."""
    id: int
    note_id: int
    title: str
    content: str
    tags: Optional[List[str]] = None
    changed_at: datetime

    class Config:
        from_attributes = True

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        """Ensure tags are always returned as a list (never null)."""
        data = super().model_dump(*args, **kwargs)
        if data.get("tags") is None:
            data["tags"] = []
        return data


# PUBLIC_INTERFACE
class PagedNotes(BaseModel):
    """Response model for a paginated list of notes."""
    items: List[NoteOut]
    total: int = Field(..., description="Total matching items (across all pages)")
    page: int
    page_size: int
