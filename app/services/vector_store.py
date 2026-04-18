import faiss
import numpy as np
from app.utils.text_splitter import Chunk


class VectorStore:
    def __init__(self):
        self.index = None
        self.chunks = []

    def create_index(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)

    def add_chunks(self, chunks: list[Chunk]):
        if self.index is None:
            raise ValueError("Index not created")

        embeddings = [chunk.embedding for chunk in chunks]

        if not embeddings or any(embedding is None for embedding in embeddings):
            raise ValueError("Some chunks do not have embeddings")

        embeddings_array = np.array(embeddings, dtype="float32")
        self.index.add(embeddings_array)
        self.chunks.extend(chunks)

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[tuple]:
        if self.index is None:
            raise ValueError("Index not created")

        if not self.chunks:
            raise ValueError("No chunks available in vector store")

        top_k = min(top_k, len(self.chunks))

        query_array = np.array(query_embedding, dtype="float32").reshape(1, -1)

        distances, indices = self.index.search(query_array, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1:
                results.append((self.chunks[idx], dist))

        return results
    
vector_store = VectorStore()