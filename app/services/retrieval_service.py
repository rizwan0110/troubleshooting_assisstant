from app.utils.text_splitter import Chunk
from app.services.vector_store import VectorStore
from app.services.embedding_service import generate_query_embedding


def retrieve_relevant_chunks(query: str, vector_store: VectorStore, top_k: int = 5) -> list[Chunk]:
    query_embedding = generate_query_embedding(query)
    results = vector_store.search(query_embedding, top_k)
    chunks = [chunk for chunk, dist in results]
    return chunks