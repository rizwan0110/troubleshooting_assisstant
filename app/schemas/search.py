from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5