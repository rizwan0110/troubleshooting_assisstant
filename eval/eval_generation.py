import json
import logging
from app.services.hybrid_retriever import HybridRetriever
from app.services.reranker import Reranker
from app.services.generation_service import generate_answer
from app.utils.text_splitter import Chunk

logger = logging.getLogger(__name__)


def evaluate_generation(hybrid_retriever: HybridRetriever, reranker: Reranker, test_path: str = "eval/test_questions.json"):
    with open(test_path) as f:
        test_data = json.load(f)

    total_keyword_score = 0.0
    total_questions = len(test_data)

    for item in test_data:
        query = item["query"]
        expected = item["expected_answer_contains"]

        # Step 1: Retrieve
        candidates = hybrid_retriever.retrieve(query, top_k=15)

        # Step 2: Rerank
        reranked = reranker.rerank(query, candidates, top_k=5)

        # Step 3: Build chunks for generation
        chunks = []
        for rc in reranked:
            chunk = Chunk(
                text=rc.text,
                chunk_id=rc.metadata.get("chunk_id", ""),
                doc_id=rc.metadata.get("doc_id", ""),
                source=rc.metadata.get("source", ""),
                section_title=rc.metadata.get("section_title", ""),
                chunk_index=rc.metadata.get("chunk_index", 0),
            )
            chunks.append(chunk)

        # Step 4: Generate answer
        result = generate_answer(query, chunks)
        answer = result.get("answer", "") if isinstance(result, dict) else str(result)
        answer_lower = answer.lower()

        # Step 5: Keyword coverage score
        matches = sum(1 for kw in expected if kw.lower() in answer_lower)
        score = matches / len(expected) if expected else 0
        total_keyword_score += score

        # Per-query log
        print(f"\nQuery: {query}")
        print(f"  Answer (first 200 chars): {answer[:200]}...")
        print(f"  Expected keywords: {expected}")
        print(f"  Matched: {matches}/{len(expected)} ({score:.2%})")

    avg_score = total_keyword_score / total_questions
    print(f"\n{'='*50}")
    print(f"  GENERATION EVALUATION RESULTS")
    print(f"{'='*50}")
    print(f"  Questions tested       : {total_questions}")
    print(f"  Avg keyword coverage   : {avg_score:.2%}")
    print(f"{'='*50}\n")

    return {
        "avg_keyword_coverage": avg_score
    }