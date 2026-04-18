from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IngestResponse(BaseModel):
    message: str
    word_count: int
    chunks_created: int
    
class QueryResponse(BaseModel):
    message:str
    
    
class ErrorResponse(BaseModel):
    error:str
    details: Optional[str] = None
    timestamp:datetime
    request_id:int
    
