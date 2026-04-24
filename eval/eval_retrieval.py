import json
import logging
from app.services.hybrid_retriever import HybridRetriever
from app.services.reranker import Reranker

logger = logging.getLogger(__name__)


def chunk_is_relevant(chunk_text: str, keywords: list[str]) -> bool:
    text_lower = chunk_text.lower()
    matches = sum(1 for kw in keywords if kw.lower() in text_lower)
    return matches >= len(keywords) / 2


def evaluate_retrieval(
    hybrid_retriever: HybridRetriever,
    reranker: Reranker,
    test_path: str = "eval/test_questions.json",
):
    with open(test_path) as f:
        test_data = json.load(f)

    mrr_total = 0.0
    precision_total = 0.0
    recall_total = 0.0

    for item in test_data:
        query = item["query"]
        keywords = item["expected_chunk_keywords"]

        # Retrieve + Rerank
        candidates = hybrid_retriever.retrieve(query, top_k=15)
        reranked = reranker.rerank(query, candidates, top_k=5)

        # Count relevant chunks in top 5
        relevant_count = sum(1 for r in reranked if chunk_is_relevant(r.text, keywords))

        # Count total relevant chunks in full candidate pool
        total_relevant = sum(
            1 for c in candidates if chunk_is_relevant(c.text, keywords)
        )

        # Precision@5: of 5 returned, how many are relevant?
        precision_total += relevant_count / len(reranked) if reranked else 0

        # Recall@5: of all relevant chunks, how many did we return in top 5?
        recall_total += relevant_count / total_relevant if total_relevant > 0 else 0

        # MRR: position of first relevant chunk
        for i, r in enumerate(reranked):
            if chunk_is_relevant(r.text, keywords):
                mrr_total += 1.0 / (i + 1)
                break

        # Per-query log
        print(f"\nQuery: {query}")
        print(
            f"  Relevant in top 5: {relevant_count} | Total relevant: {total_relevant}"
        )

    n = len(test_data)
    print(f"\n{'='*50}")
    print(f"  RETRIEVAL EVALUATION RESULTS")
    print(f"{'='*50}")
    print(f"  Questions tested  : {n}")
    print(f"  Precision@5       : {precision_total / n:.2%}")
    print(f"  Recall@5          : {recall_total / n:.2%}")
    print(f"  MRR               : {mrr_total / n:.4f}")
    print(f"{'='*50}\n")

    return {
        "precision_at_5": precision_total / n,
        "recall_at_5": recall_total / n,
        "mrr": mrr_total / n,
    }
