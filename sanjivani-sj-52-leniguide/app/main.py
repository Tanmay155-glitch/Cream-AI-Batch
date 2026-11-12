"""
FastAPI REST API service for LeniGuide.
Provides endpoints for cave record search, retrieval, and question handling.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from fastapi import FastAPI, Query, HTTPException, Path as PathParam
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Ensure app module can be imported
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.records import load_records, get_by_id
from app.smart_search import SmartSearch


# ============================================================================
# Pydantic Models
# ============================================================================

class QuestionRequest(BaseModel):
    """Request model for submitting questions."""
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


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="LeniGuide API",
    description="Cave-by-cave guide to Ajanta and Ellora UNESCO World Heritage Sites",
    version="1.0.0",
    contact={
        "name": "Tanmay Subhash Gawali",
        "email": "tanmay.gawali@sanjivani.org.in"
    }
)

# Global state
records: List[Dict[str, Any]] = []
smart_search: Optional[SmartSearch] = None
questions_log: List[Dict[str, Any]] = []


def initialize_questions_file():
    """Initialize questions.json with default 10 LeniGuide questions if not exists."""
    questions_file = project_root / "data" / "questions.json"
    
    if not questions_file.exists():
        # Default 10 questions for LeniGuide
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


@app.on_event("startup")
async def startup_event():
    """Load cave records, initialize search, and load questions on startup."""
    global records, smart_search
    
    try:
        records = load_records()
        smart_search = SmartSearch(records)
        print(f"✓ Loaded {len(records)} cave records")
        print(f"✓ Initialized smart search engine")
    except Exception as e:
        print(f"✗ Error loading records: {e}")
        records = []
        smart_search = None
    
    # Initialize and load questions
    initialize_questions_file()
    load_questions()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "product": "LeniGuide",
        "project_id": "SJ-52",
        "student": "Tanmay Subhash Gawali (2124UMLM2016)",
        "description": "Cave-by-cave guide to Ajanta and Ellora caves",
        "endpoints": {
            "health": "/health",
            "records": "/records?limit=20",
            "record_by_id": "/records/{id}",
            "search": "/search?q=Kailasa",
            "questions": "/questions (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns API status and basic statistics.
    """
    return {
        "status": "ok",
        "product": "LeniGuide",
        "project_id": "SJ-52",
        "records_count": len(records),
        "search_enabled": smart_search is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/records")
async def get_records(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return")
):
    """
    Get all cave records with optional limit.
    
    Args:
        limit: Maximum number of records to return (1-100)
    
    Returns:
        List of cave records
    """
    return records[:limit]


@app.get("/records/{id}")
async def get_record_by_id(
    id: str = PathParam(..., description="Record ID (e.g., 'Ajanta-1', 'Ellora-16', '1', '16')")
):
    """
    Get a specific cave record by ID.
    
    Supports multiple ID formats:
    - Composite: "Ajanta-1", "Ellora-16", "ajanta_1" (case-insensitive)
    - Cave number: "1", "16", "32"
    - Record index: 1-20 (1-based) or 0-19 (0-based)
    
    Args:
        id: Record identifier
    
    Returns:
        Cave record dictionary
    
    Raises:
        HTTPException: 404 if record not found
    """
    # Try composite ID or cave number lookup
    record = get_by_id(records, id)
    
    if record:
        return record
    
    # Try as integer index (handle both 0-based and 1-based)
    try:
        idx = int(id)
        
        # Try 0-based index
        if 0 <= idx < len(records):
            return records[idx]
        
        # Try 1-based index
        if 1 <= idx <= len(records):
            return records[idx - 1]
    except ValueError:
        pass
    
    # Try underscore separator (Ajanta_1)
    if '_' in id:
        parts = id.split('_', 1)
        if len(parts) == 2:
            site, cave_no = parts
            record = get_by_id(records, site, cave_no)
            if record:
                return record
    
    # Record not found
    raise HTTPException(
        status_code=404,
        detail=f"Record '{id}' not found. Try formats like 'Ajanta-1', 'Ellora-16', or cave number '1'-'34'"
    )


@app.get("/search")
async def search_records(
    q: str = Query(default="", description="Search query"),
    limit: int = Query(default=5, ge=1, le=50, description="Maximum results to return")
):
    """
    Search cave records using TF-IDF and cosine similarity.
    
    Args:
        q: Search query (e.g., "Kailasa temple", "Buddhist paintings")
        limit: Maximum number of results (1-50)
    
    Returns:
        List of matching cave records with similarity scores
    """
    if not q or not q.strip():
        # Return first N records if no query
        return records[:limit]
    
    if smart_search is None:
        # Fallback to simple substring search if smart search unavailable
        from app.records import search
        matches = search(records, q)
        return matches[:limit]
    
    # Use TF-IDF smart search
    results = smart_search.search(q, top_k=limit)
    
    return results


@app.get("/questions")
async def get_questions(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum questions to return")
):
    """
    Get all submitted questions.
    
    Args:
        limit: Maximum number of questions to return
    
    Returns:
        List of questions
    """
    return questions_log[:limit]


@app.post("/questions", response_model=QuestionResponse)
async def submit_question(request: QuestionRequest):
    """
    Submit a question about caves and get relevant suggestions.
    
    Args:
        request: Question request with user name and question text
    
    Returns:
        Question response with status and cave suggestions
    """
    # Determine user name (support both 'name' and 'user_name' fields)
    user_name = request.user_name or request.name or "Student"
    
    # Get relevant cave suggestions using smart search
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
    
    # Log the question
    question_entry = {
        "user": user_name,
        "question": request.question,
        "timestamp": datetime.now().isoformat(),
        "suggestions_count": len(suggestions)
    }
    questions_log.append(question_entry)
    
    # Save to file
    try:
        questions_file = project_root / "data" / "questions.json"
        questions_file.parent.mkdir(exist_ok=True)
        
        # Save updated list (append new user-submitted questions only, preserve originals)
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
    # Count caves by site
    site_counts = {}
    religion_counts = {}
    
    for record in records:
        site = record.get("site", "Unknown")
        site_counts[site] = site_counts.get(site, 0) + 1
        
        # Extract religion from religion_period
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
    
    return {
        "total_records": len(records),
        "caves_by_site": site_counts,
        "caves_by_religion": religion_counts,
        "questions_received": len(questions_log),
        "api_version": "1.0.0"
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


# ============================================================================
# Main Entry Point (for testing)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("LENIGUIDE FASTAPI SERVER")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)
    print("\nStarting server at http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 80)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
