import logging

from fastapi import APIRouter, Request

from app.core.config import settings
from app.schemas.search import SearchRequest

from app.services.generation.generation_service import generate_answer
from app.services.monitoring.token_tracker import token_tracker
from app.utils.chunk_utils import reranked_to_chunks

from infra.cache import get_from_cache, save_to_cache
from infra.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
def home(request: Request):
    return {"version": settings.VERSION}


@router.get("/health")
def health_check():
    logger.info("Health check called")
    return {"status": "OK"}


@router.post("/ask")
@limiter.limit("10/minute")
def ask_question(request: Request, search_request: SearchRequest):
    """
    Runs the full RAG pipeline: cache check -> hybrid retrieval -> rerank -> generate.
    """
    logger.info("Received query | query=%s", search_request.query)

    cached = get_from_cache(search_request.query)
    if cached:
        logger.info("Cache hit for query=%s", search_request.query)
        return cached

    scored_chunks = request.app.state.hybrid_retriever.retrieve(
        query=search_request.query, top_k=15
    )

    reranked = request.app.state.reranker.rerank(
        query=search_request.query,
        chunks=scored_chunks,
        top_k=search_request.top_k,
    )

    chunks = reranked_to_chunks(reranked)

    result = generate_answer(search_request.query, chunks)

    save_to_cache(search_request.query, result)

    return result


@router.get("/token-usage")
def get_token_usage():
    return token_tracker.get_summary()
