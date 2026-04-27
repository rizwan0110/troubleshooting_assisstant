import sys

sys.path.append(".")

from app.services.vector_store import VectorStore
from app.services.ingest_service import ingest_documents
from app.services.hybrid_retriever import HybridRetriever
from app.services.reranker import Reranker
from eval.eval_retrieval import evaluate_retrieval
from eval.eval_generation import evaluate_generation

# Step 1: Ingest
vector_store = VectorStore()
ingest_documents("data/docker_docs", vector_store)

# Step 2: Initialize retriever and reranker
hybrid_retriever = HybridRetriever(vector_store, alpha=0.5)
hybrid_retriever.build_bm25_index()
reranker = Reranker()

# Step 3: Run retrieval eval
results = evaluate_retrieval(hybrid_retriever, reranker, test_path="eval/test_questions.json")

# Step 4: Run generation eval
evaluate_generation(hybrid_retriever, reranker, test_path="eval/test_questions.json")

# Step 5: CI gate
MIN_PRECISION = 0.40    # current: 0.48
MIN_MRR = 0.65          # current: 0.75
MIN_RECALL = 0.50       # current: 0.60

failed = False

if results["recall"] < MIN_RECALL:
    print(f"FAIL: Recall {results['recall']:.2%} is below minimum {MIN_RECALL:.2%}")
    failed = True

if results["mrr"] < MIN_MRR:
    print(f"FAIL: MRR {results['mrr']:.4f} is below minimum {MIN_MRR:.4f}")
    failed = True

if results["precision_at_5"] < MIN_PRECISION:
    print(f"FAIL: Precision@5 {results['precision_at_5']:.2%} is below minimum {MIN_PRECISION:.2%}")
    failed = True

if failed:
    print("\nCI GATE: FAILED — evaluation scores below threshold")
    sys.exit(1)
else:
    print("\nCI GATE: PASSED")