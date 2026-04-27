import logging

from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.exceptions import ValidationException
from app.schemas.responses import IngestResponse
from app.schemas.search import SearchRequest

from app.services.ingestion.ingest_service import ingest_documents
from app.services.generation.generation_service import generate_answer
from app.services.monitoring.token_tracker import token_tracker
from app.services.retrieval.hybrid_retriever import HybridRetriever
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


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: Request):
    """
    Ingests documents from the local data/docker_docs folder,
    builds the vector store and BM25 index.
    """
    logger.info("Starting ingestion from local documents")

    # Reset the existing app.state vector store rather than creating a new one.
    request.app.state.vector_store.reset()

    result = ingest_documents(
        folder_path="data/docker_docs",
        vector_store=request.app.state.vector_store,
        chunk_size=500,
    )

    request.app.state.hybrid_retriever = HybridRetriever(
        request.app.state.vector_store, alpha=settings.HYBRID_ALPHA
    )
    request.app.state.hybrid_retriever.build_bm25_index()

    logger.info(
        "Ingestion completed | documents=%s chunks=%s dimension=%s",
        result["documents_loaded"],
        result["chunks_created"],
        result["embedding_dimension"],
    )

    return IngestResponse(
        message="Documents ingested successfully",
        documents_loaded=result["documents_loaded"],
        chunks_created=result["chunks_created"],
        embedding_dimension=result["embedding_dimension"],
        index_created=result["index_created"],
        total_chunks_in_store=result["total_chunks_in_store"],
    )


@router.post("/ask")
@limiter.limit("10/minute")
def ask_question(request: Request, search_request: SearchRequest):
    """
    Runs the full RAG pipeline: cache check -> hybrid retrieval -> rerank -> generate.
    """
    if request.app.state.hybrid_retriever is None:
        raise ValidationException(
            message="Index not ready. Call POST /ingest first.",
            details=None,
        )

    logger.info("Received query | query=%s", search_request.query)

    cached = get_from_cache(search_request.query)
    if cached:
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