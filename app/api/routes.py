from fastapi import APIRouter
from app.schemas.requests import IngestRequest
from app.schemas.responses import IngestResponse
from app.services.ingest_service import process_text

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):
    word_count, chunks_count = process_text(request.text)

    return IngestResponse(
        message="Text Processed", word_count=word_count, chunks_created=chunks_count
    )
