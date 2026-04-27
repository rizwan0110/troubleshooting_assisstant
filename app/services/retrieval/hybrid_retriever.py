from dataclasses import dataclass
from rank_bm25 import BM25Okapi
from infra.vector_store import VectorStore
from app.services.ingestion.embedding_service import EmbeddingService


@dataclass
class ScoredChunk:
    text: str
    dense_score: float
    sparse_score: float
    combined_score: float
    metadata: dict


class HybridRetriever:
    def __init__(
        self,
        vector_store: VectorStore,
        alpha: float = 0.5,
        embedding_service: EmbeddingService = None,
    ):
        self.vector_store = vector_store
        self.alpha = alpha
        self.bm25 = None
        self.embedding_service = embedding_service or EmbeddingService()

    def build_bm25_index(self):
        tokenized_corpus = [
            chunk.text.lower().split() for chunk in self.vector_store.chunks
        ]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def _normalize_scores(self, scores: list[float]) -> list[float]:
        # Min-max normalise to [0, 1], higher is better.
        min_score = min(scores)
        max_score = max(scores)
        if max_score == min_score:
            return [0.0] * len(scores)
        return [(s - min_score) / (max_score - min_score) for s in scores]

    def _normalize_distances(self, distances: list[float]) -> list[float]:
        # Convert distances to similarities — invert so lower distance = higher score.
        min_dist = min(distances)
        max_dist = max(distances)
        if max_dist == min_dist:
            return [1.0] * len(distances)
        return [1.0 - (d - min_dist) / (max_dist - min_dist) for d in distances]

    def retrieve(self, query: str, top_k: int = 5) -> list[ScoredChunk]:
        # Step 1: Dense retrieval
        query_embedding = self.embedding_service.generate_query_embedding(query)
        dense_results = self.vector_store.search(query_embedding, top_k=top_k * 2)

        # Step 2: BM25 scoring
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Step 3: Build a score map keyed by chunk_id
        score_map = {}

        # Add dense results
        distances = [dist for _, dist in dense_results]
        normalized_dense = self._normalize_distances(distances)

        for i, (chunk, dist) in enumerate(dense_results):
            score_map[chunk.chunk_id] = {
                "chunk": chunk,
                "dense_score": normalized_dense[i],
                "sparse_score": 0.0,
            }

        # Step 4: Add BM25 scores for ALL chunks
        all_chunks = self.vector_store.chunks
        normalized_bm25 = self._normalize_scores(bm25_scores.tolist())

        for i, chunk in enumerate(all_chunks):
            if chunk.chunk_id in score_map:
                score_map[chunk.chunk_id]["sparse_score"] = normalized_bm25[i]
            elif normalized_bm25[i] > 0:
                score_map[chunk.chunk_id] = {
                    "chunk": chunk,
                    "dense_score": 0.0,
                    "sparse_score": normalized_bm25[i],
                }

        # Step 5: Compute combined score and build ScoredChunks
        results = []
        for entry in score_map.values():
            combined = (
                self.alpha * entry["dense_score"]
                + (1 - self.alpha) * entry["sparse_score"]
            )
            results.append(
                ScoredChunk(
                    text=entry["chunk"].text,
                    dense_score=entry["dense_score"],
                    sparse_score=entry["sparse_score"],
                    combined_score=combined,
                    metadata={
                        "chunk_id": entry["chunk"].chunk_id,
                        "doc_id": entry["chunk"].doc_id,
                        "source": entry["chunk"].source,
                        "section_title": entry["chunk"].section_title,
                        "chunk_index": entry["chunk"].chunk_index,
                    },
                )
            )

        # Step 6: Sort by combined score (highest first) and return top_k
        results.sort(key=lambda x: x.combined_score, reverse=True)
        return results[:top_k]
