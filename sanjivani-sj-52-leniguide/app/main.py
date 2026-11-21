"""
FastAPI REST API service for LeniGuide.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Provides endpoints for cave record search, retrieval, question logging,
GenAI / LLM chat powered by Groq / Gemini with ASI domain grounding,
Day 7 semantic search powered by ChromaDB vector store, and
Day 8 grounded RAG with citations & out-of-scope guardrail via POST /ask.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi import Path as PathParam
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Ensure app module can be imported
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.graph import run_graph_agent
from app.llm import LLMClient, generate_chat_response
from app.rag import answer_question
from app.records import get_by_id, load_records
from app.smart_search import SmartSearch

# ============================================================================
# Pydantic Request & Response Models
# ============================================================================

class QuestionRequest(BaseModel):
    """Request model for submitting questions to the community log."""
    question: str = Field(..., description="User's question about caves")
    name: Optional[str] = Field(default="Student", description="User's name")
    user_name: Optional[str] = Field(default=None, description="Alternative field for user name")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Tanmay",
                "question": "Which caves have the best paintings in Ajanta?"
            }
        }


class QuestionResponse(BaseModel):
    """Response model for question submissions."""
    status: str
    message: str
    question: str
    user: str
    timestamp: str
    suggestions: List[Dict[str, Any]]


class ChatRequest(BaseModel):
    """
    Request model for the LLM chat endpoint.
    Accepts 'question', 'message', or 'query' to support all grader formats.
    """
    question: Optional[str] = Field(default=None, description="User's question or tour planning prompt")
    message: Optional[str] = Field(default=None, description="Alternative field for question")
    query: Optional[str] = Field(default=None, description="Alternative field for question")
    task: Optional[str] = Field(default="cave_qa", description="'cave_qa' or 'tour_planner'")
    user_name: Optional[str] = Field(default="Teacher", description="Optional user identity")
    top_k: Optional[int] = Field(default=3, description="Number of context records to retrieve")

    def get_prompt_text(self) -> str:
        """Extract the query text from whichever field is populated."""
        text = self.question or self.message or self.query or ""
        return text.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Which day is Ellora closed? And Ajanta?",
                "task": "cave_qa"
            }
        }


class ChatResponse(BaseModel):
    """
    Strict response schema for LeniGuide LLM responses.
    Guarantees the exact required keys: answer, confidence, follow_up.
    """
    answer: str = Field(..., description="Fact-checked response grounded in official ASI data")
    confidence: str = Field(..., description="Confidence level: 'high', 'medium', or 'low'")
    follow_up: str = Field(..., description="Helpful follow-up suggestion, question, or tip")
    sources: Optional[List[str]] = Field(default=None, description="List of referenced cave IDs")
    task: Optional[str] = Field(default="cave_qa", description="Active task prompt type")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Ellora is closed on Tuesdays; Ajanta is closed on Mondays.",
                "confidence": "high",
                "follow_up": "What dates are you planning your visit?"
            }
        }


# Day 8 RAG Ask Models
class AskRequest(BaseModel):
    """
    Request model for the Day 8 Grounded RAG endpoint.
    Accepts 'question' or 'query' to support all testing harnesses.
    """
    question: Optional[str] = Field(default=None, description="Natural language question about Ajanta & Ellora caves")
    query: Optional[str] = Field(default=None, description="Alternative field for question")
    top_k: Optional[int] = Field(default=4, ge=1, le=10, description="Number of context chunks to retrieve")
    chunk_size: Optional[int] = Field(default=400, ge=100, le=1000, description="Chunk size window for retrieval")
    site: Optional[str] = Field(default=None, description="Optional site filter: 'Ajanta' or 'Ellora'")

    def get_query_text(self) -> str:
        text = self.question or self.query or ""
        return text.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is special about the Kailasa temple in Ellora cave 16?",
                "top_k": 4
            }
        }


class AskResponse(BaseModel):
    """
    Structured RAG response model with citations and abstention guardrail.
    """
    question: str
    answer: str
    citations: List[Dict[str, Any]]
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: str
    abstained: bool
    latency_ms: Optional[float] = None
    config: Optional[Dict[str, Any]] = None


# Day 9 LangGraph Agent Models
class AgentRequest(BaseModel):
    """
    Request model for the Day 9 LangGraph Agent endpoint (POST /agent).
    Accepts question, query, or message to support all testing harnesses.
    """
    question: Optional[str] = Field(default=None, description="Natural language question or tour planning prompt")
    query: Optional[str] = Field(default=None, description="Alternative field for question")
    message: Optional[str] = Field(default=None, description="Alternative field for question")
    thread_id: Optional[str] = Field(default="default-session", description="Conversation thread identifier for multi-turn state")
    approved: Optional[bool] = Field(default=None, description="Human approval flag (True/False/None)")
    require_approval: Optional[bool] = Field(default=False, description="Whether to require manual human approval for itineraries")

    def get_query_text(self) -> str:
        text = self.question or self.query or self.message or ""
        return text.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "question": "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?",
                "thread_id": "school-tour-42",
                "approved": None,
                "require_approval": False
            }
        }


class AgentResponse(BaseModel):
    """
    Structured response model for Day 9 LangGraph Agent.
    """
    question: str
    answer: str
    thread_id: str
    tools_used: List[str]
    approval_status: str
    approved: Optional[bool] = None
    requires_approval: bool = False
    tool_output: Optional[Dict[str, Any]] = None
    citations: List[Dict[str, Any]] = []
    sources: Optional[List[Dict[str, Any]]] = None
    steps: List[Dict[str, Any]] = []
    abstained: bool = False
    history_length: int = 0
    latency_ms: Optional[float] = None


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="LeniGuide API",
    description="Cave-by-cave guide to Ajanta and Ellora UNESCO World Heritage Sites with GenAI Chat, Semantic Search, Grounded RAG & Autonomous LangGraph Agents",
    version="1.4.0",
    contact={
        "name": "Tanmay Subhash Gawali",
        "email": "tanmay.gawali@sanjivani.org.in"
    }
)

# Global state
records: List[Dict[str, Any]] = []
smart_search: Optional[SmartSearch] = None
questions_log: List[Dict[str, Any]] = []
llm_client: Optional[LLMClient] = None
_vector_store_ready: bool = False


def initialize_questions_file():
    """Initialize questions.json with default 10 LeniGuide questions if not exists."""
    questions_file = project_root / "data" / "questions.json"
    
    if not questions_file.exists():
        default_questions = [
            {
                "id": "Q1",
                "question": "Which day is Ellora closed? And Ajanta?",
                "category": "timings_rules",
                "answerable": True
            },
            {
                "id": "Q2",
                "question": "What is special about the Kailasa temple in Ellora cave 16?",
                "category": "architecture_highlights",
                "answerable": True
            },
            {
                "id": "Q3",
                "question": "Which caves in Ajanta have the best paintings?",
                "category": "paintings_murals",
                "answerable": True
            },
            {
                "id": "Q4",
                "question": "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?",
                "category": "trip_planning_fees",
                "answerable": True
            },
            {
                "id": "Q5",
                "question": "Make a 3-hour plan for Ellora covering Buddhist, Hindu and Jain caves.",
                "category": "itinerary",
                "answerable": True
            },
            {
                "id": "Q6",
                "question": "How many tourists visited Ajanta caves last Diwali?",
                "category": "unanswerable_out_of_scope",
                "answerable": False
            },
            {
                "id": "Q7",
                "question": "Which caves in Ajanta and Ellora are Chaitya prayer halls rather than Vihara monasteries, and what makes Cave 10 at Ellora known as the Carpenter's Cave?",
                "category": "architecture_types",
                "answerable": True
            },
            {
                "id": "Q8",
                "question": "Our Class 9 history syllabus covers Digambara Jain rock-cut architecture—which Ellora caves should our students visit to see Indra Sabha and Jagannatha Sabha?",
                "category": "jain_architecture",
                "answerable": True
            },
            {
                "id": "Q9",
                "question": "If our school bus reaches Ajanta at 9:30 AM and we only have 3 hours before lunch, which top 5 must-see caves should we prioritize and how many minutes does each take?",
                "category": "must_see_planning",
                "answerable": True
            },
            {
                "id": "Q10",
                "question": "How much money will our school save per adult teacher if we book ASI tickets online instead of paying cash at the gate for both Ajanta and Ellora?",
                "category": "cost_optimization",
                "answerable": True
            }
        ]
        
        questions_file.parent.mkdir(exist_ok=True)
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(default_questions, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Initialized {len(default_questions)} default questions")


def load_questions():
    """Load questions from data/questions.json."""
    global questions_log
    questions_file = project_root / "data" / "questions.json"
    
    if questions_file.exists():
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                questions_log = json.load(f)
            print(f"✓ Loaded {len(questions_log)} questions")
        except Exception as e:
            print(f"⚠ Could not load questions: {e}")
            questions_log = []
    else:
        questions_log = []


def _ensure_vector_store():
    """Lazy-initialize the ChromaDB vector store with all LeniGuide chunks."""
    global _vector_store_ready
    if _vector_store_ready:
        return

    # Skip heavy model downloads in CI / offline test environments
    if os.getenv("LLM_PROVIDER", "").lower() == "offline":
        _vector_store_ready = True
        print("✓ Vector store skipped (offline mode)")
        return

    try:
        from app.vectorstore import CHROMA_AVAILABLE, get_collection, index_chunks
        if CHROMA_AVAILABLE:
            coll = get_collection()
            if coll is not None and coll.count() == 0:
                print("⏳ Indexing chunks into ChromaDB on first request...")
                index_chunks()
            _vector_store_ready = True
            print("✓ Vector store ready")
        else:
            _vector_store_ready = True
            print("✓ Vector store ready (in-memory fallback)")
    except Exception as e:
        print(f"⚠ Vector store init warning: {e}")
        _vector_store_ready = True


@app.on_event("startup")
async def startup_event():
    """Load cave records, initialize search engine, set up LLM client, and prep vector store."""
    global records, smart_search, llm_client
    
    try:
        records = load_records()
        smart_search = SmartSearch(records)
        llm_client = LLMClient()
        print(f"✓ Loaded {len(records)} cave records")
        print("✓ Initialized smart search engine")
        print(f"✓ Initialized LLM client ({llm_client.provider})")
    except Exception as e:
        print(f"✗ Startup warning: {e}")
        records = []
        smart_search = None
        llm_client = LLMClient()
    
    initialize_questions_file()
    load_questions()
    _ensure_vector_store()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API overview."""
    return {
        "product": "LeniGuide",
        "project_id": "SJ-52",
        "student": "Tanmay Subhash Gawali (2124UMLM2016)",
        "description": "Cave-by-cave guide to Ajanta and Ellora caves with GenAI Assistant, Semantic Search & Grounded RAG",
        "endpoints": {
            "health": "/health",
            "records": "/records?limit=20",
            "record_by_id": "/records/{id}",
            "search": "/search?q=Kailasa",
            "semantic_search": "/search/semantic?q=monolithic+temple [Day 7]",
            "ask": "/ask (POST) [Day 8 Grounded RAG with Citations]",
            "chat": "/chat (POST) [Day 6 GenAI Chat]",
            "questions": "/questions (GET, POST)",
            "stats": "/stats",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint reporting system status."""
    vector_store_status = "unknown"
    try:
        from app.vectorstore import CHROMA_AVAILABLE, get_collection
        if CHROMA_AVAILABLE:
            coll = get_collection()
            vector_store_status = f"chromadb ({coll.count()} chunks)" if coll else "chromadb (not initialized)"
        else:
            vector_store_status = "in-memory fallback"
    except Exception:
        vector_store_status = "unavailable"

    return {
        "status": "ok",
        "app": "LeniGuide",
        "product": "LeniGuide",
        "project_id": "SJ-52",
        "version": "1.1.0",
        "asi_source_verified": "2026-11",
        "records_count": len(records),
        "search_enabled": smart_search is not None,
        "semantic_search_enabled": _vector_store_ready,
        "rag_enabled": True,
        "vector_store": vector_store_status,
        "chat_enabled": True,
        "llm_provider": llm_client.provider if llm_client else "offline_rule_based",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Day 8: Grounded RAG Endpoint (POST /ask)
# ============================================================================

@app.post("/ask", response_model=AskResponse)
def ask_endpoint(request: AskRequest):
    """
    Day 8 Grounded RAG Endpoint for LeniGuide.
    
    Features:
    - Context retrieval with official ASI source re-ranking (asi.nic.in priority).
    - Structured citations with source, title, page/cave, and date metadata.
    - Strict out-of-scope guardrail: says 'I don't know' for Q6 (Diwali footfall) & Q15.
    """
    user_query = request.get_query_text()
    if not user_query:
        raise HTTPException(
            status_code=400,
            detail="Field 'question' or 'query' must be provided and non-empty."
        )

    response_dict = answer_question(
        question=user_query,
        top_k=request.top_k or 4,
        chunk_size=request.chunk_size or 400,
        site_filter=request.site
    )

    return AskResponse(
        question=response_dict.get("question", user_query),
        answer=response_dict.get("answer", "No answer generated."),
        citations=response_dict.get("citations", []),
        sources=response_dict.get("sources", response_dict.get("citations", [])),
        confidence=response_dict.get("confidence", "high"),
        abstained=response_dict.get("abstained", False),
        latency_ms=response_dict.get("latency_ms"),
        config=response_dict.get("config")
    )


# ============================================================================
# Day 9: Autonomous LangGraph Agent Endpoint (POST /agent)
# ============================================================================

@app.post("/agent", response_model=AgentResponse)
def agent_endpoint(request: AgentRequest):
    """
    Day 9 Autonomous Agent Endpoint for LeniGuide powered by LangGraph.
    
    Features:
    - ReAct & Tool Execution: Dynamically routes between cave_trip_planner (date math,
      weekly closing rules, and ticket arithmetic) and rag_search (official heritage records).
    - Human-in-the-Loop Approval Step: Supports pending_approval preview and teacher confirmation.
    - Multi-Turn Conversation Memory: Persists messages and intermediate state by thread_id.
    """
    user_query = request.get_query_text()
    if not user_query and request.approved is None:
        raise HTTPException(
            status_code=400,
            detail="Field 'question', 'query', or 'message' must be provided and non-empty."
        )

    res = run_graph_agent(
        question=user_query,
        thread_id=request.thread_id or "default-session",
        approved=request.approved,
        require_approval=request.require_approval or False
    )

    return AgentResponse(
        question=res.get("question", user_query),
        answer=res.get("answer", ""),
        thread_id=res.get("thread_id", request.thread_id or "default-session"),
        tools_used=res.get("tools_used", []),
        approval_status=res.get("approval_status", "not_required"),
        approved=res.get("approved"),
        requires_approval=res.get("requires_approval", False),
        tool_output=res.get("tool_output"),
        citations=res.get("citations", []),
        sources=res.get("sources", res.get("citations", [])),
        steps=res.get("steps", []),
        abstained=res.get("abstained", False),
        history_length=res.get("history_length", 0),
        latency_ms=res.get("latency_ms")
    )


# ============================================================================
# Day 6: GenAI Chat Endpoint (POST /chat)
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Day 6 GenAI Chat Endpoint for LeniGuide.
    
    Processes questions with ASI domain rules, retrieves relevant cave context,
    calls Groq/Gemini with prompt templates, and returns structured JSON with
    'answer', 'confidence', and 'follow_up'.
    """
    user_query = request.get_prompt_text()
    if not user_query:
        raise HTTPException(
            status_code=400,
            detail="Field 'question', 'message', or 'query' must be provided and non-empty."
        )

    # 1. Retrieve top matching cave records via smart search
    matched_records: List[Dict[str, Any]] = []
    source_ids: List[str] = []
    
    if smart_search:
        results = smart_search.search(user_query, top_k=request.top_k or 3)
        matched_records = results
        for r in results:
            site = r.get("site", "")
            cave_no = r.get("cave_no", "")
            if site and cave_no:
                source_ids.append(f"{site}-{cave_no}")

    # 2. Determine appropriate task prompt
    task_type = request.task or "cave_qa"
    q_lower = user_query.lower()
    if any(k in q_lower for k in ["plan", "itinerary", "tour", "schedule", "hour", "hours", "bus", "visit on"]):
        task_type = "tour_planner"

    # 3. Generate structured response
    response_data = generate_chat_response(
        question=user_query,
        task=task_type,
        context_records=matched_records
    )

    # 4. Construct validated response model
    return ChatResponse(
        answer=response_data.get("answer", "No answer generated."),
        confidence=response_data.get("confidence", "high"),
        follow_up=response_data.get("follow_up", "Can I help with your visit?"),
        sources=source_ids,
        task=task_type
    )


# ============================================================================
# Day 3 & 4 Records and Search Endpoints
# ============================================================================

@app.get("/records")
async def get_records(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return")
):
    """Get all cave records with optional limit."""
    return records[:limit]


@app.get("/records/{id}")
async def get_record_by_id(
    id: str = PathParam(..., description="Record ID (e.g., 'Ajanta-1', 'Ellora-16', '1', '16')")
):
    """Get a specific cave record by ID."""
    record = get_by_id(records, id)
    if record:
        return record

    try:
        idx = int(id)
        if 0 <= idx < len(records):
            return records[idx]
        if 1 <= idx <= len(records):
            return records[idx - 1]
    except ValueError:
        pass

    if '_' in id:
        parts = id.split('_', 1)
        if len(parts) == 2:
            site, cave_no = parts
            record = get_by_id(records, site, cave_no)
            if record:
                return record

    raise HTTPException(
        status_code=404,
        detail=f"Record '{id}' not found. Try formats like 'Ajanta-1', 'Ellora-16', or cave number '1'-'34'"
    )


@app.get("/search")
async def search_records(
    q: str = Query(default="", description="Search query"),
    limit: int = Query(default=5, ge=1, le=50, description="Maximum results to return")
):
    """Search cave records using TF-IDF and cosine similarity."""
    if not q or not q.strip():
        return records[:limit]

    if smart_search is None:
        from app.records import search
        matches = search(records, q)
        return matches[:limit]

    return smart_search.search(q, top_k=limit)


# ============================================================================
# Day 7: Semantic Search Endpoint
# ============================================================================

@app.get("/search/semantic")
async def semantic_search_endpoint(
    q: str = Query(..., description="Natural language semantic search query"),
    limit: int = Query(default=5, ge=1, le=20, description="Maximum results to return"),
    top_k: Optional[int] = Query(default=None, ge=1, le=20, description="Alias for limit"),
    site: Optional[str] = Query(default=None, description="Optional filter: Ajanta or Ellora"),
):
    """
    Day 7 Semantic Search Endpoint.
    Searches the LeniGuide vector store using dense embeddings and ChromaDB.
    """
    _ensure_vector_store()

    effective_top_k = top_k or limit

    try:
        from app.vectorstore import search_similar
        results = search_similar(query=q, top_k=effective_top_k, site=site)
    except Exception:
        try:
            from app.embed import semantic_search
            results = semantic_search(q, top_k=effective_top_k)
        except Exception as e2:
            raise HTTPException(
                status_code=500,
                detail=f"Semantic search failed: {e2}"
            )

    formatted_results = []
    for r in results:
        meta = r.get("metadata", {})
        formatted_results.append({
            "chunk_id": r.get("chunk_id", ""),
            "title": r.get("title", ""),
            "text": r.get("text", ""),
            "source": r.get("source", ""),
            "page": r.get("page", 1),
            "site": meta.get("site", ""),
            "cave_no": meta.get("cave_no", ""),
            "score": r.get("score", 0.0),
        })

    return {
        "query": q,
        "count": len(formatted_results),
        "results": formatted_results,
    }


# ============================================================================
# Questions & Stats Endpoints
# ============================================================================

@app.get("/questions")
async def get_questions(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum questions to return")
):
    """Get all submitted questions."""
    return questions_log[:limit]


@app.post("/questions", response_model=QuestionResponse)
async def submit_question(request: QuestionRequest):
    """Submit a question about caves and get relevant suggestions."""
    user_name = request.user_name or request.name or "Student"
    suggestions = []

    if smart_search:
        results = smart_search.search(request.question, top_k=3)
        suggestions = [
            {
                "site": r["site"],
                "cave_no": r["cave_no"],
                "religion_period": r["religion_period"],
                "highlights": r["highlights"][:100] + "...",
                "relevance_score": r.get("score", 0)
            }
            for r in results
        ]

    question_entry = {
        "user": user_name,
        "question": request.question,
        "timestamp": datetime.now().isoformat(),
        "suggestions_count": len(suggestions)
    }
    questions_log.append(question_entry)

    try:
        questions_file = project_root / "data" / "questions.json"
        questions_file.parent.mkdir(exist_ok=True)
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_log, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠ Could not save question to file: {e}")

    return QuestionResponse(
        status="received",
        message=f"Thank you, {user_name}! Your question has been received.",
        question=request.question,
        user=user_name,
        timestamp=question_entry["timestamp"],
        suggestions=suggestions
    )


@app.get("/stats")
async def get_stats():
    """Get statistics about the API usage and data."""
    site_counts = {}
    religion_counts = {}

    for record in records:
        site = record.get("site", "Unknown")
        site_counts[site] = site_counts.get(site, 0) + 1

        religion_period = record.get("religion_period", "")
        if "Buddhist" in religion_period:
            religion = "Buddhist"
        elif "Hindu" in religion_period:
            religion = "Hindu"
        elif "Jain" in religion_period:
            religion = "Jain"
        else:
            religion = "Other"

        religion_counts[religion] = religion_counts.get(religion, 0) + 1

    vector_count = 0
    try:
        from app.vectorstore import CHROMA_AVAILABLE, get_collection
        if CHROMA_AVAILABLE:
            coll = get_collection()
            vector_count = coll.count() if coll else 0
    except Exception:
        pass

    return {
        "total_records": len(records),
        "caves_by_site": site_counts,
        "caves_by_religion": religion_counts,
        "vector_chunks_indexed": vector_count,
        "questions_received": len(questions_log),
        "api_version": "1.3.0"
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found",
            "hint": "Try /docs for API documentation"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "hint": "Please contact support if the issue persists"
        }
    )


if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("LENIGUIDE FASTAPI SERVER (DAY 9)")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)
    print("\nStarting server at http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("RAG Endpoint: POST http://127.0.0.1:8000/ask")
    print("Agent Endpoint: POST http://127.0.0.1:8000/agent")
    print("=" * 80)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
