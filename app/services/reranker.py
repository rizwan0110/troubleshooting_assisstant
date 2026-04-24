from sentence_transformers.cross_encoder import CrossEncoder
from app.services.hybrid_retriever import ScoredChunk
from typing import List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RerankedChunk:
    text: str
    rerank_score: float
    dense_score: float
    sparse_score: float
    metadata: dict


class Reranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
        logger.info(f"Reranker loaded: {model_name}")

    def rerank(
        self, query: str, chunks: List[ScoredChunk], top_k: int = 5
    ) -> List[RerankedChunk]:
        if not chunks:
            return []

        # Create (query, chunk_text) pairs for cross-encoder
        pairs = [(query, chunk.text) for chunk in chunks]

        # Cross-encoder scores each pair jointly
        scores = self.model.predict(pairs)

        # Attach rerank scores to chunks
        reranked = []
        for chunk, score in zip(chunks, scores):
            reranked.append(
                RerankedChunk(
                    text=chunk.text,
                    rerank_score=float(score),
                    dense_score=chunk.dense_score,
                    sparse_score=chunk.sparse_score,
                    metadata=chunk.metadata,
                )
            )

        # Sort by rerank score descending
        reranked.sort(key=lambda x: x.rerank_score, reverse=True)

        # Log before vs after
        logger.info(f"Rerank results for: '{query[:50]}'")
        for i, r in enumerate(reranked[:top_k]):
            logger.info(
                f"  #{i+1} | rerank: {r.rerank_score:.4f} | dense: {r.dense_score:.4f} | sparse: {r.sparse_score:.4f}"
            )

        return reranked[:top_k]
