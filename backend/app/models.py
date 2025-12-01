from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class DocumentChunk(BaseModel):
    id: str
    content: str
    content_vector: List[float]
    source_file: str
    page_number: Optional[int] = None
    # need timezone for azure search
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="user's question")

class SourceDocument(BaseModel):
    source_file: str
    page_number: Optional[int] = None
    content_snippet: str
    relevance_score: Optional[float] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
