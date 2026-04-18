from pydantic import BaseModel

class IngestRequest(BaseModel):
    text:str
    

class QueryRequest(BaseModel):
    question:str
    
    