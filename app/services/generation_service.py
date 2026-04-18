from typing import List
from app.utils.text_splitter import Chunk
from infra.llm_client import generate_response
from app.core.retry import retry_on_api_failure


@retry_on_api_failure(max_attempts=3, min_wait=1, max_wait=10)
def generate_answer(query: str, chunks: List[Chunk]) -> dict:
    context_text = "\n\n".join(
        [
            f"Source: {chunk.source}\nSection: {chunk.section_title}\nContent: {chunk.text}"
            for chunk in chunks
        ]
    )

    prompt = f"""
You are an AI troubleshooting assistant for support engineers and developer.

Use ONLY the provided context to answer the question.

If the answer is not found in the context, say:
"I could not find enough information in the documentation."


Context:
{context_text}

Question:
{query}
"""

    
    answer = generate_response(prompt, query=query)
    sources = [
        {
            "chunk_id": chunk.chunk_id,
            "doc_id": chunk.doc_id,
            "source": chunk.source,
            "section_title": chunk.section_title,
        }
        for chunk in chunks
    ]

    return {
        "answer": answer,
        "sources": sources
    }