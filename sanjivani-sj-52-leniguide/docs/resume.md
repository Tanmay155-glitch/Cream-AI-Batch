# Resume Bullets — LeniGuide (SJ-52)

**Student:** Tanmay Subhash Gawali | **Reg No:** 2124UMLM2016 | **Branch:** CSE AI & ML

---

## AI / ML Engineering Resume Bullets

1. **Built LeniGuide**, a production-grade Retrieval-Augmented Generation (RAG) application serving 20 verified UNESCO heritage cave records via FastAPI, ChromaDB vector search (`chunk_size=450, top_k=4`), and ASI source re-ranking — achieving **93.3% evaluation accuracy** across a 15-row benchmark with **100% out-of-scope abstention** and **< 320 ms p95 cold-query latency** on Groq Llama-3.1-8B.

2. **Designed and deployed a multi-agent LangGraph workflow** with autonomous tool routing (`cave_trip_planner` date-math + `rag_search`), human-in-the-loop approval gating, and thread-based conversation memory — delivering **100% ticket-arithmetic accuracy** (₹320 cash / ₹280 online for 4 adults + 40 free students) while reducing repeated-query latency by **99%** via a TTL response cache; hardened the API with input-length validation, compiled-regex prompt-injection filtering, and structured JSON observability logging (latency, tokens, cost per request).

3. **Containerized and continuously deployed** the full-stack application (FastAPI + Streamlit) using Docker Compose, automated a **14-test pytest suite** (covering RAG citations, agent tool calls, security guardrails, and cache behaviour) and **Ruff linting** in GitHub Actions CI, and shipped to Render cloud with a public health endpoint — all documented in a portfolio-ready README with a Mermaid architecture diagram, evaluation results table, and production metrics.
