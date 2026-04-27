from app.utils.document_loader import load_documents
from app.utils.text_splitter import split_document_into_chunks
from app.services.ingestion.embedding_service import EmbeddingService
from infra.vector_store import VectorStore


def ingest_documents(
    folder_path: str,
    vector_store: VectorStore,
    chunk_size: int = 500,
    embedding_service: EmbeddingService = None,
) -> dict:
    embedding_service = embedding_service or EmbeddingService()

    documents = load_documents(folder_path)

    if not documents:
        raise ValueError(f"No documents found in '{folder_path}'")

    all_chunks = []

    for doc in documents:
        chunks = split_document_into_chunks(doc, chunk_size=chunk_size)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError("No chunks were created from the documents")

    all_chunks = embedding_service.generate_embeddings(all_chunks)

    if not all_chunks[0].embedding:
        raise ValueError("Embeddings were not generated correctly")

    embedding_dimension = len(all_chunks[0].embedding)

    vector_store.create_index(embedding_dimension)
    vector_store.add_chunks(all_chunks)

    return {
        "message": "Documents ingested successfully",
        "documents_loaded": len(documents),
        "chunks_created": len(all_chunks),
        "embedding_dimension": embedding_dimension,
        "index_created": vector_store.index is not None,
        "total_chunks_in_store": len(vector_store.chunks),
    }