# Overview

This project is a production-style **troubleshooting assistant for engineers** that answers questions using internal technical documentation. Engineers can ask questions related to issues they face while troubleshooting systems, and the platform retrieves relevant information from pre-ingested documents to generate helpful answers.

The system uses **hybrid retrieval (BM25 + vector search)** to find relevant content, **cross-encoder** reranking to improve document relevance, and **citation-backed responses** to ensure answers are grounded in source documents.

Documents are ingested offline by an administrator, while end users interact with the system through a query interface to retrieve information quickly and reliably.

The project is designed with **production-oriented backend practices**, including modular service architecture, evaluation pipelines, and scalable system design.

# Architecture

The system is designed around a production-style query pipeline for engineering troubleshooting. An engineer sends a question to the FastAPI API, which forwards the request to the service layer. The service layer handles the application logic and coordinates retrieval and response generation.

For answering questions, the system uses hybrid retrieval by combining BM25 and vector search to find relevant document chunks. These results are then improved using cross-encoder reranking before being passed to the LLM, which generates the final answer with citations from the retrieved documents.

Documents are ingested separately through an offline ingestion pipeline managed by an administrator. This keeps ingestion isolated from the main query path and allows the online system to focus on fast, reliable question answering.

---system diagram in system-- "C:\Users\rizwa\Desktop\Projects\rag_project_arch_1.png"

# Future Scaling

As the number of users grows, the system can scale horizontally by running multiple FastAPI instances behind a load balancer. Because the query API is designed to be stateless, requests can be distributed across different servers without depending on local session memory.

As the document collection grows, the retrieval layer can be scaled by moving to a more robust vector database and optimizing indexing and search performance. Additional improvements such as caching frequent queries, separating ingestion into its own service, and adding monitoring/tracing can further improve performance and reliability.


------------
# RAG Troubleshooting Assistant

## Overview

This project is a production-style troubleshooting assistant for engineers that answers questions using internal technical documentation. Engineers can ask questions related to issues they face while troubleshooting systems, and the platform retrieves relevant information from pre-ingested documents to generate helpful answers.

The system uses hybrid retrieval (BM25 + vector search) to find relevant content, cross-encoder reranking to improve document relevance, and citation-backed responses to ensure answers are grounded in source documents.

Documents are ingested offline by an administrator, while end users interact with the system through a query interface to retrieve information quickly and reliably.

## Tech Stack

- **API:** FastAPI (Python)
- **Embeddings:** OpenAI / sentence-transformers
- **Vector Store:** FAISS
- **Sparse Retrieval:** BM25 (rank-bm25)
- **Reranking:** Cross-encoder (sentence-transformers)
- **LLM:** OpenAI GPT (for answer generation)
- **Containerization:** Docker

## Architecture

The system follows a three-stage pipeline:

1. **Ingestion (offline)** — An administrator loads documents into the system. Documents are split into chunks, embedded, and stored in a FAISS vector index. A BM25 index is also built for keyword matching.

2. **Retrieval** — When an engineer asks a question, the system runs two searches in parallel: BM25 for keyword matching and FAISS for semantic matching. Scores from both are normalized and combined (hybrid retrieval). A cross-encoder then reranks the top candidates for precision.

3. **Generation** — The top-ranked chunks are passed to the LLM with the original question. The LLM generates an answer grounded in the retrieved chunks with citations.

---system diagram---

## Project Structure

rag_project/
├── app/
│   ├── core/           # Config, logging, middleware, exceptions
│   ├── schemas/        # Pydantic request/response models
│   ├── services/       # Business logic (retrieval, reranking, generation)
│   ├── utils/          # Text splitting, document loading
│   └── main.py         # FastAPI app and endpoints
├── eval/               # Evaluation scripts and test data
├── data/               # Source documents for ingestion
├── Dockerfile
├── requirements.txt
└── README.md

## API Endpoints

| Endpoint   | Method | Description                        |
|------------|--------|------------------------------------|
| `/health`  | GET    | Health check                       |
| `/ingest`  | POST   | Ingest documents into vector store |
| `/ask`     | POST   | Ask a question, get an answer      |

## How to Run

```bash
# Clone the repo
git clone https://github.com/yourusername/rag_project.git
cd rag_project

# Set up virtual environment
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env  # add your API keys

# Run the app
uvicorn app.main:app --reload

# Ingest documents, then query
POST /ingest
POST /ask  {"query": "What is a Docker container?", "top_k": 5}
```

## Evaluation

The project includes an evaluation pipeline that measures retrieval and generation quality.

**Retrieval Metrics:**
- **Precision@5** — of the 5 returned chunks, how many were relevant
- **Recall@5** — of all relevant chunks, how many were found in the top 5
- **MRR** — how high the first relevant chunk appears in results

Run evaluation:
```bash
python eval/run_eval.py
```

## Design Decisions

- **Hybrid retrieval over dense-only:** Dense search misses exact keyword matches (error codes, technical terms). BM25 catches these. Combining both covers more query types.
- **Reranking stage:** Bi-encoders are fast but approximate. Adding a cross-encoder reranker improves precision on the final result set.
- **Stateless API:** No session state on the server, making it easy to scale horizontally behind a load balancer.

## What's Next

- Production hardening (retry logic, rate limiting, caching)
- CI/CD pipeline
- Agentic workflow with state management