from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IngestResponse(BaseModel):
    message: str
    documents_loaded: int
    chunks_created: int
    embedding_dimension: int
    index_created: bool
    total_chunks_in_store: int


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime
    request_id: Optional[str] = None
