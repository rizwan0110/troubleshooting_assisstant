from sentence_transformers import SentenceTransformer
from app.utils.text_splitter import Chunk
from typing import List
from app.core.retry import retry_on_api_failure
from app.core.timeout import timeout_config



model = SentenceTransformer("all-MiniLM-L6-v2")



@retry_on_api_failure(max_attempts=3, min_wait=1, max_wait=10)
def generate_embeddings(chunks: List[Chunk]) -> List[Chunk]:
    """
    Generate embeddings for a list of chunks and attach each embedding to its corresponding chunk.
    """

    texts = [chunk.text for chunk in chunks]

    embeddings = model.encode_document(texts, batch_size=32)

    for chunk, embedding in zip(chunks, embeddings):
        chunk.embedding = embedding.tolist()

    return chunks

@retry_on_api_failure(max_attempts=3, min_wait=1, max_wait=10)
def generate_query_embedding(query: str) -> List[float]:
    """
    Generate embedding for a query string.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    embedding = model.encode_query(query)

    return embedding.tolist()