import sys

sys.path.append(".")

from app.services.vector_store import VectorStore
from app.services.ingest_service import ingest_documents
from app.services.hybrid_retriever import HybridRetriever
from app.services.reranker import Reranker
from eval.eval_retrieval import evaluate_retrieval

# Step 1: Ingest
vector_store = VectorStore()
ingest_documents("data/docker_docs", vector_store)

# Step 2: Initialize retriever and reranker
hybrid_retriever = HybridRetriever(vector_store, alpha=0.5)
hybrid_retriever.build_bm25_index()
reranker = Reranker()

# Step 3: Run eval
evaluate_retrieval(hybrid_retriever, reranker, test_path="eval/test_question.json")

from eval.eval_generation import evaluate_generation

# Step 4: Run Gerneration eval
evaluate_generation(hybrid_retriever, reranker, test_path="eval/test_question.json")
