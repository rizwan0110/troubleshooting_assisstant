"""
Shared utilities for chunk conversion.

Centralising RerankedChunk → Chunk conversion here ensures that
prod (routes.py) and eval (eval_generation.py) always use identical
logic — preventing silent eval/prod mismatches.
"""
from typing import List
from app.services.retrieval.reranker import RerankedChunk
from app.utils.text_splitter import Chunk


def reranked_to_chunks(reranked: List[RerankedChunk]) -> List[Chunk]:
    """Convert a list of RerankedChunk objects to Chunk objects."""
    return [
        Chunk(
            text=rc.text,
            chunk_id=rc.metadata.get("chunk_id", ""),
            doc_id=rc.metadata.get("doc_id", ""),
            source=rc.metadata.get("source", ""),
            section_title=rc.metadata.get("section_title", ""),
            chunk_index=rc.metadata.get("chunk_index", 0),
        )
        for rc in reranked
    ]