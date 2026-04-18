import logging
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import ValidationException
from app.core.timeout import timeout_config
from app.core.cache import save_to_cache,get_from_cache,query_cache
from app.core.token_tracker import token_tracker

from app.schemas.responses import ErrorResponse
from app.schemas.search import SearchRequest

from app.services.vector_store import VectorStore
from app.services.ingest_service import ingest_documents
from app.services.embedding_service import generate_query_embedding

from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.generation_service import generate_answer
from app.services.hybrid_retriever import HybridRetriever
from app.utils.text_splitter import Chunk

from app.services.reranker import Reranker

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limiter import limiter




setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

app.add_middleware(RequestIDMiddleware)

app.state.limiter = limiter
#app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.state.vector_store = VectorStore()
app.state.reranker = Reranker()

logger.info(f"Timeout config: connect={timeout_config.connect}s, read={timeout_config.read}s")

logger.info(f"Cache config: maxsize={query_cache.maxsize}, ttl={query_cache.timer():.0f}s")

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    error_response = ErrorResponse(
        error=exc.message,
        details=exc.details,
        timestamp=datetime.now()
    )

    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(error_response)
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")

    error_response = ErrorResponse(
        error="Internal server error",
        details=None,
        timestamp=datetime.now()
    )

    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response)
    )


@app.get("/")
def home():
    return {"version": settings.VERSION}


@app.get("/health")
def health_check():
    logger.info("Health check called")
    return {"status": "OK"}


@app.post("/ingest")
def ingest():
    logger.info("Starting ingestion from local documents")

    app.state.vector_store = VectorStore()

    try:
        result = ingest_documents(
            folder_path="data/docker_docs",
            vector_store=app.state.vector_store,
            chunk_size=500
        )

        # Build BM25 AFTER chunks exist
        app.state.hybrid_retriever = HybridRetriever(app.state.vector_store, alpha=0.5)
        app.state.hybrid_retriever.build_bm25_index()

        logger.info(
            "Ingestion completed successfully | documents=%s chunks=%s dimension=%s",
            result["documents_loaded"],
            result["chunks_created"],
            result["embedding_dimension"],
        )

        return result

    except ValueError as exc:
        logger.warning("Ingestion failed: %s", str(exc))
        return JSONResponse(
            status_code=400,
            content={"message": str(exc)}
        )




@app.post("/ask")
@limiter.limit("10/minute")
def ask_question(request: Request, search_request: SearchRequest):
    logger.info("Received query request | query=%s", search_request.query)

    # Step 0: Check cache
    cached = get_from_cache(search_request.query)
    if cached:
        return cached

    # Step 1: Hybrid retrieval
    scored_chunks = app.state.hybrid_retriever.retrieve(
        query=search_request.query,
        top_k=15
    )

    # Step 2: Rerank
    reranked = app.state.reranker.rerank(
        query=search_request.query,
        chunks=scored_chunks,
        top_k=search_request.top_k
    )

    # Step 3: Build chunks + generate
    chunks = []
    for rc in reranked:
        chunk = Chunk(
            text=rc.text,
            chunk_id=rc.metadata["chunk_id"],
            doc_id=rc.metadata["doc_id"],
            source=rc.metadata["source"],
            section_title=rc.metadata["section_title"],
            chunk_index=rc.metadata["chunk_index"],
        )
        chunks.append(chunk)

    result = generate_answer(search_request.query, chunks)

    # Step 4: Save to cache
    save_to_cache(search_request.query, result)

    return result


@app.get("/token-usage")
def get_token_usage():
    return token_tracker.get_summary()