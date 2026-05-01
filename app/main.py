import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import ValidationException
from app.schemas.responses import ErrorResponse

from infra.vector_store import VectorStore
from infra.rate_limiter import limiter
from infra.timeout import timeout_config
from infra.cache import query_cache

from app.services.ingestion.ingest_service import ingest_documents  
from app.services.retrieval.hybrid_retriever import HybridRetriever       
from app.services.retrieval.reranker import Reranker

from app.api.routes import router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────
    logger.info(
        "Timeout config: connect=%ss, read=%ss",
        timeout_config.connect,
        timeout_config.read,
    )
    logger.info(
        "Cache config: maxsize=%s, ttl=%.0fs",
        query_cache.maxsize,
        query_cache.timer(),
    )

    app.state.limiter = limiter
    app.state.reranker = Reranker()

    # ── Auto-ingest on startup ────────────────────────────
    logger.info("Starting document ingestion...")
    vector_store = VectorStore()
    ingest_result = ingest_documents(
        settings.DOCS_FOLDER, 
        vector_store,
    )
    logger.info(
        "Ingestion complete — docs: %s, chunks: %s",
        ingest_result["documents_loaded"],
        ingest_result["chunks_created"],
    )

    hybrid_retriever = HybridRetriever(vector_store, alpha=settings.HYBRID_ALPHA)
    hybrid_retriever.build_bm25_index()
    logger.info("BM25 index built. App is ready to serve requests.")

    app.state.vector_store = vector_store
    app.state.hybrid_retriever = hybrid_retriever

    yield
    # ── Shutdown ─────────────────────────────────────────
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(
            ErrorResponse(
                error=exc.message,
                details=exc.details,
                timestamp=datetime.now(),
                request_id=getattr(request.state, "request_id", None),
            )
        ),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(
            ErrorResponse(
                error="Internal server error",
                details=None,
                timestamp=datetime.now(),
                request_id=getattr(request.state, "request_id", None),
            )
        ),
    )


# Router
app.include_router(router)