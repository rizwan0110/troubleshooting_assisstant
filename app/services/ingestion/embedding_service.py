from sentence_transformers import SentenceTransformer
from app.utils.text_splitter import Chunk
from app.core.config import settings
from infra.retry import retry_on_api_failure


class EmbeddingService:
    """
    Wraps a SentenceTransformer model for document and query embedding.
    """

    def __init__(self, model_name: str = None):
        self.model = SentenceTransformer(model_name or settings.EMBEDDING_MODEL)

    @retry_on_api_failure(max_attempts=3, min_wait=1, max_wait=10)
    def generate_embeddings(self, chunks: list[Chunk]) -> list[Chunk]:
        """
        Generate embeddings for a list of chunks and attach each
        embedding to its corresponding chunk.
        """
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode_document(texts, batch_size=32)

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding.tolist()

        return chunks

    @retry_on_api_failure(max_attempts=3, min_wait=1, max_wait=10)
    def generate_query_embedding(self, query: str) -> list[float]:
        """
        Generate embedding for a query string.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        embedding = self.model.encode_query(query)
        return embedding.tolist()