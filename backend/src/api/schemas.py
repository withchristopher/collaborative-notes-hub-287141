from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(20, ge=1, le=200, description="Number of items per page")


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Note title")
    content: str = Field(..., description="Note content as markdown or rich text")
    # Accept None on input but normalize to [] on output via model serializer hooks
    tags: Optional[List[str]] = Field(None, description="List of tags for the note")


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated note title")
    content: Optional[str] = Field(None, description="Updated note content")
    tags: Optional[List[str]] = Field(None, description="Updated list of tags for the note (replaces all tags)")


class NoteOut(NoteBase):
    id: int = Field(..., description="Note identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        data = super().model_dump(*args, **kwargs)
        # Normalize tags to [] for response
        if data.get("tags") is None:
            data["tags"] = []
        return data


class NoteHistoryOut(BaseModel):
    id: int
    note_id: int
    title: str
    content: str
    tags: Optional[List[str]] = None
    changed_at: datetime

    class Config:
        from_attributes = True

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        data = super().model_dump(*args, **kwargs)
        if data.get("tags") is None:
            data["tags"] = []
        return data


class PagedNotes(BaseModel):
    items: List[NoteOut]
    total: int = Field(..., description="Total matching items (across all pages)")
    page: int
    page_size: int
